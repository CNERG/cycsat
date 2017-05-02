"""
terrain.py
"""
import numpy as np
import math
import random

import os
from PIL import Image, ImageDraw
import bisect

from cycsat.archetypes import Shape, Rule, Base
from cycsat.image import write_array

from osgeo import ogr, gdal, osr
from geopandas import gpd

from shapely.geometry import Polygon, Point, LineString, box
from shapely.ops import cascaded_union, unary_union
from shapely.ops import polygonize

#------------------------------------------------------------------------------
# TOOLS
#------------------------------------------------------------------------------


def list_bearings(landscape):
    """List the bearings of the feature (N, E, S, W) as points."""

    minx, miny, maxx, maxy = landscape.bounds
    halfx = (maxx - minx) / 2
    halfy = (maxy - miny) / 2

    N = Point(minx + halfx, maxy)
    E = Point(maxx, miny + halfy)
    S = Point(minx + halfx, miny)
    W = Point(minx, miny + halfy)

    return [N, E, S, W]


#------------------------------------------------------------------------------
# LANDSCAPE GENERATORS
#------------------------------------------------------------------------------

def simple_land(maxx, maxxy, r=1.5):
    """Takes the dimensions of a site and returns two shapes: water and land."""
    site = box(0, 0, maxx, maxxy)
    N, E, S, W = list_bearings(site)
    Y = random.choice([N, S])
    X = random.choice([E, W])
    points = sorted([[X.x, X.y], [Y.x, Y.y]], key=lambda x: x[0])

    coast_pts = midpoint_displacement(points[0], points[1], r)
    coastline = LineString(coast_pts)
    union = unary_union([LineString(list(site.exterior.coords)), coastline])

    land = sorted([geom for geom in polygonize(union)], key=lambda x: x.area)
    return Shape(wkt=land[-2].wkt, rgb='[0,0,255]')

# def simple(width, length):
#     """Creates a simple land and water terrain returns terrain shapes"""
#     n = math.ceil(math.log(width, 2))
#     data = mpd(n)
#     terrain = data[0:width, 0:length]

#     mask = np.where(terrain < terrain.mean(), 1, 0)

#     # create temporary storage names
#     out_number = str(np.random.randint(low=100000, high=999999))
#     out_raster = 'temp/' + out_number
#     out_shp = 'temp/' + out_number + '.shp'

#     # write out a raster file
#     write_array(mask, out_raster)
#     ds = gdal.Open(out_raster + '.tif')
#     band = ds.GetRasterBand(1)

#     drv = ogr.GetDriverByName('ESRI Shapefile')
#     out = drv.CreateDataSource(out_shp)
#     out_layer = out.CreateLayer('terrains', srs=None)

#     fd = ogr.FieldDefn('DN', ogr.OFTInteger)
#     out_layer.CreateField(fd)

#     gdal.Polygonize(band, None, out_layer, 0, [], callback=None)
#     out = None

#     gdf = gpd.read_file(out_shp)
#     gdf['area'] = gdf.area

#     land = Shape(stable_wkt=gdf.sort_values('area', ascending=False).iloc[0]['geometry'].wkt,
#                  level=0)

#     water_shapes = list()
#     water_bodies = gdf.sort_values('area', ascending=False).iloc[
#         1:]['geometry'].tolist()
#     for body in water_bodies:
#         water_shape = Shape(stable_wkt=body.wkt, level=0)
#         water_shapes.append(water_shape)

#     return gdf  # [land]+water_shapes


# =============================================================================
# Terrain generation: Mid-point distance replacement
# =============================================================================

def get_corners(array):
    """Returns the corners of an array."""
    corners = array[tuple(slice(None, None, j - 1) for j in array.shape)]
    return corners


def jitter(x, jit):
    noise = np.random.normal(0, jit)
    return int(x + noise)


def init_corners(array):
    """Sets the corners of an array to a random value"""
    corners = get_corners(array)
    corners += np.random.randint(0, 100, (2, 2))
    return array


def midpoints(array, jit):
    """Sets the edges to the mean of the corners"""
    midpoint = int(array.shape[0] / 2)
    corners = get_corners(array)

    array[0, midpoint] = jitter(corners[0, :].mean(), jit=jit)
    array[midpoint, -1] = jitter(corners[-1, :].mean(), jit=jit)
    array[-1, midpoint] = jitter(corners[:, -1].mean(), jit=jit)
    array[midpoint, 0] = jitter(corners[:, 0].mean(), jit=jit)
    array[midpoint, midpoint] = jitter(corners.mean(), jit=jit)

    return array


def mpd(n=3, jit=0):
    """Midpoint distance replacement"""

    size = (2**n) + 1
    heightmap = np.zeros((size, size))

    # initialize corners and midpoints (pass 1)
    init_corners(heightmap)
    midpoints(heightmap, jit)

    slices = nested_quarters(n, heightmap)

    for level in sorted(slices):
        for array in sorted(slices[level]):
            midpoints(slices[level][array], jit)

    return heightmap


