'''

shapes.py

'''
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import Column, String

from shapely.geometry import Polygon, Point

from cycsat.image import materialize
from cycsat.archetypes import Shape, Rule


class Circle(Shape):
    __mapper_args__ = {'polymorphic_identity': 'circle'}

    def __init__(self,material=materialize(rgb=[31,84,168]),radius=400,level=0,xoff=0,yoff=0,rotation=0,visibility=100):
    	self.radius = radius
    	self.level = level
    	self.material = material
    	self.xoff = xoff
    	self.yoff = yoff
    	self.visibility = visibility

    	self.geometry = Point(xoff,yoff).buffer(self.radius).wkt

    @declared_attr
    def geometry(self):
    	return Shape.__table__.c.get('geometry', Column(String))


class Rectangle(Shape):
    __mapper_args__ = {'polymorphic_identity': 'rectangle'}

    def __init__(self,material=materialize(rgb=[110,160,62]),width=300,length=400,level=0,xoff=0,yoff=0,rotation=0):
    	self.width = width
    	self.length = length
    	self.level = level
    	self.material = material
    	self.xoff = xoff
    	self.yoff = yoff

    	self.geometry = Polygon([(xoff,yoff),(xoff,self.width),(self.length,self.width),(self.length,yoff)]).wkt

    @declared_attr
    def geometry(self):
    	return Shape.__table__.c.get('geometry', Column(String))


class Plume(Shape):
    __mapper_args__ = {'polymorphic_identity': 'plume'}

    def __init__(self,radius=800,level=3,material=materialize(rgb=[255,255,255]),xoff=500,yoff=500,visibility=5):
        self.radius = radius
        self.level = level
        self.material = material
        self.xoff = xoff
        self.yoff = yoff
        self.visibility = visibility

        self.geometry = Point(xoff,yoff).buffer(self.radius).wkt

        self.rules = [
        Rule(table='TimeSeriesPower',oper='greater than',value=0)
        ]

    @declared_attr
    def geometry(self):
        return Shape.__table__.c.get('geometry', Column(String))
