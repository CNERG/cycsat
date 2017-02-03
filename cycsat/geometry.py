"""
geometry.py
"""
from sqlalchemy import Column, Integer, String

import random
import itertools

import numpy as np

from shapely.geometry import Polygon, Point
from shapely.wkt import loads as load_wkt
from shapely.affinity import translate as shift_shape
from shapely.ops import cascaded_union

# =============================================================================
# Spatial analysis functions
# =============================================================================

def pointilize(feature):
	"""Turns a Polygon into a array of Points"""
	x,y = feature.exterior.xy
	coords = [Point(x,y) for x,y in zip(x,y)]
	return coords

# def shift_towards(feature,target,increment=1):
# 	"""Shifts a shape towards a target shape until they cross."""
# 	target_centroid = target.centroid
# 	cross = False
# 	while not cross:

# =============================================================================
# General
# =============================================================================

def build_geometry(Entity):
	"""Builds a geometry given an instance"""

	if Entity.wkt:
		geometry = load_wkt(Entity.wkt)
	else:
		width = Entity.width*10
		length = Entity.length*10
		geometry = Polygon([(0,0),(0,width),(length,width),(length,0)])
		
	return geometry


def build_feature_footprint(Feature):
	"""Returns a geometry that is the union of all a feature's static shapes"""
	shapes = [shape.build_geometry() for shape in Feature.shapes if shape.visibility==100]
	union = cascaded_union(shapes)
	return union


def check_disjoints(shapes):
	"""Checks if there are any overlaps in a list of shapes"""

	for a, b in itertools.combinations(shapes, 2):
		if a.disjoint(b):
			continue
		else:
			return False

	return True


def posit_point(geometry,attempts=100):
	"""Generates a random point within a geometry"""
	
	for i in range(attempts):

		# define the geometry boundary
		x_min, y_min, x_max, y_max = geometry.bounds
		
		# create a random point within geometry
		posited_point = Point(random.uniform(x_min,x_max+1), random.uniform(y_min,y_max+1))

		if posited_point.within(geometry):
			return posited_point
	print('placement failed after {',attempts,'} attempts.')
	return False


# =============================================================================
# Site construction
# =============================================================================

def create_plan(Site,attempts=100):
	"""Creates a random layout for all the features of a facility and 
	gives each feature a placed geometry

	Keyword arguments:
	attempts -- the maximum number attempts to be made
	"""
	Site.build_geometry()
	facilities = Site.facilities

	for facility in facilities:
		placed = place_facility(facility,Site.footprint)
		if placed:
			continue
		else:
			print('site plan failed')

# =============================================================================
# Facility construction
# =============================================================================


def create_blueprint(Facility,attempts=100):
	"""Creates a random layout for all the features of a facility and 
	gives each feature a placed geometry.

	Keyword arguments:
	attempts -- the maximum number attempts to be made.
	"""
	bounds = Facility.build_geometry()

	# this is for visual tests
	test_bounds = list()
	test_bounds.append(bounds)

	# place features
	placed_features = list()
	for feature in Facility.features:
		if placed_features:
			bounds = placement_bounds(bounds,placed_features)
			test_bounds.append(bounds) # for visual testing
		
		placed = place_feature(feature,bounds,attempts=attempts)
		

		if placed:
			placed_features.append(placed)
			continue
		else:
			print('blueprint failed')
			return False

	bounds = placement_bounds(bounds,placed_features)
	test_bounds.append(bounds)
	return test_bounds


def build_facility(Facility):
	"""Randomly places all the features of a facility"""	
	built = 0
	while (built == 0):
		tbs = create_blueprint(Facility)
		# valid = assess_blueprint(Facility)
		if tbs:
			built = 1
			Facility.defined = True
			return tbs
		else:
			Facility.defined = False
			pass


# =============================================================================
# Placement
# =============================================================================


def place(Entity,placement,ContextEntity=None):
	"""Places a shape to a coordinate position"""
	placed_x = placement.coords.xy[0][0]
	placed_y = placement.coords.xy[1][0]

	if ContextEntity:
		location = ContextEntity.build_geometry()
		geometry = Entity.build_geometry()
	else:
		geometry = Entity.build_geometry()
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
		Entity.wkt = shift_shape(geometry,xoff=shift_x,yoff=shift_y).wkt
	
	return Entity


def place_feature(Feature,geometry,random=True,location=False,attempts=100):
	"""Places a feature within a geometry and checks typology of shapes

	Keyword arguments:
	Feature -- feature to place
	geometry -- containing geometry
	random -- if 'True', placement is random, else Point feaure is required
	location -- centroid location to place Feature
	attempts -- the maximum number attempts to be made.
	"""
	
	for i in range(attempts):

		if random:
			posited_point = posit_point(geometry)
		else:
			posited_point = location
		if not posited_point:
			print('Point feature required for placement.')
			break

		placed_shapes = list()
		typology_checks = list()
		for shape in Feature.shapes:
			place(shape,posited_point)
			placement = shape.build_geometry()
			placed_shapes.append(placement)
			typology_checks.append(placement.within(geometry))

		if False not in typology_checks:
			Feature.wkt = cascaded_union(placed_shapes).wkt
			return Feature

	print(Feature.id,'placement failed after {',attempts,'} attempts.')
	return False


def placement_bounds(facility_footprint,placed_features):
	"""Takes a list of placed features and a facility footprint 
	and generates a geometry of all possible locations to be placed."""

	placed_footprints = list()
	for feature in placed_features:

		# check Rules



		feature_footprint = build_feature_footprint(feature)
		placed_footprints.append(feature_footprint)
	
	union_footprints = cascaded_union(placed_footprints)
	bounds = facility_footprint.difference(union_footprints)

	return bounds


def place_facility(Facility,geometry,attempts=100):
	"""Places a facility within a site geometry and checks typology"""
	
	attempts = 0
	while attempts<attempts:

		posited_point = posit_point(geometry)

		place(Facility,posited_point)
		placement = Facility.build_geometry()
		typology_check = placement.within(geometry)

		if typology_check:
			return True
		else:
			attempts+=1

	print(Facility.id,'facility placement failed after',attempts,'attempts.')
	return False


# def evaluate_rule(Rule,feature_footprint,facility_footprint,placed_features):
# 	"""Evaluates a spatial rule and returns a boundary geometry"""

# 	targets = [feature for feature in placed_features if name==Rule.target]
# 	target_union = cascaded_union(targets)

# 	if Rule.operation=='within':
# 		return target_union
	
# 	elif Rule.operation=='near':
# 		target_union

# 	elif Rule.operation=='distant':
# 		pass
	
# 	else:
# 		pass


# =============================================================================
# Placement testing
# =============================================================================




# =============================================================================
# Retired functions
# =============================================================================

def assess_blueprint(Facility):
	"""Checks to see the blueprint has any illegal overlaps"""

	shape_stack = dict()

	# build a shape stack by level
	for feature in Facility.features:
		for shape in feature.shapes:
			geometry = shape.build_geometry()
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