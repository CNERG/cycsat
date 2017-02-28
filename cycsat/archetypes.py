"""
archetypes.py
"""
import ast, random

from descartes import PolygonPatch
from matplotlib import pyplot as plt

from .image import Sensor
from .geometry import create_blueprint, place, build_facility
from .geometry import build_geometry, build_footprint, near, line_func
from .geometry import rotate_facility, evaluate_rule

from .laboratory import materialize

import pandas as pd
import numpy as np

import copy
from random import randint
import operator
import ast

from shapely.geometry import Polygon, Point, LineString
from shapely.wkt import loads as load_wkt
from shapely.ops import cascaded_union
from shapely.affinity import rotate, translate

from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Table, Boolean
from sqlalchemy.dialects.sqlite import BLOB
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship


Base = declarative_base()

operations = {
	"equals": operator.eq,
	"not equal": operator.ne,
	"not equal": operator.ne,
	"less than": operator.lt,
	"less than or equals": operator.le,
	"greater than": operator.gt,
	"greater than of equals": operator.ge
}


class Satellite(Base):
	"""A collection of instruments"""

	__tablename__ = 'CycSat_Satellite'

	id = Column(Integer, primary_key=True)
	name = Column(String)
	prototype = Column(String)
	mmu = Column(Integer)
	width = Column(Integer)
	length = Column(Integer)

	__mapper_args__ = {'polymorphic_on': prototype}


class Instrument(Base):
	"""Parameters for generating a scene"""

	__tablename__ = 'CycSat_Instrument'

	id = Column(Integer, primary_key=True)
	name = Column(String)
	mmu = Column(Integer, default=1) # in 10ths of centimeters
	width = Column(Integer)
	length = Column(Integer)
	min_spectrum = Column(String)
	max_spectrum = Column(String)
	prototype = Column(String)

	__mapper_args__ = {'polymorphic_on': prototype}

	satellite_id = Column(Integer, ForeignKey('CycSat_Satellite.id'))
	satellite = relationship(Satellite, back_populates='instruments')
		

	def build_geometry(self):
		self.geometry = build_geometry(self)


	def target(self,Facility):
		"""Creates a sensor object and focuses it on a facility"""
		self.Sensor = Sensor(self)
		self.Facility = Facility

		self.shapes = []
		for feature in Facility.features:
			for shape in feature.shapes:
				self.shapes.append(materialize(shape))
		
		self.Sensor.focus(Facility)
		self.Sensor.calibrate(Facility)


	def capture(self,timestep,path,Mission=None,World=None):
		"""Adds shapes at timestep to a image"""

		self.Sensor.reset()

		# gets all events from a timestep
		events = [Event.shape_id for Event in self.Facility.events if Event.timestep==timestep]
		# get all shapes from a timestep (if there is an event)
		shapes = [Shape for Shape in self.shapes if Shape.id in events]
		
		shape_stack = dict()
		for shape in shapes:
			if shape.level in shape_stack:
				shape_stack[shape.level].append(shape)
			else:
				shape_stack[shape.level] = [shape]

		for level in sorted(shape_stack):
			for shape in shape_stack[level]:
				self.Sensor.capture_shape(shape)
		
		# create and save the scene object
		scene = Scene(timestep=timestep)
		self.scenes.append(scene)
		self.Facility.scenes.append(scene)
		if Mission:
			Mission.scenes.append(scene)
		World.save([Mission,self,self.Facility])
		
		path = path+str(scene.id)
		self.Sensor.write(path)


class Mission(Base):
	"""Collection of images from a satellite"""

	__tablename__ = 'CycSat_Mission'

	id = Column(Integer, primary_key=True)
	name = Column(String)
	timesteps = Column(String)
	
	satellite_id = Column(Integer, ForeignKey('CycSat_Satellite.id'))
	satellite = relationship(Satellite, back_populates='missions')


Satellite.missions = relationship('Mission', order_by=Mission.id,back_populates='satellite')
Satellite.instruments = relationship('Instrument', order_by=Instrument.id, back_populates='satellite')


class Site(Base):
	"""Collection of facilities"""

	__tablename__ = 'CycSat_Site'

	id = Column(Integer, primary_key=True)
	name = Column(String)
	
	width = Column(Integer)
	length = Column(Integer)

	mission_id = Column(Integer, ForeignKey('CycSat_Mission.id'))
	mission = relationship(Mission, back_populates='sites')


Mission.sites = relationship('Site', order_by=Site.id,back_populates='mission')


