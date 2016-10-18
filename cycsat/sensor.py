'''
sensor.py

Object/API for writing scenes from pre-built geometries.

'''

import shapely
import json

from skimage.draw import polygon
from shapely.geometry import Polygon, Point

import shapely
import numpy as np

import gdal


class Image(object):
	'''
	'''

	def __init__(self,length,width,bands=3):
		'''
		'''
		self.bands = dict()
		for band in range(bands):
			self.bands[band+1] = np.zeros((length, width),dtype=np.uint8)

	def add_feature(self,feature,spectra):
		'''
		Add a geometry to a canvas, returns new canvas
		'''

		coords = np.array(list(feature.exterior.coords))
		rr, cc = polygon(coords[:,0], coords[:,1], self.bands[1].shape)

		for band in zip(self.bands, spectra):
			self.bands[band[0]][rr, cc] = band[1]


extensions = {
    'GTiff':'.tif'
}

# draw a site
# 1. take a site's dems and draw a basemap
# 2. get all the features from the site that are "static"


def array_to_image(image,path,image_format='GTiff'):

    rows = image.bands[1].shape[-2]
    cols = image.bands[1].shape[-1]

    bands = len(image.bands)

    driver = gdal.GetDriverByName(image_format)

    # add file extension based on driver
    outRaster = driver.Create(path+extensions[image_format], cols, rows, bands, gdal.GDT_Byte)

    for band in image.bands:
    	outband = outRaster.GetRasterBand(band)
    	outband.WriteArray(image.bands[band])
    	outband.FlushCache()








