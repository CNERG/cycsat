'''
geometry.py

'''

import shapely
import json

from skimage.draw import polygon
from shapely.geometry import Polygon, Point

import shapely
import numpy as np

frame = np.zeros((500,500),dtype=np.int32)
building = Polygon([(300, 300), (480, 320), (380, 430), (220, 590)])


def canvas(length,width,dtype=np.int32):
	'''
	'''
	canvas = np.zeros((length, width),dtype=dtype)

	return canvas


def add_feature(feature,canvas):
	'''
	Add a geometry to a canvas, returns new canvas

	'''
	coords = np.array(list(feature.exterior.coords))

	rr, cc = polygon(coords[:,0], coords[:,1], canvas.shape)

	canvas[rr, cc] = 1

	return canvas

class Sensor(object):
	'''
	'''

	def __init__(self):
		'''
		'''
		self.canvas = np.array()



'''
adding a feature to a site will involve placing that feature so that it makes sense (eg no overlap)

turbine building - rectangle
containment building - circle
cooling tower - circle

'''



