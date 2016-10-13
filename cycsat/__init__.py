"""
__init__.py

This file initializes cycsat, imports the Sensor class, and creates the 
Session class, which is used for reading the sqlite3 database.

"""

# Check here for dependencies. #

# import cycsat modules
from .data_model import Base

import sqlite3

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

Session = sessionmaker()

class Agency(object):
	'''
	An interface for working with sqlalchemy, sqlite3, and data classes
	
	'''

	def __init__(self,database):
		'''
		'''
		global Session
		global Base

		# add db extension if unspecified
		if database[:-2]!='.db':
			database+='.db'
		
		self.database = database
		self.engine = create_engine('sqlite+pysqlite:///'+self.database, module=sqlite3.dbapi2,echo=False)
		
		Session.configure(bind=self.engine)
		self.session = Session()

		Base.metadata.create_all(self.engine)




