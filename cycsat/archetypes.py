"""
archetypes.py
"""
import ast
import random
import io
from collections import defaultdict

import imageio
import tempfile

from descartes import PolygonPatch
from matplotlib import pyplot as plt

from .image import Sensor
from .geometry import build_geometry, build_footprint, near_rule, line_func
from .geometry import posit_point, rules, posit_point2

# from .laboratory import materialize

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

    def assemble(self, Simulator, attempts=100):
        """Assembles the build, i.e. places all the features of all the facilities."""
        for facility in self.facilities:
            facility.place_features(Simulator, timestep=-1, attempts=attempts)


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

class Facility(Base):
    """A collection of features on a collection of terrains."""
    __tablename__ = 'CycSat_Facility'

    id = Column(Integer, primary_key=True)
    AgentId = Column(Integer)
    name = Column(String)
    maxx = Column(Integer, default=1000)
    maxy = Column(Integer, default=1000)
    defined = Column(Boolean, default=False)
    prototype = Column(String)
    template = Column(String)
    # geometry = Column(String)

    __mapper_args__ = {'polymorphic_on': template}

    # __mapper_args__ = {'polymorphic_on': prototype}
    build_id = Column(Integer, ForeignKey('CycSat_Build.id'))
    build = relationship(Build, back_populates='facilities')

    def bounds(self):
        geometry = build_geometry(self)
        return geometry

    def footprint(self):
        return build_footprint(self)

    def rotate(self, degrees=None):
        """Rotates all the features of a facility."""
        if not degrees:
            degrees = random.randint(-180, 180) + 0.01

        for feature in self.features:
            rotate_feature(feature, degrees, self.bounds().centroid)

    def axis(self):
        footprint = self.bounds()
        minx, miny, maxx, maxy = footprint.bounds
        site_axis = LineString([[-maxx, 0], [maxx * 2, 0]])
        #site_axis = rotate(site_axis, self.ax_angle)
        return site_axis

    def dep_graph(self, Simulator):
        """Returns groups of features based on their dependencies."""
        graph = dict((f.name, f.depends_on(Simulator)) for f in self.features)
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

    def assemble(self, Simulator, timestep=-1, attempts=100):
        """Assembles all the Features of a Facility according to their Rules.

        Keyword arguments:
        timestep -- the timestep of the Facility to draw
        attempts -- the max # of attempts to place a feature
        """
        # determine which features to draw (by timestep)
        if timestep > -1:
            feature_ids = set()
            events = [
                event for event in self.events if event.timestep == timestep]
            for event in events:
                feature_ids.add(event.feature.id)
            if not feature_ids:
                return True
        else:
            feature_ids = [
                feature.id for feature in self.features if feature.visibility == 100]

        # create dependency groups
        dep_grps = self.dep_graph(Simulator)

        placed_features = list()

        for group in dep_grps:
            for feature in group:
                if feature.id not in feature_ids:
                    placed_features.append(feature)
                    continue

                footprint = self.bounds()

                # find geometry of features that could overlap (share the same
                # z-level)
                overlaps = [feat.footprint()
                            for feat in placed_features if feat.level == feature.level]
                overlaps = cascaded_union(overlaps)

                # mask out placed features that could overlap
                footprint = footprint.difference(overlaps)

                # place the feature
                placed = feature.place_feature(Simulator,
                                               mask=footprint, attempts=attempts, build=True)

                # if placement fails, the assemble fails
                if not placed:
                    return False

                placed_features.append(feature)
                for shape in feature.shapes:
                    shape.add_location(timestep, shape.placed_wkt)

        # if no Features fail then assembly succeeds
        return True

    def place_features(self, Simulator, timestep=-1, attempts=100):
        """Places all the features of a facility according to their rules
        and events at the provided timestep."""
        for x in range(attempts):
            result = self.assemble(Simulator, timestep, attempts)
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
                #print(feature.name, timestep, 'False')
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

        self.place_features(Simulator, timestep=timestep)
        Simulator.save(self)

