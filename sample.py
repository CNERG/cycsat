import os
from shutil import copyfile
import random

from cycsat.archetypes import Agent

agents = pd.Series([Agent(name=i) for i in range(10)])

for agent in agents:
    agent.run(name=random.randint(0, 10))
