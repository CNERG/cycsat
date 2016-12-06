"""
sensor.py

"""
import shapely
import json
import ast

from .geometry import place

from skimage.transform import resize, downscale_local_mean
from skimage.draw import polygon
from shapely.geometry import Polygon, Point

import shapely
import numpy as np

import gdal


extensions = {
    'GTiff':'.tif'
}

# the sensor could be the top level object

class Sensor(object):

	def __init__(self,Instrument,method='normal'):
		"""Initiate a sensor instance

		Keyword arguments:
		Instrument -- Instrument instance to draw the image
		method -- 'normal' (random normal distribution around mean) or 'mean'
		"""
		width = Instrument.width*10
		length = Instrument.length*10
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

		cross_hairs = self.ifov.centroid
		
		for shape in self.shapes:
			place(shape,cross_hairs,Facility)


	def calibrate(self,Facility,method='normal'):
		"""Generates a sensor with all the static shapes"""
		shape_stack = dict()

		# add all the static (in level order) to the image
		for feature in Facility.features:
			for shape in feature.shapes:

				if shape.visibility!=100:
					continue
				if shape.level in shape_stack:
					shape_stack[shape.level].append(shape)
				else:
					shape_stack[shape.level] = [shape]

		for level in sorted(shape_stack):
			for shape in shape_stack[level]:
				add_shape(self,shape,geometry='focused',background=True)


	def capture_shape(self,Shape,geometry='focused'):
		"""Adds a shape to the foreground image"""
		add_shape(self,Shape,geometry=geometry,background=False)


	def write(self,path,img_format='GTiff'):
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



def add_shape(Sensor,Shape,geometry='abstract',background=True):
		"""Adds a shape to the sensor objects image, by default the background image"""

		image = Sensor.foreground
		if background:
			image = Sensor.background

		geometry = Shape.build_footprint(geometry=geometry)
		material = np.fromstring(Shape.material)

		mask = (Sensor.wavelength >= Sensor.min_spectrum) & (Sensor.wavelength <= Sensor.max_spectrum)
		spectrum = material[mask]
		value = round(spectrum.mean())
		
		coords = np.array(list(geometry.exterior.coords))
		rr, cc = polygon(coords[:,0], coords[:,1], image.shape)
		
		if Sensor.method == 'normal':
			image[rr, cc] = np.random.normal(loc=value,scale=20,size=image[rr, cc].shape)
		else:
			image[rr, cc] = value


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











