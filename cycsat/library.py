'''
library.py

'''
from .data_model import Facility, Feature, Shape, Circle, Rectangle


reactor = Facility(name='reactor',width=862, length=877)

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

reactor.features = [cooling_tower, cooling_tower2, 
					turbine_building, containment1, containment2]