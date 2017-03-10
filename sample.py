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
from descartes import PolygonPatch

from cycsat.simulation import Simulation
from cycsat.archetypes import Mission, Facility, Site, Satellite, Shape, Rule, Event
from cycsat.prototypes.satellite import LANDSAT8, RGB
from cycsat.prototypes.reactor import SampleReactor
from cycsat.prototypes.instrument import Blue, Red, Green
from cycsat.image import Sensor


from cycsat.geometry import Polygon, Point, box
from cycsat.archetypes import Facility, Feature, Rule, Condition, Shape

#------------------------------------------------------------------------------------
# Defining the facilities
#------------------------------------------------------------------------------------

Pad = Feature(name='concrete pad',level=0,visibility=100)
Pad.shapes = [Shape(stable_wkt=box(0,0,6000,6000).wkt,rgb='[204,204,204]')]

CoolingTower1 = Feature(name='cooling tower 1')
CoolingTower1.shapes = [Shape(stable_wkt=Point(0,0).buffer(800).wkt,rgb='[70,70,70]')]

CoolingTower2 = Feature(name='cooling tower 2')
CoolingTower2.shapes = [Shape(stable_wkt=Point(0,0).buffer(800).wkt,rgb='[70,70,70]')]
CoolingTower2.rules.append(Rule(oper='NEAR',target='cooling tower 1',value=100))

Plume = Feature(name='plume',visibility=99, level=2)
Plume.shapes = [Shape(stable_wkt=Point(500,500).buffer(500).wkt,rgb='[255,255,255]')]
Plume.rules = [Rule(oper='WITHIN',target='cooling tower 1',value=300)]

Reactor = Facility()
Reactor.name = 'demo'
Reactor.width = 862
Reactor.length = 862
Reactor.features = [CoolingTower1,
				    CoolingTower2,
				    Plume,
				    #Pad
				    ]

template = {'Reactor':Reactor}

#------------------------------------------------------------------------------------
# Running the simulations
#------------------------------------------------------------------------------------

# # create the simulation by reading the database and supplying a template list
sim = Simulation('reactor_test_sample.sqlite')
# sim.build(template)

