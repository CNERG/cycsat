"""
sensor.py

"""
import shapely
import json
import ast

from skimage.transform import resize, downscale_local_mean
from skimage.draw import polygon
from shapely.geometry import Polygon, Point

import shapely
import numpy as np

import gdal


extensions = {
    'GTiff':'.tif'
}


class Sensor(object):

	def __init__(self,Instrument,method='normal'):
		"""Initiate a sensor instance

		Keyword arguments:
		width -- width of image
		length -- length of image
		Instrument -- Instrument instance to draw the image
		method -- 'normal' (random normal distribution around mean) or 'mean'
		"""
		width = Instrument.ifov_width*10
		length = Instrument.ifov_length*10
		self.ifov = Instrument.build_ifov()
		
		self.name = Instrument.name
		self.mmu = Instrument.mmu
		self.min_spectrum = float(Instrument.min_spectrum)
		self.max_spectrum = float(Instrument.max_spectrum)

		self.background = np.zeros((width,length),dtype=np.uint8)
		self.foreground = self.background.copy()
		
		self.wavelength = (np.arange(281)/100) + 0.20
		self.method = method
		
	
	def reset(self):
		"""Resets the capture array to the background array"""
		self.foreground = self.background.copy()

	
	def focus(self,Facility):
		"""Focuses the intrument on a facility"""
		self.shapes = []
		for feature in Facility.features:
			for shape in feature.shapes:
				self.shapes.append(shape)

		self.build_footprint()
		cross_hairs = self.footprint.centroid
		
		for shape in self.shapes:
			place(shape,cross_hairs,Facility)

		world.write(Facility)




	def add_shape(self,Shape,background=True):
		"""Adds a shape to the image, default background image"""

		image = self.foreground
		if background:
			image = self.background

		geometry = Shape.build_footprint(placed=True)
		material = np.fromstring(Shape.material)

		mask = (self.wavelength >= self.min_spectrum) & (self.wavelength <= self.max_spectrum)
		spectrum = material[mask]
		value = round(spectrum.mean())
		
		coords = np.array(list(geometry.exterior.coords))
		rr, cc = polygon(coords[:,0], coords[:,1], image.shape)
		
		if self.method == 'normal':
			image[rr, cc] = np.random.normal(loc=value,scale=20,size=image[rr, cc].shape)
		else:
			image[rr, cc] = value


	def capture(self,path,img_format='GTiff'):
		"""Writes an image using GDAL

		Keyword arguments:
		path -- the path to write the image
		img_format -- the GDAL format
		"""
		origin = 0

		rows = round(self.foreground.shape[-2]/self.mmu)
		cols = round(self.foreground.shape[-1]/self.mmu)

		driver = gdal.GetDriverByName(img_format)

		outRaster = driver.Create(path+extensions[img_format], cols, rows, 1, gdal.GDT_Byte)
		outRaster.SetGeoTransform((origin,self.mmu,0,origin,0,self.mmu*-1))

		outband = outRaster.GetRasterBand(1)
		if (self.mmu > 1):
			band_array = downscale_local_mean(self.foreground,(self.mmu,self.mmu))
			band_array = resize(band_array,(rows,cols),preserve_range=True)
		else:
			band_array = self.foreground

		outband.WriteArray(band_array)
		outband.FlushCache()


def materialize(name='Default',rgb=None,blob=True):
	"""Returns an array of reflection values indexed by wavelength
	
	Keyword arguments:
	name -- name of the material
	rgb -- RGB values, for simplicity
	blob -- return as blob for data storage
	"""
	wavelength = (np.arange(281)/100) + 0.20
	reflectance = np.zeros(281)+255

	if rgb:
		reflectance[(wavelength >= 0.64) & (wavelength <= 0.67) ] = rgb[0]
		reflectance[(wavelength >= 0.53) & (wavelength <= 0.59) ] = rgb[1]
		reflectance[(wavelength >= 0.45) & (wavelength <= 0.51) ] = rgb[2]

	if blob:
		return reflectance.tostring()
	else:
		return reflectance











