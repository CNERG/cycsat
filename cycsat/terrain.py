"""
"""
import numpy as np
import math


def jitter(x,low=0,high=5):
	return int(x+np.random.normal(low,high))

jitter = np.vectorize(jitter)


def init_corners(array):
	"""Sets the corners of an array to a random value"""
	corners = array[tuple(slice(None, None, j-1) for j in array.shape)]
	corners+= np.random.randint(0,255,(2,2))
	return array

def midpoints(array):
	"""Sets the edges to the mean of the corners"""
	midpoint = int(array.shape[0]/2)
	corners = array[tuple(slice(None, None, j-1) for j in array.shape)]

	edges = jitter(corners)

	array[0,midpoint] = int(edges[0,:].mean())
	array[midpoint,-1] = int(edges[-1,:].mean())
	array[-1,midpoint] = int(edges[:,-1].mean())
	array[midpoint,0] = int(edges[:,0].mean())
	
	array[midpoint,midpoint] = jitter(edges.mean())

	return array


def mpd(size=9):

	if (size % 2 == 0):
		size+=1

	array = np.zeros((size,size))
	
	# initialize corners
	init_corners(array)
	midpoints(array)
	# count iterations
	iterations = int(math.log(array.shape[0]-1)/math.log(2))-1
	print(iterations)

	number = 2
	for i in range(iterations):
		width = size/number
		data = np.zeros(number)+width

		integer = np.vectorize(int)
		data = integer(data.cumsum())+1
		data[-1]+=-1
		number+=2
	
		miny = 0	
		for y in data:
			minx = 0
			for x in data:
				print(miny,y,minx,x)
				midpoints(array[miny:y,minx:x])
				minx=x-1
			miny=y-1

	return array







	# midpoints(array)

# class Landscape(object):
# 	"""
# 	"""
# 	def __init__(self,size=5,clases=2):

# 		if (size % 2 == 0):
# 			size+=1

# 		self.data = 
# 		

# 		midpoint = int(size/2)
# 		edges = jitter(np.random.randint(0,255,size=4))

# 		self.data[0,midpoint] = edges[0]
# 		self.data[midpoint,-1] = edges[1]
# 		self.data[-1,midpoint] = edges[2]
# 		self.data[midpoint,0] = edges[3]
		
# 		self.data[midpoint,midpoint] = jitter(edges.mean())[0]



