
# coding: utf-8

# ### spatial decision modeling

import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, box
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
        # initalize
        self.agents.apply(lambda x: x.init(self))

        for t in self.timesteps[1:]:
            self.agents.apply(lambda x: x.run(self))

    def clear(self):
        self.agents.apply(lambda x: x.__init__())


class Landscape:

    def __init__(self, maxx, maxy):
        self.maxx = maxx
        self.maxy = maxy
        self.vector = box(0, 0, maxx, maxy)
        self.raster = np.zeros((maxx, maxy))


class Agent:

    def __init__(self):
        # stores time relevant data for variables (columns)
        self.data = gpd.GeoDataFrame()

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
               'value': self.data.value.iloc[-1]}

        self.data = self.data.append(new, ignore_index=True)


# ------------------------------------------------------------------
# testing
# ------------------------------------------------------------------

    # creating the simulation
s = Simulation(Landscape(100, 100),
               [Agent() for x in range(3)],
               timesteps=pd.date_range('1/1/2015', '12/31/2015'))
