"""
simulation.py
"""
from .prototypes import samples

from .archetypes import Facility
from .archetypes import Base

from random import randint
import os
import shutil

from skimage.io import imread

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

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
		self.database = database
		self.world = World(database)
		self.reader = sqlite3.connect(self.world.database)


	def read(self,sql):
		"""Read sql query as pandas dataframe"""
		df = pd.read_sql_query(sql,self.reader)
		return df


	def build(self,AgentId=None):
		"""Builds all the facilities in an output database from cyclus"""

		facilities = list()

		sql = 'select * from AgentEntry'
		if AgentId:
			sql = 'select * from AgentEntry where AgentId='+str(AgentId)
		AgentEntry = self.read(sql)
		
		for agent in AgentEntry.iterrows():
			prototype = agent[1]['Spec'][10:]

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
		self.dir = 'output/'+self.world.database+'/'+str(Mission.id)+'/'
		
		if not os.path.exists(self.dir):
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
				instrument.target(facility) #,self.world)

				for timestep in range(start,end):
					print(timestep,instrument.id,facility.id)
					instrument.capture(timestep,self.dir,
						Mission=self.mission,World=self.world)

				self.world.write(facility)


	def plot_timestep(self,timestep,instrument_id=1,sql=''):
		"""Plots a timestep given a sql query and a facility list"""

		facilities = self.world.select(Facility,sql=sql,first=False)
		query = self.read(sql='SELECT * FROM CycSat_Scene')
		scenes = query[(query['timestep']==timestep) & (query['instrument_id'] == instrument_id)]

		scene_collection = dict()
		for facility in facilities:
			scene = scenes[scenes['facility_id']==facility.id]
			try:
				scene_collection[facility.id] = {'name':facility.name,'scene_id':scene.iloc[0]['id']}
			except:
				continue

		fig = plt.figure()
		fig.suptitle('timestep: '+str(timestep))

		# add sub plots
		ax0 = fig.add_subplot(2,2,1)
		ax1 = fig.add_subplot(2,2,2)
		ax2 = fig.add_subplot(2,2,3)
		ax3 = fig.add_subplot(2,2,4)

		axes = [ax0, ax1, ax2, ax3]

		for i, facility in enumerate(scene_collection):

			ax = axes[i]
			facility = scene_collection[facility]
			im_path = self.dir+str(facility['scene_id'])+'.tif'
			im1 = imread(im_path)

			ax.imshow(im1,'gray')
			ax.set_title(scene_collection[3]['name'])
		
		plt.savefig('plots/'+str(timestep)+'.pdf')
		plt.clf()
		plt.cla()


























		