class Facility(Base):
	"""A collection of features"""

	__tablename__ = 'CycSat_Facility'

	id = Column(Integer, primary_key=True)
	AgentId = Column(Integer)
	name = Column(String)
	width = Column(Integer)
	length = Column(Integer)
	terrain = Column(BLOB)
	prototype = Column(String)
	defined = Column(Boolean,default=False)
	ax_angle = Column(Integer)
	wkt = Column(String)

	__mapper_args__ = {'polymorphic_on': prototype}
	
	site_id = Column(Integer, ForeignKey('CycSat_Site.id'))
	site = relationship(Site, back_populates='facilities')

	def geometry(self):
		self.geo = build_geometry(self)
		return self.geo

	def footprint(self):
		return build_footprint(self)

	def rotate(self,degrees):
		rotate_facility(self,degrees)

	def axis(self):
		if self.ax_angle:
			footprint = self.geometry()
			minx, miny, maxx, maxy = footprint.bounds
			site_axis = LineString([[-maxx,0],[maxx*2,0]])
			site_axis = rotate(site_axis,self.ax_angle)
			return site_axis
		else:
			print('This facility has not been built. Use the build() method \n'
				  'before creating the axis.')

	def build(self,attemps=100):
		"""Randomly places all the features of a facility"""
		build_facility(self,attempts=100)

	def simulate(self,timestep,reader,world):
		"""Evaluates the conditions for dynamic shapes at a given timestep and
		generates events.

		Keyword arguments:
		timestep -- the timestep for simulation
		reader -- a reader connection for reading data from the database
		"""
		dynamic_features = [feature for feature in self.features if feature.visibility!=100]

		events = list()
		for feature in dynamic_features:
			evaluations = []
			for condition in feature.conditions:
				qry = "SELECT Value FROM %s WHERE AgentId=%s AND Time=%s;" % (condition.table,self.AgentId,timestep)
				df = pd.read_sql_query(qry,reader)
				value = df['Value'][0]

				if operations[condition.oper](value,condition.value):
					evaluations.append(True)
				else:
					evaluations.append(False)

			if False in evaluations:
				continue
			else:
				event = Event(timestep=timestep)
				feature.events.append(event)
				self.events.append(event)

				world.save(feature)

		world.save(self)


	def plot(self,axis=None,timestep=None):
		"""plots a facility and its static features or a timestep."""
		if axis:
			ax = axis
		else:
			fig, ax = plt.subplots(1,1,sharex=True,sharey=True)
		
		ax.set_xlim([0,self.width*10])
		ax.set_ylim([0,self.length*10])
		ax.set_axis_bgcolor('green')
		ax.set_aspect('equal')
		ax.set_title(self.name)

		for feature in self.features:
			rgb = feature.get_rgb(plotting=True)
			patch = PolygonPatch(feature.footprint(),facecolor=rgb)
			ax.add_patch(patch)
			plt.text(feature.geo.centroid.x,feature.geo.centroid.y,feature.name)


Site.facilities = relationship('Facility', order_by=Facility.id,back_populates='site')


class Feature(Base):
	"""Collection of shapes"""

	__tablename__ = 'CycSat_Feature'

	id = Column(Integer, primary_key=True)
	name = Column(String)
	visibility = Column(Integer)
	prototype = Column(String)
	#wkt = Column(String)
	rgb = Column(String)
	level = Column(Integer)

	__mapper_args__ = {'polymorphic_on': prototype}

	facility_id = Column(Integer, ForeignKey('CycSat_Facility.id'))
	facility = relationship(Facility, back_populates='features')

	def footprint(self,placed=True):
		"""Returns a shapely geometry of the static shapes"""
		self.geo = build_footprint(self,placed=placed)
		return self.geo

	def get_rgb(self,plotting=False):
		"""Returns the RGB be value as a list [RGB] which is stored as text"""
		try:
			rgb = ast.literal_eval(self.rgb)
		except:
			rgb = self.rgb

		if plotting:
			return [x/255 for x in rgb]
		else:
			return rgb

	
	def evaluate_rules(self,placed_features):
		"""Evaluates all the rules of a feature given a list of placed features
		and returns a geometry where the feature can be drawn."""

		evaluation = {
		'bounds': self.facility.geometry(),
		'coords': list(),
		'alignment': None
		}

		# track list of targeted features
		targets = list()

		# if there are no rules return the footprint
		if not self.rules:
			evaluation['bounds'] = footprint
		
		# otherwise evaluate the rules
		else:
			masks = list()

			# loop through rules to find possible locations and coords
			for rule in self.rules:
				targets.append(rule.target)
				rule_eval = rule.evaluate(placed_features,evaluation['bounds'])
				masks.append(rule_eval['bounds'])
				evaluation['coords'] = rule_eval['coords']+evaluation['coords']

				if rule_eval['alignment']:
					evaluation['alignment'] = rule_eval['alignment']

			# find the intersection of all the masks (if any!)
			evaluation['bounds'] = masks.pop(0)
			for mask in masks:
				evaluation['bounds'] = evaluation['bounds'].intersection(mask)
			
			# if the intersection fails return False, this feature will
			# not be drawn
			if evaluation['bounds'].area == 0:
				print('no possible location for:',self.name)
				return False, None

		# find all the other features that are simply 'obstacles' in the same level
		non_targets = [feature for feature in placed_features if feature.name not in targets]
		non_targets = [feature.footprint() for feature in non_targets 
							if feature.level == self.level]

		# if there are no 'non-targets' return the valid geometry
		if not non_targets:
			evaluation['coords'] = [x for x in evaluation['coords'] if x.within(evaluation['bounds'])]
			return evaluation

		overlaps = cascaded_union(non_targets)
		evaluation['bounds'] = evaluation['bounds'].difference(overlaps)
		evaluation['coords'] = [x for x in evaluation['coords'] if x.within(evaluation['bounds'])]

		print(evaluation)

		return evaluation


