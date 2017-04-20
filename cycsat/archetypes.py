"""
archetypes.py
"""
import ast
import random
import io

import imageio
import tempfile

from descartes import PolygonPatch
from matplotlib import pyplot as plt

from .image import Sensor
from .geometry import assemble, place
from .geometry import build_geometry, build_footprint, near_rule, line_func
from .geometry import rotate_facility, evaluate_rules

from .laboratory import materialize

import pandas as pd
import numpy as np

import copy
import operator

from shapely.geometry import Polygon, Point, LineString
from shapely.wkt import loads as load_wkt
from shapely.ops import cascaded_union
from shapely.affinity import rotate, translate

from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Table, Boolean
from sqlalchemy.dialects.sqlite import BLOB
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm.session import make_transient


# multiple inheritance for a template library
Base = declarative_base()


operations = {
    "equals": operator.eq,
    "not equal": operator.ne,
    "not equal": operator.ne,
    "less than": operator.lt,
    "less than or equals": operator.le,
    "greater than": operator.gt,
    "greater than or equals": operator.ge
}


class Build(Base):
    """A possible realization of all Facilities and Features in a simulation."""

    __tablename__ = 'CycSat_Build'
    id = Column(Integer, primary_key=True)
    name = Column(String)

    def assemble(self, attempts=100):
        """Assembles the build, i.e. places all the features of all the facilities."""
        for facility in self.facilities:
            facility.place_features(timestep=-1, attempts=attempts)


class Process(Base):
    """A proccess run by cycsat under a particluar user-initiated 'Build'.
    """
    __tablename__ = 'CycSat_Procces'

    id = Column(Integer, primary_key=True)
    name = Column(String)  # description of the the event/error
    result = Column(Integer, default=0)
    message = Column(String)

    build_id = Column(Integer, ForeignKey('CycSat_Build.id'))
    build = relationship(Build, back_populates='processes')

Build.processes = relationship('Process', order_by=Process.id, back_populates='build',
                               cascade='all, delete, delete-orphan')


class Simulation(Base):
    """A collection of instruments."""

    __tablename__ = 'CycSat_Simulation'

    id = Column(Integer, primary_key=True)
    name = Column(String)


class Satellite(Base):
    """A collection of instruments."""

    __tablename__ = 'CycSat_Satellite'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    mmu = Column(Integer)
    width = Column(Integer)
    length = Column(Integer)


class Instrument(Base):
    """Parameters for generating a scene"""
    __tablename__ = 'CycSat_Instrument'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    mmu = Column(Integer, default=1)  # in 10ths of centimeters
    width = Column(Integer)
    length = Column(Integer)
    min_spectrum = Column(String)
    max_spectrum = Column(String)
    prototype = Column(String)
    wkt = Column(String)

    __mapper_args__ = {'polymorphic_on': prototype}

    satellite_id = Column(Integer, ForeignKey('CycSat_Satellite.id'))
    satellite = relationship(Satellite, back_populates='instruments')

    def geometry(self):
        self.geo = build_geometry(self)
        return self.geo

    def target(self, Facility):
        """Creates a sensor object and focuses it on a facility"""
        self.Sensor = Sensor(self)
        self.Facility = Facility

        self.shapes = []
        for feature in Facility.features:
            for shape in feature.shapes:
                self.shapes.append(materialize(shape))

        self.Sensor.focus(Facility)
        self.Sensor.calibrate(Facility)

    def capture(self, timestep, path, Mission=None, World=None):
        """Adds shapes at timestep to a image"""

        self.Sensor.reset()

        # gets all events from a timestep
        events = [
            Event.shape_id for Event in self.Facility.events if Event.timestep == timestep]
        # get all shapes from a timestep (if there is an event)
        shapes = [Shape for Shape in self.shapes if Shape.id in events]

        shape_stack = dict()
        for shape in shapes:
            if shape.level in shape_stack:
                shape_stack[shape.level].append(shape)
            else:
                shape_stack[shape.level] = [shape]

        for level in sorted(shape_stack):
            for shape in shape_stack[level]:
                self.Sensor.capture_shape(shape)

        # create and save the scene object
        scene = Scene(timestep=timestep)
        self.scenes.append(scene)
        self.Facility.scenes.append(scene)

        path = path + str(scene.id)
        self.Sensor.write(path)

Satellite.instruments = relationship(
    'Instrument', order_by=Instrument.id, back_populates='satellite')


#------------------------------------------------------------------------------
# OBERVABLES
#------------------------------------------------------------------------------

# class Observable:
#     """A high level class for managing objects with geometry and turning
#     intrumented lists into pandas dataframes."""

#     def bounds(self):
#         return load_wkt(self.geometry)

#     def footprint(self):
#         return load_wkt(self.geometry)

