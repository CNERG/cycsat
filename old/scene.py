import os

import numpy as np

import gdal, ogr, os, osr
from osgeo import ogr

import image

'''
This module will include all the classes that make up a "scene." A scene
represents the combination of a canvas.

'''

class Canvas(object):
	'''
	The canvas object.

    Attributes:
        name: A descriptive name.
        width: The with of the canvas in pixels

    '''

    # list of feature objects in this image
	#self.features = []

	def __init__(self,name,mmu=1,width,length,random=False):
		self.name = name
		self.mmu = mmu
		
		self.data = np.zeros((width,length),dtype=np.int32)

	def change_mmu(self,mmu):
		'''Change the minimim mapping unit (pixel size in meters).'''
		self.mmu = mmu

	def draw_canvas(self,path=None,image_format='GTiff'):
		'''Draws the canvas saving it as an image.'''
		image.array_to_image(self.name,self.data,image_format=image_format)