Facility.features = relationship('Feature', order_by=Feature.id,back_populates='facility')


class Shape(Base):
	"""A geometry with condtions and rules"""

	__tablename__ = 'CycSat_Shape'

	id = Column(Integer, primary_key=True)
	name = Column(String)
	category = Column(String)
	level = Column(Integer,default=0)
	visibility = Column(Integer, default=100)
	prototype = Column(String)
	xoff = Column(Integer,default=0)
	yoff = Column(Integer,default=0)
	placed_wkt = Column(String)
	stable_wkt = Column(String)

	material_code = Column(Integer)
	rgb = Column(String)

	__mapper_args__ = {'polymorphic_on': prototype}
	
	feature_id = Column(Integer, ForeignKey('CycSat_Feature.id'))
	feature = relationship(Feature, back_populates='shapes')

	def geometry(self,placed=True):
		"""Returns a shapely geometry"""
		if placed:
			geom = self.placed_wkt
		else:
			geom = self.stable_wkt

		self.geo = load_wkt(geom)
		return self.geo

Feature.shapes = relationship('Shape', order_by=Shape.id,back_populates='feature')


class Condition(Base):
	"""Condition for a shape or feature to have an event (appear) in a timestep (scene)"""
	
	__tablename__ = 'CycSat_Condition'

	id = Column(Integer, primary_key=True)
	table = Column(String)
	oper = Column(String)
	value = Column(Integer)

	shape_id = Column(Integer, ForeignKey('CycSat_Shape.id'))
	shape = relationship(Shape, back_populates='conditions')

	feature_id = Column(Integer, ForeignKey('CycSat_Feature.id'))
	feature = relationship(Feature, back_populates='conditions')


Shape.conditions = relationship('Condition', order_by=Condition.id,back_populates='shape')
Feature.conditions = relationship('Condition', order_by=Condition.id,back_populates='feature')


class Rule(Base):
	"""Spatial rule for where a feature or shape can appear."""
	
	__tablename__ = 'CycSat_Rule'

	id = Column(Integer, primary_key=True)
	oper = Column(String) # e.g. within, disjoint, near etc.
	target = Column(Integer)
	value = Column(Integer,default=0)
	direction = Column(String)

	shape_id = Column(Integer, ForeignKey('CycSat_Shape.id'))
	shape = relationship(Shape, back_populates='rules')

	feature_id = Column(Integer, ForeignKey('CycSat_Feature.id'))
	feature = relationship(Feature, back_populates='rules')


	def evaluate(self,placed_features,footprint):
		evaluation = evaluate_rule(self,placed_features,footprint)
		return evaluation

Shape.rules = relationship('Rule', order_by=Rule.id,back_populates='shape')
Feature.rules = relationship('Rule', order_by=Rule.id,back_populates='feature')


class Event(Base):
	"""An instance of a non-static shape at a facility for a given timestep"""

	__tablename__ = 'CycSat_Event'

	id = Column(Integer, primary_key=True)
	timestep = Column(Integer)

	feature_id = Column(Integer, ForeignKey('CycSat_Feature.id'))
	feature = relationship(Feature,back_populates='events')

	facility_id = Column(Integer, ForeignKey('CycSat_Facility.id'))
	facility = relationship(Facility,back_populates='events')


Feature.events = relationship('Event',order_by=Event.id,back_populates='feature')
Facility.events = relationship('Event',order_by=Event.id,back_populates='facility')


class Scene(Base):
	__tablename__ = 'CycSat_Scene'

	id = Column(Integer, primary_key=True)
	timestep = Column(Integer)

	mission_id = Column(Integer, ForeignKey('CycSat_Mission.id'))
	mission = relationship(Mission,back_populates='scenes')

	facility_id = Column(Integer, ForeignKey('CycSat_Facility.id'))
	facility = relationship(Facility,back_populates='scenes')

	instrument_id = Column(Integer, ForeignKey('CycSat_Instrument.id'))
	instrument = relationship(Instrument, back_populates='scenes')

# Site.scenes = relationship('Scene', order_by=Scene.id,back_populates='site')
Facility.scenes = relationship('Scene',order_by=Scene.id,back_populates='facility')
Instrument.scenes = relationship('Scene', order_by=Scene.id,back_populates='instrument')
Mission.scenes = relationship('Scene', order_by=Scene.id,back_populates='mission')

