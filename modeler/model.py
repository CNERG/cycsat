import numpy as np
import pandas as pd
import geopandas as gpd

from shapely.geometry import Point, box, shape
from shapely.affinity import translate

from descartes import PolygonPatch
import random
from collections import defaultdict
import inspect

import xarray as xr
from matplotlib import pyplot as plt


class Simulation:

    def __init__(self, surfaces=None, agents=None, timesteps=None):
        """Sets up the xarray dataset and basic spatial simulation structure.

        Parameters
        ----------
        surfaces : numpy array
        agents : a list of agent instances
        timesteps : series of timesteps

        """
        self.timesteps = pd.Series(timesteps)
        self.surfaces = pd.Series(surfaces)
        self.agents = pd.Series(agents)

    def data(self):
        """Combine the agent logs."""
        agent_logs = list()
        for i, agent in enumerate(self.agents):
            agent_log = agent.log
            agent_logs.append(agent_log.assign(agent=i))
        return pd.concat(agent_logs)

    def plot(self, ax=None, surfaces=False, column=None):
        if ax:
            ax = ax
        else:
            fig, ax = plt.subplots(1)
            ax.set_aspect('equal')

        if surfaces:
            self.surfaces.apply(lambda x: x.plot(ax=ax))
        else:
            self.surfaces.apply(lambda x: x.plot(ax=ax, box=True))
        self.agents.apply(lambda x: x.plot(ax=ax, column=column))

    def run(self):
        """Initializes all agents and initializes the simulation."""

        self.clear_agents()
        self.agents.apply(lambda x: x.init(self))
        for timestep in self.timesteps[1:]:
            self.agents.apply(lambda x: x.run(self))

    def clear_agents(self):
        """Clears the data log for all agents."""
        self.agents.apply(lambda x: x.__init__())


class Surface:

    def __init__(self, data):
        self.data = data
        self.box = box(0, 0, *data.shape)

    def plot(self, ax=None, box=False):
        if ax:
            ax = ax
        else:
            fig, ax = plt.subplots(1)
            ax.set_aspect('equal')
        if box:
            return ax.add_patch(PolygonPatch(self.box))
        return ax.imshow(self.data)


class Agent:

    def __init__(self):
        # log of updates
        self.log = gpd.GeoDataFrame()

    def plot(self, ax=None, column=None):
        if ax:
            ax = ax
        else:
            fig, ax = plt.subplots(1)
            ax.set_aspect('equal')
        return self.log.plot(ax=ax, column=column)

    def record(self, data):
        self.log = self.log.append(data, ignore_index=True)

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
        self.record({'geometry': translate(self.log.geometry.iloc[-1], xoff, yoff),
                     'value': np.random.normal(0)})
