"""
terrain.py
"""
import numpy as np
import math


class Terrain(object):
	"""
	"""
	def __init__(self,width,length):
		n = math.ceil(math.log(width,2))
		dem = mpd(n)
		clip = dem[0:width,0:length]
		flat = clip.ravel()

		return flat.tostring()


# =============================================================================
# Terrain generation
# =============================================================================

def get_corners(array):
	"""Returns the corners of an array."""
	corners = array[tuple(slice(None, None, j-1) for j in array.shape)]
	return corners


def jitter(x,high=10):
	noise = np.random.normal(0,high)
	return int(x+noise)


def init_corners(array):
	"""Sets the corners of an array to a random value"""
	corners = get_corners(array)
	corners+= np.random.randint(0,255,(2,2))
	return array


def midpoints(array,jit):
	"""Sets the edges to the mean of the corners"""
	midpoint = int(array.shape[0]/2)
	corners = get_corners(array)

	array[0,midpoint] = jitter(corners[0,:].mean())
	array[midpoint,-1] = jitter(corners[-1,:].mean())
	array[-1,midpoint] = jitter(corners[:,-1].mean())
	array[midpoint,0] = jitter(corners[:,0].mean())
	array[midpoint,midpoint] = jitter(corners.mean())

	return array


def mpd(n=3,jit=5):
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


def floodFill(c,r,mask,value=1):
	"""Fills water."""
	
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






