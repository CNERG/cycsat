import os

from math import pow
from math import sqrt

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

from .geometry import posit_point, grid, intersect
from .laboratory import Material
from .metrics import Log


class Agent:

    def __init__(self, name=None, **attrs):

        self.__handle__ = name
        self.__dependents__ = list()
        self.__material__ = False
        self.agents = list()
        self.rules = list()
        self.journal = list()
        self.time = 0
        self.attrs = attrs
        self.parent = False

        self.log(init=True)

    def __repr__(self):
        return '<{}>'.format(self.__handle__)

    @property
    def level(self):
        """Determines the agent's level by looking for ancestors."""
        level = 0
        if self.parent:
            level += 1
            level += self.parent.level
        return level

    def print_diagram(self):
        """Prints a diagram of this agents and all its children."""
        print('    ' * self.level, self)
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
        self.journal.append(log)

    @property
    def dataframe(self):
        data = [log.data for log in self.journal]
        return GeoDataFrame(data)

    @property
    def name(self):
        if self.__handle__:
            return self.__handle__
        else:
            return self.__class__.__name__

    def rename(self, name):
        self.__handle__ = name

    @property
    def agentframe(self):
        """Attributes frame of all sub agents."""
        agent_frame = GeoDataFrame()
        for agent in self.agents:
            attrs = agent.dataframe.tail(1)
            attrs = attrs.assign(agent=agent)
            agent_frame = agent_frame.append(
                attrs, ignore_index=True)
        return agent_frame

    @property
    def agenttree(self):
        return self.__agenttree__()

    def plot(self, **args):

        gif = False
        if 'virtual' in args:
            gif = True
            virtual = args.pop('virtual')

        fig = self.agenttree.plot(**args)

        if gif:
            plt.savefig(virtual, format='png')
            return virtual

        return fig

    def vector_gif(self, runs, name=None, fps=1):

        plt.ioff()
        plots = list()
        for run in range(runs):
            self.run()

            virtual_plot = io.BytesIO()
            plot = self.plot(virtual=virtual_plot)
            plots.append(plot)
            plt.close()

        images = list()
        for plot in plots:
            plot.seek(0)
            image = imageio.imread(plot)
            images.append(image)

        if not name:
            name = self.name + '.gif'

        imageio.mimsave(name, images, fps=fps)
        plt.ion()

    def __agenttree__(self, origin=[]):
        """Collects the current attributes of all agents by cascading."""

        if self.geometry is None:
            return pd.DataFrame()

        log = self.dataframe.tail(1)

        if len(origin) > 0:
            log = log.assign(geometry=log.translate(
                xoff=origin[0], yoff=origin[1]))
            origin += self.origin
        else:
            log = log.assign(geometry=self.relative_geo)
            origin = np.array([0.0, 0.0])

        for agent in self.agents:
            log = log.append(agent.__agenttree__(
                origin=origin.copy()), ignore_index=True)

        return log

    @property
    def origin(self):
        return np.array([self.geometry.bounds[0], self.geometry.bounds[1]])

    @property
    def relative_geo(self):
        minx, miny, maxx, maxy = [round(coord)
                                  for coord in self.geometry.bounds]
        rel_geo = translate(
            self.geometry, xoff=-1 * minx, yoff=-1 * miny)
        return rel_geo

    def set_material(self, Material):
        self.__material__ = Material

    def material_response(self, wavelength):
        if self.__material__:
            return self.__material__.observe(wavelength)
        else:
            print('No material set.')
            return 0

    def get_agent(self, name):
        return [a for a in self.agents if a.name.startswith(name)]

    def add_agent(self, agent):
        agent.__handle__ = agent.name + ' ' + str(len(self.agents) + 1)
        agent.parent = self
        self.agents.append(agent)

    def add_agents(self, agents):
        for agent in agents:
            self.add_agent(agent)

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

    def run(self, **args):
        """Evaluates the __run__ function and runs through sub agents."""
        self.time += 1
        if self.geometry is None:
            self.geometry = self.attrs['geometry']
        try:
            if self.__run__():
                self.log()
        except BaseException as e:
            print('run failed:')
            print(str(e))

        for sub_agent in self.agents:
            sub_agent.run()

    def grid(self, grid_size=1, buffer=10, align='none'):
        return grid(self, grid_size, buffer)

    def place(self, iterations=100, attempts=100):
        """Places sub agents.

        Parameters
        ----------
        agent - the agent to place the shape within
        iterations - the times to try before failing
        attempts - the attempts before the placement of a subagent fails
        """

        if sum([a.geometry.area for a in self.agents]) > self.geometry.area:
            print('Insufficent area for subagents.')
            return False

        mask = self.relative_geo
        dep_graph = self.dep_graph()

        for batch in dep_graph:
            for agent in batch:

                evals = [rule.evaluate()
                         for rule in self.rules if rule.__target__ == agent.name]

                valid_area = [mask] + evals
                region = intersect(valid_area)
                placed = agent.place_in(
                    region, mask, attempts=attempts)

                # if placed:
                #     evals = [rule.sharpen()
                # for rule in self.rules if rule.__target__ == agent.name]

                if placed:
                    mask = mask.difference(agent.geometry)
                    agent.log()
                else:
                    return False

        for sub_agent in self.agents:
            result = sub_agent.place()
            if not result:
                return False
        return True

    def dep_graph(self):
        """Returns groups of agents based on their dependencies found from rules.
        """
        # clear dependencies
        for agent in self.agents:
            agent.__dependents__ = list()

        # map dependencies
        for rule in self.rules:
            depend = rule.depend
            try:
                if depend:
                    if depend.name != self.name:
                        rule.target.__dependents__.append(depend.name)
            except:
                pass

        # create dependency graph
        graph = dict((a.name, set(a.__dependents__))
                     for a in self.agents)

        name_to_instance = dict((a.name, a) for a in self.agents)

        # where to store the batches
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

            # Add the batch to the list
            batches.append([name_to_instance[name] for name in ready])

        # Return the list of batches
        return batches

    def place_in(self, region, restrict=None, attempts=100):
        """Places an agent within a region that is contained by the parent.

        Parameters
        ----------
        region - region to place agent in
        strict - if True, cannot be outside parent (default False)
        attempts - attempts before failure
        """

        for i in range(attempts):
            placement = posit_point(region, attempts=attempts)
            if placement:
                x, y = [placement.coords.xy[0][
                    0], placement.coords.xy[1][0]]
                _x, _y = [self.geometry.centroid.coords.xy[0][
                    0], self.geometry.centroid.coords.xy[1][0]]
                shift_x = x - _x
                shift_y = y - _y

                placed = translate(
                    self.geometry, xoff=shift_x, yoff=shift_y)

                if restrict is not None:
                    if placed.within(restrict):
                        self.geometry = placed
                        return True
                    else:
                        continue

                self.geometry = placed
                return True

        return False

    def mask(self):
        """Returns an array mask of the agent's geometry."""

        # get dimensions corners
        minx, miny, maxx, maxy = [round(coord)
                                  for coord in self.geometry.bounds]
        ylen = maxy - miny
        xlen = maxx - minx

        image = np.ones((ylen, xlen))

        coords = np.array(list(self.relative_geo.exterior.coords))
        if len(coords) == 5:
            return image * 0

        rr, cc = polygon(coords[:, 0], coords[:, 1], image.shape)
        image[rr, cc] = 0

        return image

    def render_value(self, value_field, image=[], origin=[], res=1):
        """Cascades through agents and renders geometries as a numpy array."""

        if len(image) == 0:
            image = self.mask() + getattr(self, value_field)
            origin = np.array([0.0, 0.0])
        else:
            shifted = translate(self.geometry,
                                xoff=origin[0], yoff=origin[1])

            minx, miny, maxx, maxy = [round(coord) for coord in shifted.bounds]

            # clear and add pixels
            image[miny:maxy, minx:maxx] *= self.mask()
            invert = 1 - self.mask()
            image[miny:maxy,
                  minx:maxx] += (invert * getattr(self, value_field))

            origin += self.origin

        for agent in self.agents:
            image = agent.render_value(value_field, image=image,
                                       origin=origin.copy())

        if res != 1:
            image = downscale_local_mean(
                image, (res, res))

        return image

    def render_material(self, wavelength, image=[], origin=[], res=1):
        """Cascades through agents and renders geometries as a numpy array."""

        if len(image) == 0:
            image = self.mask() + self.material_response(wavelength)
            origin = np.array([0.0, 0.0])
        else:
            shifted = translate(self.geometry,
                                xoff=origin[0], yoff=origin[1])

            minx, miny, maxx, maxy = [round(coord) for coord in shifted.bounds]

            # clear and add pixels
            image[miny:maxy, minx:maxx] *= self.mask()
            invert = 1 - self.mask()
            image[miny:maxy,
                  minx:maxx] += (invert * self.material_response(wavelength))

            origin += self.origin

        for agent in self.agents:
            image = agent.render_material(wavelength, image=image,
                                          origin=origin.copy())

        if res != 1:
            image = downscale_local_mean(
                image, (res, res))

        return image

    def render_composite(self, wavelengths=[0.48, 0.56, 0.66], res=1):

        bands = list()
        for wl in wavelengths:
            bands.append(self.render_material(wl, res=res))

        img = np.zeros((bands[0].shape[0], bands[
                       0].shape[1], 3), dtype=np.uint8)

        for i, band in enumerate(bands):
            img[:, :, i] = band * 255

        return img

    def move(self, xoff, yoff):
        self.geometry = translate(self.geometry, xoff, yoff)

    def __run__(self, **args):
        return True
