"""
simulation.py
"""
import inspect
import pandas as pd
import geopandas as gpd

from .archetypes import Site, Instrument, Observable, Shape, Rule
from .archetypes import Base, Satellite, Simulation, Build

import cycsat.archetypes as archetypes

from shapely.wkt import loads as load_wkt

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

    def __init__(self, path):
        global Base
        global archetypes

        Session = sessionmaker()
        self.path = path

        self.engine = create_engine(
            'sqlite+pysqlite:///' + self.path, module=sqlite3.dbapi2, echo=False)

        Session.configure(bind=self.engine)
        self.session = Session()
        Base.metadata.create_all(self.engine)

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

    def bind_table(self, table=None):
        """Binds a database table to a function for retriving a pandas dataframe view of the database"""
        def get_table(id=None, table=table, interface=self):
            sql = 'SELECT * FROM ' + table
            data = interface.query(sql)
            if id:
                return data[data.id == id].ix[0].obj
            else:
                return data

        get_table.__name__ = table
        return get_table


class Simulator(Database):

    def __init__(self, path, base=archetypes):
        Database.__init__(self, path, base)
        for table in self.archetypes:
            func = self.bind_table(table=table)
            table_name = table.replace('CycSat_', '')
            setattr(self, table_name, func)

            # get information about the simulation
        self.duration = self.query(
            'SELECT Duration FROM Info')['Duration'][0]

    def build(self, templates, name='untitled', attempts=100):
        """Builds sites.

        Keyword arguments:
        attempts -- (optional) max number of of attempts
        sites -- (optional) a list of sites to build, default all
        name -- (optional) name for the build 'Build'
        """
        build = Build(name=name)

        # get Agents to build
        AgentEntry = self.query('select * from AgentEntry')

        for agent in AgentEntry.iterrows():
            prototype = agent[1]['Prototype']

            # this will need to be changed with other kinds are used
            if agent[1]['Kind'] == 'Facility':
                if prototype in templates:
                    site = templates[prototype]()
                    site.AgentId = agent[1]['AgentId']
                    site.prototype = prototype
                    build.sites.append(site)

        self.save(build)
        build.assemble(self, attempts=attempts)
        self.save(build)

    def simulate(self, sql=None, name='None'):
        """Generates features for all site"""
        simulation = Simulation(name=name)

        if sql:
            sites = self.Site().query(sql)
        else:
            sites = self.Site()

        for site in sites.iterrows():
            if site[1]['defined']:
                print('simulating', site[1]['id'], site[1]['AgentId'])
                for timestep in range(self.duration):
                    site[1]['obj'].simulate(self, simulation, timestep)

        self.session.add(simulation)
        self.session.commit()

    def plot(self, sql=None, timestep=-1, virtual=None, label=False):
        """Plots site that meet a sql query at a given timestep

        Keyword arguments:
        sql -- sql to select Facilities, default all
        timestep -- timestep to plot
        virtual -- create a virtual, internal plot
        """
        if not sql:
            sql = 'AgentId == AgentId'

        sites = self.Site().query(sql)

        if len(sites) == 1:
            fig, axes = sites.iloc[0].obj.plot(timestep=timestep)
        else:
            # find the factors
            factors = set()
            for i in range(1, len(sites) + 1):
                if len(sites) % i == 0:
                    factors.add(i)

            # figure out the dimensions for the plot
            factors = list(factors)
            cols = factors[round(len(factors) / 2) - 1]
            rows = int(len(sites) / cols)

            fig, axes = plt.subplots(cols, rows)  # len(sites))

            for ax, site in zip(axes.flatten(), sites.iterrows()):
                site[1].obj.plot(ax=ax, timestep=timestep, label=label)

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


class Simulator2(Database):

    # def __init__(self, path):
    #     Database.__init__(self, path)
    #     self.builds = self.session.query(Build).all()

    def __init__(self, path):
        Database.__init__(self, path)
        for table in self.archetypes:
            func = self.bind_table(table=table)
            table_name = table.replace('CycSat_', '')
            setattr(self, table_name, func)

        self.duration = self.query(
            'SELECT Duration FROM Info')['Duration'][0]

    def save(self, build=None):
        """Saves a build to the database."""
        if build:
            self.session.add(build)
        self.session.commit()

    def load_build(self, build_id):
        """Loads a build by id number."""
        build = self.session.query(Build).filter(Build.id == build_id).one()
        build.database = self
        return build

    def create_build(self, templates, name='untitled', attempts=100):
        """Creates site for a new build.

        Keyword arguments:
        attempts -- (optional) max number of of attempts
        sites -- (optional) a list of sites to build, default all
        name -- (optional) name for the build 'Build'
        """
        build = Build(name=name)
        build.database = self

        # get Agents to build
        AgentEntry = self.query('select * from AgentEntry')

        for agent in AgentEntry.iterrows():
            prototype = agent[1]['Prototype']

            # this will need to be changed with other kinds are used
            if agent[1]['Kind'] == 'Facility':
                if prototype in templates:
                    site = templates[prototype]()
                    site.AgentId = agent[1]['AgentId']
                    site.prototype = prototype
                    build.sites.append(site)

        self.save(build)
        build.assemble(attempts=attempts)
        self.save(build)
