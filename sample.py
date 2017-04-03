import os
from shutil import copyfile
import random

# copying the test database (this is just for repeated testing)
# src = 'C:/Users/Owen/Documents/Academic/CNERG/cycsat/simulations/four_reactors.sqlite'
# dst = 'C:/Users/Owen/Documents/Academic/CNERG/cycsat/reactor_test_sample.sqlite'
# copyfile(src, dst)

# =============================================================================
# TESTING CYCSAT STARTS HERE
# =============================================================================
from cycsat.simulation import CycSat
from cycsat.archetypes import Facility, Feature, Shape, Rule
from cycsat.prototypes.reactor import SampleReactor

sr = SampleReactor()

sr = Facility(name='test',width=800,length=800)


# this defines what the 
templates = {
	'Reactor' : sr,
}

sim = CycSat('reactor_test_sample.sqlite')
# sim.build('new',templates=templates)