import numpy as np
import pandas as pd
import geopandas as gpd

from shapely.geometry import Point, box, shape
from shapely.affinity import translate

from descartes import PolygonPatch
import random
import seaborn as sns
from collections import defaultdict
import inspect

import xarray as xr


class Simulation:

    def __init__(self, landscape=None, agents=None, timesteps=None):
        """Sets up the xarray dataset and basic spatial simulation structure.

        Parameters
        ----------
        landscape : a Landscape object
        agents : a list of agent instances
        timesteps : series of timesteps

        """
        self.landscape = landscape
        self.agents = pd.Series(agents, name='agents')
        self.timesteps = pd.Series(timesteps, name='timesteps')

        # geometry = np.empty((self.timesteps.size, self.agents.size))

        # self.data = xr.Dataset(
        #     {'geometry': (('timestep', 'agent'), geometry)},
        #     {'timestep': timesteps,
        #      'agent': self.agents.index}
        # )

    def run(self):
        """Initializes all agents and initializes the simulation."""

        self.agents.apply(lambda x: x.init(self))
        for t in self.timesteps[1:]:
            self.agents.apply(lambda x: x.run(self))

    def clear_agents(self):
        """Clears the data log for all agents."""
        self.agents.apply(lambda x: x.__init__())


class Layer:

    def __init__(self, envelope):
        self.envelope = geometry
        minx, miny, maxx, maxxy = geometry.bounds
        self.raster = geometry = np.empty(())

    def raster(self):
        geometry.bounds

        # self.data = xr.Dataset(
        #     {'geometry': (('timestep', 'agent'), geometry)},
        #     {'timestep': timesteps,
        #      'agent': self.agents.index}
        # )


class Agent:

    def __init__(self, geometry=None):

        # stores time relevant data for variables (columns)
        self.data = gpd.GeoDataFrame()
        self.geometry = geometry

    def init(self, simulation):
        # example place randomly on Map
        minx, miny, maxx, maxy = simulation.landscape.vector.bounds
        x = random.randint(minx, maxx)
        y = random.randint(miny, maxy)

        self.data = self.data.append(
            {'geometry': Point(x, y).buffer(1),
             'value': 0}, ignore_index=True)

    def run(self, simulation):
        # randomly decide the direction
        xoff = random.choice([-1, 1]) * 1
        yoff = random.choice([-1, 1]) * 1

        # simulate a timestep
        new = {'geometry': translate(self.data.geometry.iloc[-1], xoff, yoff),
               'value': self.data.value.iloc[-1] + np.random.normal(0)}

        self.data = self.data.append(new, ignore_index=True)


class SpatialObject:

    def __init__(self, geometry=None, array=None):
        if geometry and array:
            print('both parameters geometry')
        self.set_geometry(geometry)

    def set_geometry(self, geometry):
        self.geometry = geometry


# ------------------------------------------------------------------
# testing
# ------------------------------------------------------------------

s = Simulation(Landscape(100, 100),
               [Agent() for x in range(3)],
               timesteps=pd.date_range('1/1/2015', '12/31/2015'))
