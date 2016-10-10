"""
agency.py

This file contains all the classes and functions that make up what might be 
called an space "agency." Instruments, satellites, and missions.

"""

class Instrument(object):
	"""
	This object is a particular instrument associated with a satellite.
	
	Attributes:
		name:
	
	"""

	def __init__(self,name):
		self.name = name

class Satellite(object):
	"""
	
	Attributes:
		name:
		payload: the sensors this sateillte carries (eg. thermal, infared)
	
	"""

	def __init__(self,name):
		self.name = name

class Mission(object):
	"""
	This object represents a single mission for a particular satellite.

	Attributes:
		name:
		return_interval: the frequency of return visits
		duration: the length of time this mission will run
		targets: the network of facilites targeted by this mission

	"""

	def __init__(self,name):
		self.name = name