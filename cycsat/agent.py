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

    def __init__(self, **variables):
        # clear the log and add init arguments
        self.data = GeoDataFrame()
        self.time = 0
        self.variables = variables
        self.log(**variables)
        self.parent = False
        self.__agents__ = list()

    @property
    def agents(self):
        return pd.Series(self.__agents__)

    @property
    def subdata(self):
        """Collects the current attributes of all agents by cascading."""
        log = self.data.tail(1)
        for agent in self.agents:
            log = log.append(agent.subdata, ignore_index=True)
        return log

    def add_agents(self, agents):
        if type(agents) is list:
            for agent in agents:
                agent.parent = self
                self.agents.append(agent)
        else:
            agent.parent = self
            self.agents.append(agent)

    def log(self, **args):
        """Log the agent's variables."""

        # if new args are added
        for arg in args:
            setattr(self, arg, args[arg])
            self.variables[arg] = args[arg]

        # get a snapshot of varibles
        log = {}
        for var in self.variables:
            log[var] = getattr(self, var)

        # append the log to dataframe
        self.data = self.data.append(log, ignore_index=True)

    def run(self, **args):
        """Evaluates the __run__ function and runs through sub agents."""
        self.time += 1

        try:
            result = self.__run__()
            if result:
                self.log(**result)
        except:
            pass

        for sub_agent in self.agents:
            sub_agent.run()

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
                    return geometry
        return False


     def surface(self, value_field):
        """Generates a blank raster surface using the provided value field."""
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

    def __run__(self, **args):
        """DEFINED. Returns a dictionary of attributes."""

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

    def setup(self, attempts=100):
        """Places the agent and all of it's sub agents randomly into a provided region.

        Parameters
        ----------
        agent - the agent to place the shape within
        attempts - the attempts before the placement fails
        """

        self.data = self.data.head(1)

        if self.parent:
            geometry = self.place_in(self.parent.geometry)
        else:
            geometry = self.geometry

        if geometry:
            self.data = self.data.set_value(0, 'geometry', geometry)
            self.geometry = geometry

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
