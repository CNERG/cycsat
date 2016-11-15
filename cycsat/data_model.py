"""
data_model.py

Contains the data model classes.

"""
from .sensor import Canvas
from .geometry import create_blueprint, assess_blueprint

from random import randint
from shapely.geometry import Polygon, Point
from shapely.wkt import loads as load_wkt

from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Table, Numeric, Boolean
from sqlalchemy.dialects.sqlite import BLOB
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship


Base = declarative_base()


class Satellite(Base):
	'''
	A collection of instruments and missions

	'''
	__tablename__ = 'satellite'

	id = Column(Integer, primary_key=True)
	name = Column(String)

	def get_instruments(self):

		instruments = dict()
		for instrument in self.instruments:
			instruments[instrument.name] = instrument

		return instruments

	def get_missions(self):

		missions = dict()
		for mission in self.missions:
			missions[mission.name] = mission

		return missions


class Instrument(Base):
	'''
	A set of parameters for generating a scene associated with a sateillite

	'''
	__tablename__ = 'instrument'

	id = Column(Integer, primary_key=True)
	name = Column(String, unique=True)
	mmu = Column(Integer, default=1) # in 10ths of centimeters	
	bands = Column(Integer, default=3)

	satellite_id = Column(Integer, ForeignKey('satellite.id'))
	satellite = relationship(Satellite, back_populates='instruments')


class Mission(Base):
	'''
	A single mission for a particular satellite

	'''
	__tablename__ = 'mission'

	id = Column(Integer, primary_key=True)
	name = Column(String)
	timesteps = Column(String)
	
	satellite_id = Column(Integer, ForeignKey('satellite.id'))
	satellite = relationship(Satellite, back_populates='missions')

	def get_sites(self):

		sites = dict()
		for site in self.sites:
			sites[site.name] = site

		return sites


Satellite.missions = relationship('Mission', order_by=Mission.id,back_populates='satellite')
Satellite.instruments = relationship('Instrument', order_by=Instrument.id, back_populates='satellite')


class Site(Base):
	'''	
	A geographic area (landscape) with a collection of facilities

	'''
	__tablename__ = 'site'

	id = Column(Integer, primary_key=True)
	name = Column(String)
	
	width = Column(Integer)
	length = Column(Integer)

	mission_id = Column(Integer, ForeignKey('mission.id'))
	mission = relationship(Mission, back_populates='sites')

	def get_features(self):

		features = dict()
		for feature in self.features:
			features[feature.name] = feature

		return features

	def draw(self):
		'''
		'''
		pass


Mission.sites = relationship('Site', order_by=Site.id,back_populates='mission')


class Facility(Base):
	'''
	A collection of features at a site
		width and length: kilometers
		
	'''
	__tablename__ = 'facility'

	id = Column(Integer, primary_key=True)
	name = Column(String)
	width = Column(Integer)
	length = Column(Integer)
	xoff = Column(Integer)
	yoff = Column(Integer)

	site_id = Column(Integer, ForeignKey('site.id'))
	site = relationship(Site, back_populates='facilities')


	def build_footprint(self):
		'''
		'''
		# convert meters to centimeters
		width = self.width*10
		length = self.length*10
		self.footprint = Polygon([(0,0),(0,width),(length,width),(length,0)])
		return self.footprint


	def define(self):
		'''
		'''
		built = 0
		while (built == 0):
			create_blueprint(self)
			valid = assess_blueprint(self)
			if valid:
				built = 1
			else:
				pass


	def make_canvas(self):
		'''
		generates a plan of all the static shapes
		'''
		shape_stack = dict()

		self.canvas = Canvas(self.width*10,self.length*10)

		for feature in self.features:
			for shape in feature.shapes:

				if shape.visibility!=100:
					continue
				if shape.level in shape_stack:
					shape_stack[shape.level].append(shape)
				else:
					shape_stack[shape.level] = [shape]

		for level in sorted(shape_stack):
			for shape in shape_stack[level]:
				self.canvas.add_shape(shape)

	def draw(self,path,Instrument):
		'''
		'''
		self.make_canvas()
		self.canvas.draw(path,Instrument)

	def generate_events(self):
		'''
		'''

	
	def get_features(self):
		features = dict()
		for feature in self.features:
			features[feature.name] = feature
		return features


