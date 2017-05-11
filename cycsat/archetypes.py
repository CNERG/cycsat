"""
archetypes.py
"""
import ast
import random
import io
from collections import defaultdict
import sys

import imageio
import tempfile

from descartes import PolygonPatch
from matplotlib import pyplot as plt

from .image import Sensor
from .geometry import build_geometry, build_footprint, near_rule, line_func
from .geometry import posit_point, rules, posit_point2, intersect

# from .laboratory import materialize

import pandas as pd
import numpy as np

import copy
import operator

from shapely.geometry import Polygon, Point, LineString
from shapely.wkt import loads as load_wkt
from shapely.ops import cascaded_union
from shapely.affinity import rotate, translate

from skimage.draw import polygon

import gdal

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
    """A possible realization of all sites and Observables in a simulation."""

    __tablename__ = 'CycSat_Build'
    id = Column(Integer, primary_key=True)
    name = Column(String)

    def assemble(self, attempts=100):
        """Assembles the build, i.e. places all the observables of all the sites."""
        for site in self.sites:
            site.place_observables(
                self.database, timestep=-1, attempts=attempts)

    def simulate(self, name='untiled', start=0, end=None):
        if not end:
            end = self.database.duration

        simulation = Simulation(name=name, start=start, end=end)

        for site in self.sites:
            if site.defined:
                print('simulating', site.AgentId)
                site.simulate(simulation, start, end)

        self.simulations.append(simulation)
        self.database.session.commit()

    def plot(self, timestep=-1, **params):
        """Plots site that meet a sql query at a given timestep

        Keyword arguments:
        timestep -- timestep to plot
        virtual -- create a virtual, internal plot (for backend use)
        """
        if len(self.sites) == 1:
            fig, axes = self.sites[0].plot(timestep=timestep)
        else:
            factors = set()
            for i in range(1, len(self.sites) + 1):
                if len(self.sites) % i == 0:
                    factors.add(i)

            # figure out the dimensions for the plot
            factors = list(factors)
            cols = factors[round(len(factors) / 2) - 1]
            rows = int(len(self.sites) / cols)

            fig, axes = plt.subplots(cols, rows)

            for ax, site in zip(axes.flatten(), self.sites):
                site.plot(ax=ax, timestep=timestep)

        if 'virtual' in params:
            plt.savefig(params['virtual'], format='png')
            return virtual

        return fig, axes


class Simulation(Base):
    """A collection of instruments."""

    __tablename__ = 'CycSat_Simulation'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    start = Column(String)
    end = Column(String)

    build_id = Column(Integer, ForeignKey('CycSat_Build.id'))
    build = relationship(Build, back_populates='simulations')

Build.simulations = relationship(
    'Simulation', order_by=Simulation.id, back_populates='build')


