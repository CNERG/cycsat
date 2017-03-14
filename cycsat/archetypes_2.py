
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Table, Boolean
from sqlalchemy.dialects.sqlite import BLOB
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from sqlalchemy import text, exists
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


Base = declarative_base()


class Build(Base):
	"""A an action taken by a user on a facility. Contains a 'Procces' log of
	cycsat actions to carry out the job."""

	__tablename__ = 'CycSat_Build'
	id = Column(Integer, primary_key=True)
	name = Column(String)


class Process(Base):
	"""A proccess run by cycsat under a particluar user-initiated 'Build'.
	"""
	__tablename__ = 'CycSat_Procces'

	id = Column(Integer, primary_key=True)
	name = Column(String) # description of the the event/error
	result = Column(Integer,default=0)
	message = Column(String)

	job_id = Column(Integer, ForeignKey('CycSat_Build.id'))
	job = relationship(Build, back_populates='processes')

Build.processes = relationship('Process', order_by=Process.id,back_populates='job',
								 cascade='all, delete, delete-orphan')