
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

        geometry = np.empty((self.timesteps.size, self.agents.size))

        self.data = xr.Dataset(
            {'geometry': (('timestep', 'agent'), geometry)},
            {'timestep': timesteps,
             'agent': self.agents.index}
        )

    def run(self):
        pass

#     def plot(self,timestep=0):
#         fig = plt.figure()
#         ax = fig.add_subplot(111)
#         ax.set_xlim([0,self.Map.maxx])
#         ax.set_ylim([0,self.Map.maxy])
#         ax.add_patch(PolygonPatch(self.Map.vector))
#         ax.set_aspect('equal')

#         for agent in self.agents:
#             for point in agent.track:
#                 ax.add_patch(PolygonPatch(point.buffer(1),facecolor='red'))

#         return fig, ax


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

    def place(self, simulation):
        # example place randomly on Map
        minx, miny, maxx, maxy = simulation.landscape.vector.bounds
        x = random.randint(minx, maxx)
        y = random.randint(miny, maxy)
        self.data = self.data.append(
            {'geometry': Point(x, y)}, ignore_index=True)


class Variable:
    pass


#     def run(self, timestep):
#         """This function defines what the agent does at a timestep"""

#         # randomly decide the direction
#         xoff = random.choice([-1,1])*1
#         yoff = random.choice([-1,1])*1

#         # create the record of the action (dictionary)
#         data = {
#             'geometry': translate(self.location(), xoff ,yoff)
#         }

#         # track location
#         self.track.append(data,ignore_index=True)

# ps = list()
# for agent in s.agents:
#     for t in agent.track:
#         ps.append({'geometry':t.buffer(1),'agent':agent.name})

# gdf = geopandas.GeoDataFrame(ps)

# fig = plt.figure(figsize=(7, 5))
# ax = fig.add_subplot(111)
# gdf.plot(ax=ax,column='agent',categorical=True,legend=True)

# ------------------------------------------------------------------
# testing
# ------------------------------------------------------------------

    # creating the simulation
s = Simulation(Landscape(100, 100),
               [Agent() for x in range(3)],
               timesteps=pd.date_range('1/1/2015', '12/31/2015'))
