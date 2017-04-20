"""
simulation.py
"""
import math
import inspect
import pandas as pd
import geopandas as gpd

from .archetypes import Facility, Instrument, Feature, Shape, Event, Rule
from .archetypes import Base, Satellite, Simulation, Build, Process

import cycsat.archetypes as archetypes

from shapely.wkt import loads as load_wkt

from random import randint
import os
import shutil
import io

from skimage.io import imread

import imageio

import sqlite3
import matplotlib.pyplot as plt

from sqlalchemy import text, exists
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import make_transient


class Database:
    """Interface for connecting to sqlite database."""

    def __init__(self, path, base):
        Session = sessionmaker()

        self.path = path
        self.Base = getattr(base, 'Base')

        self.engine = create_engine(
            'sqlite+pysqlite:///' + self.path, module=sqlite3.dbapi2, echo=False)

        Session.configure(bind=self.engine)
        self.session = Session()
        self.Base.metadata.create_all(self.engine)

        self.connection = sqlite3.connect(self.path)

        self.archetypes = dict()
        for name, obj in inspect.getmembers(archetypes):
            if inspect.isclass(obj):
                try:
                    self.archetypes[obj.__tablename__] = obj
                except:
                    continue

    def query(self, sql):
        """Query the database and return a pandas dataframe."""
        if 'CycSat_' in sql:
            print(sql)
            table = sql[sql.find('FROM') + 5:].split(' ')[0]
            archetype = self.archetypes[table]
            cols = archetype.__table__.columns.keys()
            data = self.session.query(archetype).all()

            df = pd.DataFrame([[getattr(i, j) for j in cols] + [i]
                               for i in data], columns=cols + ['obj'])

            if 'geometry' in df.columns.tolist():
                df = df.assign(geometry=df.geometry.apply(load_wkt))
                df = gpd.GeoDataFrame(df, geometry='geometry')
            return df

        df = pd.read_sql_query(sql, self.connection)
        return df

    def save(self, Objects):
        """Saves objects to the database. Takes a list of a single object."""
        if isinstance(Objects, list):
            self.session.add_all(Objects)
        else:
            self.session.add(Objects)
        self.session.commit()

    def bind_table(self, table):
        """Binds a database table to a function for retriving a pandas dataframe view of the database"""
        def get_table(table=table, interface=self, ):
            sql = 'SELECT * FROM ' + table
            return interface.query(sql)

        get_table.__name__ = table
        return get_table


class Simulator(Database):

    def __init__(self, path, base=archetypes):
        Database.__init__(self, path, base)
        for table in self.archetypes:
            func = self.bind_table(table)
            table_name = table.replace('CycSat_', '')
            setattr(self, table_name, func)

            # get information about the simulation
        self.duration = self.query(
            'SELECT Duration FROM Info')['Duration'][0]

    def build(self, templates, name='untitled', attempts=100):
        """Builds facilities.

        Keyword arguments:
        attempts -- (optional) max number of of attempts
        facilities -- (optional) a list of facilities to build, default all
        name -- (optional) name for the build 'Build'
        """
        build = Build(name=name)

        # get Agents to build
        AgentEntry = self.query('select * from AgentEntry')

        for agent in AgentEntry.iterrows():
            prototype = agent[1]['Prototype']

            if agent[1]['Kind'] == 'Facility':
                if prototype in templates:
                    facility = templates[prototype]()
                    facility.AgentId = agent[1]['AgentId']
                    facility.prototype = prototype
                    build.facilities.append(facility)

        self.save(build)
        build.assemble(self, attempts=attempts)
        self.save(build)

    def simulate(self, build_id, name='None'):
        """Generates events for all facilties"""
        simulation = Simulation(name=name)

        self.duration = self.query(
            'SELECT Duration FROM Info')['Duration'][0]

        facilities = self.Facility()[self.Facility().build_id == build_id]
        for facility in facilities.iterrows():
            if facility[1]['defined']:
                for timestep in range(self.duration):
                    facility[1]['obj'].simulate(self, simulation, timestep)

        self.session.add(simulation)
        self.session.commit()

    def plot(self, sql=None, timestep=-1, virtual=None):
        """Plots facilites that meet a sql query at a given timestep

        Keyword arguments:
        sql -- sql to select Facilities, default all
        timestep -- timestep to plot
        virtual -- create a virtual, internal plot
        """
        if not sql:
            sql = 'AgentId == AgentId'

        facilities = self.Facility().query(sql)

        if len(facilities) == 1:
            fig, axes = facilities.iloc[0].obj.plot(timestep=timestep)
        else:
            # find the factors
            factors = set()
            for i in range(1, len(facilities) + 1):
                if len(facilities) % i == 0:
                    factors.add(i)

            # figure out the dimensions for the plot
            factors = list(factors)
            cols = factors[round(len(factors) / 2) - 1]
            rows = int(len(facilities) / cols)

            fig, axes = plt.subplots(cols, rows)  # len(facilities))

            for ax, facility in zip(axes.flatten(), facilities.iterrows()):
                facility[1].obj.plot(ax=ax, timestep=timestep)

        if virtual:
            plt.savefig(virtual, format='png')
            return virtual

        return fig, axes

    def gif(self, sql, timesteps, name, fps=1):
        """Creates a GIF"""

        plt.ioff()
        plots = list()
        for step in timesteps:
            f = io.BytesIO()
            b = self.plot(sql=sql, timestep=step, virtual=f)
            plots.append(b)
            plt.close()

        images = list()
        for plot in plots:
            plot.seek(0)
            image = imageio.imread(plot)
            images.append(image)
        imageio.mimsave(name + '.gif', images, fps=fps)
        plt.ion()
