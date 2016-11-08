"""

geometry.py

units in centimeters

"""
from sqlalchemy import Column, Integer, String

from random import randint
import itertools

import numpy as np
from shapely.geometry import Polygon, Point
from shapely.wkt import loads as load_wkt
from shapely.affinity import translate as shift_shape
from shapely.ops import cascaded_union

'''
a blueprint object is a copy of all the shapes placed onto the footprint of a facility

'''

def create_blueprint(Facility,max_attempts=20):
	'''
	Posits (or proposes) locations for all the features at a facility
	
	'''
	Facility.build_footprint()

	# place features
	for feature in Facility.features:
		placed = place_feature(feature, Facility.footprint,max_attempts=max_attempts)
		if placed:
			continue
		else:
			print('blueprint failed')


def assess_blueprint(Facility):
	'''
	'''
	shape_stack = dict()

	# build a shape stack by level
	for feature in Facility.features:
		for shape in feature.shapes:
			geometry = shape.build_geometry(placed=True)
			if shape.level in shape_stack:
				shape_stack[shape.level].append(geometry)
			else:
				shape_stack[shape.level] = [geometry]

	level_overlaps = []
	for level in shape_stack:
		level_overlaps.append(check_disjoints(shape_stack[level]))

	if False in level_overlaps:
		return False
	else:
		return True


def check_disjoints(shapes):

	for a, b in itertools.combinations(shapes, 2):
		if a.disjoint(b):
			continue
		else:
			return False

	return True


def posit_point(footprint):
	'''
	'''
	# define the footprint boundary
	length = footprint.bounds[-2]
	width = footprint.bounds[-1]

	# create a random point within footprint
	posited_point = Point(randint(0,width+1), randint(0,length+1))

	return posited_point


def place_shape(Shape,placement):
	'''
	Shifts a shape to a posited point and checks if it falls within the footprint
	'''
	placed_x = placement.coords.xy[0][0]
	placed_y = placement.coords.xy[1][0]

	geometry = Shape.build_geometry()
		
	shape_x = geometry.centroid.coords.xy[0][0]
	shape_y = geometry.centroid.coords.xy[1][0]
	
	shift_x = placed_x - shape_x + Shape.xoff
	shift_y = placed_y - shape_y + Shape.yoff

	Shape.placement = shift_shape(geometry,xoff=shift_x,yoff=shift_y).wkt
	
	return Shape


def place_feature(Feature,footprint,max_attempts=20):
	'''
	Posits (or proposes) a random placement for a feature within a facility footprint, returns
	a shape stack with proposed locations
	'''
	attempts = 0
	while attempts<max_attempts:

		posited_point = posit_point(footprint)

		typology_checks = list()
		for shape in Feature.shapes:
			place_shape(shape,posited_point)
			placement = shape.build_geometry(placed=True)
			typology_checks.append(placement.within(footprint))

		if False not in typology_checks:
			return True
		else:
			attempts+=1

	print(Feature.id,'placement failed after',max_attempts,'attempts.')
	return False

'''
basic shapely shape templates

'''


