'''
sensor.py

Object/API for writing scenes from pre-built geometries.

'''

import shapely
import json
import ast

from skimage.draw import polygon
from shapely.geometry import Polygon, Point
#from scipy.ndimage

import shapely
import numpy as np

import gdal

# use Instrument pbject


class Canvas(object):
	'''
	'''
	def __init__(self,width,length, bands=3):
		'''
		'''
		self.bands = dict()
		for band in range(bands):
			self.bands[band+1] = np.zeros((length,width),dtype=np.uint8)

	def add_shape(self,Shape):
		'''
		Add a shapely geometries to a canvas
		'''
		geometry = Shape.build_geometry(placed=True)
		spectra = ast.literal_eval(Shape.color)
		
		coords = np.array(list(geometry.exterior.coords))
		rr, cc = polygon(coords[:,0], coords[:,1], self.bands[1].shape)

		for band in zip(self.bands, spectra):
			self.bands[band[0]][rr, cc] = band[1]

	def draw(self,path):
		'''
		'''
		arrays_to_image(self,path)


extensions = {
    'GTiff':'.tif'
}

# draw a site
# 1. take a site's dems and draw a basemap
# 2. get all the features from the site that are "static"


# need to add info for resamplign and 

def arrays_to_image(Canvas,path,image_format='GTiff'):

    rows = Canvas.bands[1].shape[-2]
    cols = Canvas.bands[1].shape[-1]

    bands = len(Canvas.bands)

    driver = gdal.GetDriverByName(image_format)

    # add file extension based on driver
    outRaster = driver.Create(path+extensions[image_format], cols, rows, bands, gdal.GDT_Byte)

    for band in Canvas.bands:
    	outband = outRaster.GetRasterBand(band)
    	outband.WriteArray(Canvas.bands[band])
    	outband.FlushCache()








