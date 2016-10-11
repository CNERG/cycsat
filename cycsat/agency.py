"""
agency.py

Contains the Instrument, Satellites, and Mission classes.

"""

class Instrument(object):
	"""
	This object is a particular instrument associated with a satellite.
	
	Attributes:
	
	"""

	def __init__(self,name):
		self.name = name

class Satellite(object):
	"""

	Attributes:
	
	"""

	def __init__(self,name):
		self.name = name

class Mission(object):
	"""
	This object represents a single mission for a particular satellite.

	Attributes:

	"""

	def __init__(self,name):
		self.name = name