#     def _get_children(self, archetype):
#         cols = archetype.__table__.columns.keys()
#         data = getattr(self, archetype.__tablename__)

#         df = pd.DataFrame([[getattr(i, j) for j in cols] + [i]
#                            for i in data], columns=cols + ['obj'])

#         if 'geometry' in df.columns.tolist():
#             df = df.assign(geometry=df.geometry.apply(load_wkt))
#             df = gpd.GeoDataFrame(df, geometry='geometry')
#         return df


class Facility(Base):
    """A collection of features on a collection of terrains."""
    __tablename__ = 'CycSat_Facility'

    id = Column(Integer, primary_key=True)
    AgentId = Column(Integer)
    name = Column(String)
    maxx = Column(Integer)
    maxy = Column(Integer)
    defined = Column(Boolean, default=False)
    prototype = Column(String)
    template = Column(String)
    geometry = Column(String)

    __mapper_args__ = {'polymorphic_on': template}

    # __mapper_args__ = {'polymorphic_on': prototype}
    build_id = Column(Integer, ForeignKey('CycSat_Build.id'))
    build = relationship(Build, back_populates='facilities')

    def bounds(self):
        geometry = build_geometry(self)
        self.geometry = geometry.wkt
        return geometry

    def footprint(self):
        return build_footprint(self)

    def rotate(self, degrees):
        rotate_facility(self, degrees)

    def axis(self):
        if self.ax_angle:
            footprint = self.geometry()
            minx, miny, maxx, maxy = footprint.bounds
            site_axis = LineString([[-maxx, 0], [maxx * 2, 0]])
            site_axis = rotate(site_axis, self.ax_angle)
            return site_axis
        else:
            print('This facility has not been built. Use the build() method \n'
                  'before creating the axis.')

    def dep_graph(self):
        """Returns groups of features based on their dependencies."""
        graph = dict((f.name, f.depends_on()) for f in self.features)
        name_to_instance = dict((f.name, f) for f in self.features)

        # where to store the batches
        batches = list()

        while graph:
            # Get all features with no dependencies
            ready = {name for name, deps in graph.items() if not deps}
            if not ready:
                msg = "Circular dependencies found!\n"
                raise ValueError(msg)
            # Remove them from the dependency graph
            for name in ready:
                graph.pop(name)
            for deps in graph.values():
                deps.difference_update(ready)

            # Add the batch to the list
            batches.append([name_to_instance[name] for name in ready])

        # Return the list of batches
        return batches

    def place_features(self, timestep=-1, attempts=100):
        """Places all the features of a facility according to their rules
        and events at the provided timestep."""
        for x in range(attempts):
            result = assemble(self, timestep, attempts)
            if result:
                self.defined = True
                return True
            else:
                self.defined = False
                continue

    def simulate(self, Simulator, sim, timestep):
        """Evaluates the conditions for dynamic shapes at a given timestep and
        generates events. All conditions must be True in order for the event to be
        created.

        Keyword arguments:
        Simulator -- a cycsat Simulator object
        timestep -- the timestep for simulation
        """
        dynamic_features = [
            feature for feature in self.features if feature.visibility != 100]

        events = list()
        for feature in dynamic_features:
            evaluations = []
            for condition in feature.conditions:
                qry = "SELECT Value FROM %s WHERE AgentId=%s AND Time=%s;" % (
                    condition.table, self.AgentId, timestep)
                df = Simulator.query(qry)
                value = df['Value'][0]

                if operations[condition.oper](value, condition.value):
                    evaluations.append(True)
                else:
                    evaluations.append(False)

            if False in evaluations:
                print(feature.name, timestep, 'False')
                continue
            else:
                if random.randint(1, 100) < feature.visibility:
                    print(feature.name, timestep, 'True')
                    event = Event(timestep=timestep)
                    feature.events.append(event)
                    self.events.append(event)
                    sim.events.append(event)
                    Simulator.save(feature)
                else:
                    continue

        self.place_features(timestep=timestep)
        Simulator.save(self)

    def timestep_shapes(self, timestep=0):
        """Returns the ordered shapes to draw at a facility for a given timestep."""
        shapes = list()

        for feature in self.features:
            # add all if a static feature
            if feature.visibility == 100:
                shapes += [(shape.level, shape) for shape in feature.shapes]
            else:
                events = [e for e in feature.events if e.timestep == timestep]
                if len(events) > 0:
                    shapes += [(shape.level, shape)
                               for shape in feature.shapes]

        return sorted(shapes, key=lambda x: x[0])

    def plot(self, ax=None, timestep=-1, labels=False, save=False, name='plot.png', virtual=None):
        """plots a facility and its static features or a timestep."""
        if ax:
            new_fig = False
            ax.set_aspect('equal')
        else:
            new_fig = True
            fig, ax = plt.subplots(1, 1, sharex=True, sharey=True)

        # set up the plot
        ax.set_xlim([0, self.maxx])
        ax.set_ylim([0, self.maxy])
        ax.set_axis_bgcolor('green')
        ax.set_title('Agent: ' + str(self.AgentId) +
                     '\ntimestep:' + str(timestep))
        ax.set_aspect('equal')

        shapes = self.timestep_shapes(timestep)
        for shape in shapes:
            shape = shape[1]
            if shape.feature.visibility == 100:
                geometry = shape.geometry()
            else:
                geometry = shape.geometry(timestep=timestep)

            rgb = shape.get_rgb(plotting=True)
            patch = PolygonPatch(geometry, facecolor=rgb)
            ax.add_patch(patch)

            if labels:
                plt.text(feature.geo.centroid.x,
                         feature.geo.centroid.y, feature.name)

        plt.tight_layout()

        if save:
            plt.savefig(name)

        if virtual:
            plt.savefig(virtual, format='png')
            return virtual

        if new_fig:
            return fig, ax

    def gif(self, timesteps, name, fps=1):
        """plots a facility and its static features or a timestep."""
        plt.ioff()
        plots = list()
        for step in timesteps:
            f = io.BytesIO()
            f = self.plot(timestep=step, virtual=f)
            plots.append(f)
            plt.close()

        images = list()
        for plot in plots:
            plot.seek(0)
            images.append(imageio.imread(plot))
        imageio.mimsave(name + '.gif', images, fps=fps)
        plt.ion()


