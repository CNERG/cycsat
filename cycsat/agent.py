import os

import pandas as pd
from geopandas import GeoDataFrame
import numpy as np
import random
import rasterio

from skimage.draw import polygon
from skimage.transform import rotate as rotate_image
from skimage.transform import downscale_local_mean

from scipy.ndimage import gaussian_filter
from scipy.interpolate import griddata, interp2d, bisplrep, Rbf

from shapely.geometry import Point
from shapely.affinity import rotate, translate
from shapely.ops import cascaded_union, unary_union, polygonize


class Agent:

    def __init__(self, **variables):
        """Creates an agent. Takes any variables ats attributes."""

        self.data = GeoDataFrame()
        self.time = 0
        self.variables = variables
        self.parent = False
        self.log(init=True)
        self.agents = list()

    @property
    def agentframe(self):
        """Attributes frame of all sub agents."""
        agent_frame = GeoDataFrame()
        for agent in self.agents:
            agent_frame = agent_frame.append(
                agent.data.tail(1), ignore_index=True)
        return agent_frame

    @property
    def agenttree(self):
        """Collects the current attributes of all agents by cascading."""
        log = self.data.tail(1)
        for agent in self.agents:
            log = log.append(agent.agenttree, ignore_index=True)
        return log

    def add_agents(self, agents):
        """Adds sub agents. Takes a list of agents or single agent."""
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

    def log(self, init=False):
        """Logs the agent's variables."""
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

    def place(self, time=None, attempts=100):
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
            if len(self.agents) > 0:
                mask = self.geometry
                for sub_agent in self.agents:
                    mask = mask.difference(sub_agent.place_in(mask))
                    sub_agent.log()

        for sub_agent in self.agents:
            sub_agent.place()

    def place_in(self, region, attempts=100):
        """Places an agent within its parent region."""

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
                if placed.within(region):
                    self.geometry = placed
                    return self.geometry

        return self.geometry

    def surface(self, variable, pts=10, time=None):
        """Generates a blank raster surface using the provided value field.
        This needs to work with a material.
        """

        # get dimensions of self
        minx, miny, maxx, maxy = [round(coord)
                                  for coord in self.geometry.bounds]

        coords = np.array(list(self.geometry.exterior.coords))
        rr, cc = polygon(coords[:, 0], coords[:, 1], image.shape)

        #image[rr, cc] = getattr(self, value_field)

        image = np.zeros((maxx, maxy))

        if time:
            value = self.data.iloc[0][variable]
        else:
            value = getattr(self, variable)

        image = np.zeros((maxx, maxy)) + value
        return image

    def render(self, value_field, image=[], res=1):

        # if no image is provided create a blank
        if len(image) == 0:
            image = self.surface(value_field)
            image = rotate_image(image, 90)
            # else add the agent to the image
        else:
            coords = np.array(list(self.geometry.exterior.coords))
            rr, cc = polygon(coords[:, 0], coords[:, 1], image.shape)
            image[rr, cc] = getattr(self, value_field)

        if self.agents:
            for agent in self.agents:
                image = agent.render(value_field, image=image)

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
