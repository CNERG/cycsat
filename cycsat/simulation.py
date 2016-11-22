"""
simulation.py

"""
from .prototypes import samples

from .archetypes import Facility
from .archetypes import Base

from random import randint
import os
import shutil

import sqlite3
import pandas as pd

from sqlalchemy import text
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


Session = sessionmaker()


class World(object):
	"""Interface for managing the facility geometry (i.e. the "world)"""

	def __init__(self,database):
		global Session
		global Base
		
		self.database = database
		self.engine = create_engine('sqlite+pysqlite:///'+self.database, module=sqlite3.dbapi2,echo=False)
		
		Session.configure(bind=self.engine)
		self.session = Session()

		Base.metadata.create_all(self.engine)

	def select(self,Archetype,sql='',first=True):
		"""Selects archetype instances from database

		Keyword arguments:
		Archetype -- the archetype class to select
		sql -- the sql query

		"""
		query = self.session.query(Archetype).filter(text(sql)).order_by(Archetype.id)
		
		if first:
			return query.first()
		else:
			return query.all()


	def write(self,Entities):
		"""Writes archetype instances to database"""

		if isinstance(Entities, list):
			self.session.add_all(Entities)
		else:
			self.session.add(Entities)

		self.session.commit()


class Simulator(object):
	"""Interface for running simulations and building the "world" """
	def __init__(self,database):
		self.world = World(database)
		self.reader = sqlite3.connect(self.world.database)


	def read(self,sql):
		"""Read sql query as pandas dataframe"""
		df = pd.read_sql_query(sql,self.reader)
		return df


	def build(self):
		"""Builds all the facilities in an output database from cyclus"""

		facilities = list()
		AgentEntry = self.read('select * from AgentEntry')
		
		for agent in AgentEntry.iterrows():

			prototype = agent[1]['Prototype']

			if agent[1]['Kind']=='Facility':
				facility = samples[prototype](AgentId=agent[1]['AgentId'])

				facility.build()
				facilities.append(facility)
			
		self.world.write(facilities)

	def simulate(self):
		"""Generates events for all facilties"""

		self.duration = self.read('SELECT Duration FROM Info')['Duration'][0]
		facilities = self.world.select(Facility,first=False)

		for facility in facilities:
			for timestep in range(self.duration):
				try:
					facility.simulate(timestep,self.reader,self.world)
				except:
					continue


	def prepare(self,Mission,Satellite):
		"""Prepare the folder structure for data collection"""

		self.mission = Mission
		self.satellite = Satellite

		Satellite.missions.append(Mission)
		self.world.write(Satellite)

		if not os.path.exists('output'):
			os.makedirs('output')
		
		self.dir = 'output/'+Mission.name+'-'+str(Mission.id)+'/'
		
		try:
			shutil.rmtree(self.dir)
		except:
			pass
		
		os.makedirs(self.dir)


	def launch(self,sql='',min_timestep=None,max_timestep=None):
		"""Collect images for all facilities using a satellite"""

		facilities = self.world.select(Facility,sql=sql,first=False)

		start = 0
		if min_timestep:
			start = min_timestep

		end = self.duration
		if max_timestep:
			end = max_timestep

		for facility in facilities:
			for instrument in self.satellite.instruments:
				instrument.calibrate(facility)

				for timestep in range(start,end):
					print(timestep,instrument.id,facility.id)
					instrument.capture(facility,timestep,self.dir)










		









