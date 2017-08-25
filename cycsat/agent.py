import os
import sys

from math import pow
from math import sqrt
from math import floor

import re
import io
import imageio

import pandas as pd
from geopandas import GeoDataFrame
import numpy as np
import random
import rasterio
from matplotlib import pyplot as plt

from skimage.draw import polygon
from skimage.transform import rotate as rotate_image
from skimage.transform import downscale_local_mean

from shapely.geometry import Point, box
from shapely.affinity import rotate, translate
from shapely.ops import cascaded_union, unary_union, polygonize

from .geometry import posit_point, grid, intersect, rescale
from .geometry import shift_geometry
from .laboratory import Material
from .metrics import Log


class Agent:

    def __init__(self, name=None, level=0, **attrs):

        self._handle = name
        self._dependents = list()
        self._material = False
        self.agents = list()
        self.rules = list()
        self.journal = list()
        self.level = level
        self.time = 0
        self.attrs = attrs
        self.parent = False
        self._placed = False

        self.log(init=True)

    def __repr__(self):
        return '<{}>'.format(self._handle)

    @property
    def name(self):
        if self._handle:
            return self._handle
        else:
            return self.__class__.__name__

    def rename(self, name):
        self._handle = name

    @property
    def _depth(self):
        """Determines the agent's level by looking for ancestors."""
        level = 0
        if self.parent:
            level += 1
            level += self.parent._depth
        return level

    def print_diagram(self):
        """Prints a diagram of this agents and all its children"""
        print('    ' * self._depth, self)
        for agent in self.agents:
            agent.print_diagram()

    def log(self, init=False):
        """Looks for changes and logs the agents attributes if there is a change."""
        log = Log(agent=self)

        if init:
            self.time = 0
            self.journal = list()
            for attr in self.attrs:
                setattr(self, attr, self.attrs[attr])
            for agent in self.agents:
                agent.log(init=True)

        for attr in self.attrs:
            setattr(log, attr, getattr(self, attr))

        log.time = self.time

        if log.geometry is not None:
            self.journal.append(log)

    @property
    def dataframe(self):
        data = [log.data for log in self.journal]
        return GeoDataFrame(data)

    def _collect_agents(self, origin=[], agentframe=None):
        """Collects agents by cascading to gather information for global placement."""
        if len(origin) == 0:
            origin = np.array([0, 0])
            agentframe = pd.DataFrame()
        else:
            agentframe = agentframe.append({'agent': self,
                                            'depth': self._depth,
                                            'level': self.level,
                                            'origin': origin.copy()}, ignore_index=True)
            origin += self.origin

        for agent in self.agents:
            agentframe = agent._collect_agents(origin.copy(), agentframe)

        return agentframe

    def _agenttree(self, origin=[]):
        """Hidden function collects the current attributes of all agents by cascading
        and returns the global origin."""
        if self.geometry is None:
            return pd.DataFrame()

        df = self.dataframe.tail(1)

        if len(origin) > 0:
            df = df.assign(geometry=df.translate(
                xoff=origin[0], yoff=origin[1]))
            origin += self.origin
        else:
            df = df.assign(geometry=self.relative_geo)
            origin = np.array([0.0, 0.0])

        for agent in self.agents:
            df = df.append(agent._agenttree(
                origin=origin.copy()), ignore_index=True)

        return df

    @property
    def agentframe(self):
        """Attribute frame of direct sub agents."""
        agent_frame = GeoDataFrame()
        for agent in self.agents:
            attrs = agent.dataframe.tail(1)
            attrs = attrs.assign(agent=agent)
            agent_frame = agent_frame.append(
                attrs, ignore_index=True)
        return agent_frame

    @property
    def agenttree(self):
        """Atrribute data frame of all sub agents."""
        return self._agenttree()

    def plot(self, data='vector', wavelengths='default', **args):
        """Plots the agent with all subagents.

        Parameters
        ----------

        """

        gif = False
        if 'virtual' in args:
            gif = True
            virtual = args.pop('virtual')

        if data == 'raster':
            if 'mmu' in args:
                mmu = args.pop('mmu')
            else:
                mmu = 1
            fig = plt.imshow(np.flipud(rotate_image(self.render_composite(
                wavelengths=wavelengths, mmu=mmu), 90, resize=True)), origin='lower')

        else:
            fig = self.agenttree.plot(**args)

        if gif:
            plt.savefig(virtual, format='png')
            return virtual

        return fig

    def gif(self, runs, data='vector', name=None, fps=1):

        plt.ioff()
        plots = list()
        for run in range(runs):
            self.run()
            virtual_plot = io.BytesIO()
            plot = self.plot(data=data, virtual=virtual_plot)
            plots.append(plot)
            plt.close()

        images = list()
        for plot in plots:
            plot.seek(0)
            image = imageio.imread(plot)
            images.append(image)

        if not name:
            name = self.name + '_{}.gif'.format(data)

        imageio.mimsave(name, images, fps=fps)
        plt.ion()

    @property
    def origin(self):
        return np.array([floor(self.geometry.bounds[0]), floor(self.geometry.bounds[1])])

    @property
    def relative_geo(self):
        minx, miny, maxx, maxy = [floor(coord)
                                  for coord in self.geometry.bounds]
        rel_geo = translate(
            self.geometry, xoff=-1 * minx, yoff=-1 * miny)
        return rel_geo

    def set_material(self, Material):
        self._material = Material

    def material_response(self, wavelength):
        if self._material:
            return self._material.observe(wavelength)
        else:
            print('No material set.')
            return 0

    def get_agent(self, name):
        return [a for a in self.agents if a.name.startswith(name)]

    def add_agent(self, agent, scale=False, scale_ratio=0.25):

        if scale:
            rescale(self, agent, scale_ratio)
            agent.log()

        agent._handle = agent.name + ' ' + str(len(self.agents) + 1)
        agent.parent = self
        self.agents.append(agent)

    def add_agents(self, agents, scale=False, scale_ratio=0.25):
        for agent in agents:
            self.add_agent(agent, scale, scale_ratio)

    def add_attrs(self, **args):
        """Adds a new variable to track in the log."""
        for arg in args:
            setattr(self, arg, args[arg])

        if self.attrs:
            self.attrs.update(args)
        else:
            self.attrs = args

    def add_rule(self, rule):
        rule.agent = self
        self.rules.append(rule)

    def run(self, state={}, **args):
        """Evaluates the custom-defined _run function and runs through sub agents.
        Takes a dictionary as a state of variables."""
        self.time += 1
        if self.geometry is None:
            self.geometry = self.attrs['geometry']
        try:
            self._run(state)
            self.log()
        except BaseException as e:
            print('run failed:')
            print(str(e))

        for sub_agent in self.agents:
            sub_agent.run(state)

        return state

    def grid(self, grid_size=1, buffer=10, align='none'):
        return grid(self, grid_size, buffer)

    def place(self, verbose=False, attempts=100):
        """Attempts to place all sub agents.

        Parameters
        ----------
        verbose - print detailed placement results
        attempts - the attempts before the placement of a subagent fails
        """
        if sum([a.geometry.area for a in self.agents]) > self.geometry.area:
            if verbose:
                print('Insufficent area for subagents.')
            return False

        mask = self.relative_geo
        dep_graph = self.dep_graph()

        for batch in dep_graph:
            for agent in batch:
                evals = [rule.evaluate()
                         for rule in self.rules if rule._target == agent.name]

                valid_area = [mask] + evals
                region = intersect(valid_area)
                if not region:
                    if verbose:
                        print(agent.name, 'rule failure')
                    return False

                placed = agent.place_in(
                    region, mask, attempts=attempts)
                if placed:
                    mask = mask.difference(agent.geometry)
                    agent.log()
                else:
                    if verbose:
                        print('failed on:', agent.name)
                    return False

        for sub_agent in self.agents:
            result = sub_agent.place(verbose, attempts)
            if not result:
                return False

        self._placed = True
        return True

    def dep_graph(self):
        """Returns groups of agents based on their dependencies found from rules.
        """
        # clears dependencies variable from early builds
        for agent in self.agents:
            agent._dependents = list()

        # map dependencies
        for rule in self.rules:
            depend = rule.depend
            try:
                if depend:
                    if depend.name != self.name:
                        rule.target._dependents.append(depend.name)
            except:
                pass

        # create dependency graph
        graph = dict((a.name, set(a._dependents))
                     for a in self.agents)

        name_to_instance = dict((a.name, a) for a in self.agents)
        batches = list()
        while graph:
            # Get all observables with no dependencies
            ready = {name for name, deps in graph.items() if not deps}
            if not ready:
                msg = "Circular dependencies found!"
                raise ValueError(msg)
            # Remove them from the dependency graph
            for name in ready:
                graph.pop(name)
            for deps in graph.values():
                deps.difference_update(ready)

            # add the batch to the list
            batches.append([name_to_instance[name] for name in ready])

        # return the list of batches
        return batches

    def place_in(self, region, restrict='default', attempts=100):
        """Places an agent within a region that is contained by the parent.

        Parameters
        ----------
        region : region to place agent in
        restrict : bounds to restric placement by, 'default' means parent
        attempts : attempts before failure
        """
        if restrict == 'default':
            if self.parent:
                restrict == self.parent
            else:
                restrict = False
        for i in range(attempts):
            placement = posit_point(region, attempts=attempts)
            if placement:
                placed = shift_geometry(self.geometry, placement)
                if restrict != False:
                    if placed.within(restrict):
                        self.geometry = placed
                        return True
                    else:
                        continue
                self.geometry = placed
                return True
        return False

    def build(self, verbose=True, attempts=100):
        """Attempts to place all the agent's sub-agents until success.

        Parameters
        ----------
        verbose : Flag for printing out detailed results
        attempts : The number of attempts before failure, this paramater cascades
                down to the place and place_in functions

        """
        for i in range(attempts):
            if verbose:
                sys.stdout.write("attempt: %d   \r" % (i + 1))
                sys.stdout.flush()

            if self.place(verbose, attempts):
                if verbose:
                    print('success in {} attempts'.format(i + 1))
                return True
            else:
                continue
        if verbose:
            print('failure in {} attempts'.format(i + 1))
        return False

    def mask(self, inverted=False, xoff=0, yoff=0):
        """Returns an array mask of the agent's geometry."""

        # get corners
        minx, miny, maxx, maxy = [floor(coord)
                                  for coord in self.geometry.bounds]
        ylen = maxy - miny
        xlen = maxx - minx

        image = np.ones((xlen, ylen))

        coords = np.array(list(self.relative_geo.exterior.coords))
        if len(coords) == 5:
            return image * 0

        rr, cc = polygon(coords[:, 0], coords[:, 1], image.shape)
        image[rr, cc] = 0

        if inverted:
            image = 1 - image
        return image

    def render_value(self, value_field, image=[], origin=[], mmu=1):
        """Cascades through agents and renders geometries as a numpy array."""

        if len(image) == 0:
            image = self.mask() + getattr(self, value_field)
            origin = np.array([0.0, 0.0])
        else:
            shifted = translate(self.geometry,
                                xoff=origin[0], yoff=origin[1])

            minx, miny, maxx, maxy = [round(coord) for coord in shifted.bounds]

            image[minx:maxx, miny:maxy] *= self.mask()

            invert = 1 - self.mask()
            image[minx:maxx,
                  miny:maxy] += (invert * getattr(self, value_field))

            origin += self.origin

        for agent in self.agents:
            image = agent.render_value(value_field, image=image,
                                       origin=origin.copy())

        if mmu != 1:
            image = downscale_local_mean(
                image, (mmu, mmu))

        return image

    def render(self, wavelength, mmu=1):
        imagestack = self._collect_agents().sort_values('level')
        canvas = self.mask() + self.material_response(wavelength)
        for row in imagestack.iterrows():
            agent = row[1].agent
            level = row[1].level
            origin = row[1].origin

            shifted = translate(agent.geometry,
                                xoff=origin[0], yoff=origin[1])
            minx, miny, maxx, maxy = [floor(coord) for coord in shifted.bounds]
            canvas[minx:maxx, miny:maxy] *= agent.mask()
            invert = 1 - agent.mask()
            canvas[minx:maxx,
                   miny:maxy] += (invert * agent.material_response(wavelength))

        if mmu != 1:
            canvas = downscale_local_mean(canvas, (mmu, mmu))

        return canvas

    def render_composite(self, wavelengths='default', mmu=1):
        if wavelengths == 'default':
            wavelengths = [0.48, 0.56, 0.66]

        bands = list()
        for wl in wavelengths:
            bands.append(self.render(wl, mmu=mmu))

        img = np.zeros((bands[0].shape[0], bands[
            0].shape[1], 3), dtype=np.uint8)

        for i, band in enumerate(bands):
            img[:, :, i] = band * 255

        return img

    def move(self, xoff, yoff):
        self.geometry = translate(self.geometry, xoff, yoff)

    def _run(self, state):
        return True
