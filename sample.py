import os
from shutil import copyfile
import random

# copying the test database (this is just for repeated testing)
src = 'C:/Users/Owen/Documents/Academic/CNERG/cycsat/simulations/four_reactors.sqlite'
dst = 'C:/Users/Owen/Documents/Academic/CNERG/cycsat/reactor_test_sample.sqlite'
copyfile(src, dst)

# =============================================================================
# TESTING CYCSAT STARTS HERE
# =============================================================================
from cycsat.simulation import Simulator
from cycsat.prototypes.ByronIL import ByronIL
from cycsat.laboratory import USGSMaterial
from cycsat.prototypes.instrument import Red

#------------------------------------------------------------------------
# Define a Reactor
#------------------------------------------------------------------------

db = Simulator('reactor_test_sample.sqlite')
temps = {'Reactor1': ByronIL}
db.build(temps)
# db.simulate()

m = USGSMaterial('whitebark-pine_ynp-wb-1.30869.asc')

# site = db.Site(1)
# red = Red()
# red.calibrate(site)
