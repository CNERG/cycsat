"""
simulation.py
"""
import pandas as pd
import geopandas as gpd

import matplotlib as plt

from .archetypes import Facility, Instrument, Feature, Shape, Event, Rule
from .archetypes import Base, Satellite, Simulation, Build, Process

from random import randint
import os
import shutil
import io

from skimage.io import imread

import imageio

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
		# create the build and add the templates
		build = Build(name=name)
		for prototype in templates:
			template = templates[prototype]
			template.prototype = prototype
			build.facilities.append(template)
		self.save(build)

		# get Agents to build
		AgentEntry = self.read('select * from AgentEntry')

		built_facilities = list()
		for agent in AgentEntry.iterrows():
			prototype = agent[1]['Spec'][10:]

			if agent[1]['Kind']=='Facility':

				template = self.session.query(Facility).filter(Facility.prototype==prototype). \
				filter(Facility.template==True).all()
				
				if template:
					facility = self.copy_facility(template[0])
					facility.AgentId = agent[1]['AgentId']
					built_facilities.append(facility)
		
		build.facilities+=built_facilities
		self.session.expunge(build)
		self.session.add(build)
		self.session.commit()

		facilities = self.session.query(Facility).filter(Facility.template==False).filter(Facility.build_id==build.id).all()
		for facility in facilities:
			facility.place_features(timestep=-1,attempts=attempts)
			self.save(facility)

		# delete templates
		templates = self.session.query(Facility).filter(Facility.template==True).all()
		for template in templates:
			self.session.delete(template)
			self.session.commit()

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
			features.append(c)

		copy = facility
		self.session.expunge(copy)
		make_transient(copy)
		copy.id = None
		copy.template = False

		copy.features = features
		#self.refresh()

		return copy

	def plot(self,sql,timestep=-1,virtual=None):
		"""Plots facilites that meet a sql query at a given timestep"""

		facilities = self.facilities.query(sql)
		facilities = facilities[facilities.template==False]

		if len(facilities)==1:
			fig, ax = facilities.iloc[0].obj.plot(timestep=timestep)
			return fig, ax
		
		fig, axes = plt.subplots(len(facilities))

		for ax,facility in zip(axes,facilities.iterrows()):
			facility[1].obj.plot(ax=ax,timestep=timestep)
		
		if virtual:
			plt.savefig(virtual,format='png')
			return virtual

		return fig, axes

	def gif(self,sql,timesteps,name,fps=1):
		"""Creates a GIF of these """

		plt.ioff()
		plots = list()
		for step in timesteps:
			f = io.BytesIO()
			f = self.plot(sql=sql,timestep=step,virtual=f)
			plots.append(f)
			plt.close()

		images = list()
		for plot in plots:
			plot.seek(0)
			images.append(imageio.imread(plot))
		imageio.mimsave(name+'.gif', images, fps=fps)
		plt.ion()































		









