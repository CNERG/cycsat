"""
geometry.py
"""
from collections import defaultdict
import random
import itertools
import time
import itertools
import math
import os

from descartes import PolygonPatch
from matplotlib import pyplot as plt

import numpy as np

import geopandas as gpd

from shapely.geometry import Polygon, Point, LineString, box
from shapely.wkt import loads as load_wkt
from shapely.affinity import translate
from shapely.affinity import rotate
from shapely.affinity import scale
from shapely.ops import cascaded_union, unary_union, polygonize

DIR = os.path.dirname(__file__) + '/'
FPT_DIR = DIR + '/data/footprints/'


def LoadFootprints(library, size):
    df = gpd.read_file(FPT_DIR + library + '.shp')
    df = df.assign(sort_area=df.area)
    df = df.sort_values('sort_area')
    df = df.tail(size)
    df = df.to_crs({'init': 'epsg:3857'})
    geos = df.geometry.apply(shift_geometry)
    return geos


def relative_position(mask, x, y, padding=10):

    minx, miny, maxx, maxy = container.bounds

    width = (maxx - minx) * x
    length = (maxy - miny) * y

    return Point(width, length).buffer(padding)


def grid(agent, grid_size=1, buffer=10):
    minx, miny, maxx, maxy = agent.geometry.bounds
    grid_size = grid_size + 2

    x = np.linspace(minx, maxx, num=grid_size)[1:-1]
    y = np.linspace(miny, maxy, num=grid_size)[1:-1]

    c = list(itertools.product(x, y))
    return [Point(i[0], i[1]).buffer(buffer) for i in c]


def intersect(polygons, default=None):
    """Finds the intersection of a list of polygons.

    Keyword arguments:
    polygons -- a list of polygons
    default -- the default mask
    """
    if len(polygons) == 0:
        return default
    if len(polygons) == 1:
        return polygons[0]

    results = [poly1.intersection(poly2) for poly1, poly2 in itertools.combinations(
        polygons, 2) if poly1.intersects(poly2)]

    # if there is more than one result try again
    if len(results) > 1:
        results = [poly1.intersection(poly2) for poly1, poly2 in itertools.combinations(
            results, 2) if poly1.intersects(poly2)]

    points = [poly.representative_point() for poly in results]

    canidates = list()
    for point, result in zip(points, results):
        checks = list()
        for poly in polygons:
            checks.append(point.within(poly))
        if False in checks:
            continue
        else:
            canidates.append(result)
    if canidates:
        return cascaded_union(canidates)

    return False


def posit_point(mask, attempts=1000):
    """Generates a random point within a mask."""
    x_min, y_min, x_max, y_max = mask.bounds

    for i in range(attempts):
        x = random.uniform(x_min, x_max + 1)
        y = random.uniform(y_min, y_max + 1)
        posited_point = Point(x, y)

        if posited_point.within(mask):
            return posited_point


def calulate_shift(point1, point2):

    if point1.x > point2.x:
        xdir = -1
    else:
        xdir = 1
    if point1.y > point2.y:
        ydir = -1
    else:
        ydir = 1

    xdist = abs((point1.x - point2.x))
    ydist = abs((point1.y - point2.y))

    return xdist * xdir, ydist * ydir


def shift_geometry(geometry, endpoint=(0, 0)):
    endpoint = Point(endpoint)
    xoff, yoff = calulate_shift(geometry.centroid, endpoint)
    new_geometry = translate(geometry, xoff, yoff)
    return new_geometry


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


def rescale(parent, child, ratio=0.25):
    """Rescales a child agent to be a ratio of the parent's width."""

    pminx, pminy, pmaxx, pmaxy = parent.geometry.bounds
    cminx, cminy, cmaxx, cmaxy = child.geometry.bounds
    adjust_width = (pmaxx - pminx) * ratio
    factor = adjust_width / (cmaxx - cminx)
    child.geometry = scale(child.geometry, xfact=factor, yfact=factor)
