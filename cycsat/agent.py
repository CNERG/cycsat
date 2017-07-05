import os

from math import pow
from math import sqrt

import pandas as pd
from geopandas import GeoDataFrame
import numpy as np
import random
import rasterio

from cycsat.laboratory import USGSMaterial

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
        self.materials = [USGSMaterial('lawn_grass_gds91b.31126.asc')]

    @property
    def agentframe(self):
        """Attributes frame of all sub agents."""
        agent_frame = GeoDataFrame()
        for agent in self.agents:
            agent_frame = agent_frame.append(
                agent.data.tail(1), ignore_index=True)
        return agent_frame

    def agenttree(self, origin=[]):
        """Collects the current attributes of all agents by cascading."""

        log = self.data.tail(1)

        if len(origin) > 0:
            log = log.assign(geometry=log.translate(
                xoff=origin[0], yoff=origin[1]))
            origin += self.origin
        else:
            log = log.assign(geometry=self.relative_geo)
            origin = np.array([0.0, 0.0])

        for agent in self.agents:
            log = log.append(agent.agenttree(origin.copy()), ignore_index=True)

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

    def translate(self, shift):
        if shift:
            return translate(self.geometry, xoff=shift[0], yoff=shift[1])

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
                mask = self.relative_geo
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

    def surface(self, value_field, ctrlpts=10):

        # get dimensions corners
        minx, miny, maxx, maxy = [round(coord)
                                  for coord in self.geometry.bounds]
        ylen = maxy - miny
        xlen = maxx - minx

        image = np.zeros((ylen, xlen))

        rel_geo = translate(
            self.geometry, xoff=-1 * minx, yoff=-1 * miny)

        coords = np.array(list(rel_geo.exterior.coords))
        rr, cc = polygon(coords[:, 0], coords[:, 1], image.shape)
        image[rr, cc] = getattr(self, value_field)
        return image

    def render(self, value_field, image=[], origin=[], res=1):

        # if no image is provided create a blank
        if len(image) == 0:
            image = self.surface(value_field)
            origin = np.array([0.0, 0.0])
            # image = rotate_image(image, 90)
        else:
            origin += self.origin
            minx, miny, maxx, maxy = [round(coord)
                                      for coord in self.geometry.bounds]
            minx += origin[0]
            maxx += origin[0]
            image[miny:maxy, minx:maxx] = self.surface(value_field)

        for agent in self.agents:
            image = agent.render(value_field, image=image,
                                 origin=origin.copy())

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


# def pointValue(x, y, power, smoothing, xv, yv, values):
#     nominator = 0
#     denominator = 0
#     for i in range(0, len(values)):
#         dist = sqrt((x - xv[i]) * (x - xv[i]) + (y - yv[i])
#                     * (y - yv[i]) + smoothing * smoothing)
#         # If the point is really close to one of the data points, return the
#         # data point value to avoid singularities
#         if(dist < 0.0000000001):
#             return values[i]
#         nominator = nominator + (values[i] / pow(dist, power))
#         denominator = denominator + (1 / pow(dist, power))
#     # Return NODATA if the denominator is zero
#     if denominator > 0:
#         value = nominator / denominator
#     else:
#         value = -9999
#     return value


# def invDist(xv, yv, values, xsize=100, ysize=100, power=2, smoothing=0):
#     valuesGrid = np.zeros((ysize, xsize))
#     for x in range(0, xsize):
#         for y in range(0, ysize):
#             valuesGrid[y][x] = pointValue(
#                 x, y, power, smoothing, xv, yv, values)
#     return valuesGrid
