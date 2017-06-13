import os
from shutil import copyfile
import random
import pandas as pd

from cycsat.archetypes import Agent

agents = pd.Series([Agent(value=i) for i in range(10)])

for agent in agents:
    for i in range(100):
        agent.run(value=i)
