#------------------------------------------------------------------------------
# GEOMETRY FUNCTIONS
#------------------------------------------------------------------------------

from collections import defaultdict
from sqlalchemy import Column, Integer, String

import random
import itertools
import time

from descartes import PolygonPatch
from matplotlib import pyplot as plt

import numpy as np

from shapely.geometry import Polygon, Point, LineString, box
from shapely.wkt import loads as load_wkt
from shapely.affinity import translate as shift_shape
from shapely.affinity import rotate
from shapely.ops import cascaded_union

#------------------------------------------------------------------------------
# BLUEPRINT OBJECT
#------------------------------------------------------------------------------

class BluePrint(object):
	def __init__(self):
		self.name = None

#------------------------------------------------------------------------------
# GENERAL
#------------------------------------------------------------------------------

def build_geometry(Entity):
	"""Builds a geometry given an instance."""
	if Entity.wkt:
		geometry = load_wkt(Entity.wkt)
	else:
		width = Entity.width*10
		length = Entity.length*10
		geometry = Polygon([(0,0),(0,width),(length,width),(length,0)])
		
	return geometry


def build_footprint(Entity,placed=True):
	"""Returns a geometry that is the union of all a feature's static shapes."""
	archetype = Entity.__class__.__bases__[0].__name__
	if archetype == 'Facility':
		shapes = [feature.footprint() for feature in Entity.features if feature.visibility==100]
	else:
		shapes = [shape.geometry(placed=placed) for shape in Entity.shapes if shape.visibility==100]
	union = cascaded_union(shapes)
	if union.__class__.__name__ == 'MultiPolygon':
		return box(union)
	return union


def posit_point(definition,attempts=1000):
	"""Generates a random point given a defintion of contraints. Currently a 'mask' and an 'alignment'
	(or axis).
	"""
	mask = definition['mask']
	align = definition['align']
	axis = None

	if align:
		align = align[0]
		axis = align['axis']
		value = align['value']

	x_min, y_min, x_max, y_max = mask.bounds

	for i in range(attempts):
		x = random.uniform(x_min,x_max+1)
		y = random.uniform(y_min,y_max+1)

		if axis=='X':
			x = value
		if axis=='Y':
			y = value

		posited_point = Point(x,y)
			
		if posited_point.within(mask):
			return posited_point
	
	print('point placement failed after {',attempts,'} attempts.')
	return False


# def grid_line(Feature,axis='X'):
# 	"""Returns list of points of a grid line for an axis for a target feature."""
	
# 	footprint = Feature.facility.geometry()
# 	x_min, y_min, x_max, y_max = geometry.bounds
	
# 	x,y = Feature.geometry().centroid.xy

# 	if 'X':
# 		xs = np.empty(round((y_max-y_min/0.5))


def line_func(line,precision=1):
	"""Returns a list of coords for a staight line given end coords"""
	start, end = list(line.coords)
	m = (end[1]-start[1])/(end[0]-start[0])
	b = start[1]-(m*start[0])
	x = np.linspace(start[0],end[0],round(line.length))
	y = (m*x)+b
	
	coords = list(zip(x,y))
	points = [Point(c[0],c[1]) for c in coords]

	return points

#------------------------------------------------------------------------------
# SITE PREP
#------------------------------------------------------------------------------

def axf(m,x,b,invert=False):
	"""Returns a LineString that represents a linear function."""
	if invert:
		return ((-1/m)*x)+b
	return (m*x)+b


def area_ratio(polygons):
	"""Returns the area ratio of two polygons"""
	poly1 = polygons[0].area
	poly2 = polygons[1].area
	return poly1/(poly1+poly2)


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


def site_axis(Facility):
	"""Generates a site axis."""
	site_axis = LineString([[-maxx,maxy/2],[maxx*2,maxy/2]])
	rotate(site_axis,random.randint(-180,180))

	return site_axis

#------------------------------------------------------------------------------
# FACILITY CONSTRUCTION
#------------------------------------------------------------------------------

