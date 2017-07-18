import os

from math import pow
from math import sqrt

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

from shapely.geometry import Point, box
from shapely.affinity import rotate, translate
from shapely.ops import cascaded_union, unary_union, polygonize

from .geometry import posit_point


class Agent:

    def __init__(self, **attrs):
        """Creates an agent."""

        self.data = GeoDataFrame()
        self.time = 0
        self.attrs = attrs
        self.parent = False
        self.log(init=True)
        self.agents = list()
        self.materials = []

    def log(self, init=False):
        """Logs the agent's attrs."""

        if init:
            for attr in self.attrs:
                setattr(self, attr, self.attrs[attr])
            log = self.attrs
        else:
            log = {}
            for attr in self.attrs:
                log[attr] = getattr(self, attr)

        if self.geometry is not None:
            log['time'] = self.time
            self.data = self.data.append(log, ignore_index=True)

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

    def agenttree(self, origin=[]):
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
            log = log.append(agent.agenttree(
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

    def add_agents(self, agents):
        """Adds sub agents. Takes a list of agents or single agent."""
        if type(agents) is list:
            for agent in agents:
                agent.parent = self
                self.agents.append(agent)
        else:
            agents.parent = self
            self.agents.append(agents)

    def add_attrs(self, **args):
        """Adds a new variable to track in the log."""
        for arg in args:
            setattr(self, arg, args[arg])

        if self.attrs:
            self.attrs.update(args)
        else:
            self.attrs = args

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

    def assemble(self, time=None, iterations=100, attempts=100):
        """Places the agent and all of it's sub agents.

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

            if len(self.agents) > 0:
                mask = self.relative_geo
                for sub_agent in self.agents:
                    placed = sub_agent.place_in(mask, attempts)
                    if placed:
                        mask = mask.difference(sub_agent.geometry)
                        sub_agent.log()
                    else:
                        return False

        for sub_agent in self.agents:
            result = sub_agent.assemble()
            if not result:
                return False
        return True

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
                    return True
        return False

    def mask(self):
        """Returns a array mask of the agent's geometry."""

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

        # if no image is provided create a blank
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
        """DEFINED"""
        pass