class Event(Base):
    """A possible realization of all sites and Observables in a simulation."""

    __tablename__ = 'CycSat_Event'
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
    min_spectrum = Column(String)
    max_spectrum = Column(String)
    prototype = Column(String)
    wkt = Column(String)

    __mapper_args__ = {'polymorphic_on': prototype}

    satellite_id = Column(Integer, ForeignKey('CycSat_Satellite.id'))
    satellite = relationship(Satellite, back_populates='instruments')

    def calibrate(self, Site):
        """Prepares an instrument to create images of a site."""

        self.Site = Site

        # for static shapes
        self.background = np.zeros((Site.maxx, Site.maxy), dtype=np.uint8)
        self.foreground = self.background

        statics = Site.timestep_shapes()
        for shape in statics:
            self.add_shape(shape)

    def add_shape(self, Shape, timestep=-1):

        if Shape.observable.visibility == 100:
            image = self.background
        else:
            image = self.foreground

        geometry = Shape.geometry(timestep=timestep)
        data = Shape.observe()
        if len(data) > 0:

            reflectance = data[(data.wavelength > self.min_spectrum) & (
                data.wavelength < self.max_spectrum)].reflectance.max()

            coords = np.array(list(geometry.exterior.coords))
            rr, cc = polygon(coords[:, 0], coords[:, 1], image.shape)
            image[rr, cc] = reflectance

    def plot(self, ax=None, timestep=-1):
        """Plots the the captured image at a given timestep."""

        self.capture(timestep)

        if ax:
            new_fig = False
        else:
            new_fig = True
            fig, ax = plt.subplots(1, 1, sharex=True, sharey=True)

        # set up the plot
        ax.set_xlim([0, self.Site.maxx])
        ax.set_ylim([0, self.Site.maxy])
        ax.set_title('Agent: ' + str(self.Site.AgentId) +
                     '\ntimestep:' + str(timestep))
        ax.set_aspect('equal')

        ax.imshow(self.foreground)

        return ax

    def capture(self, timestep=-1):
        """Adds shapes at timestep to a image"""

        # clear the memory
        self.foreground = self.background

        # add shapes from timestep
        shapes = self.Site.timestep_shapes(timestep=timestep)
        for shape in shapes:
            if shape.observable.visibility < 100:
                self.add_shape(shape, timestep=timestep)

    # def write(self, path, img_format='GTiff'):
    #     """Writes an image using GDAL

    #     Parameters
    #     ----------
    #     path: the path to write the image
    #     img_format: the GDAL format
    #     """
    #     origin = 0

    #     rows = round(self.foreground.shape[-2] / self.mmu)
    #     cols = round(self.foreground.shape[-1] / self.mmu)

    #     driver = gdal.GetDriverByName(img_format)

    #     outRaster = driver.Create(
    #         path + extensions[img_format], cols, rows, 1, gdal.GDT_Byte)
    #     outRaster.SetGeoTransform(
    #         (origin, self.mmu, 0, origin, 0, self.mmu * -1))

    #     outband = outRaster.GetRasterBand(1)
    #     if (self.mmu > 1):
    #         band_array = downscale_local_mean(
    #             self.foreground, (self.mmu, self.mmu))
    #         band_array = resize(band_array, (rows, cols), preserve_range=True)
    #     else:
    #         band_array = self.foreground

    #     outband.WriteArray(band_array)
    #     outband.FlushCache()


Satellite.instruments = relationship(
    'Instrument', order_by=Instrument.id, back_populates='satellite')


#------------------------------------------------------------------------------
# OBERVABLES
#------------------------------------------------------------------------------

