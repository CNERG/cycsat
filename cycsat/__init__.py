"""
__init__.py

Imports important objects when cycscene is imported.

"""

# Check here for dependencies. #

class Session(object):
	'''
	This object is for managing cycsensor.
	
	Attributes:
		id: the session id
		database: a sqlite3 file

	'''

	def __init__(self,name=None):
		self.name = name






