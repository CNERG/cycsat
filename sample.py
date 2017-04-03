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

SampleReactor = Facility(name='test reactor',width=1100,length=1100)

ConcretePad = Feature(name='concrete pad')
ConcretePad.level = 0
ConcretePad.visibility = 100
ConcretePad.shapes = [Rectangle(width=700,length=685,rgb=[155,155,155])]
ConcretePad.rules = [Rule(oper='ROTATE',value=0)]
SampleReactor.features.append(ConcretePad)

ParkingLot = Feature(name='parking lot')
ParkingLot.level = 1
ParkingLot.visibility = 100
ParkingLot.shapes = [Rectangle(width=223,length=224,rgb=[70,70,70])]
ParkingLot.rules = [Rule(oper='NEAR',target='concrete pad',value=0),
					Rule(oper='ROTATE',value=0)]
SampleReactor.features.append(ParkingLot)

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


# Containment1 = Feature(name='containment 1')
# Containment1.level = 1
# Containment1.visibility = 100
# Containment1.shapes = [Circle(radius=30,rgb=[70,70,70])]
# Containment1.rules = [Rule(oper='WITHIN',target='concrete pad')]
# SampleReactor.features.append(Containment1)

# Containment2 = Feature(name='containment 2')
# Containment2.level = 1
# Containment2.visibility = 100
# Containment2.shapes = [Circle(radius=30,rgb=[70,70,70])]
# Containment2.rules = [Rule(oper='WITHIN',target='concrete pad'),
# 					  Rule(oper='NEAR',target='containment 1',value=20),
# 					  Rule(oper='AXIS',target='containment 1',direction='X')]
# SampleReactor.features.append(Containment2)

# Turbine = Feature(name='turbine building')
# Turbine.level = 1
# Turbine.visibility = 100
# Turbine.shapes = [Rectangle(width=223,length=30,rgb=[70,70,70])]
# Turbine.rules = [Rule(oper='WITHIN',target='concrete pad'),
# 				 Rule(oper='NEAR',target='containment 1',value=50),
# 				 Rule(oper='ROTATE',value=0),
# 				 Rule(oper='AXIS',target='containment 1',direction='Y')]
# SampleReactor.features.append(Turbine)

# Building = Feature(name='set building')
# Building.level = 1
# Building.visibility = 100
# Building.shapes = [#Rectangle(width=75,length=15,rgb=[70,70,70],xoff=-40),]
# 				   Rectangle(width=75,length=15,rgb=[70,70,70]),
# 				   Rectangle(width=75,length=15,rgb=[70,70,70],xoff=40)]
# Building.rules = [Rule(oper='WITHIN',target='concrete pad'),
# 				 Rule(oper='ROTATE',value=0)]
# SampleReactor.features.append(Building)


# this defines what the a reactor is
templates = {
	'Reactor' : SampleReactor,
}

# load and build the dataset
sim = CycSat('reactor_test_sample.sqlite')
#sim.build('new',templates=templates)