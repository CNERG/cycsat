"""
__init__.py

This file initializes cycsat, imports the Sensor class, and creates the 
Session class, which is used for reading the sqlite3 database.

"""

# Check here for dependencies. #

from cycsat import agency
from cycsat import target
from cycsat import sensor

class Session(object):
	'''
	This object is for managing cycsensor.
	
	Attributes:
		id: the session id
		database: a sqlite3 file

	'''

	def __init__(self,name=None):
		self.name = name






