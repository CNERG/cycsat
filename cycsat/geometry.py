"""

features.py

units in centimeters

"""

from random import randint

import numpy as np
from shapely.geometry import Polygon, Point
from shapely.wkt import loads as load_wkt
from shapely.affinity import translate as shift_shape

def place_features(Site):
	'''
	Builds a site by fixing the placement of all it's features and giving them geometries.

	'''

	canvas = Polygon([(0,0),(0,Site.width),(Site.length,Site.width),(Site.length,0)])
	built_features = []

	for feature in Site.features:

		shape = load_wkt(feature.geometry)

		runs = 1
		unbuilt = True

		while unbuilt:

			shape_x = shape.centroid.coords.xy[0][0]
			shape_y = shape.centroid.coords.xy[1][0]
		
			posit = Point(randint(0,Site.width+1), randint(0,Site.length+1))
			posit_x = posit.coords.xy[0][0]
			posit_y = posit.coords.xy[1][0]

			shift_x = posit_x - shape_x
			shift_y = posit_y - shape_y

			posited = shift_shape(shape,xoff=shift_x,yoff=shift_y)

			if posited.within(canvas):
				
				overlaps = [posited.disjoint(x) for x in built_features]

				if False in overlaps:
					runs+=1
					continue
				else:
					built_features.append(posited)
					unbuilt = False
					continue
			else:
				runs+=1
				continue

			if runs>20:
				print('failed to place')
				break

	return built_features

'''
basic shapely shape templates

'''

class Circle(object):
	def __init__(self,width=4000):
		self.geometry = Point(0,0).buffer(width)	

class Rectangle(object):
	def __init__(self,width=3800,length=8500):
		self.geometry = Polygon([(0,0),(0,width),(length,width),(length,0)])