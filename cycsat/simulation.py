"""
simulation.py
"""
import pandas as pd
import geopandas as gpd

import matplotlib as plt

from .prototypes import samples
from .archetypes import Facility, Instrument, Feature, Shape, Event, Rule
from .archetypes import Base, Satellite, Mission, Simulation, Build, Process

from random import randint
import os
import shutil

from skimage.io import imread

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

from sqlalchemy import text, exists
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import make_transient


Session = sessionmaker()


class CycSat(object):
	"""This is the Cycsat simulation object used to manage simulations
	"""
	def __init__(self,database):
		"""Connects to a CYCLUS database."""
		global Session
		global Base

		# connect using SQLAlchemy
		self.database = database
		self.engine = create_engine('sqlite+pysqlite:///'+self.database, module=sqlite3.dbapi2,echo=False)
		Session.configure(bind=self.engine)
		self.session = Session()
		Base.metadata.create_all(self.engine)

		# connect using pandas for querying rules in the database
		self.reader = sqlite3.connect(self.database)
		self.duration = pd.read_sql_query('SELECT Duration FROM Info',self.reader)['Duration'][0]

	def refresh(self):
		self.__init__(self.database)

	def gen_df(self,Table,geo=None):
		cols = Table.__table__.columns.keys()
		records = self.session.query(Table).all()
		df = pd.DataFrame([[getattr(i,j) for j in cols]+[i] for i in records],columns=cols+['obj'])
		if geo:
			df = gpd.GeoDataFrame(df,geometry=geo)
		return df

	@property
	def satellites(self):
		return self.gen_df(Satellite)

	@property
	def missions(self):
		return self.gen_df(Mission)

	@property
	def instruments(self):
		return self.gen_df(Instrument)

	@property
	def facilities(self):
		return self.gen_df(Facility)

	@property
	def features(self):
		return self.gen_df(Feature)

	@property
	def shapes(self):
		return self.gen_df(Shape)

	@property
	def events(self):
		return self.gen_df(Event)

	@property
	def rules(self):
		return self.gen_df(Rule)

	@property
	def builds(self):
		return self.gen_df(Build)

	@property
	def processes(self):
		return self.gen_df(Process)

	def save(self,Entities):
		"""Writes archetype instances to database"""
		if isinstance(Entities, list):
			self.session.add_all(Entities)
		else:
			self.session.add(Entities)
		self.session.commit()

	def read(self,sql):
		"""Read SQL query as pandas dataframe"""
		df = pd.read_sql_query(sql,self.reader)
		return df

	def build(self,name,templates=None,attempts=100):
		"""Builds facilities.
		
		Keyword arguments:
		attempts -- (optional) max number of of attempts
		facilities -- (optional) a list of facilities to build, default all
		name -- (optional) name for the build 'Build'
		"""
		# create the build
		build = Build(name=name)

		# get Agents to build
		AgentEntry = self.read('select * from AgentEntry')

		for agent in AgentEntry.iterrows():
			prototype = agent[1]['Spec'][10:]

			if agent[1]['Kind']=='Facility':
				
				facility = samples[prototype](AgentId=agent[1]['AgentId'])
				# facility = templates[prototype]
				# facility.AgentId = agent[1]['AgentId']
				facility.place_features(timestep=-1,attempts=attempts)
				
				build.facilities.append(facility)
		
		self.save(build)

	def simulate(self,build_id,name='None'):
		"""Generates events for all facilties"""
		simulation = Simulation(name=name)

		self.duration = self.read('SELECT Duration FROM Info')['Duration'][0]
		
		facilities = self.facilities[self.facilities.build_id==build_id]
		for facility in facilities.iterrows():
			if facility[1]['defined']:
				for timestep in range(self.duration):
					try:
						facility[1]['obj'].simulate(self,simulation,timestep)
					except:
						continue

		self.session.add(simulation)
		self.session.commit()

	def copy_facility(self,facility):
		"""Copies a facility template and related rows."""
		
		features = list()
		for feature in facility.features:
			c = feature.copy(self.session)
			print(c)
			features.append(c)

		self.session.expunge(facility)
		make_transient(facility)
		facility.id = None

		facility.features = features
		self.refresh()

		return facility

	def copy_facility2(self,facility):
		"""Copies a facility template and related rows."""
		
		features = list()
		for feature in facility.features:
			c = feature.copy(self.session)
			print(c)
			features.append(c)

		self.session.expunge(facility)
		make_transient(facility)
		facility.id = None

		facility.features = features
		self.refresh()

		return facility
























		









