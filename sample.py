import os
from shutil import copyfile

# copying the test database (this is just for repeated testing)
src = 'C:/Users/Owen/Documents/Academic/CNERG/reactor_test.sqlite'
dst = 'C:/Users/Owen/Documents/Academic/CNERG/cycsat/reactor_test.sqlite'
copyfile(src, dst)

###################################################################################################
'''
STAGING GROUND:
TESTING CYCSAT STARTS HERE
'''
###################################################################################################

from cycsat.simulation import Simulator
from cycsat.prototypes.instrument import RedBand, BlueBand, GreenBand
from cycsat.archetypes import Satellite,Instrument, Mission, Shape, Facility,Scene, Event
from cycsat.prototypes.satellite import StandardRGB

# initialize the simulator object
sim = Simulator('reactor_test.sqlite')
sim.build()

# select a facility and draw it using the RedBand
sim.simulate()

# define mission and satellite
mission = Mission(name='first test mission')
satellite = StandardRGB(name='test satellite')

sim.prepare(mission,satellite)
sim.launch(mission,satellite)

# "launch" sat and collect write scenes for a new mission
#sim.launch(Mission(name='test'),StandardRGB())