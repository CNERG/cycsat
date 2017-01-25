import os
from shutil import copyfile

# # copying the test database (this is just for repeated testing)
src = 'C:/Users/Owen/Documents/Academic/CNERG/cycsat/simulations/four_reactors.sqlite'
dst = 'C:/Users/Owen/Documents/Academic/CNERG/cycsat/reactor_test_sample.sqlite'
copyfile(src, dst)

# =============================================================================
# TESTING CYCSAT STARTS HERE
# =============================================================================

from cycsat.simulation import Simulator, Cysat
from cycsat.archetypes import Mission, Facility, Site, Satellite, Terrain, Shape
from cycsat.prototypes.satellite import LANDSAT8, RGB
from cycsat.prototypes.reactor import SampleReactor
from cycsat.prototypes.shapes import Circle
from cycsat.image import Sensor


sim = Cysat('reactor_test_sample.sqlite')
