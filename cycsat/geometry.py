"""
geometry.py
"""
from collections import defaultdict
from sqlalchemy import Column, Integer, String

import random
import itertools
import time

from descartes import PolygonPatch
from matplotlib import pyplot as plt

import numpy as np

from shapely.geometry import Polygon, Point, LineString, box
from shapely.wkt import loads as load_wkt
from shapely.affinity import translate as shift_shape
from shapely.affinity import rotate
from shapely.ops import cascaded_union, unary_union, polygonize


#------------------------------------------------------------------------------
# GENERAL
#------------------------------------------------------------------------------


def intersect(polygons, default=None):
    """Finds the intersection of a list of polygons.

    Keyword arguments:
    polygons -- a list of polygons
    default -- the default mask
    """

    rings = [LineString(pol.exterior.coords) for pol in polygons]
    union = unary_union(rings)
    results = [geom for geom in polygonize(union)]

    points = [poly.representative_point() for poly in results]

    # first check if one polygon conatins all the points
    for poly in polygons:
        checks = list()
        for point in points:
            checks.append(point.within(poly))
        if False not in checks:
            return poly

    final = default
    for point, result in zip(points, results):
        checks = list()
        for poly in polygons:
            checks.append(point.within(poly))
        if False in checks:
            continue
        else:
            return result
    return default


def build_geometry(Entity):
    """Builds a geometry given an instance."""
    try:
        geometry = load_wkt(Entity.geometry)
    except:
        geometry = box(0, 0, Entity.maxx, Entity.maxy)
    return geometry


def build_footprint(Entity, placed=True):
    """Returns a geometry that is the union of all a feature's static shapes."""
    archetype = Entity.__class__.__bases__[0].__name__
    if archetype == 'Facility':
        shapes = [feature.footprint()
                  for feature in Entity.features if feature.visibility == 100]
    else:
        shapes = [shape.geometry(placed=placed) for shape in Entity.shapes]
    union = cascaded_union(shapes)
    if union.__class__.__name__ == 'MultiPolygon':
        return box(union)
    return union


def posit_point(definition, attempts=1000):
    """Generates a random point given a defintion of constraints. Currently a 'mask' and an 'alignment'
    (or axis).
    """
    mask = definition['mask']
    align = definition['align']
    axis = None

    if align:
        align = align[0]
        axis = align['axis']
        value = align['value']

    x_min, y_min, x_max, y_max = mask.bounds

    for i in range(attempts):
        x = random.uniform(x_min, x_max + 1)
        y = random.uniform(y_min, y_max + 1)

        if axis == 'X':
            x = value
        if axis == 'Y':
            y = value

        posited_point = Point(x, y)

        if posited_point.within(mask):
            return posited_point

    print('point placement failed after {', attempts, '} attempts.')
    return False


def posit_point2(mask, attempts=1000):
    """Generates a random point within a mask."""
    x_min, y_min, x_max, y_max = mask.bounds

    for i in range(attempts):
        x = random.uniform(x_min, x_max + 1)
        y = random.uniform(y_min, y_max + 1)
        posited_point = Point(x, y)

        if posited_point.within(mask):
            return posited_point

    print('point placement failed after {', attempts, '} attempts.')
    return False


def line_func(line, precision=1):
    """Returns a list of coords for a staight line given end coords"""
    start, end = list(line.coords)
    m = (end[1] - start[1]) / (end[0] - start[0])
    b = start[1] - (m * start[0])
    x = np.linspace(start[0], end[0], round(line.length))
    y = (m * x) + b

    coords = list(zip(x, y))
    points = [Point(c[0], c[1]) for c in coords]

    return points


#------------------------------------------------------------------------------
# SITE PREP
#------------------------------------------------------------------------------


# def axf(m, x, b, invert=False):
#     """Returns a LineString that represents a linear function."""
#     if invert:
#         return ((-1 / m) * x) + b
#     return (m * x) + b


# # this is for creating terrain
# def site_axis(Facility):
#     """Generates a site axis."""
#     site_axis = LineString([[-maxx, maxy / 2], [maxx * 2, maxy / 2]])
#     rotate(site_axis, random.randint(-180, 180))

#     # # create a site axis
#     # site_axis = LineString([[-maxx,maxy/2],[maxx*2,maxy/2]])

#     # site_rotation = random.randint(-180,180)
#     # site_axis = rotate(site_axis,site_rotation,'center',use_radians=False)
#     # Facility.ax_angle = site_rotation

#     return site_axis

#------------------------------------------------------------------------------
# FEATURE PLACEMENT
#------------------------------------------------------------------------------

def list_bearings(Feature):
    """List the bearings of the feature (N, E, S, W) as points."""
    footprint = Feature.footprint()
    minx, miny, maxx, maxy = footprint.bounds
    halfx = (maxx - minx) / 2
    halfy = (maxy - miny) / 2

    N = Point(minx + halfx, maxy)
    E = Point(maxx, miny + halfy)
    S = Point(minx + halfx, miny)
    W = Point(minx, miny + halfy)

    return [N, E, S, W]

#------------------------------------------------------------------------------
# PLACMENT RULES (returns either a mask, position, or alignment)
#------------------------------------------------------------------------------


def within_rule(feature, target_geometry, value, *unused):
    mask = target_geometry.buffer(value)
    return {'mask': mask}


def near_rule(feature, target_geometry, value, *unused):
    """Places a feature a specified value to a target feature."""
    feature_geometry = feature.footprint(placed=False)

    cushion = 0
    threshold = 100

    # buffer the target geometry by the provided value
    inner_buffer = target_geometry.buffer(value)

    mask = feature_geometry.bounds
    diagaonal_dist = Point(mask[0:2]).distance(Point(mask[2:]))
    buffer_value = diagaonal_dist + (diagaonal_dist * cushion)
    second_buffer = inner_buffer.buffer(buffer_value)
    mask = second_buffer.difference(inner_buffer)
    return {'mask': mask}


def axis_rule(feature, target_geometry, value, direction, *unused):
    x, y = target_geometry.centroid.xy
    if direction == 'X':
        value = x[0]
    elif direction == 'Y':
        value = y[0]
    else:
        return {'align': None}
    return {'align': {'axis': direction, 'value': value}}


def rotate_rule(feature, target_geometry, value, direction, *unused):
    return {'rotate': value}


rules = {
    'WITHIN': within_rule,
    'NEAR': near_rule,
    'AXIS': axis_rule,
    'ROTATE': rotate_rule
}
