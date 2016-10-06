"""
target.py

The target module.

Contains the satillite, sensor (one satillite has many sensors), site, and feature
classes.

"""

class Facility(object):
	'''
	This object is a site (eg. reactor).
	
	Attributes:
		id: the sites unique id
		name: name of site
		canvas: the basemap to draw on includes static features
		
	'''

	def __init__(self,name=None):
		self.name = name

	def add_feature():
		'''
		Adds a feature to the site.

		'''
		pass


	def next(self):
		'''
		Composes the next scene

		'''

'''
to create a scene

1. get a list of all the features
2. for all the features that have a proability that allows them to appear, create events in the
events table
3. Use the events (visable features) to generate a scene!

'''

class Feature(object):
	'''
	This object is a feature associated with a site.
	
	Attributes:
		liklihood: % chance this feature will appear in each scene.
		name: 
		shape:
		
	'''

	def __init__(self,name=None):
		self.name = name