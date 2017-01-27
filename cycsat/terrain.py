"""
terrain.py
"""
import numpy as np
import math

from cycsat.archetypes import Shape, Rule, Base
from cycsat.image import write_array

from osgeo import ogr, gdal, osr
from geopandas import gpd


def simple(width,length):
	"""Creates a simple land and water terrain returns terrain shapes"""
	n = math.ceil(math.log(width,2))
	data = mpd(n)
	terrain = data[0:width,0:length]

	mask = np.where(terrain < terrain.mean(),1,0)

	# create temporary storage names
	out_number = str(np.random.randint(low=100000,high=999999))
	out_raster = 'temp/'+out_number
	out_shp = 'temp/'+out_number+'.shp'

	# write out a raster file
	write_array(mask,out_raster)
	ds = gdal.Open(out_raster+'.tif')
	band = ds.GetRasterBand(1)

	drv = ogr.GetDriverByName('ESRI Shapefile')
	out = drv.CreateDataSource(out_shp)
	out_layer = out.CreateLayer('terrains',srs=None)

	fd = ogr.FieldDefn('DN',ogr.OFTInteger)
	out_layer.CreateField(fd)

	gdal.Polygonize(band,None,out_layer,0,[],callback=None)
	out = None

	gdf = gpd.read_file(out_shp)
	gdf['area'] = gdf.area

	land = Shape(category='Terrain',
				 name='Land',
				 wkt=gdf.sort_values('area',ascending=False).iloc[0]['geometry'].wkt,
				 level=0)

	water_shapes = list()
	water_bodies= gdf.sort_values('area',ascending=False).iloc[1:]['geometry'].tolist()
	for body in water_bodies:
		water_shape = Shape(category='Terrain',
			                name='Water',
			                wkt=body.wkt,
			                level=0)
		water_shapes.append(water_shape)

	return gdf #[land]+water_shapes


# =============================================================================
# Terrain generation: Mid-point distance replacement
# =============================================================================

def get_corners(array):
	"""Returns the corners of an array."""
	corners = array[tuple(slice(None, None, j-1) for j in array.shape)]
	return corners


def jitter(x,jit):
	noise = np.random.normal(0,jit)
	return int(x+noise)


def init_corners(array):
	"""Sets the corners of an array to a random value"""
	corners = get_corners(array)
	corners+= np.random.randint(0,100,(2,2))
	return array


def midpoints(array,jit):
	"""Sets the edges to the mean of the corners"""
	midpoint = int(array.shape[0]/2)
	corners = get_corners(array)

	array[0,midpoint] = jitter(corners[0,:].mean(),jit=jit)
	array[midpoint,-1] = jitter(corners[-1,:].mean(),jit=jit)
	array[-1,midpoint] = jitter(corners[:,-1].mean(),jit=jit)
	array[midpoint,0] = jitter(corners[:,0].mean(),jit=jit)
	array[midpoint,midpoint] = jitter(corners.mean(),jit=jit)

	return array


def mpd(n=3,jit=0):
	"""Midpoint distance replacement"""

	size = (2**n)+1
	heightmap = np.zeros((size,size))
	
	# initialize corners and midpoints (pass 1)
	init_corners(heightmap)
	midpoints(heightmap,jit)

	slices = nested_quarters(n,heightmap)

	for level in sorted(slices):
		for array in sorted(slices[level]):
			midpoints(slices[level][array],jit)

	return heightmap
	

def nested_quarters(n,array):
	"""
	"""
	iterations = n-2
	slices = dict()

	# first iteration
	targets = quarter_array(array)
	slices[0] = targets
	
	# following iterations
	for i in range(iterations):
		target = i
		slices[target+1] = dict()
		for array in slices[target]:
			quarters = quarter_array(slices[target][array])
			for quarter in quarters:
				slices[target+1][array+quarter] = quarters[quarter]

	return slices


def quarter_array(array):
	"""Divides an array into quarters and returns a dictionary of views"""
	spread = int(array.shape[0]/2)+1
	
	views = dict()
	views['A'] = array[0:spread,0:spread]
	views['B'] = array[0:spread,spread-1:(spread*2)-1]
	views['C'] = array[spread-1:(spread*2)-1,0:spread]
	views['D'] = array[spread-1:(spread*2)-1,spread-1:(spread*2)-1]

	return views


# =============================================================================
# 	Flooding
# =============================================================================


def terrain_min(terrain):
	"""Takes a terrain and returns the coordinates of the minimum point."""
	x,y = np.unravel_index(terrain.argmin(),terrain.shape)
	return (x,y)


def floodFill(c,r,mask,value=1):
	"""Fills water at given pour point."""
	
	# cells already filled
	filled = set()
	# cells to fill
	fill = set()
	fill.add((c,r))

	width = mask.shape[1]
	height = mask.shape[0]

	flood = np.zeros_like(mask,dtype=np.int8)

	while fill:
		x,y = fill.pop()
		if y == height or x == width or x < 0 or y < 0:
			continue
		if mask[y][x] == value:
			flood[y][x] = value
			filled.add((x,y))

			west = (x-1,y)
			east = (x+1,y)
			north = (x,y-1)
			south = (x,y+1)

			if not west in filled:
				fill.add(west)
			if not east in filled:
				fill.add(east)
			if not north in filled:
				fill.add(north)
			if not south in filled:
				fill.add(south)

	return flood

def define_terrain_defunct(width,length):
	"""
	"""
	n = math.ceil(math.log(width,2))
	data = mpd(n)
	dem = data[0:width,0:length]

	x,y = terrain_min(dem)
	mask = np.where(dem < dem.mean(),1,0)
	flood = floodFill(x,y,mask)

	out_number = str(np.random.randint(low=100000,high=999999))
	out_raster = 'temp/'+out_number
	out_shp = 'temp/'+out_number+'.shp'
	
	write_array(flood,out_raster)

	ds = gdal.Open(out_raster+'.tif')
	band = ds.GetRasterBand(1)

	drv = ogr.GetDriverByName("ESRI Shapefile")

	out = drv.CreateDataSource(out_shp)
	out_layer = out.CreateLayer('terrains',srs=None)

	fd = ogr.FieldDefn("DN",ogr.OFTInteger)
	out_layer.CreateField(fd)

	gdal.Polygonize(band,None,out_layer,0,[],callback=None)
	out = None

	gdf = gpd.read_file(out_shp)
	return band






