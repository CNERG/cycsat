"""
database.py

Contains the database functions.

"""
# import classes

# import third-party modules
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
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

class Facility(object):
	'''	
	'''

	__tablename__ = 'facility'

	id = Column(Integer, primary_key=True)
	name = Column(String)
	satellite_id = Column(Integer, ForeignKey('satellite.id'))

	satellite = relationship(Satellite, back_populates='missions')

'''
to create a scene

1. get a list of all the features
2. for all the features that have a proability that allows them to appear, create events in the
events table
3. Use the events (visable features) to generate a scene!

'''

class Feature(object):
	'''
	This object is a feature associated with a site.
	
	Attributes:
		liklihood: % chance this feature will appear in each scene.
		name: 
		shape:
		
	'''

	def __init__(self,name=None):
		self.name = name


'''
observation classes
**********************************
'''

class Event(object):
	'''
	Events are junction tables (many-to-many) between features and scenes.
	One Feature has many Events. Events are simply the probability
	
	Attributes:
		
	'''

	def __init__(self,name=None):
		self.name = name


class Scene(object):
	'''
	This object is a canvas with features from a particular time in
	a simulation.
	
	Attributes:
		
	'''

	def __init__(self,name=None):
		self.name = name

