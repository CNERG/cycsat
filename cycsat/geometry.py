#------------------------------------------------------------------------------
# GEOMETRY FUNCTIONS
#------------------------------------------------------------------------------
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
from shapely.ops import cascaded_union

#------------------------------------------------------------------------------
# GENERAL
#------------------------------------------------------------------------------


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
    """Generates a random point given a defintion of contraints. Currently a 'mask' and an 'alignment'
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


def posit_point2(bounds, attempts=1000):
    """Generates a random point within a mask."""
    x_min, y_min, x_max, y_max = mask.bounds

    for i in range(attempts):
        x = random.uniform(x_min, x_max + 1)
        y = random.uniform(y_min, y_max + 1)
        posited_point = Point(x, y)

        if posited_point.within(mask):
            return posited_point

    print('point placement failed after {', attempts, '} attempts.')
    return Point(0, 0)


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
    """List the bearings of the feature (N,E,S,W) as points."""
    footprint = Feature.footprint()
    minx, miny, maxx, maxy = footprint.bounds
    halfx = (maxx - minx) / 2
    halfy = (maxy - miny) / 2

    N = Point(minx + halfx, maxy)
    E = Point(maxx, miny + halfy)
    S = Point(minx + halfx, miny)
    W = Point(minx, miny + halfy)

    return [N, E, S, W]


# def evaluate_rules(Feature, mask=None):
#     """Evaluates a a feature's rules and returns instructions
#     for drawing that feature.

#     Keyword arguments:
#     mask -- the mask of possible areas
#     """
#     results = defaultdict(list)

#     for rule in Feature.rules:
#         direction = rule.direction
#         value = rule.value
#         event = None

#         # get all the features 'targeted' in the rule
#         targets = [feature for feature in Feature.facility.features
#                    if (feature.name == rule.target)]

#         # use sql instead?

#         # search the rules of the targets
#         target_rules = list()
#         for target in targets:
#             target_rules += target.rules

#         # if the rotate rule has targets use them to align
#         if rule.oper == 'ROTATE':
#             rotation = [target.rotation for target in targets]
#             if rotation:
#                 value = rotation[0]
#             else:
#                 value = rule.value
#         else:
#             value = rule.value

#         # # if the rule is self-targeted get the event for placement info
#         # if rule.target == "%self%":
#         #     lag = 0
#         #     if '%lag' in rule.value:
#         #         lag = rule.value.split('=')[-1]
#         #     value = rule.value - lag
#         #     event = rule.feature.sorted_events()[value]

#         # otherwised merge all the targets
#         target_footprints = [target.footprint(
#             placed=True) for target in targets]
#         target_geometry = cascaded_union(target_footprints)

#         if value is None:
#             value = 0
#         result = rules[rule.oper](
#             Feature, target_geometry, value, direction, event)

#         for kind, data in result.items():
#             results[kind].append(data)

#     # combines the results of all the rules
#     if results['mask']:
#         combined_mask = mask
#         for m in results['mask']:
#             combined_mask = combined_mask.intersection(m)
#         results['mask'] = combined_mask
#     else:
#         results['mask'] = mask

#     return results


def rotate_feature(Feature, rotation, center='center'):
    """Rotates a feature."""

    for shape in Feature.shapes:
        geometry = shape.geometry()
        rotated = rotate(geometry, rotation, origin=center, use_radians=False)
        shape.placed_wkt = rotated.wkt


def place(Shape, placement, build=False, center=None, rotation=0):
    """Places a Shape to a coordinate position.

    Keyword arguments:
    build -- draws from the shapes the stable_wkt rather than placed 
    """
    placed_x = placement.coords.xy[0][0]
    placed_y = placement.coords.xy[1][0]

    if build:
        geometry = Shape.geometry(placed=False)
    else:
        geometry = Shape.geometry(placed=True)

    shape_x = geometry.centroid.coords.xy[0][0]
    shape_y = geometry.centroid.coords.xy[1][0]

    try:
        xoff = Shape.xoff
        yoff = Shape.yoff
    except:
        xoff = 0
        yoff = 0

    shift_x = placed_x - shape_x + xoff
    shift_y = placed_y - shape_y + yoff

    shifted = shift_shape(geometry, xoff=shift_x, yoff=shift_y)

    if rotation != 0:
        shifted = rotate(shifted, rotation, origin='center', use_radians=False)
    Shape.placed_wkt = shifted.wkt

    return Shape


def place_feature(Feature, mask=None, build=False, rand=True, location=False, attempts=100):
    """Places a feature within a geometry and checks typology of shapes

    Keyword arguments:
    Feature -- feature to place
    bounds -- containing bounds
    random -- if 'True', placement is random, else Point feaure is required
    location -- centroid location to place Feature
    attempts -- the maximum number attempts to be made
    build -- draws from the shapes stable_wkt
    """
    # the center for the facility for a center point for rotation
    center = Feature.facility.bounds().centroid

    # evalute the rules of the facility
    definition = Feature.eval_rules(mask=mask)
    mask = definition['mask']

    if 'rotate' in definition:
        rotate = definition['rotate'][0]
    else:
        rotate = random.randint(-180, 180)

    Feature.rotation = rotate

    for i in range(attempts):
        posited_point = posit_point(definition)
        if not posited_point:
            return False

        placed_shapes = list()
        typology_checks = list()
        for shape in Feature.shapes:

            place(shape, posited_point, build, center, rotation=rotate)
            placement = shape.geometry()

            placed_shapes.append(placement)
            typology_checks.append(placement.within(mask))

        if False not in typology_checks:
            Feature.wkt = cascaded_union(placed_shapes).wkt
            return True

    print(Feature.name, 'placement failed after {', attempts, '} attempts.')
    return False


# def placement_bounds(facility_footprint, placed_features):
#     """Takes a list of placed features and a facility footprint
#     and generates a geometry of all possible locations to be placed."""

#     placed_footprints = list()
#     for feature in placed_features:
#         feature_footprint = build_footprint(feature)
#         placed_footprints.append(feature_footprint)

#     # this needs to discriminate between within features and not

#     union_footprints = cascaded_union(placed_footprints)
#     bounds = facility_footprint.difference(union_footprints)

#     return bounds


#------------------------------------------------------------------------------
# PLACMENT RULES (returns either a mask, position, or alignment)
#------------------------------------------------------------------------------

# rules should take features, targets (or shapes) (other features), and a value

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