class Site(Base):
    """A collection of observables on a collection of terrains."""
    __tablename__ = 'CycSat_Site'

    id = Column(Integer, primary_key=True)
    AgentId = Column(Integer)
    name = Column(String)
    maxx = Column(Integer, default=1000)
    maxy = Column(Integer, default=1000)
    defined = Column(Boolean, default=False)
    prototype = Column(String)
    template = Column(String)
    ax_angle = Column(Integer, default=0)

    __mapper_args__ = {'polymorphic_on': template}

    # __mapper_args__ = {'polymorphic_on': prototype}
    build_id = Column(Integer, ForeignKey('CycSat_Build.id'))
    build = relationship(Build, back_populates='sites')

    def bounds(self):
        geometry = build_geometry(self)
        return geometry

    def footprint(self):
        return build_footprint(self)

    def rotate(self, degrees=None):
        """Rotates all the observables of a site."""
        if not degrees:
            degrees = random.randint(-180, 180) + 0.01

        self.ax_angle = degrees

        for observable in self.observables:
            observable.rotate(degrees, by='facility')

    def center(self):
        fcenter = self.footprint().centroid
        bcenter = self.bounds().centroid

        shift_x = bcenter.x - fcenter.x
        shift_y = bcenter.y - fcenter.y

        for observable in self.observables:
            observable.shift(shift_x, shift_y)

    def axis(self):
        footprint = self.bounds()
        minx, miny, maxx, maxy = footprint.bounds
        site_axis = LineString([[-maxx, 0], [maxx * 2, 0]])
        site_axis = rotate(site_axis, self.ax_angle, center=footprint.centroid)
        return site_axis

    def dep_graph(self):
        """Returns groups of observables based on their dependencies."""
        graph = dict((f.name, f.depends_on())
                     for f in self.observables)
        name_to_instance = dict((f.name, f) for f in self.observables)

        # where to store the batches
        batches = list()

        while graph:
            # Get all observables with no dependencies
            ready = {name for name, deps in graph.items() if not deps}
            if not ready:
                msg = "Circular dependencies found!"
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

    def assemble(self, simulation=None, timestep=-1, attempts=100):
        """Assembles all the Observables of a Site according to their Rules.

        Parameters
        ----------
        timestep: the timestep of the Site to draw
        attempts: the max # of attempts to place a observable
        """
        # if timestep = -1 initialize all observables
        if timestep == -1:
            observable_ids = [
                obs.id for obs in self.observables if obs.visibility == 100]

        else:
            if not simulation:
                print('no simulation provided')
                return False

            sim_feats = [
                feat for feat in self.features if feat.simulation_id == simulation.id]

            observable_ids = set()
            features = [
                feature for feature in sim_features if feature.timestep == timestep]
            for feature in features:
                observable_ids.add(feature.observable.id)
            if not observable_ids:
                return True

        # create dependency groups
        dep_grps = self.dep_graph()

        placed_observables = list()
        for group in dep_grps:
            for observable in group:
                if observable.id not in observable_ids:
                    placed_observables.append(observable)
                    continue

                footprint = self.bounds()
                overlaps = cascaded_union([feat.footprint(timestep)
                                           for feat in placed_observables if feat.level == observable.level])

                placed = observable.place(
                    simulation, mask=overlaps, attempts=100, timestep=timestep)

                if not placed:
                    return False

                placed_observables.append(observable)

        # rotate and center
        if timestep == -1:
            self.rotate()
            self.center()

        return True

    def place_observables(self, simulation=None, timestep=-1, attempts=100):
        """Places all the observables of a site according to their rules
        and features at the provided timestep."""
        for x in range(attempts):
            result = self.assemble(
                simulation, timestep=timestep, attempts=attempts)
            if result:
                self.defined = True
                return True
            else:
                self.defined = False
                continue

    def simulate(self, simulation, start=0, end=None):
        """Evaluates the conditions for dynamic shapes at a given timestep and
        generates features. All conditions must be True in order for the feature to be
        created.

        Parameters
        ----------
        simulation: the simulation to add to
        """
        if not end:
            end = self.build.database.duration

        dynamic_observables = [
            observable for observable in self.observables if observable.visibility != 100]

        for timestep in range(start, end):

            features = list()
            for observable in dynamic_observables:
                evaluations = []
                for condition in observable.conditions:
                    qry = "SELECT Value FROM %s WHERE AgentId=%s AND Time=%s;" % (
                        condition.table, self.AgentId, timestep)
                    df = self.build.database.query(qry)
                    value = df['Value'][0]

                    if operations[condition.oper](value, condition.value):
                        evaluations.append(True)
                    else:
                        evaluations.append(False)

                if False in evaluations:
                    continue
                else:
                    if random.randint(1, 100) < observable.visibility:
                        feature = Feature(timestep=timestep)
                        observable.features.append(feature)
                        self.features.append(feature)
                        simulation.features.append(feature)
                        self.build.database.save(observable)
                    else:
                        continue

        self.place_observables(simulation, timestep=timestep)
        self.build.database.session.commit()

    def timestep_shapes(self, timestep=-1):
        """Returns the observable shapes (in level order) at a given timestep.

        Parameters:
        -----------
        timestep : integer, or None, default None
            If None, returns only statics shapes
        complete : bool, default True
            If True returns both static and dynamic observables at timestep
        """
        statics = list()
        dynamics = list()

        for obs in self.observables:
            if obs.visibility == 100:
                statics += obs.shapes

        if timestep > -1:
            features = [
                feat for feat in self.features if feat.timestep == timestep]
            if len(features) > 0:
                for feature in features:
                    dynamics += feature.observable.shapes

        shapes = statics + dynamics
        return sorted(shapes, key=lambda x: (x.observable.level, x.level))

    def plot(self, ax=None, timestep=-1, label=False, save=False, name='plot.png', virtual=None):
        """plots a site and its static observables or a timestep."""
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

        observable_ids = set()
        shapes = self.timestep_shapes(timestep)
        for shape in shapes:
            if shape.observable.visibility == 100:
                geometry = shape.geometry()
            else:
                geometry = shape.geometry(timestep=timestep)

            rgb = shape.get_rgb(plotting=True)
            patch = PolygonPatch(geometry, facecolor=rgb)
            ax.add_patch(patch)

            if label:
                observable_ids.add(shape.observable_id)

        if label:
            for observable in self.observables:
                if observable.id in observable_ids:
                    c = observable.footprint(placed=True).centroid
                    plt.text(c.x, c.y, observable.name)

        if save:
            plt.savefig(name)

        if virtual:
            plt.savefig(virtual, format='png')
            return virtual

        if new_fig:
            return fig, ax

    def gif(self, timesteps, name, fps=1):
        """plots a site and its static observables or a timestep."""
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

    def capture(self, Sensor):
        """Captures a synthetic image of the satellite at a timestep."""

