'''
simulator.py

'''

from random import randint

from .database import Base
from .database import Satellite, Instrument, Mission
from .database import Site, Feature, Event, Scene

import sqlite3

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


Session = sessionmaker()


class Designer(object):
	'''
	An interface for working with sqlalchemy, sqlite3, and data classes
	
	'''

	def __init__(self,name):
		'''
		'''
		global Session
		global Base

		# add db extension if unspecified
		if name[:-2]!='.db':
			name+='.db'
		
		self.name = name
		self.engine = create_engine('sqlite+pysqlite:///'+self.name, module=sqlite3.dbapi2,echo=False)
		
		Session.configure(bind=self.engine)
		self.session = Session()

		Base.metadata.create_all(self.engine)

	def select(self,Entity,id=None,satellite=None,one=True,name=None):
		'''
		select a 
		'''

		if name:
			query = self.session.query(Entity).filter_by(name=name)
		elif id:
			query = self.session.query(Entity).filter_by(id=id)
		else:
			query = self.session.query(Entity)
			if one:
				return query.first()
			else:
				return query.all()

		return query.first()


	def save(self,Entities):
		'''
		add changed or new entities to a project

		'''

		if isinstance(Entities, list):
			self.session.add_all(Entities)
		else:
			self.session.add(Entities)

		self.session.commit()


def get_all_shapes(Mission):
	'''
	'''
	shapes = []
	for site in Mission.sites:
		for facility in site.facilities:
			for feature in facility.features:
				for shape in feature.shapes:
					shapes.append(shape)

	return shapes

# def create_event(Shape):
# 	'''
# 	'''

# 	die_roll = randint(1,99)

# 	if Shape.visibility < die_roll:
# 		break
# 	else:
# 		pass