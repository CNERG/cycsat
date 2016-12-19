"""
terrain.py
"""
import numpy as np
import math

# =============================================================================
# Terrain generation
# =============================================================================


def build_terrain(width,length,method='mpd'):
	"""
	"""
	n = math.ceil(math.log(width,2))
	land = mpd(n)
	clip = land[0:width,0:length]
	flat = clip.ravel()

	return flat.tostring()


def jitter(x,high=10):
	noise = np.random.normal(0,high)
	return int(x+noise)


def init_corners(array):
	"""Sets the corners of an array to a random value"""
	corners = array[tuple(slice(None, None, j-1) for j in array.shape)]
	corners+= np.random.randint(0,255,(2,2))
	return array


def midpoints(array,jit):
	"""Sets the edges to the mean of the corners"""
	midpoint = int(array.shape[0]/2)
	corners = array[tuple(slice(None, None, j-1) for j in array.shape)]

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

from skimage.morphology import watershed