# this needs to be fixed
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
    level = Column(Integer)
    rotation = Column(Integer, default=0)

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

    # def depends_on(self, mask=None):
    #     deps = set()
    #     for rule in self.rules:
    #         if rule.target:
    #             deps.add(rule.target)
    #     return deps

    def depends_on(self, Simulator):
        all_deps = set()
        for rule in self.rules:
            deps = rule.depends_on(Simulator)
            for d in deps['name'].tolist():
                all_deps.add(d)
        return all_deps

    def place_feature(self, Simulator, mask=None, build=False, rand=True, location=False, attempts=100):
        """Places a feature within a geometry and checks typology of shapes

        Keyword arguments:
        self -- feature to place
        bounds -- containing bounds
        random -- if 'True', placement is random, else Point feaure is required
        location -- centroid location to place self
        attempts -- the maximum number attempts to be made
        build -- draws from the shapes stable_wkt
        """
        # the center for the facility for a center point for rotation
        center = self.facility.bounds().centroid

        # if building set reset the placement geometry
        if build:
            for shape in self.shapes:
                shape.placed_wkt = shape.stable_wkt

        # evalute the rules of the feature to determine the mask
        results = self.evaluate_rules(Simulator, mask=mask)
        mods = [rule.run(Simulator)
                for rule in self.rules if rule.kind == 'transform']

        for i in range(attempts):
            posited_point = posit_point2(results['union'])
            if not posited_point:
                return False

            placed_shapes = list()
            typology_checks = list()
            for shape in self.shapes:

                shape.place(posited_point, build, center)
                placement = shape.geometry()

                placed_shapes.append(placement)
                typology_checks.append(placement.within(results['rpl']))

            if False not in typology_checks:
                self.wkt = cascaded_union(placed_shapes).wkt
                Simulator.save(self)
                return True

        print(self.name, 'placement failed after {', attempts, '} attempts.')
        return False

    def evaluate_rules(self, Simulator, kinds=['rpl', 'pl'], mask=None):
        """Evaluates a a feature's rules and returns instructions
        for drawing that feature.

        Keyword arguments:
        types -- the types of rules to evaluate
        mask -- the mask of possible areas
        """
        if not mask:
            mask = self.facility.bounds()

        union_mask = [mask]
        results = dict()

        for kind in kinds:
            # the default of rpl (restrict) rules is the mask
            evals = [rule.run(Simulator)
                     for rule in self.rules if rule.kind == kind]

            if len(evals) == 0:
                results[kind] = mask
            elif len(evals) == 1:
                results[kind] = evals[0]
            else:
                results[kind] = evals[0]
                for e in evals[1:]:
                    results[kind] = results[kind].intersection(e)
            union_mask += [results[kind]]

        results['union'] = cascaded_union(union_mask)
        return results


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

    def place(self, placement, build=False, center=None):  # , rotation=0):
        """Places a self to a coordinate position.

        Keyword arguments:
        build -- draws from the shapes the stable_wkt rather than placed
        """
        placed_x = placement.coords.xy[0][0]
        placed_y = placement.coords.xy[1][0]

        geometry = self.geometry(placed=True)

        shape_x = geometry.centroid.coords.xy[0][0]
        shape_y = geometry.centroid.coords.xy[1][0]

        try:
            xoff = self.xoff
            yoff = self.yoff
        except:
            xoff = 0
            yoff = 0

        shift_x = placed_x - shape_x + xoff
        shift_y = placed_y - shape_y + yoff

        shifted = translate(geometry, xoff=shift_x, yoff=shift_y)
        self.placed_wkt = shifted.wkt

        return self


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


class Material(Base):
    """A material of a shape. Shapes can have many materials in many mass quantitites."""

    __tablename__ = 'CycSat_Material'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    mass = Column(Integer, default=0)

    shape_id = Column(Integer, ForeignKey('CycSat_Shape.id'))
    shape = relationship(Shape, back_populates='materials')

    __mapper_args__ = {'polymorphic_on': name}

    def plot(self):
        sample = self.measure()

        std = sample.describe().reflectance.loc['std']
        top = sample.describe().reflectance.loc['75%']
        bottom = sample.describe().reflectance.loc['25%']

        df = sample[(sample.reflectance > bottom) & (sample.reflectance < top)]
        if len(df) == 0:
            df = sample
        ax = df.plot(x='wavelength', y='reflectance')
        ax.set_title(self.name)
        return ax

    def measure(self):
        try:
            return self.observe()

        except:
            try:
                rgb = self.shape.get_rgb()
            except:
                rgb = [random.randint(0, 255) for i in range(3)]

            wavelength = (np.arange(281) / 100) + 0.20
            reflectance = np.zeros(281)
            reflectance[(wavelength >= 0.64) & (wavelength <= 0.67)] = rgb[0]
            reflectance[(wavelength >= 0.53) & (wavelength <= 0.59)] = rgb[1]
            reflectance[(wavelength >= 0.45) & (wavelength <= 0.51)] = rgb[2]
            std = np.zeros(281)

            return pd.DataFrame({'wavelength': wavelength,
                                 'reflectance': reflectance,
                                 'std': std})

Shape.materials = relationship('Material', order_by=Material.id, back_populates='shape',
                               cascade='all, delete, delete-orphan')


class Rule(Base):
    """Spatial rule for where a feature or shape can appear."""

    __tablename__ = 'CycSat_Rule'

    id = Column(Integer, primary_key=True)
    # this is the name of the function of the Rule object to apply to itself
    name = Column(String)
    kind = Column(String)
    pattern = Column(String)
    value = Column(String)

    __mapper_args__ = {'polymorphic_on': name}

    feature_id = Column(Integer, ForeignKey('CycSat_Feature.id'))
    feature = relationship(Feature, back_populates='rules')

    def depends_on(self, Simulator):
        """Finds any features at the same Facility that match the
        pattern of the rule"""
        # should use REGEX
        df = Simulator.Feature()
        df = df[(df.name.str.startswith(self.pattern)) & (
            df.facility_id == self.feature.facility_id)]
        return df

Feature.rules = relationship('Rule', order_by=Rule.id, back_populates='feature',
                             cascade='all, delete, delete-orphan')


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


# class Scene(Base):
#     __tablename__ = 'CycSat_Scene'

#     id = Column(Integer, primary_key=True)
#     timestep = Column(Integer)

#     facility_id = Column(Integer, ForeignKey('CycSat_Facility.id'))
#     facility = relationship(Facility, back_populates='scenes')

#     instrument_id = Column(Integer, ForeignKey('CycSat_Instrument.id'))
#     instrument = relationship(Instrument, back_populates='scenes')

# Facility.scenes = relationship(
#     'Scene', order_by=Scene.id, back_populates='facility')
# Instrument.scenes = relationship(
#     'Scene', order_by=Scene.id, back_populates='instrument')
