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


class Agent:

    def __init__(self, name=None, geometry=None, level=0, **attrs):
        """Agent class.

        Parameter
        ---------
        name : string, optional
                A name for the agent

        geometry : Shapely geometry, optional
                The geometry of the agent

        level : integer, default: 0
                The order to draw the agent in the agent tree, i.e. lower levels
                are drawn first.

        attrs : other named parameters, optional
                These paramaters will be stored in a dictionary and become the
                tracked attributes of this agent.
        ---------
        """
        self.time = 0  # the time of the agent
        self._handle = name  # name
        self.attrs = attrs  # the attributes being tracked
        self.attrs['geometry'] = geometry
        self.level = level
        self._on = True  # if the agent is visable
        self._dependents = list()  # list of dependents (internal use only)
        self._material = False  # the material
        self._statelog = list()  # the log of states over time
        self.agents = list()  # sub-agents
        self.rules = list()  # placement rules
        self.parent = False  # the parent agent
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
        its sub-agents, i.e. the agent tree."""
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
        """Returns the current state of all the agent's tracked attributes
        as a dictionary at the given time. _metavars is a dictionary of variables
        used by cycsat internally.
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
        """Returns the sub-agents with attributes as a pandas DataFrame."""
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
        """Returns an atrribute dataframe of all agents and sub-agents, i.e. the agent tree."""
        return self._agenttree(show_metavars=show_metavars)

    def plot(self, data='vector', band_args='default', **args):
        """Plots the agent tree.

        Parameter
        ---------
        data : {'vector', raster'}, default: 'vector'
                Sets the way to display the data.

        band_args : dictionary or 'default', default: 'default'
                A dictionary of arguments for rendering bands if data is 'raster'
                The 'default' option renders an RGB image, but this will only work
                for the USGSMaterial.
        ---------
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
            if 'ax' in args:
                ax = args.pop('ax')
            else:
                ax = plt
            fig = ax.imshow(np.flipud(rotate_image(self.render_ndarray(
                band_args=band_args, mmu=mmu), 90, resize=True)), origin='lower', **args)
            fig.axes.set_title('{}\n time: {}'.format(self.name, self.time))
        else:
            fig = self._agenttree().plot(**args)
            fig.set_title('{}\n time: {}'.format(self.name, self.time))
        if gif:
            plt.savefig(virtual, format='png')
            return virtual
        return fig

    def render(self, band_args='default', **args):
        """Shortcut for agent.plot(data='raster')."""
        return self.plot(data='raster', band_args=band_args, **args)

    def gif(self, runs, data='vector', filename=None, fps=1):
        """Export an animated GIF of the agent tree.

        Parameters
        ----------
        runs : integer
                The number of runs to animate.

        data : {'vector', 'raster'}, default: 'vector'
                Sets the way to display the data.

        filename : string, optional, default: None (cycsat creates a name)

        fps : integer > 1, default: 1
                Frames per second.
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
        """The origin (or lower corner) of the agent's geometry."""
        return np.array([floor(self.geometry.bounds[0]), floor(self.geometry.bounds[1])])

    @property
    def relative_geo(self):
        """The geometry of the agent with its origin set to (0,0). This is the geometry that
        all sub-agents will be placed into."""
        minx, miny, maxx, maxy = [floor(coord)
                                  for coord in self.geometry.bounds]
        rel_geo = translate(
            self.geometry, xoff=-1 * minx, yoff=-1 * miny)
        return rel_geo

    def set_material(self, Material):
        """Sets the Material of the agent. Requires a Material instance."""
        self._material = Material

    def material_response(self, **args):
        """Returns the Material response given a set of variables.
        For example to render a USGSMaterial a 'wavelength' variable must be passed."""
        if self._material:
            return self._material.observe(**args)
        else:
            print(self.name, ': no material set.')
            return 0

    def get_agent(self, name):
        """Get a list of sub-agents by name. Searches for any agent with with a name that starts
        with the provided name."""
        return [a for a in self.agents if a.name.startswith(name)]

    def add_agent(self, agent, scale_ratio=1):
        """Add sub-agent to agent.

        Parameter
        ----------
        agent : Agent instance
                The sub-agent to add.

        scale_ratio : ratio, > 0 > 1, default: 1
                The ratio to scale the geometry of the sub-agent to fit inside the parent.
                See rescale in geomtry.py.
        ----------
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

        Parameter
        ---------
        agents : list of Agent instances

        scale_ratio : ratio, > 0 > 1, default: 1
                The ratio to scale the geometry of the sub-agent to fit inside the parent.
                See rescale in geomtry.py.
        ---------
        """
        for agent in agents:
            self.add_agent(agent, scale_ratio)

    def add_attrs(self, **args):
        """Adds new attributes to track in the _statelog. Paramters passed
        become newly tracked attributes."""
        for arg in args:
            setattr(self, arg, args[arg])
        if self.attrs:
            self.attrs.update(args)
        else:
            self.attrs = args

    def add_rule(self, rule):
        """Adds a placment rule. Rules must be added
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

    def run(self, state={}):
        """Evaluates the user-defined _run function and runs through agent tree.

        Parameter
        ---------
        state : dictionary
                A dictionary of global variables.
        ---------
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
            nodeps = {name for name, deps in graph.items() if not deps}
            if not nodeps:
                msg = "Circular dependencies found!"
                raise ValueError(msg)
            # Remove them from the dependency graph
            for name in nodeps:
                graph.pop(name)
            for deps in graph.values():
                deps.difference_update(nodeps)
            # add the batch to the list
            batches.append([name_to_instance[name] for name in nodeps])
        return batches

    def place(self, verbose=False, attempts=100):
        """Attempts to place agent tree.

        Parameter
        ---------
        verbose : bool, default: False
                If True prints detailed placement results.

        attempts : integer, default: 100
                The attempts to make before the placement fails
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

        Parameter
        ---------
        region : Shapely geometry
                The region to place the agent in

        restrict : Shapely geometry, default: 'default'
                This defines the bounds to restric the placement by. The 'default' option is the agent's parent

        attempts : integer, default: 100
                Attempts before failure
        ---------
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

        Parameter
        ---------
        verbose : bool, default: True
                If True prints detailed placement results.

        attempts : integer, default: 100
                Attempts before failure
        ---------
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
        """Returns an array mask of the agent's geometry. If inverted param is True
        the mask will be in 1s rather than 0s."""
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

        Parameter
        ---------
        attr : string, optional, default: None
                the named attribute to the base pixel value on

        mmu : integer, >= 1, default: 1,
                The minimum mapping unit, i.e size of pixel. Must be >= 1.
        ---------
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

        Parameter
        ---------
        band_args : list of dictionaries, default: 'default'
                a list of dictionaries with rendering arguments. Each
                dictionary of arguments will create a band. The 'default' will
                render an RGB image for agents with USGSMaterials.

        mmu : integer, >= 1, default: 1,
                The minimum mapping unit, i.e size of pixel. Must be >= 1.
        ---------
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
