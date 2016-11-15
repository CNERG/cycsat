'''
sensor.py

Object/API for writing scenes from pre-built geometries.

'''

import shapely
import json
import ast

from skimage.transform import resize, downscale_local_mean
from skimage.draw import polygon
from shapely.geometry import Polygon, Point
#from scipy.ndimage

import shapely
import numpy as np

import gdal

extensions = {
    'GTiff':'.tif'
}

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

	def draw(self,path,Instrument,image_format='GTiff'):
		'''
		need to add pixel size, reduce resoultion (zoom) and increase pizel size
		'''
		origin = 0

		rows = round(self.bands[1].shape[-2]/Instrument.mmu)
		cols = round(self.bands[1].shape[-1]/Instrument.mmu)

		bands = len(self.bands)
		driver = gdal.GetDriverByName(image_format)

		outRaster = driver.Create(path+extensions[image_format], cols, rows, bands, gdal.GDT_Byte)
		outRaster.SetGeoTransform((origin,Instrument.mmu,0,origin,0,Instrument.mmu*-1))

		for band in self.bands:
			outband = outRaster.GetRasterBand(band)

			if (Instrument.mmu > 1):
				band_array = downscale_local_mean(self.bands[band],(Instrument.mmu,Instrument.mmu))
				band_array = resize(band_array,(rows,cols),preserve_range=True)
				#band_array = band_array.round()
			else:
				band_array = self.bands[band]

			outband.WriteArray(band_array)
			outband.FlushCache()