Build.facilities = relationship(
    'Facility', order_by=Facility.id, back_populates='build')


class Feature(Base):
    """Collection of shapes"""

    __tablename__ = 'CycSat_Feature'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    visibility = Column(Integer, default=100)
    prototype = Column(String)
    rgb = Column(String)
    level = Column(Integer)
    rotation = Column(Integer)

    __mapper_args__ = {'polymorphic_on': prototype}

    facility_id = Column(Integer, ForeignKey('CycSat_Facility.id'))
    facility = relationship(Facility, back_populates='features')

    def sorted_events(self):
        """Returns a sorted list (by timestep) of events."""
        events = dict((event.timestep, event) for event in self.events)
        return events

    def footprint(self, placed=True):
        """Returns a shapely geometry of the static shapes"""
        footprint = build_footprint(self, placed)
        return footprint

    def depends_on(self, mask=None):
        deps = set()
        for rule in self.rules:
            if rule.target:
                deps.add(rule.target)
        return deps

    def eval_rules(self, mask=None):
        return evaluate_rules(self, mask)

    def copy(self, session):
        """Copies the Feature and all it's related records."""

        copies = {
            'shapes': list(),
            'rules': list(),
            'conditions': list(),
        }

        for records in copies.keys():
            for record in getattr(self, records):
                copy = record
                try:
                    session.expunge(copy)
                except:
                    pass
                make_transient(copy)
                copy.id = None
                copies[records].append(copy)

        try:
            session.expunge(self)
        except:
            pass
        make_transient(self)
        self.id = None
        self.facility_id = None

        self.shapes = copies['shapes']
        self.rules = copies['rules']
        self.condition = copies['conditions']

        return self


Facility.features = relationship('Feature', order_by=Feature.id, back_populates='facility',
                                 cascade='all, delete, delete-orphan')


class Shape(Base):
    """A geometry with condtions and rules"""
    __tablename__ = 'CycSat_Shape'

    id = Column(Integer, primary_key=True)
    level = Column(Integer, default=0)
    prototype = Column(String)
    placed_wkt = Column(String)
    stable_wkt = Column(String)
    material_code = Column(Integer)
    rgb = Column(String)
    xoff = Column(Integer, default=0)
    yoff = Column(Integer, default=0)

    __mapper_args__ = {'polymorphic_on': prototype}

    feature_id = Column(Integer, ForeignKey('CycSat_Feature.id'))
    feature = relationship(Feature, back_populates='shapes')

    def add_location(self, timestep, wkt):
        loc = Location(timestep=timestep, wkt=self.placed_wkt)
        self.locations.append(loc)

    def get_rgb(self, plotting=False):
        """Returns the RGB be value as a list [RGB] which is stored as text"""
        try:
            rgb = ast.literal_eval(self.rgb)
        except:
            rgb = self.rgb

        if plotting:
            return [x / 255 for x in rgb]
        else:
            return rgb

    def geometry(self, placed=True, timestep=None):
        """Returns a shapely geometry"""

        if timestep:
            locations = [
                loc for loc in self.locations if loc.timestep == timestep]
            if locations:
                return load_wkt(locations[0].wkt)

        if not self.placed_wkt:
            geom = self.stable_wkt
        else:
            if placed:
                geom = self.placed_wkt
            else:
                geom = self.stable_wkt

        self.geo = load_wkt(geom)
        return self.geo

    def materialize(self):
        materialize(self)