Build.sites = relationship(
    'Site', order_by=Site.id, back_populates='build')


class Observable(Base):
    """Collection of shapes"""

    __tablename__ = 'CycSat_Observable'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    visibility = Column(Integer, default=100)
    consistent = Column(Boolean, default=True)
    prototype = Column(String)
    level = Column(Integer, default=0)
    rotation = Column(Integer, default=0)

    __mapper_args__ = {'polymorphic_on': prototype}

    site_id = Column(Integer, ForeignKey('CycSat_Site.id'))
    site = relationship(Site, back_populates='observables')

    def appears(self, timestep=-1):
        """Gets the shapes of this observable at a supplied timestep.
        """
        features = [feat for feat in self.features if feat.timestep == timestep]
        if features:
            return True
        else:
            return False

    def sorted_features(self):
        """Returns a sorted list (by timestep) of features."""
        features = dict((feature.timestep, feature)
                        for feature in self.features)
        return features

    def footprint(self, timestep=-1):
        """Returns a shapely geometry of the static shapes"""
        footprint = build_footprint(self, timestep)
        return footprint

    def rotate(self, degrees, timestep=-1, by='itself'):
        if by == 'facility':
            center = self.site.bounds().centroid
        else:
            center = 'center'
        if self.name != 'land':
            self.rotation = degrees
            for shape in self.shapes:
                shape.rotate(degrees=degrees, timestep=timestep, center=center)

    def shift(self, shift_x, shift_y, timestep=-1):
        if self.name != 'land':

            for shape in self.shapes:
                shape.shift(shift_x, shift_y, timestep=timestep)

    def morph(self, Simulator, timestep=-1):
        """Runs a observable's transform rules that modify it's shape inplace."""
        mods = [rule.run(Simulator, timestep=timestep)
                for rule in self.rules if rule.kind == 'transform']
        return True

    def depends_on(self):
        all_deps = set()
        for rule in self.rules:
            deps = rule.depends_on()
            for d in deps['name'].tolist():
                all_deps.add(d)
        return all_deps

    def place(self, simulation, mask=None, timestep=-1, rand=True, location=False, attempts=100):
        """Places a observable within a geometry and checks typology of shapes

        Parameters
        ----------
        bounds: containing bounds
        random: if 'True', placement is random, else Point feaure is required
        location: centroid location to place self
        attempts: the maximum number attempts to be made
        build: draws from the shapes stable_wkt
        """
        # the center for the site for a center point for rotation
        center = self.site.bounds().centroid

        if self.name == 'land':
            return True

            # evalute the rules of the observable to determine the mask
        results = self.evaluate_rules(
            simulation, timestep=timestep, overlaps=mask)

        if not results['place']:
            print('no place')
            return False

        for i in range(attempts):
            posited_point = posit_point2(results['place'])
            if not posited_point:
                return False

            typology_checks = list()
            for shape in self.shapes:
                loc = shape.place(posited_point, timestep=timestep)
                typology_checks.append(
                    loc.geometry.within(results['restrict']))

            if False not in typology_checks:
                self.site.build.database.session.commit()
                # self.morph(simulation, timestep)
                return True

        # ax = plt.subplot(111)
        # ax.set_xlim([0, self.site.maxx])
        # ax.set_ylim([0, self.site.maxy])

        # ax.add_patch(PolygonPatch(results['restrict'], alpha=0.5))
        # ax.add_patch(PolygonPatch(
        #     results['place'], facecolor='red', alpha=0.5))

        # ax.add_patch(PolygonPatch(
        #     loc.geometry, facecolor='green', alpha=0.5))

        # print(results['place'])
        print(self.name, 'placement failed after {', attempts, '} attempts.')
        # sys.exit()

        return False

    def evaluate_rules(self, simulation, timestep=-1, mask=None, overlaps=None):
        """Evaluates a a observable's rules and returns instructions
        for drawing that observable.

        Parameters
        ----------
        types: the types of rules to evaluate
        mask: the mask of possible areas
        """
        if not mask:
            mask = self.site.bounds()

        restrict = list()
        place = list()

        rules = [rule for rule in self.rules if rule.kind != 'transform']

        for rule in rules:
            result = rule.run(simulation, timestep=timestep)
            if rule.kind == 'restrict':
                restrict.append(result)
                place.append(result)

            if rule.kind == 'place':
                place.append(result)

        results = {
            'restrict': intersect(restrict, mask),
            'place': intersect(place, mask)
        }

        if overlaps:
            if results['restrict']:
                results['restrict'] = results['restrict'].difference(overlaps)
            if results['place']:
                results['place'] = results['place'].difference(overlaps)

        return results


