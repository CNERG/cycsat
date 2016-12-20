import os
from shutil import copyfile

# # copying the test database (this is just for repeated testing)
src = 'C:/Users/Owen/Documents/Academic/CNERG/cycsat/simulations/four_reactors.sqlite'
dst = 'C:/Users/Owen/Documents/Academic/CNERG/cycsat/reactor_test_sample.sqlite'
copyfile(src, dst)

# =============================================================================
# TESTING CYCSAT STARTS HERE
# =============================================================================

from cycsat.simulation import Simulator
from cycsat.archetypes import Mission, Facility, Site, Satellite
from cycsat.prototypes.satellite import LANDSAT8, RGB
from cycsat.prototypes.reactor import SampleReactor
from cycsat.image import Sensor

# initialize the simulator object and build the world
sim = Simulator('reactor_test_sample.sqlite')
sim.build(AgentId=20)

# # generate events table
# sim.simulate()

# #define mission and satellite
# satellite = RGB(name='test')
# mission = Mission(name='first test mission')

# # # prepare and launch mission
# sim.prepare(mission,satellite)
# sim.launch("Prototype='Reactor' AND AgentId=20",0,3)

# # sim.dir = 'output/first test mission-1/'
# # for i in range(40):
# # 	try:
# # 		sim.plot_timestep(i,instrument_id=2)
# # 	except:
# # 		continue

# # from cycsat import terrain, image