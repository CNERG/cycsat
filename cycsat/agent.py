import os
import sys
from math import floor
import random
import re
import io

import imageio

import pandas as pd
import numpy as np
from geopandas import GeoDataFrame

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


class Agent:

    def __init__(self, name=None, geometry=None, level=0, **attrs):
        """
        Agent class.

        Parameters
        ----------
        name - (optional) a name for the agent
        level - (default = 0) the height, or the order to draw the agent on images
        attrs - (optional) a dictionary of attributes to track and use during
            simulations.
        """
        self.time = 0
        self._handle = name
        self.attrs = attrs
        self.attrs['geometry'] = geometry
        self.level = level
        self._on = True
        self._dependents = list()
        self._material = False
        self._statelog = list()
        self.agents = list()
        self.rules = list()
        self.parent = False
        self.reset()

    def __repr__(self):
        return '<{}>'.format(self._handle)

    @property
    def name(self):
        """The name of the agent. Used for rule evaluations."""
        if self._handle:
            return self._handle
        else:
            return self.__class__.__name__

    @property
    def depth(self):
        """The agent's hierarchical tree depth."""
        level = 0
        if self.parent:
            level += 1
            level += self.parent.depth
        return level

    def rename(self, name):
        """Renames the agent."""
        self._handle = name

    def print_tree(self):
        """Prints a hierarchical diagram of this agent and all
        its sub-agents."""
        print('    ' * self.depth, self)
        for agent in self.agents:
            agent.print_tree()

    def reset(self):
        """Clears the agent's data and resets the attributes to
        initial conditions."""
        self.time = 0
        self._statelog = list()
        for attr in self.attrs:
            setattr(self, attr, self.attrs[attr])
        self.log_state()

    def get_state(self, time='current'):
        """Returns the current state of all attributes as a dictionary at the given time.

        _metavars is a dictionary of variables used by cycsat internally.
        """
        if time == 'current':
            state = {}
            state['_metavars'] = {'_on': self._on}
            for attr in self.attrs:
                state[attr] = getattr(self, attr)
        else:
            try:
                state = [state for state in self._statelog if state[
                    'time'] == time][0].copy()
            except:
                state = {}
        return state

    def log_state(self):
        """Records the current state of the agent at the current time."""
        # remove existing logs from current time
        lookup = lambda state: False if state['time'] == self.time else True
        statelog = np.array(self._statelog)
        self._statelog = statelog[
            [lookup(state) for state in statelog]].tolist()
        # get state an log it
        state = self.get_state()
        state['time'] = self.time
        self._statelog.append(state)

    def set_state(self, time):
        """Set the attributes of the agent to a previous time."""
        state = self.get_state(time)
        if len(state) == 0:
            print('state {} does not exist.'.format(time))
            return False
        metavars = state.pop('_metavars')
        for var in metavars:
            setattr(self, var, metavars[var])
        for attr in state:
            setattr(self, attr, state[attr])
        for agent in self.agents:
            agent.set_state(time)
        return True

    @property
    def dataframe(self):
        """Returns a dataframe of all the agent's state data."""
        return GeoDataFrame(self._statelog)

    @property
    def agentframe(self):
        """Returns the agents"""
        agent_frame = GeoDataFrame()
        for agent in self.agents:
            attrs = agent.dataframe.tail(1)
            attrs = attrs.assign(agent=agent)
            agent_frame = agent_frame.append(
                attrs, ignore_index=True)
        return agent_frame

    def _agenttree(self, show_metavars=True, origin=[], agentframe=None):
        """Collects agents by cascading to gather information for global placement."""
        if agentframe is None:
            agentframe = pd.DataFrame()
            origin = np.array([0, 0])
        # get header variables (internal variables)
        headers = {'_agent': self,
                   '_depth': self.depth,
                   '_level': self.level,
                   '_origin': origin.copy()}
        state = self.get_state()
        metavars = state.pop('_metavars')
        # if the agent is ON then add to frame
        if (metavars['_on'] == True) or (metavars['_on'] == 1):
            if show_metavars:
                headers = {**headers, **metavars}
            else:
                headers = {'_agent': self}
            state['geometry'] = translate(
                state['geometry'], xoff=origin[0], yoff=origin[1])
            agentframe = agentframe.append({**headers, **state}, ignore_index=True)

        if len(origin) != 0:
            origin += self.origin

        for agent in self.agents:
            agentframe = agent._agenttree(
                show_metavars, origin.copy(), agentframe)
        return GeoDataFrame(agentframe)

    def agenttree(self, show_metavars=False):
        """Atrribute data frame of all sub agents."""
        return self._agenttree(show_metavars=show_metavars)

    def plot(self, data='vector', band_args='default', **args):
        """Plots the agent with all subagents.

        Parameters
        ----------
        data - 'vector' or 'raster' for a raster image
        band_args - the arguments for rendering bands, default RGB
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
            fig = plt.imshow(np.flipud(rotate_image(self.render_ndarray(
                band_args=band_args, mmu=mmu), 90, resize=True)), origin='lower')
        else:
            fig = self._agenttree().plot(**args)
        if gif:
            plt.savefig(virtual, format='png')
            return virtual
        return fig

    def render(self, band_args='default', **args):
        return self.plot(data='raster', band_args=band_args, **args)

    def gif(self, runs, data='vector', filename=None, fps=1):
        """Export an animated GIF of the agent runs.

        Parameters
        ----------
        runs - the number of runs
        data - 'vector' or 'raster'
        filename - filename (optional)
        fps - frames per second
        ----------
        """
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

        if not filename:
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

    def material_response(self, **args):
        if self._material:
            return self._material.observe(**args)
        else:
            print(self.name, ': no material set.')
            return 0

    def get_agent(self, name):
        return [a for a in self.agents if a.name.startswith(name)]

    def add_agent(self, agent, scale_ratio=1):
        """Add sub-agents to agent.

        Parameters:
        ----------
        agent - the agent to add
        scale_ratio - the ratio to scale the geometry of the agent by
        """
        if scale_ratio != 1:
            rescale(self, agent, scale_ratio)
            agent.log_state()

        name_conflicts = len(
            [c for c in self.agents if c.name.startswith(agent.name)])
        if name_conflicts:
            number = ' ' + str(name_conflicts)
        else:
            number = ''
        agent._handle = agent.name + number
        agent.parent = self
        self.agents.append(agent)

    def add_agents(self, agents, scale_ratio=1):
        """Add multiple sub-agents to agent.

        Parameters:
        ----------
        agents - a list of agents
        scale_ratio the ratio to scale the geometry of the agents by
        ----------
        """
        for agent in agents:
            self.add_agent(agent, scale_ratio)

    def add_attrs(self, **args):
        """Adds new attributes to track in the statelog. Paramters passed
        become newly tracked attributes."""
        for arg in args:
            setattr(self, arg, args[arg])
        if self.attrs:
            self.attrs.update(args)
        else:
            self.attrs = args

    def add_rule(self, rule):
        """Adds a placment rule for this agent's sub-agents. Rules must be added
        through this function."""
        rule.agent = self
        self.rules.append(rule)

    def turn_on(self):
        """Turns the agent ON making it VISIBLE in images and dataframes."""
        self._on = True
        self.log_state()
        for agent in self.agents:
            agent.turn_on()

    def turn_off(self):
        """Turns the agent OFF making it INVISIBLE in images and dataframes."""
        self._on = False
        self.log_state()

        for agent in self.agents:
            agent.turn_off()

    def move(self, xoff, yoff):
        """Move the agent by an xoff and yoff value."""
        self.geometry = translate(self.geometry, xoff, yoff)

    def _run(self, state):
        """User-defined run function."""
        pass

    def run(self, state={}, **args):
        """Evaluates the user-defined _run function and runs through sub-agents.

        Parameters:
        ----------
        state - a dictionary of global variables
        ----------
        """
        self.time += 1
        self._run(state)
        self.log_state()
        for sub_agent in self.agents:
            sub_agent.run(state)
        return state

    def dep_graph(self):
        """Returns groups of agents based on their dependencies using placement rules.
        """
        # clears dependencies tree from earlier builds
        for agent in self.agents:
            agent._dependents = list()
        # map dependencies
        for rule in self.rules:
            depend = rule.dependent_on
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
        return batches

    def place(self, verbose=False, attempts=100):
        """Attempts to place all sub-agents.

        Parameters:
        ----------
        verbose - if True print detailed placement results
        attempts - the attempts before the placement of a subagent fails
        ----------
        """
        # check for sufficent area
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
                    agent.log_state()
                else:
                    if verbose:
                        print('failed on:', agent.name)
                    return False
        for sub_agent in self.agents:
            result = sub_agent.place(verbose, attempts)
            if not result:
                return False
        return True

    def place_in(self, region, restrict='default', attempts=100):
        """Places an agent within a region.

        Parameters:
        ----------
        region - region to place agent in
        restrict - bounds to restric placement by, 'default' is the agent's parent
        attempts - attempts before failure
        ----------
        """
        if restrict == 'default':
            if self.parent:
                if self.parent.geometry is not None:
                    restrict = self.parent.geometry
                else:
                    restrict = False
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

        Parameters:
        ----------
        verbose : if True, print detailed placement results
        attempts : attempts before failure
        ----------
        """
        for i in range(attempts):
            if verbose:
                sys.stdout.write("attempt: %d   \r" % (i + 1))
                sys.stdout.flush()

            if self.place(verbose, attempts):
                if verbose:
                    print('success in {} attempts'.format(i + 1))
                return {'status': True, 'attempts': i + 1}
            else:
                continue
        if verbose:
            print('failure in {} attempts'.format(i + 1))
        return {'status': False, 'attempts': attempts}

    def mask(self, inverted=False):
        """Returns an array mask of the agent's geometry.

        Parameters:
        ----------
        inverted - if True, the agent's mask is 1 not 0
        ----------
        """
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

    def render_1darray(self, attr=None, mmu=1, **args):
        """Renders an image of this agent as a numpy array. If attr is left
        as None additional args are used to render the agent's surface

        Parameters:
        -----------
        attr - the attribute to base pixel value on (optional)
        mmu - minimum mapping unit, i.e size of pixel. Must be >= 1.
        -----------
        """
        if attr is not None:
            value = getattr(self, attr)
        else:
            value = self.material_response(**args)
        canvas = self.mask() + value
        if len(self.agents) == 0:
            return canvas
        imagestack = self._agenttree().sort_values('_level')
        for row in imagestack.iterrows():
            agent = row[1]._agent
            level = row[1]._level
            origin = row[1]._origin
            if attr is not None:
                value = getattr(agent, attr)
            else:
                value = agent.material_response(**args)

            shifted = translate(agent.geometry,
                                xoff=origin[0], yoff=origin[1])
            minx, miny, maxx, maxy = [floor(coord) for coord in shifted.bounds]
            canvas[minx:maxx, miny:maxy] *= agent.mask()
            invert = 1 - agent.mask()
            canvas[minx:maxx,
                   miny:maxy] += (invert * value)
        if mmu != 1:
            canvas = downscale_local_mean(canvas, (mmu, mmu))
        return canvas

    def render_ndarray(self, band_args='default', mmu=1):
        """Renders an n-d array using a list of band argument dictionaries.

        Parameters:
        ----------
        band_args - a list of dictionaries with rendering arguments. Each
                dictionary of arguments will create a band
        mmu - minimum mapping unit, i.e. size of pixel. Must be >= 1.
        ----------
        """
        if band_args == 'default':
            band_args = [{'wavelength': 0.48},
                         {'wavelength': 0.56},
                         {'wavelength': 0.66}]
        bands = list()
        for band_arg in band_args:
            bands.append(self.render_1darray(mmu=mmu, **band_arg))

        img = np.zeros((bands[0].shape[0], bands[
            0].shape[1], 3), dtype=np.uint8)
        for i, band in enumerate(bands):
            img[:, :, i] = band * 255
        return img