Site.observables = relationship('Observable', order_by=Observable.id, back_populates='site',
                                cascade='all, delete, delete-orphan')


class Shape(Base):
    """A geometry with condtions and rules"""
    __tablename__ = 'CycSat_Shape'

    id = Column(Integer, primary_key=True)
    level = Column(Integer, default=0)
    prototype = Column(String)
    wkt = Column(String)
    material_code = Column(Integer)
    rgb = Column(String)
    xoff = Column(Integer, default=0)
    yoff = Column(Integer, default=0)

    __mapper_args__ = {'polymorphic_on': prototype}

    observable_id = Column(Integer, ForeignKey('CycSat_Observable.id'))
    observable = relationship(Observable, back_populates='shapes')

    def add_loc(self, timestep=-1, wkt=None):
        loc = [loc for loc in self.locations if loc.timestep == timestep]
        if loc:
            if wkt:
                loc[0].wkt = wkt
            else:
                return loc[0]

        if wkt:
            loc = Location(timestep=timestep, wkt=wkt)
            self.locations.append(loc)
            return loc

        else:
            loc = [loc for loc in self.locations if loc.timestep == -1]
            if loc:
                loc = Location(timestep=timestep, wkt=loc[0].wkt)
            else:
                loc = Location(timestep=timestep, wkt=self.wkt)
            self.locations.append(loc)
            return loc

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

    def geometry(self, timestep=-1, placement=False):
        """Returns a shapely geometry"""

        if self.observable.visibility == 100 or placement:
            if self.observable.consistent:
                loc = [loc for loc in self.locations if loc.timestep == -1]
                if loc:
                    return loc[0].geometry
                else:
                    return load_wkt(self.wkt)

        loc = [loc for loc in self.locations if loc.timestep == timestep]
        if loc:
            return loc[0].geometry
        else:
            return load_wkt(self.wkt)

    def materialize(self):
        materialize(self)

    def place(self, placement, timestep=-1):  # , rotation=0):
        """Places a self to a coordinate position.

        Parameters
        ----------
        build: draws from the shapes the stable_wkt rather than placed
        """
        loc = self.add_loc(timestep)

        placed_x = placement.coords.xy[0][0]
        placed_y = placement.coords.xy[1][0]

        geometry = loc.geometry

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

        loc.wkt = translate(geometry, xoff=shift_x, yoff=shift_y).wkt
        return loc

    def rotate(self, degrees, center='center', timestep=-1):
        loc = self.add_loc(timestep)
        loc.wkt = rotate(
            loc.geometry, degrees, origin=center, use_radians=False).wkt
        return loc

    def shift(self, shift_x, shift_y, timestep=-1):
        loc = self.add_loc(timestep)
        loc.wkt = translate(loc.geometry, xoff=shift_x, yoff=shift_y).wkt
        return loc

    def observe(self):
        """Returns a dataframe of wavelength and reflectance values."""
        if self.materials:
            return self.materials[0].observe()
        else:
            try:
                rgb = self.get_rgb()
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