Site.facilities = relationship('Facility', order_by=Facility.id,back_populates='site')


class Feature(Base):
	'''
	A collection of shapes 
		
	'''
	__tablename__ = 'feature'

	id = Column(Integer, primary_key=True)
	name = Column(String)
	visibility = Column(Integer)

	facility_id = Column(Integer, ForeignKey('facility.id'))
	facility = relationship(Facility, back_populates='features')


Facility.features = relationship('Feature', order_by=Feature.id,back_populates='facility')


# events = Table('events', Base.metadata,
# 				Column('shape_id', ForeignKey('feature.id'),primary_key=True),
# 				Column('scene_id', ForeignKey('scene.id'),primary_key=True)
# 				)


class Shape(Base):
	'''
	A single shape or object that makes up a feature
		
	'''
	__tablename__ = 'shape'

	id = Column(Integer, primary_key=True)
	name = Column(String)
	level = Column(Integer,default=0)
	visibility = Column(Integer, default=100)
	color = Column(String, default='[0,0,0]')
	archetype = Column(String)
	placement = Column(String)
	xoff = Column(Integer,default=0)
	yoff = Column(Integer,default=0)
	
	feature_id = Column(Integer, ForeignKey('feature.id'))
	feature = relationship(Feature, back_populates='shapes')

	#scenes = relationship('Scene',secondary=events,back_populates='shapes')

	__mapper_args__ = {'polymorphic_on': archetype}

	def build_geometry(self,placed=False):
		if placed:
			return load_wkt(self.placement)
		else:
			return load_wkt(self.geometry)

Feature.shapes = relationship('Shape', order_by=Shape.id,back_populates='feature')

'''
simulation objects

'''

class Scene(Base):
	'''
	'''
	__tablename__ = 'scene'

	id = Column(Integer, primary_key=True)

	site_id = Column(Integer, ForeignKey('site.id'))
	site = relationship(Site, back_populates='scenes')

	instrument_id = Column(Integer, ForeignKey('instrument.id'))
	instrument = relationship(Instrument, back_populates='scenes')

	#shapes = relationship('Shape',secondary=events,back_populates='scenes')

Site.scenes = relationship('Scene', order_by=Scene.id,back_populates='site')
Instrument.scenes = relationship('Scene', order_by=Scene.id,back_populates='instrument')


'''
shape types
'''

class Circle(Shape):
    __mapper_args__ = {'polymorphic_identity': 'circle'}

    def __init__(self,color='[31,84,168]',radius=400,level=0,xoff=0,yoff=0,rotation=0,visibility=100):
    	self.radius = radius
    	self.level = level
    	self.color = color
    	self.xoff = xoff
    	self.yoff = yoff
    	self.visibility = visibility

    	self.geometry = Point(xoff,yoff).buffer(self.radius).wkt

    @declared_attr
    def geometry(self):
    	return Shape.__table__.c.get('geometry', Column(String))

class Rectangle(Shape):
    __mapper_args__ = {'polymorphic_identity': 'rectangle'}

    def __init__(self,color='[110,160,62]',width=300,length=400,level=0,xoff=0,yoff=0,rotation=0):
    	self.width = width
    	self.length = length
    	self.level = level
    	self.color = color
    	self.xoff = xoff
    	self.yoff = yoff

    	self.geometry = Polygon([(xoff,yoff),(xoff,self.width),(self.length,self.width),(self.length,yoff)]).wkt

    @declared_attr
    def geometry(self):
    	return Shape.__table__.c.get('geometry', Column(String))