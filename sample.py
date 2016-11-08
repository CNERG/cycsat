from cycsat.simulator import Designer

#from cycsat.geometry import draft_blueprint, assess_blueprint
from cycsat.geometry import place_shape, place_feature
from cycsat.geometry import create_blueprint, assess_blueprint

from cycsat.database import Base
from cycsat.database import Satellite,Instrument, Mission, Shape, Facility
from cycsat.database import Site, Feature

from cycsat.database import Circle, Rectangle

import os

try:
	os.remove('space agency.db')
except:
	pass

# open/create a agency
hq = Designer('space agency')

# create a satellite
sat = Satellite(name='land viewer')

# create a new mission with one site
mission = Mission(name='pilot mission')
sat.missions.append(mission)

# add a new site
site = Site(name='landscape',width=5000,length=5000)

facility = Facility(name='reactor',width=862, length=877)

# create a cooling tower with some shapes
cooling_tower = Feature(name='cooling tower 1')
cooling_tower.shapes.append(Circle(radius=900,color='[146,149,155]'))
cooling_tower.shapes.append(Circle(level=1,radius=620,color='[79,81,84]'))
cooling_tower.shapes.append(Circle(level=2,radius=800,color='[255,255,255]',xoff=500,yoff=500,visibility=25))

#create a cooling tower with some shapes
cooling_tower2 = Feature(name='cooling tower 2')
cooling_tower2.shapes.append(Circle(radius=900,color='[146,149,155]'))
cooling_tower2.shapes.append(Circle(level=1,radius=620,color='[79,81,84]'))

# create a cooling tower with some shapes
turbine_building = Feature(name='turbine building')
turbine_building.shapes.append(Rectangle(width=580,length=2220,color='[208,40,14]'))

# create a containement building
containment1 = Feature(name='containment building 1')
containment1.shapes.append(Circle(radius=520,color='[70,70,70]'))
containment1.shapes.append(Circle(radius=340,level=1,color='[70,70,70]'))

# create a containment building
containment2 = Feature(name='containment building 2')
containment2.shapes.append(Circle(radius=520,color='[70,70,70]'))
containment2.shapes.append(Circle(radius=520,level=1,color='[70,70,70]'))

facility.features = [cooling_tower, cooling_tower2, 
					turbine_building, containment1, containment2]

site.facilities.append(facility)
mission.sites.append(site)

# save the data to the database
hq.save(sat)
facility.build()
hq.save(facility)