def create_blueprint(Facility,attempts=100):
	"""Creates a random layout for all the features of a facility and 
	gives each feature a placed geometry.

	Keyword arguments:
	attempts -- the maximum number attempts to be made to place each feature
	"""
	footprint = Facility.geometry()
	minx, miny, maxx, maxy = footprint.bounds
	
	# create a site axis
	site_axis = LineString([[-maxx,maxy/2],[maxx*2,maxy/2]])
	
	site_rotation = random.randint(-180,180)
	site_axis = rotate(site_axis,site_rotation,'center',use_radians=False)
	Facility.ax_angle = site_rotation

	# track placed features
	placed_features = list()

	# dependency groups
	dep_grps = Facility.dep_graph()

	for group in dep_grps:
		for feature in group:

			print('-'*25)
			print('placing',feature.name)
			footprint = Facility.geometry()
			overlaps = [feat for feat in placed_features if feat.level==feature.level]

			print('CONSTRANING FEATURES')
			for o in overlaps:
				print('		',o.name,o.footprint().area)

			overlaps = [feat.footprint() for feat in placed_features if feat.level==feature.level]

			overlaps = cascaded_union(overlaps)
			
			footprint = footprint.difference(overlaps)
			
			print('footprint area:',footprint.area)
			
			definition = feature.eval_rules(mask=footprint)
			placed = place_feature(feature,footprint,build=True)

			if placed:
				print(feature.name,'placed')
				print('-'*25)
				placed_features.append(feature)
				continue
			else:
				print('blueprint failed')
				return False

	Facility.rotate(site_rotation)
	return True


def rotate_facility(Facility,degrees=None):
	"""Rotates all the features of a facility."""
	if not degrees:
		degrees = random.randint(-180,180)+0.01

	for feature in Facility.features:
		rotate_feature(feature,degrees,Facility.geometry().centroid)


def build_facility(Facility,attempts=100):
	"""Randomly places all the features of a facility"""	
	for x in range(attempts):
		result = create_blueprint(Facility)
		if result:
			Facility.defined = True
			break
		else:
			Facility.defined = False
			continue
	return result

#------------------------------------------------------------------------------
# FEATURE PLACEMENT
#------------------------------------------------------------------------------

def list_bearings(Feature):
	"""List the bearings of the feature (N,E,S,W) as points."""
	footprint = Feature.footprint()
	minx, miny, maxx, maxy = footprint.bounds
	halfx = (maxx-minx)/2
	halfy = (maxy-miny)/2
	
	N = Point(minx+halfx,maxy)
	E = Point(maxx,miny+halfy)
	S = Point(minx+halfx,miny)
	W = Point(minx,miny+halfy)
	
	return [N,E,S,W]


def evaluate_rules(Feature,mask=None):
	"""Evaluates a a feature's rules and returns instructions."""

	# if no mask is provided make the facility bounds the mask
	# if not mask:
	# 	mask = Feature.facility.geometry()

	results = defaultdict(list)

	for rule in Feature.rules:
		# get all the features 'targeted' in the rule
		targets = [feature.footprint(placed=True) for feature in Feature.facility.features 
					if (feature.name==rule.target)]

		target_geometry = cascaded_union(targets)
		direction = rule.direction
		result = rules[rule.oper](Feature,target_geometry,rule.value,direction)

		for kind, data in result.items():
			results[kind].append(data)

	if results['mask']:
		combined_mask = mask
		for m in results['mask']:
			combined_mask = combined_mask.intersection(m)
		results['mask'] = combined_mask
	else:
		results['mask'] = mask

	print(results['mask'].area)
	return results


def rotate_feature(Feature,rotation,center='center'):
	"""Rotates a feature."""

	for shape in Feature.shapes:
		geometry = shape.geometry()
		rotated = rotate(geometry,rotation,origin=center,use_radians=False)
		shape.placed_wkt = rotated.wkt


def place(Entity,placement,build=False,center=None,rotation=0):
	"""Places a shape to a coordinate position

	Keyword arguments:
	build -- draws from the shapes stable_wkt
	"""
	
	placed_x = placement.coords.xy[0][0]
	placed_y = placement.coords.xy[1][0]

	if build:
		geometry = Entity.geometry(placed=False)
	else:
		geometry = Entity.geometry(placed=True)

	shape_x = geometry.centroid.coords.xy[0][0]
	shape_y = geometry.centroid.coords.xy[1][0]

	try:
		xoff = Entity.xoff
		yoff = Entity.yoff
	except:
		xoff = 0
		yoff = 0

	shift_x = placed_x - shape_x + xoff
	shift_y = placed_y - shape_y + yoff

	shifted = shift_shape(geometry,xoff=shift_x,yoff=shift_y)
	if rotation != 0:
		shifted = rotate(shifted,rotation,origin='center',use_radians=False)

	Entity.placed_wkt = shifted.wkt
	
	return Entity