Observable.shapes = relationship('Shape', order_by=Shape.id, back_populates='observable',
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
    """Condition for a shape or observable to have an feature (appear) in a timestep (scene)"""

    __tablename__ = 'CycSat_Condition'

    id = Column(Integer, primary_key=True)
    table = Column(String)
    oper = Column(String)
    value = Column(Integer)

    observable_id = Column(Integer, ForeignKey('CycSat_Observable.id'))
    observable = relationship(Observable, back_populates='conditions')

Observable.conditions = relationship('Condition', order_by=Condition.id, back_populates='observable',
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
    """Spatial rule for where a observable or shape can appear."""

    __tablename__ = 'CycSat_Rule'

    id = Column(Integer, primary_key=True)
    # this is the name of the function of the Rule object to apply to itself
    name = Column(String)
    kind = Column(String)
    pattern = Column(String)
    value = Column(String)

    __mapper_args__ = {'polymorphic_on': name}

    observable_id = Column(Integer, ForeignKey('CycSat_Observable.id'))
    observable = relationship(Observable, back_populates='rules')

    def depends_on(self, obj=False):
        """Finds any observables at the same Site that match the
        pattern of the rule"""
        df = self.observable.site.build.database.Observable()
        df = df[(df.name.str.startswith(self.pattern)) & (
            df.site_id == self.observable.site_id)]
        if obj:
            return df['obj'].tolist()
        return df

    @property
    def database(self):
        return self.observable.site.build.database

Observable.rules = relationship('Rule', order_by=Rule.id, back_populates='observable',
                                cascade='all, delete, delete-orphan')


class Feature(Base):
    """An instance of a non - static Shape at a site for a given timestep. Modified
    by rules."""

    __tablename__ = 'CycSat_Feature'

    id = Column(Integer, primary_key=True)
    timestep = Column(Integer)
    wkt = Column(String)

    observable_id = Column(Integer, ForeignKey('CycSat_Observable.id'))
    observable = relationship(Observable, back_populates='features')

    site_id = Column(Integer, ForeignKey('CycSat_Site.id'))
    site = relationship(Site, back_populates='features')

    simulation_id = Column(Integer, ForeignKey('CycSat_Simulation.id'))
    simulation = relationship(Simulation, back_populates='features')

Observable.features = relationship(
    'Feature', order_by=Feature.id, back_populates='observable')
Site.features = relationship(
    'Feature', order_by=Feature.id, back_populates='site')
Simulation.features = relationship('Feature', order_by=Feature.id, back_populates='simulation',
                                   cascade='all, delete, delete-orphan')
