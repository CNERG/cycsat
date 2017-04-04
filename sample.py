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
from cycsat.simulation import CycSat
from cycsat.archetypes import Facility, Feature, Shape, Rule
from cycsat.shapes import Circle, Rectangle

#------------------------------------------------------------------------
# Define a Reactor
#------------------------------------------------------------------------

SampleReactor = Facility(name='test reactor',width=2000,length=2000)

ConcretePad = Feature(name='concrete pad')
ConcretePad.level = 0
ConcretePad.visibility = 100
ConcretePad.shapes = [Rectangle(width=700,length=685,rgb=[155,155,155])]
ConcretePad.rules = [Rule(oper='ROTATE',value=20)]
SampleReactor.features.append(ConcretePad)

BuildingSet = Feature(name='cooling tower 1')
BuildingSet.level = 1
BuildingSet.visibility = 100
BuildingSet.shapes = [Rectangle(width=73,length=13,rgb=[70,70,70])]
BuildingSet.rules = [Rule(oper='WITHIN',target='concrete pad'),
					 Rule(oper='ROTATE',target='concrete pad')]
SampleReactor.features.append(BuildingSet)


CoolingTower1 = Feature(name='cooling tower 1')
CoolingTower1.level = 1
CoolingTower1.visibility = 100
CoolingTower1.shapes = [Circle(radius=110,rgb=[70,70,70])]
CoolingTower1.rules = [Rule(oper='WITHIN',target='concrete pad')]
SampleReactor.features.append(CoolingTower1)


# CoolingTower2 = Feature(name='cooling tower 2')
# CoolingTower2.level = 1
# CoolingTower2.visibility = 100
# CoolingTower2.shapes = [Circle(radius=110,rgb=[70,70,70])]
# CoolingTower2.rules = [Rule(oper='WITHIN',target='concrete pad'),
# 					   Rule(oper='NEAR',target='cooling tower 1',value=100),
# 					   Rule(oper='AXIS',target='cooling tower 1',direction = 'X')]
# SampleReactor.features.append(CoolingTower2)

# this defines what the a reactor is
templates = {
	'Reactor' : SampleReactor,
}

# load and build the dataset
sim = CycSat('reactor_test_sample.sqlite')
#sim.build('new',templates=templates)