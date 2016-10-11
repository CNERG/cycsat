"""
observation.py

Contains the Event and Scene classes.

"""

import gdal

class Event(object):
	'''
	Events are junction tables (many-to-many) between features and scenes.
	One Feature has many Events. Events are simply the probability
	
	Attributes:
		
	'''

	def __init__(self,name=None):
		self.name = name


class Scene(object):
	'''
	This object is a canvas with features from a particular time in
	a simulation.
	
	Attributes:
		
	'''

	def __init__(self,name=None):
		self.name = name