Feature.shapes = relationship('Shape', order_by=Shape.id, back_populates='feature',
                              cascade='all, delete, delete-orphan')


class Location(Base):
    """The geometric/temporal record a Shape at a timestep."""
    __tablename__ = 'CycSat_Location'

    id = Column(Integer, primary_key=True)
    timestep = Column(Integer, default=0)
    wkt = Column(String)

    shape_id = Column(Integer, ForeignKey('CycSat_Shape.id'))
    shape = relationship(Shape, back_populates='locations')

    simulation_id = Column(Integer, ForeignKey('CycSat_Simulation.id'))
    simulation = relationship(Simulation, back_populates='locations')

    @property
    def geometry(self):
        return load_wkt(self.wkt)


Shape.locations = relationship('Location', order_by=Location.id, back_populates='shape',
                               cascade='all, delete, delete-orphan')
Simulation.locations = relationship('Location', order_by=Location.id, back_populates='simulation',
                                    cascade='all, delete, delete-orphan')


class Condition(Base):
    """Condition for a shape or feature to have an event (appear) in a timestep (scene)"""

    __tablename__ = 'CycSat_Condition'

    id = Column(Integer, primary_key=True)
    table = Column(String)
    oper = Column(String)
    value = Column(Integer)

    feature_id = Column(Integer, ForeignKey('CycSat_Feature.id'))
    feature = relationship(Feature, back_populates='conditions')

Feature.conditions = relationship('Condition', order_by=Condition.id, back_populates='feature',
                                  cascade='all, delete, delete-orphan')


class Rule(Base):
    """Spatial rule for where a feature or shape can appear."""

    __tablename__ = 'CycSat_Rule'

    id = Column(Integer, primary_key=True)
    oper = Column(String)  # e.g. within, disjoint, near etc.
    target = Column(Integer)
    value = Column(Integer, default=0)
    direction = Column(String)

    feature_id = Column(Integer, ForeignKey('CycSat_Feature.id'))
    feature = relationship(Feature, back_populates='rules')


Feature.rules = relationship('Rule', order_by=Rule.id, back_populates='feature',
                             cascade='all, delete, delete-orphan')


class Rule2(Base):
    """Spatial rule for where a feature or shape can appear."""

    __tablename__ = 'CycSat_Rule2'

    id = Column(Integer, primary_key=True)
    # this is the name of the function of the Rule object to apply to itself
    name = Column(String)
    target_sql = Column(Integer)
    __mapper_args__ = {'polymorphic_on': name}

    feature_id = Column(Integer, ForeignKey('CycSat_Feature.id'))
    feature = relationship(Feature, back_populates='rule2s')

Feature.rule2s = relationship('Rule2', order_by=Rule2.id, back_populates='feature',
                              cascade='all, delete, delete-orphan')


# class RuleDefinition(Rule2):
#     """The user (or default) rule function to
#     """


class Event(Base):
    """An instance of a non - static Shape at a facility for a given timestep. Modified
    by rules."""

    __tablename__ = 'CycSat_Event'

    id = Column(Integer, primary_key=True)
    timestep = Column(Integer)
    wkt = Column(String)

    feature_id = Column(Integer, ForeignKey('CycSat_Feature.id'))
    feature = relationship(Feature, back_populates='events')

    facility_id = Column(Integer, ForeignKey('CycSat_Facility.id'))
    facility = relationship(Facility, back_populates='events')

    simulation_id = Column(Integer, ForeignKey('CycSat_Simulation.id'))
    simulation = relationship(Simulation, back_populates='events')

Feature.events = relationship(
    'Event', order_by=Event.id, back_populates='feature')
Facility.events = relationship(
    'Event', order_by=Event.id, back_populates='facility')
Simulation.events = relationship('Event', order_by=Event.id, back_populates='simulation',
                                 cascade='all, delete, delete-orphan')


class Scene(Base):
    __tablename__ = 'CycSat_Scene'

    id = Column(Integer, primary_key=True)
    timestep = Column(Integer)

    facility_id = Column(Integer, ForeignKey('CycSat_Facility.id'))
    facility = relationship(Facility, back_populates='scenes')

    instrument_id = Column(Integer, ForeignKey('CycSat_Instrument.id'))
    instrument = relationship(Instrument, back_populates='scenes')

Facility.scenes = relationship(
    'Scene', order_by=Scene.id, back_populates='facility')
Instrument.scenes = relationship(
    'Scene', order_by=Scene.id, back_populates='instrument')
