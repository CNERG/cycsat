import os
from shutil import copyfile

# copying the test database (this is just for repeated testing)
src = 'C:/Users/Owen/Documents/Academic/CNERG/reactor_test.sqlite'
dst = 'C:/Users/Owen/Documents/Academic/CNERG/cycsat/reactor_test.sqlite'
copyfile(src, dst)

###################################################################################################
'''
TESTING CYCSAT STARTS HERE
'''
###################################################################################################

from cycsat.simulation import Simulator
from cycsat.archetypes import Mission
from cycsat.prototypes.satellite import LANDSAT8, RGB

# initialize the simulator object and build the world
sim = Simulator('reactor_test.sqlite')
sim.build()

# generate events table
sim.simulate()

# define mission and satellite
mission = Mission(name='first test mission')
satellite = LANDSAT8(name='test satellite')

# prepare and launch mission
sim.prepare(mission,satellite)
sim.launch("Prototype='Reactor'",0,3)