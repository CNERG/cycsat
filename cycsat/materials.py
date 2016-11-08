"""
materials.py

"""

import numpy as np

class Band(object):
	'''
	'''
	def __init__(self,minimum=0,maximum=255):
		self.minimum = minimum
		self.maximum = maximum

class Material(object):
	'''
	'''
	def __init__(self):
		self.bands = dict()

class Concrete(Material):
	'''
	'''
	def __init__(self):
		Material.__init__(self)
		self.bands = {

		1: Band(0,255),
		2: Band(0,255),
		3: Band(0,255)

		}


