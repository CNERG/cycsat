"""
data_model.py

Contains the data model functions.

"""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Table
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

# create the declarative base
Base = declarative_base()

'''
Agency clases
**********************************
'''

class Satellite(Base):
	'''
	'''
	__tablename__ = 'satellite'

	id = Column(Integer, primary_key=True)
	name = Column(String)


class Instrument(Base):
	'''
	'''
	__tablename__ = 'instrument'

	id = Column(Integer, primary_key=True)
	name = Column(String)
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


Satellite.missions = relationship('Mission', order_by=Mission.id,back_populates='satellite')
Satellite.instruments = relationship('Instrument', order_by=Instrument.id, back_populates='satellite')


'''
World classes 
**********************************
'''

class Site(Base):
	'''	
	'''
	__tablename__ = 'site'

	id = Column(Integer, primary_key=True)
	name = Column(String)
	mission_id = Column(Integer, ForeignKey('mission.id'))

	mission = relationship(Mission, back_populates='sites')

Mission.sites = relationship('Site', order_by=Site.id,back_populates='mission')


class Feature(Base):
	'''
	This object is a feature associated with a site.
		
	'''
	__tablename__ = 'feature'

	id = Column(Integer, primary_key=True)
	name = Column(String)
	site_id = Column(Integer, ForeignKey('site.id'))

	site = relationship(Site, back_populates='features')
	scenes = relationship('Event', back_populates='feature')

Site.features = relationship('Feature', order_by=Feature.id,back_populates='site')


'''
Observation classes
'''

class Event(Base):
	'''
	'''
	__tablename__ = 'event'

	feature_id = Column(Integer, ForeignKey('feature.id'), primary_key=True)
	scene_id = Column(Integer, ForeignKey('scene.id'), primary_key=True)
	visible = Column(Integer)

	feature = relationship('Feature', back_populates='scenes')
	scene = relationship('Scene', back_populates='features')

class Scene(Base):
	'''
	'''
	__tablename__ = 'scene'

	id = Column(Integer, primary_key=True)
	name = Column(String)
	site_id = Column(Integer, ForeignKey('site.id'))

	site = relationship(Site, back_populates='scenes')
	features = relationship('Event', back_populates='scene')

Site.scenes = relationship('Scene', order_by=Scene.id,back_populates='site')