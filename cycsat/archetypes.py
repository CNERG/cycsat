"""
archetypes.py
"""
from .image import Sensor
from .geometry import create_blueprint, assess_blueprint, place
from .geometry import build_geometry

from .laboratory import materialize

import pandas as pd
import numpy as np

import copy
from random import randint
import operator
import ast

from shapely.geometry import Polygon, Point
from shapely.wkt import loads as load_wkt

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
		World.write([Mission,self,self.Facility])
		
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
	wkt = Column(String)

	__mapper_args__ = {'polymorphic_on': prototype}
	
	site_id = Column(Integer, ForeignKey('CycSat_Site.id'))
	site = relationship(Site, back_populates='facilities')

	def build_geometry(self):
		self.geometry = build_geometry(self)


	def build(self):
		"""Randomly places all the features of a facility"""	
		built = 0
		while (built == 0):
			create_blueprint(self)
			valid = assess_blueprint(self)
			if valid:
				built = 1
				self.defined = True
			else:
				self.defined = False
				pass

	def simulate(self,timestep,reader,world):
		"""Evaluates the conditions for dynamic shapes at a given timestep and
		generates events.

		Keyword arguments:
		timestep -- the timestep for simulation
		reader -- a reader connection for reading data from the database
		"""
		
		dynamic_shapes = []
		for feature in self.features:
			for shape in [s for s in feature.shapes if s.visibility!=100]:
				dynamic_shapes.append(shape)

		events = []
		for shape in dynamic_shapes:
			evaluations = []
			for condition in shape.conditions:
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
				shape.events.append(event)
				self.events.append(event)

				world.write(shape)

		world.write(self)


Site.facilities = relationship('Facility', order_by=Facility.id,back_populates='site')


class Feature(Base):
	"""Collection of shapes"""

	__tablename__ = 'CycSat_Feature'

	id = Column(Integer, primary_key=True)
	name = Column(String)
	order = Column(Integer)
	visibility = Column(Integer)
	prototype = Column(String)
	wkt = Column(String)

	__mapper_args__ = {'polymorphic_on': prototype}

	facility_id = Column(Integer, ForeignKey('CycSat_Facility.id'))
	facility = relationship(Facility, back_populates='features')


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
	wkt = Column(String)

	material_code = Column(Integer)
	rgb = Column(String)

	__mapper_args__ = {'polymorphic_on': prototype}
	
	feature_id = Column(Integer, ForeignKey('CycSat_Feature.id'))
	feature = relationship(Feature, back_populates='shapes')

	def build_geometry(self):
		"""Returns a shapely geometry"""
		self.geometry = load_wkt(self.wkt)
		return self.geometry

Feature.shapes = relationship('Shape', order_by=Shape.id,back_populates='feature')


class Condition(Base):
	"""Condition for a shape to have an event (appear) in a timestep (scene)"""
	
	__tablename__ = 'CycSat_Condition'

	id = Column(Integer, primary_key=True)
	table = Column(String)
	oper = Column(String)
	value = Column(Integer)

	shape_id = Column(Integer, ForeignKey('CycSat_Shape.id'))
	shape = relationship(Shape, back_populates='conditions')


Shape.conditions = relationship('Condition', order_by=Condition.id,back_populates='shape')


class Rule(Base):
	"""Spatial rule for where a shape can appear"""
	
	__tablename__ = 'CycSat_Rule'

	id = Column(Integer, primary_key=True)
	operation = Column(String) # e.g. within, disjoint, near etc.
	area = Column(Integer)

	shape_id = Column(Integer, ForeignKey('CycSat_Shape.id'))
	shape = relationship(Shape, back_populates='rules')


Shape.rules = relationship('Rule', order_by=Rule.id,back_populates='shape')


class Event(Base):
	"""An instance of a non-static shape at a facility for a given timestep"""

	__tablename__ = 'CycSat_Event'

	id = Column(Integer, primary_key=True)
	timestep = Column(Integer)

	shape_id = Column(Integer, ForeignKey('CycSat_Shape.id'))
	shape = relationship(Shape,back_populates='events')

	facility_id = Column(Integer, ForeignKey('CycSat_Facility.id'))
	facility = relationship(Facility,back_populates='events')


Shape.events = relationship('Event',order_by=Event.id,back_populates='shape')
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

