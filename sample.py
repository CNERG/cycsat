<<<<<<< HEAD
import os
from shutil import copyfile
import random
import pandas as pd

from cycsat.archetypes import Agent

agents = pd.Series([Agent(value=i) for i in range(10)])

for agent in agents:
    for i in range(100):
        agent.run(value=i)
=======
from cycsat.agent import Agent
from shapely.geometry import Polygon, box, Point

# initalize agents with random values
site = Agent(geometry=box(0, 0, 100, 100))
site.sub_agents = [Agent(geometry=Point(0, 0).buffer(10))]
>>>>>>> ab384eeb8dd8fd557d4ac8d9ae20f528aa8a296f
