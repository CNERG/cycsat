"""
simulation.py

"""

class Event(object):
	'''
	Events are junction tables (many-to-many) between features and scenes.
	One Feature has many Events. Events are simply the probability
	
	Attributes:
		frequecy: the liklihood the event will happen every scene.
		

	'''

	def __init__(self,name=None):
		self.name = name


class Scene(object):
	'''
	This object is a canvas with features from a particular time in
	a simulation.
	
	Attributes:
		time_step: the time step of the scene
		
	'''

	def __init__(self,name=None):
		self.name = name