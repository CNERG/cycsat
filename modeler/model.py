import numpy as np
import pandas as pd
import geopandas as gpd

from shapely.geometry import Point, box, shape
from shapely.affinity import translate

from descartes import PolygonPatch
import random
# import seaborn as sns
from collections import defaultdict
import inspect

import xarray as xr
from matplotlib import pyplot as plt


class Simulation:

    def __init__(self, surfaces=None, agents=None, timesteps=None):
        """Sets up the xarray dataset and basic spatial simulation structure.

        Parameters
        ----------
        surface : a Landscape object
        agents : a list of agent instances
        timesteps : series of timesteps

        """

        self.surfaces = pd.Series(surfaces, name='surfaces')
        self.agents = pd.Series(agents, name='agents')
        self.timesteps = pd.Series(timesteps, name='timesteps')

        # geometry = np.empty((self.timesteps.size, self.agents.size))

        # self.data = xr.Dataset(
        #     {'geometry': (('timestep', 'agent'), geometry)},
        #     {'timestep': timesteps,
        #      'agent': self.agents.index}
        # )

    def plot(self, ax=None, surfaces=False):
        if ax:
            ax = ax
        else:
            fig, ax = plt.subplots(1)
            ax.set_aspect('equal')

        self.surfaces.apply(lambda x: x.plot(ax=ax))
        self.agents.apply(lambda x: x.plot(ax=ax))

    def run(self):
        """Initializes all agents and initializes the simulation."""

        self.agents.apply(lambda x: x.init(self))
        for t in self.timesteps[1:]:
            self.agents.apply(lambda x: x.run(self))

    def clear_agents(self):
        """Clears the data log for all agents."""
        self.agents.apply(lambda x: x.__init__())


class Surface:

    def __init__(self, array):
        self.data = array
        self.box = box(0, 0, *array.shape)

    def plot(self, ax=None):
        if ax:
            ax = ax
        else:
            fig, ax = plt.subplots(1)
            ax.set_aspect('equal')
        return ax.imshow(self.data)

        # class Population:


class Agent:

    def __init__(self, **attrs):
        self.log = gpd.GeoDataFrame(attrs)

    def plot(self, ax=None):
        if ax:
            ax = ax
        else:
            fig, ax = plt.subplots(1)
            ax.set_aspect('equal')
        return self.log.plot(ax=ax)

    def init(self, simulation):
        # example place randomly on Map
        minx, miny, maxx, maxy = simulation.surfaces[0].box.bounds
        x = random.randint(minx, maxx)
        y = random.randint(miny, maxy)

        self.log = self.log.append(
            {'geometry': Point(x, y).buffer(1),
             'value': 0}, ignore_index=True)

    def run(self, simulation):
        # randomly decide the direction
        xoff = random.choice([-1, 1]) * 1
        yoff = random.choice([-1, 1]) * 1

        # simulate a timestep
        new = {'geometry': translate(self.log.geometry.iloc[-1], xoff, yoff),
               'value': self.log.value.iloc[-1] + np.random.normal(0)}

        self.log = self.log.append(new, ignore_index=True)
