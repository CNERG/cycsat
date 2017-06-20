import os

import pandas as pd
from geopandas import GeoDataFrame
import numpy as np
import random
import rasterio

from skimage.draw import polygon

from shapely.geometry import Point
from shapely.affinity import rotate, translate


class Agent:

    def __init__(self, **args):
        # clear the log and add init arguments
        self.data = GeoDataFrame()
        self.step = 0
        self.log(step=int(self.step), **args)
        self.agents = list()

    @property
    def subdata(self):
        """Collects the current attributes of all agents by cascading."""
        log = self.data.tail(1)
        for agent in self.agents:
            log = log.append(agent.subdata, ignore_index=True)
        return log

    def log(self, **args):
        """Record information about the agent."""

        # set and log initial attributes
        for arg in args:
            setattr(self, arg, args[arg])

        # archive attributes
        self.data = self.data.append(args, ignore_index=True)

    def surface(self, value_field):
        """Generates a blank raster surface."""
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

        return image

    def run(self, parent_agent=None, steps=1, **args):
        """Evaluates the USER DEFINED EVALUATE function and runs through sub a gents."""

        for step in range(steps):
            self.step = self.step + 1

            try:
                result = self.__run__(parent_agent=parent_agent, **args)
            except:
                result = None

            if result:
                self.log(step=int(self.step), **result)
            else:
                pass

            for sub_agent in self.agents:
                sub_agent.run(parent_agent=self)

    def __run__(self, **args):
        """USER DEFINED. Return a dictionary of attributes to record, or None."""

        #geometry = self.place_in(args['parent_agent'])
        g = translate(self.geometry, xoff=random.randint(-5, 5),
                      yoff=random.randint(-5, 5))

        return {'value': self.value + random.randint(-5, 5),
                'geometry': g}

    def evaluate(self, parent_agent=None):

        # if this is the top agent return its geometry
        if not parent_agent:
            return False

        try:
            result = self.__evaluate__(parent_agent)
            if 'shapely' in fullname(result):
                return result
            else:
                return parent_agent.geometry
        except:
            return parent_agent.geometry

    def __evaluate__(self, parent_agent, **args):
        """USER DEFINED. Given a parent agent, evaluates the placement relative to all other agents.
        """
        return parent_agent.geometry

    def place_in(self, parent_agent, attempts=100):
        """Places the agent within another agent's geometry."""
        # bounding region of parent agent

        region = self.evaluate(parent_agent=parent_agent)
        if not region:
            return self.geometry

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
                    return geometry
        return False

    def setup(self, parent_agent=None, attempts=100):
        """Places the agent and all of it's sub agents randomly into a provided region.

        Parameters
        ----------
        agent - the agent to place the shape within
        attempts - the attempts before the placement fails
        """

        self.data = self.data.head(1)

        if parent_agent:
            result = self.place_in(parent_agent)
            if result:
                self.data = self.data.set_value(0, 'geometry', result)
                self.geometry = result
        else:
            pass

        for sub_agent in self.agents:
            sub_agent.setup(parent_agent=self, attempts=attempts)


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


# class SpatialRule:

#     def __init__(self):
#         pass

#     @property
#     def targets(self, agents, attr=None):
#         """Finds the targets given a list."""


# class NEAR(SpatialRule):

#     def __init__(self, target, value):
#         self.target = target
#         self.value = value
#         pass

#     def run(self):