def place_feature(Feature,mask=None,build=False,rand=True,location=False,attempts=100):
	"""Places a feature within a geometry and checks typology of shapes

	Keyword arguments:
	Feature -- feature to place
	bounds -- containing bounds
	random -- if 'True', placement is random, else Point feaure is required
	location -- centroid location to place Feature
	attempts -- the maximum number attempts to be made
	build -- draws from the shapes stable_wkt
	"""
	# the center for the facility for a center point for rotation
	center = Feature.facility.geometry().centroid

	# evalute the rules of the facility
	definition = Feature.eval_rules(mask=mask)
	mask = definition['mask']

	if 'rotate' in definition:
		rotate = definition['rotate'][0]
		print('rotate',rotate)
	else:
		rotate = random.randint(-180,180)
	
	for i in range(attempts):
		posited_point = posit_point(definition)
		if not posited_point:
			return False

		placed_shapes = list()
		typology_checks = list()
		for shape in Feature.shapes:
			
			place(shape,posited_point,build,center,rotation=rotate)
			placement = shape.geometry()
			
			placed_shapes.append(placement)
			typology_checks.append(placement.within(mask))

		if False not in typology_checks:
			Feature.wkt = cascaded_union(placed_shapes).wkt
			return True

	print(Feature.name,'placement failed after {',attempts,'} attempts.')
	return False


def placement_bounds(facility_footprint,placed_features):
	"""Takes a list of placed features and a facility footprint 
	and generates a geometry of all possible locations to be placed."""

	placed_footprints = list()
	for feature in placed_features:
		feature_footprint = build_footprint(feature)
		placed_footprints.append(feature_footprint)
	
	# this needs to discriminate between within features and not

	union_footprints = cascaded_union(placed_footprints)
	bounds = facility_footprint.difference(union_footprints)

	return bounds


def place_facility(Facility,geometry,attempts=100):
	"""Places a facility within a site geometry and checks typology"""
	
	attempts = 0
	while attempts<attempts:

		posited_point = posit_point(geometry)

		place(Facility,posited_point)
		placement = Facility.geometry()
		typology_check = placement.within(geometry)

		if typology_check:
			return True
		else:
			attempts+=1

	print(Facility.id,'facility placement failed after',attempts,'attempts.')
	return False


#------------------------------------------------------------------------------
# PLACMENT RULES (returns either a mask, position, or alignment)
#------------------------------------------------------------------------------

def within_rule(feature,target_geometry,value,*unused):
	mask = target_geometry.buffer(value)
	return {'mask':mask}


def near_rule(feature,target_geometry,value,*unused):
	"""Places a feature a specified value to a target feature."""
	feature_geometry = feature.footprint(placed=False)

	cushion=0
	threshold=100
	
	# buffer the target geometry by the provided value
	inner_buffer = target_geometry.buffer(value)

	mask = feature_geometry.bounds
	diagaonal_dist = Point(mask[0:2]).distance(Point(mask[2:]))
	buffer_value = diagaonal_dist+(diagaonal_dist*cushion)
	second_buffer = inner_buffer.buffer(buffer_value)
	mask = second_buffer.difference(inner_buffer)
	return {'mask':mask}


def axis_rule(feature,target_geometry,value,direction,*unused):
	x,y = target_geometry.centroid.xy
	if direction == 'X':
		value = x[0]
	elif direction == 'Y':
		value = y[0]
	else:
		return {'align': None}
	return {'align':{'axis':direction,'value':value}}


def rotate_rule(feature,target_geometry,value,direction,*unused):
	return {'rotate':value}



rules = {
	'WITHIN':within_rule,
	'NEAR':near_rule,
	'AXIS':axis_rule,
	'ROTATE':rotate_rule
}