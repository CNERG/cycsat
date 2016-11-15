"""
database.py

"""

from .data_model import Facility
import cycsat.library

from .data_model import Base

from random import randint

import sqlite3

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

Session = sessionmaker()

class Writer(object):
	'''
	An interface for working with sqlalchemy, sqlite3, and data classes
	
	'''

	def __init__(self,database):
		'''
		'''
		global Session
		global Base

		# add db extension if unspecified
		if database[:-3]!='.db':
			database+='.db'
		
		self.database = database
		self.engine = create_engine('sqlite+pysqlite:///'+self.database, module=sqlite3.dbapi2,echo=False)
		
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


class Reader(object):
	'''
	'''
	def __init__(self,database):
		'''
		'''
		self.session = sqlite3.connect(database)
		self.cur = self.session.cursor()


	def read_table(self,table):
		'''
		'''
		self.cur.execute('SELECT * FROM {table};'.\
			format(table=table))

		cols = [x[0] for x in self.cur.description]
		data = self.cur.fetchall()

		result = dict()
		for i,row in enumerate(data):
			result[i] = dict()
			for col in zip(cols,row):
				result[i][col[0]] = col[1]
		return result


class Simulator(object):
	'''
	'''

	def __init__(self,output_db,input_db):
		'''
		'''
		self.writer = Writer(output_db)
		self.reader = Reader(input_db)

	def add_facilities(self):
		'''
		'''
		facilities = list()
		AgentEntry = self.reader.read_table('AgentEntry')
		for agent in AgentEntry:
			if AgentEntry[agent]['Kind']=='Facility':

				if AgentEntry[agent]['Prototype']=='Reactor':
					facility = cycsat.library.reactor
				else:
					facility = Facility(width=500,length=500)

				facilities.append(facility)

		self.writer.save(facilities)

	def build_facilities(self):
		'''
		'''
		facilities = self.writer.select(Facility,one=False)
		for facility in facilities:
			facility.define()

		self.writer.save(facilities)

	def draw_facilities(self,path,Instrument):
		'''
		'''











# def get_all_shapes(Mission):
# 	'''
# 	'''
# 	shapes = []
# 	for site in Mission.sites:
# 		for facility in site.facilities:
# 			for feature in facility.features:
# 				for shape in feature.shapes:
# 					shapes.append(shape)

# 	return shapes