def nested_quarters(n, array):
    """
    """
    iterations = n - 2
    slices = dict()

    # first iteration
    targets = quarter_array(array)
    slices[0] = targets

    # following iterations
    for i in range(iterations):
        target = i
        slices[target + 1] = dict()
        for array in slices[target]:
            quarters = quarter_array(slices[target][array])
            for quarter in quarters:
                slices[target + 1][array + quarter] = quarters[quarter]

    return slices


def quarter_array(array):
    """Divides an array into quarters and returns a dictionary of views"""
    spread = int(array.shape[0] / 2) + 1

    views = dict()
    views['A'] = array[0:spread, 0:spread]
    views['B'] = array[0:spread, spread - 1:(spread * 2) - 1]
    views['C'] = array[spread - 1:(spread * 2) - 1, 0:spread]
    views['D'] = array[
        spread - 1:(spread * 2) - 1, spread - 1:(spread * 2) - 1]

    return views


# Iterative midpoint vertical displacement
def midpoint_displacement(start, end, roughness, vertical_displacement=None,
                          num_of_iterations=8):
    """
    Given a straight line segment specified by a starting point and an endpoint
    in the form of [starting_point_x, starting_point_y] and [endpoint_x, endpoint_y],
    a roughness value > 0, an initial vertical displacement and a number of
    iterations > 0 applies the  midpoint algorithm to the specified segment and
    returns the obtained list of points in the form
    points = [[x_0, y_0],[x_1, y_1],...,[x_n, y_n]]
    """
    # Final number of points = (2^iterations)+1
    if vertical_displacement is None:
        # if no initial displacement is specified set displacement to:
        #  (y_start+y_end)/2
        vertical_displacement = (start[1] + end[1]) / 2

    # Data structure that stores the points is a list of lists where
    # each sublist represents a point and holds its x and y coordinates:
    # points=[[x_0, y_0],[x_1, y_1],...,[x_n, y_n]]
    #              |          |              |
    #           point 0    point 1        point n
    # The points list is always kept sorted from smallest to biggest x-value
    points = [start, end]
    iteration = 1
    while iteration <= num_of_iterations:
        # Since the list of points will be dynamically updated with the new computed
        # points after each midpoint displacement it is necessary to create a copy
        # of the state at the beginning of the iteration so we can iterate over
        # the original sequence.
        # Tuple type is used for security reasons since they are immutable in
        # Python.
        points_tup = tuple(points)
        for i in range(len(points_tup) - 1):
            # Calculate x and y midpoint coordinates:
            # [(x_i+x_(i+1))/2, (y_i+y_(i+1))/2]
            midpoint = list(map(lambda x: (points_tup[i][x] + points_tup[i + 1][x]) / 2,
                                [0, 1]))
            # Displace midpoint y-coordinate
            midpoint[1] += random.choice([-vertical_displacement,
                                          vertical_displacement])
            # Insert the displaced midpoint in the current list of points
            bisect.insort(points, midpoint)
            # bisect allows to insert an element in a list so that its order
            # is preserved.
            # By default the maintained order is from smallest to biggest list first
            # element which is what we want.
        # Reduce displacement range
        vertical_displacement *= 2 ** (-roughness)
        # update number of iterations
        iteration += 1
    return points


# =============================================================================
# 	Flooding
# =============================================================================


def terrain_min(terrain):
    """Takes a terrain and returns the coordinates of the minimum point."""
    x, y = np.unravel_index(terrain.argmin(), terrain.shape)
    return (x, y)


def floodFill(c, r, mask, value=1):
    """Fills water at given pour point."""

    # cells already filled
    filled = set()
    # cells to fill
    fill = set()
    fill.add((c, r))

    width = mask.shape[1]
    height = mask.shape[0]

    flood = np.zeros_like(mask, dtype=np.int8)

    while fill:
        x, y = fill.pop()
        if y == height or x == width or x < 0 or y < 0:
            continue
        if mask[y][x] == value:
            flood[y][x] = value
            filled.add((x, y))

            west = (x - 1, y)
            east = (x + 1, y)
            north = (x, y - 1)
            south = (x, y + 1)

            if not west in filled:
                fill.add(west)
            if not east in filled:
                fill.add(east)
            if not north in filled:
                fill.add(north)
            if not south in filled:
                fill.add(south)

    return flood


def define_terrain_defunct(width, length):
    """
    """
    n = math.ceil(math.log(width, 2))
    data = mpd(n)
    dem = data[0:width, 0:length]

    x, y = terrain_min(dem)
    mask = np.where(dem < dem.mean(), 1, 0)
    flood = floodFill(x, y, mask)

    out_number = str(np.random.randint(low=100000, high=999999))
    out_raster = 'temp/' + out_number
    out_shp = 'temp/' + out_number + '.shp'

    write_array(flood, out_raster)

    ds = gdal.Open(out_raster + '.tif')
    band = ds.GetRasterBand(1)

    drv = ogr.GetDriverByName("ESRI Shapefile")

    out = drv.CreateDataSource(out_shp)
    out_layer = out.CreateLayer('terrains', srs=None)

    fd = ogr.FieldDefn("DN", ogr.OFTInteger)
    out_layer.CreateField(fd)

    gdal.Polygonize(band, None, out_layer, 0, [], callback=None)
    out = None

    gdf = gpd.read_file(out_shp)
    return band
