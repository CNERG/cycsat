import os

import pandas as pd
from geopandas import GeoDataFrame
import numpy as np
import random
import rasterio

from skimage.draw import polygon
from skimage.transform import downscale_local_mean

from shapely.geometry import Point
from shapely.affinity import rotate, translate
from shapely.ops import cascaded_union, unary_union, polygonize


class Agent:

    def __init__(self, **variables):
        # clear the log and add init arguments
        self.data = GeoDataFrame()
        self.time = 0
        self.variables = variables
        self.parent = False
        self.log(init=True)
        self.agents = list()

    @property
    def agent_frame(self):
        """Collects the current attributes of all subagents."""
        agent_info = GeoDataFrame()
        for agent in self.agents:
            agent_info = agent_info.append(
                agent.data.tail(1), ignore_index=True)
        return agent_info

    def collect_agents(self):
        """Collects the current attributes of all agents by cascading."""
        log = self.data.tail(1)
        for agent in self.agents:
            log = log.append(agent.collect_agents(), ignore_index=True)
        return log

    def add_agents(self, agents):
        if type(agents) is list:
            for agent in agents:
                agent.parent = self
                self.agents.append(agent)
        else:
            agents.parent = self
            self.agents.append(agents)

    def add_variables(self, **args):
        """Adds a new variable to track in the log."""
        for arg in args:
            setattr(self, arg, args[arg])

        if self.variables:
            self.variables.update(args)
        else:
            self.variables = args

    # def agent_bounds(self):
    #     """Merge the geometries of agents together."""
    #     agents = cascaded_union([agent.geometry for agent in self.agents])
    #     self.add_variables(geometry=agents)
    #     self.log()

    def log(self, init=False):
        """Log the agent's variables."""

        if init:
            for var in self.variables:
                setattr(self, var, self.variables[var])
            log = self.variables
        else:
            log = {}
            for var in self.variables:
                log[var] = getattr(self, var)

        log['time'] = self.time
        self.data = self.data.append(log, ignore_index=True)

    def run(self, **args):
        """Evaluates the __run__ function and runs through sub agents."""
        self.time += 1
        try:
            active = self.__run__()
            if active:
                self.log()
        except:
            print('run failed')

        for sub_agent in self.agents:
            sub_agent.run()

    def place(self, attempts=100):
        """Places the agent and all of it's sub_agents.

        Parameters
        ----------
        agent - the agent to place the shape within
        attempts - the attempts before the placement fails
        """

        try:
            self.__place__()
            self.log()
        except:
            # if not place function is defined
            # place sub agents within agent
            geometry = self.geometry
            for sub_agent in self.agents:
                geometry = geometry.difference(
                    sub_agent.place_in(geometry))
                sub_agent.log()

        for sub_agent in self.agents:
            sub_agent.place()
            self.log()

    def place_in(self, region, attempts=100):
        """Places in a given region."""
        # bounding region of parent agent
        for i in range(attempts):
            placement = posit_point(region, attempts=attempts)
            if placement:
                x, y = [placement.coords.xy[0][
                    0], placement.coords.xy[1][0]]
                _x, _y = [self.geometry.centroid.coords.xy[0][
                    0], self.geometry.centroid.coords.xy[1][0]]
                shift_x = x - _x
                shift_y = y - _y

                geometry = translate(
                    self.geometry, xoff=shift_x, yoff=shift_y)
                if geometry.within(region):
                    self.geometry = geometry
                    return geometry
        return self.geometry

    def surface(self, value_field):
        """Generates a blank raster surface using the provided value field.
        This needs to work with a material.
        """

        minx, miny, maxx, maxy = [round(coord)
                                  for coord in self.geometry.bounds]

        image = np.zeros((maxx - minx, maxy - miny)) + \
            getattr(self, value_field)

        return image

    def collect_surfaces(self, value_field, image=[], res=1):

        # if no image is provided create a blank
        if len(image) == 0:
            image = self.surface(value_field)
            # else add the agent to the image
        else:
            coords = np.array(list(self.geometry.exterior.coords))
            rr, cc = polygon(coords[:, 0], coords[:, 1], image.shape)
            image[rr, cc] = getattr(self, value_field)

        if self.agents:
            for agent in self.agents:
                image = agent.collect_surfaces(value_field, image=image)

        if res != 1:
            image = downscale_local_mean(
                image, (res, res))

        return image

    def __run__(self, **args):
        """DEFINED. Returns True to record."""


def posit_point(mask, attempts=1000):
    """Generates a random point within a mask."""
    x_min, y_min, x_max, y_max = mask.bounds

    for i in range(attempts):
        x = random.uniform(x_min, x_max + 1)
        y = random.uniform(y_min, y_max + 1)
        posited_point = Point(x, y)

        if posited_point.within(mask):
            return posited_point


def fullname(o):
    return o.__module__ + "." + o.__class__.__name__


class SpatialRule:

    def __init__(self):
        """A defined set of instructions (function) for returning."""

    def evaluate(self):
        self.run.__evaluate__(to_place, target_list)
