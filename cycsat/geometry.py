"""
geometry.py

"""
from sqlalchemy import Column, Integer, String

from random import randint
import itertools

import numpy as np
from shapely.geometry import Polygon, Point
from shapely.wkt import loads as load_wkt
from shapely.affinity import translate as shift_shape
from shapely.ops import cascaded_union


def build_geometry(width,length):
	"""Builds a rectangle geometry given a width and a length"""
	geometry = Polygon([(0,0),(0,width),(length,width),(length,0)])
	return geometry


def create_blueprint(Facility,max_attempts=20):
	"""Creates a random layout for all the features of a facility and 
	gives each feature a placed geometry

	Keyword arguments:
	max_attempts -- the maximum number attempts to be made
	"""
	Facility.build_footprint()

	# place features
	for feature in Facility.features:
		placed = place_feature(feature, Facility.footprint,max_attempts=max_attempts)
		if placed:
			continue
		else:
			print('blueprint failed')


def create_plan(Site,max_attempts=20):
	"""Creates a random layout for all the features of a facility and 
	gives each feature a placed geometry

	Keyword arguments:
	max_attempts -- the maximum number attempts to be made
	"""
	Site.build_footprint()
	facilities = Site.facilities

	for facility in facilities:
		placed = place_facility(facility,Site.footprint)
		if placed:
			continue
		else:
			print('site plan failed')


def assess_blueprint(Facility):
	"""Checks to see the blueprint has any illegal overlaps"""

	shape_stack = dict()

	# build a shape stack by level
	for feature in Facility.features:
		for shape in feature.shapes:
			geometry = shape.build_footprint(geometry='placed')
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
	"""Checks if there are any overlaps in a list of shapes"""

	for a, b in itertools.combinations(shapes, 2):
		if a.disjoint(b):
			continue
		else:
			return False

	return True


def posit_point(footprint):
	"""Generates a random point within a footprint"""
	
	# define the footprint boundary
	length = footprint.bounds[-2]
	width = footprint.bounds[-1]

	# create a random point within footprint
	posited_point = Point(randint(0,width+1), randint(0,length+1))

	return posited_point


def place(Entity,placement,ContextEntity=None):
	"""Places a shape to a coordinate position"""
	placed_x = placement.coords.xy[0][0]
	placed_y = placement.coords.xy[1][0]

	if ContextEntity:
		location = ContextEntity.build_footprint()
		geometry = Entity.build_footprint(geometry='placed')
	else:
		geometry = Entity.build_footprint(geometry='abstract')
		location = geometry

	shape_x = location.centroid.coords.xy[0][0]
	shape_y = location.centroid.coords.xy[1][0]

	try:
		xoff = Entity.xoff
		yoff = Entity.yoff
	except:
		xoff = 0
		yoff = 0

	shift_x = placed_x - shape_x + xoff
	shift_y = placed_y - shape_y + yoff

	if ContextEntity:
		Entity.focus = shift_shape(geometry,xoff=shift_x,yoff=shift_y).wkt
	else:
		Entity.placement = shift_shape(geometry,xoff=shift_x,yoff=shift_y).wkt
	
	return Entity


def place_feature(Feature,footprint,max_attempts=20):
	"""Places a feature within a footprint and checks typology of shapes"""
	
	attempts = 0
	while attempts<max_attempts:

		posited_point = posit_point(footprint)

		typology_checks = list()
		for shape in Feature.shapes:
			place(shape,posited_point)
			placement = shape.build_footprint(geometry='placed')
			typology_checks.append(placement.within(footprint))

		if False not in typology_checks:
			return True
		else:
			attempts+=1

	print(Feature.id,'placement failed after',max_attempts,'attempts.')
	return False


def place_facility(Facility,footprint,max_attempts=20):
	"""Places a facility within a site footprint and checks typology"""
	
	attempts = 0
	while attempts<max_attempts:

		posited_point = posit_point(footprint)

		place(Facility,posited_point)
		placement = Facility.build_footprint(geometry='placed')
		typology_check = placement.within(footprint)

		if typology_check:
			return True
		else:
			attempts+=1

	print(Facility.id,'facility placement failed after',max_attempts,'attempts.')
	return False

