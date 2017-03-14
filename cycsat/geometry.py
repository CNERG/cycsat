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
		shapes = [shape.geometry(placed=placed) for shape in Entity.shapes]
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


# this is for creating terrain
def site_axis(Facility):
	"""Generates a site axis."""
	site_axis = LineString([[-maxx,maxy/2],[maxx*2,maxy/2]])
	rotate(site_axis,random.randint(-180,180))


	# # create a site axis
	# site_axis = LineString([[-maxx,maxy/2],[maxx*2,maxy/2]])
	
	# site_rotation = random.randint(-180,180)
	# site_axis = rotate(site_axis,site_rotation,'center',use_radians=False)
	# Facility.ax_angle = site_rotation

	return site_axis

#------------------------------------------------------------------------------
# FACILITY CONSTRUCTION
#------------------------------------------------------------------------------

def dep_graph(features):
		"""Groups features based on dependencies."""
		# create dictionary of features with dependencies
		
		graph = dict((f.name, f.depends()) for f in features)
		name_to_instance = dict( (f.name, f) for f in features )

		# where to store the batches
		batches = list()

		while graph:
			# Get all features with no dependencies
			ready = {name for name, deps in graph.items() if not deps}

			if not ready:
				msg  = "Circular dependencies found!\n"
				raise ValueError(msg)

			# Remove them from the dependency graph
			for name in ready:
				graph.pop(name)
			for deps in graph.values():
				deps.difference_update(ready)

			# Add the batch to the list
			batches.append( [name_to_instance[name] for name in ready] )

		# Return the list of batches
		return batches


def place_features(Facility,timestep=-1,attempts=100,verbose=False):
	"""Creates a random layout for all the features of a facility and 
	gives each feature a placed geometry.

	Keyword arguments:
	attempts -- the maximum number attempts to be made to place each feature
	"""
	footprint = Facility.geometry()
	minx, miny, maxx, maxy = footprint.bounds

	# determine which features to draw (by timestep) and create a list of ids
	if timestep > -1:
		feature_ids = set()
		events = [event for event in Facility.events if event.timestep==timestep]
		for event in events:
			feature_ids.add(event.feature.id)
		if not feature_ids:
			process.result = 1
			return process
	else:
		feature_ids = [feature.id for feature in Facility.features if feature.visibility==100]

	dep_grps = Facility.dep_graph()

	# track placed features
	placed_features = list()

	for group in dep_grps:
		for feature in group:
			if feature.id not in feature_ids:
				placed_features.append(feature)
				continue
			
			footprint = Facility.geometry()
			overlaps = [feat for feat in placed_features if feat.level==feature.level]
			overlaps = [feat.footprint() for feat in placed_features if feat.level==feature.level]
			overlaps = cascaded_union(overlaps)
			
			footprint = footprint.difference(overlaps)
			
			definition = feature.eval_rules(mask=footprint)
			placed = place_feature(feature,footprint,build=True)

			if placed:
				placed_features.append(feature)
				# record the new shape location
				for shape in feature.shapes:
					shape.add_location(timestep,shape.placed_wkt)
				continue
			else:
				process.result = -1
				process.message = '{ '+feature.name+' } failed to be placed.'
				return process
	
	process.result = 1
	return process


def rotate_facility(Facility,degrees=None):
	"""Rotates all the features of a facility."""
	if not degrees:
		degrees = random.randint(-180,180)+0.01

	for feature in Facility.features:
		rotate_feature(feature,degrees,Facility.geometry().centroid)


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
	results = defaultdict(list)

	for rule in Feature.rules:
		# get rule attributes
		direction = rule.direction
		value = rule.value
		event = None

		# get all the features 'targeted' in the rule
		targets = [feature for feature in Feature.facility.features 
					if (feature.name==rule.target)]

		# search the rules of the targets
		target_rules = list()
		for target in targets:
			target_rules+=target.rules

		# if the rotate rule has targets use them to align 
		if rule.oper=='ROTATE':
			rotation = [r.value for r in target_rules if r.oper=='ROTATE']
			if rotation:
				value = rotation[0]
			else:
				value = rule.value
		else:
			value = rule.value

		# if the rule is self-targeted get the event for placement info
		if rule.target=="%self%":
			lag = 0
			if '%lag' in rule.value:
				lag = rule.value.split('=')[-1]
			value = rule.value-lag
			event = rule.feature.sorted_events()[value]

		# otherwised merge all the targets
		target_footprints = [target.footprint(placed=True) for target in targets]
		target_geometry = cascaded_union(target_footprints)

		result = rules[rule.oper](Feature,target_geometry,value,direction,event)

		for kind, data in result.items():
			results[kind].append(data)

	if results['mask']:
		combined_mask = mask
		for m in results['mask']:
			combined_mask = combined_mask.intersection(m)
		results['mask'] = combined_mask
	else:
		results['mask'] = mask

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

# rules should take features, targets (or shapes) (other features), and a value

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