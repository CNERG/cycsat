import os

from math import pow
from math import sqrt

import re

import pandas as pd
from geopandas import GeoDataFrame
import numpy as np
import random
import rasterio

from skimage.draw import polygon
from skimage.transform import rotate as rotate_image
from skimage.transform import downscale_local_mean

from shapely.geometry import Point, box
from shapely.affinity import rotate, translate
from shapely.ops import cascaded_union, unary_union, polygonize

from .geometry import posit_point, grid, intersect


class Agent:

    def __init__(self, name=None, **attrs):
        """Creates an agent."""

        self.__handle__ = name
        self.__dependents__ = list()
        self.data = GeoDataFrame()
        self.time = 0
        self.initattrs = attrs
        self.attrs = attrs
        self.parent = False
        self.log(init=True)
        self.agents = list()
        self.materials = list()
        self.rules = list()

    def log(self, init=False):
        """Looks for changes and logs the agents attributes if there is a change."""
        if init:
            change = True
            for attr in self.initattrs:
                setattr(self, attr, self.initattrs[attr])
            log = self.initattrs.copy()
        else:
            change = False
            log = {}
            for attr in self.attrs:
                check = getattr(self, attr)
                compare = self.attrs[attr]
                log[attr] = getattr(self, attr)

                if check != compare:
                    change = True

        if change:
            log['time'] = self.time
            self.data = self.data.append(log, ignore_index=True)

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
            attrs = agent.data.tail(1)
            attrs = attrs.assign(agent=agent)
            agent_frame = agent_frame.append(
                attrs, ignore_index=True)
        return agent_frame

    @property
    def agenttree(self):
        return self.__agenttree()

    def __agenttree(self, origin=[]):
        """Collects the current attributes of all agents by cascading."""

        if self.geometry is None:
            return pd.DataFrame()

        log = self.data.tail(1)

        if len(origin) > 0:
            log = log.assign(geometry=log.translate(
                xoff=origin[0], yoff=origin[1]))
            origin += self.origin
        else:
            log = log.assign(geometry=self.relative_geo)
            origin = np.array([0.0, 0.0])

        for agent in self.agents:
            log = log.append(agent.__agenttree(
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

    def get_agent(self, name):
        return [a for a in self.agents if a.name.startswith(name)]

    def add_agent(self, agent):
        """Adds sub agents. Takes a list of agents or single agent."""
        num = ''
        existing = self.get_agent(agent.name)
        if existing:
            num = str(len(existing))
        agent.__handle__ = agent.name + num
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

    def add_rules(self, rules):
        """Adds placement rules to agent."""

        if type(rules) is list:
            for rule in rules:
                rule.agent = self
                self.rules.append(rule)
        else:
            rules.agent = self
            self.rules.append(rules)

    def run(self, **args):
        """Evaluates the __run__ function and runs through sub agents."""
        self.time += 1
        if self.geometry is None:
            self.geometry = self.attrs['geometry']
        try:
            self.__run__()
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
        try:
            self.__place__()
            self.log()
        except:
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
                        region, strict=True, attempts=attempts)

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

    def place_in(self, region, strict=False, attempts=100):
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

                if strict:
                    if placed.within(region):
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

    def render(self, value_field, image=[], origin=[], res=1):
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
            image = agent.render(value_field, image=image,
                                 origin=origin.copy())

        if res != 1:
            image = downscale_local_mean(
                image, (res, res))

        return image

    def move(self, xoff, yoff):
        self.geometry = translate(self.geometry, xoff, yoff)

    def __run__(self, **args):
        pass
