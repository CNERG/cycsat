"""
__init__.py

This file initializes cycsat, imports the Sensor class, and creates the 
Session class, which is used for reading the sqlite3 database.

"""

# Check here for dependencies. #

# import cycsat modules
from cycsat import agency
from cycsat import world
from cycsat import sensor

import sqlite3

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

Session = sessionmaker()

class Interface(object):
	'''
	An interface for interfacing between sqlalchemy, sqlite3, and data classes
	
	'''

	def __init__(self,database):
		
		self.database = database
		self.engine = create_engine('sqlite+pysqlite:///'+self.database, module=sqlite3.dbapi2,echo=True)
		
		global Session
		Session.configure(bind=self.engine)
		self.session = Session()




