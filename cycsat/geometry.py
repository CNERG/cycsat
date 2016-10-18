'''
geometry.py

'''

import shapely
import json

from skimage.draw import polygon
from shapely.geometry import Polygon, Point

import shapely
import numpy as np

building = Polygon([(300, 300), (480, 320), (380, 430), (220, 590)])

class Canvas(object):
	'''
	'''

	def __init__(self,length,width,bands):
		'''
		'''
		self.data = np.zeros((length, width),dtype=np.uint8)


	def add_feature(self,feature,rgb):
		'''
		Add a geometry to a canvas, returns new canvas
		'''
		coords = np.array(list(feature.exterior.coords))
		rr, cc = polygon(coords[:,0], coords[:,1], self.data.shape)

		self.data[rr, cc] = rgb



'''
adding a feature to a site will involve placing that feature so that it makes sense (eg no overlap)

turbine building - rectangle
containment building - circle
cooling tower - circle

'''



