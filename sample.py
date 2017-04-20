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
from cycsat.archetypes import Facility, Feature, Shape, Rule, Rule2
from cycsat.prototypes.ByronIL import ByronIL
from cycsat.prototypes.rule import WITHIN

#------------------------------------------------------------------------
# Define a Reactor
#------------------------------------------------------------------------

db = Simulator('reactor_test_sample.sqlite')

temps = {'Reactor1': ByronIL,
         'Reactor2': ByronIL}

db.build(temps)
