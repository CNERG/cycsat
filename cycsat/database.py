"""
data_model.py

Contains the data model classes.

"""

from shapely.wkt import loads as load_wkt

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Table, Numeric, Boolean
from sqlalchemy.dialects.sqlite import BLOB
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

# create the declarative base
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
	resolution = Column(Integer)
	
	satellite_id = Column(Integer, ForeignKey('satellite.id'))
	satellite = relationship(Satellite, back_populates='instruments')


class Mission(Base):
	'''
	A single mission for a particular satellite

	'''
	__tablename__ = 'mission'

	id = Column(Integer, primary_key=True)
	name = Column(String)
	
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

	site_id = Column(Integer, ForeignKey('site.id'))
	site = relationship(Site, back_populates='facilities')

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

	events = relationship('Event', back_populates='feature')


Facility.features = relationship('Feature', order_by=Feature.id,back_populates='facility')


class Shape(Base):
	'''
	A single shape or object that makes up a feature
		
	'''
	__tablename__ = 'shape'

	id = Column(Integer, primary_key=True)
	name = Column(String)
	level = Column(Integer,default=0)
	visibility = Column(Integer)
	color = Column(String)
	feature_id = Column(Integer, ForeignKey('feature.id'))
	feature = relationship(Feature, back_populates='shapes')

	archetype = Column(String)

	__mapper_args__ = {'polymorphic_on': archetype}

	def build_geometry(self):
		return load_wkt(self.geometry)

Feature.shapes = relationship('Shape', order_by=Shape.id,back_populates='feature')
'''

simulation objects

'''

class Event(Base):
	'''
	'''
	__tablename__ = 'event'

	visible = Column(Integer)

	feature_id = Column(Integer, ForeignKey('feature.id'), primary_key=True)
	scene_id = Column(Integer, ForeignKey('scene.id'), primary_key=True)

	feature = relationship('Feature', back_populates='events')
	scene = relationship('Scene', back_populates='events')


class Scene(Base):
	'''
	'''
	__tablename__ = 'scene'

	id = Column(Integer, primary_key=True)

	site_id = Column(Integer, ForeignKey('site.id'))
	site = relationship(Site, back_populates='scenes')

	instrument_id = Column(Integer, ForeignKey('instrument.id'))
	instrument = relationship(Instrument, back_populates='scenes')

	events = relationship('Event', back_populates='scene')

Site.scenes = relationship('Scene', order_by=Scene.id,back_populates='site')
Instrument.scenes = relationship('Scene', order_by=Scene.id,back_populates='instrument')