"""

materials_reader.py:
Translates an ASCII file into a Material.

"""
import pandas as pd
import numpy as np

import os
import ast


cdir, cfile = os.path.split(__file__)
f = os.walk(cdir+'/materials/ASCII')
samples = list()
for path,subdirs,files in f:
	for name in files:
		samples.append(
			[os.path.join(cdir,path.replace('/','\\'),name),path,name]
			)

Library = pd.DataFrame(samples,
	columns=['path','subdir','name']).sort_values('name')


class Material(object):
	"""Material object"""
	def __init__(self,material_code=None,rgb=None):
		global Library
		self.code = material_code

		if rgb:
			self.name = 'rgb'
			wavelength = (np.arange(281)/100) + 0.20
			reflectance = np.zeros(281)
			reflectance[(wavelength >= 0.64) & (wavelength <= 0.67) ] = rgb[0]
			reflectance[(wavelength >= 0.53) & (wavelength <= 0.59) ] = rgb[1]
			reflectance[(wavelength >= 0.45) & (wavelength <= 0.51) ] = rgb[2]
			std = np.zeros(281)
			self.df = pd.DataFrame({'wavelength':wavelength,
									'reflectance':reflectance,
									'std':std})
		else:
			self.name = Library.ix[int(self.code)]['path']
			self.df = pd.read_table(self.name,sep='\s+',skiprows=16,header=None,
				names=['wavelength','reflectance','std'])


	def measure(self,wl_min=None,wl_max=None,wavelength=None,window=1,estimate=True):
		"""Looks up the nearest reflectance by wavelength

		Keyword arguments:
		wl_min -- minimum wavelength
		wl_max -- maximum wavelength
		wavelength -- specific wavelength to estimate
		window -- number of records around the specific wavelength
		estimate -- will use model error using the material std
		"""
		df = self.df
		if wavelength:
			nearest = df.ix[(df.wavelength-wavelength).abs().argsort()[:window]]
		else:
			nearest = df[(df.wavelength >= wl_min) & (df.wavelength <= wl_max)]

		mean = nearest.reflectance.mean()
		std = nearest['std'].mean()+0.000001

		if self.name == 'rgb':
			return round(mean)

		if estimate:
			value = np.random.normal(loc=mean,scale=std)
		else:
			value = mean

		ubyte = round(value*255)
		return ubyte


def materialize(Shape):
	"""Takes a Shape object and adds its Material"""
	
	if Shape.material_code:
		Shape.material = Material(material_code=Shape.material_code)
	else:
		Shape.material = Material(rgb=ast.literal_eval(Shape.rgb))

	return Shape



# DEMO

# brick = Material('ammonium_chloride_gds77.27373')
# sample = np.zeros(100)+0.005
# data = pd.DataFrame(sample.cumsum()+0.25)
# data['estimate'] = data.apply(lambda x: brick.measure(x[0]),axis=1)
# data['actual'] = data.apply(lambda x: brick.measure(x[0],estimate=False),axis=1)		