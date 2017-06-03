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

from geopandas import GeoSeries
from pandas import pandas


class Simulation:

    def __init__(self, surfaces=None, agents=None, timesteps=None):
        """Sets up the xarray dataset and basic spatial simulation structure.

        Parameters
        ----------
        surfaces : numpy array
        agents : a list of agent instances
        timesteps : series of timesteps

        """
        self.timesteps = pd.DataFrame(
            {'label': timesteps, 'run': np.full((timesteps.size), False)})
        self.surfaces = pd.Series(surfaces)
        self.agents = pd.Series(agents)

    def data(self):
        """Combine the agent logs."""
        agent_data = list()
        for i, agent in enumerate(self.agents):
            agent_data.append(agent.data.assign(agent=i))
        agent_data = pd.concat(agent_data).reset_index()
        agent_data.rename(str, columns={'index': 'timestep'}, inplace=True)
        return agent_data

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

        # initial agents as the first timestep simulation run
        self.clear_agents()
        self.agents.apply(lambda x: x.init(self))
        self.timesteps.set_value(0, 'run', True)

        # run simulations for remaining timesteps
        for i, timestep in self.timesteps[1:].iterrows():
            self.agents.apply(lambda x: x.master_run(self, i))
            self.timesteps.set_value(i, 'run', True)

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


# class AgentGroup:


class Agent:

    def __init__(self):
        # log of updates
        self.metadata = pd.DataFrame()
        self.data = gpd.GeoDataFrame()

    def master_run(self, simulation, timestep):
        """Returns a dictionary the defines the agent's attributes at a single point in time."""
        data, metadata = self.run(simulation)
        self.record(data)

    def plot(self, ax=None, column=None):
        if ax:
            ax = ax
        else:
            fig, ax = plt.subplots(1)
            ax.set_aspect('equal')
        return self.data.plot(ax=ax, column=column)

    def record(self, data=None):
        """Records attributes."""
        self.metadata = self.metadata.append({}, ignore_index=True)
        if data:
            data = gpd.GeoDataFrame(index=[len(self.metadata)], data=data)
            self.data = self.data.append(data)
        else:
            pass

    def init(self, simulation):
        """Returns a dictionary that represents the agents atttributes at a particular point
        in time."""

        # example place randomly on Map
        minx, miny, maxx, maxy = simulation.surfaces[0].box.bounds
        x = random.randint(minx, maxx)
        y = random.randint(miny, maxy)

        self.record(
            {'geometry': Point(x, y).buffer(1), 'value': 0})

    def run(self, simulation):
        """Must return two dictonaries {data} and {metadata}."""

        # randomly decide the direction
        xoff = random.choice([-1, 1]) * 1
        yoff = random.choice([-1, 1]) * 1

        if random.choice([True, False]):
            return {}, {}

        # simulate a timestep
        return {'geometry': translate(self.data.geometry.iloc[-1], xoff, yoff),
                'value': self.data.value.iloc[-1] + np.random.normal(0),
                'max': self.data.value.iloc[-1] * self.data.value.max()}, {}
