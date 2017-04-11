"""
shapes.py
"""
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import Column, String

from shapely.geometry import Polygon, Point

from cycsat.archetypes import Shape, Rule, Condition
from cycsat.laboratory import Material

import geopandas as gpd


class Circle(Shape):
    __mapper_args__ = {'polymorphic_identity': 'circle'}

    def __init__(self, material_code=None, rgb=[255, 255, 255], radius=400, level=0, xoff=0, yoff=0, rotation=0, visibility=100):
        self.radius = radius
        self.level = level
        self.material_code = material_code
        self.rgb = str(rgb)
        self.xoff = xoff
        self.yoff = yoff
        self.visibility = visibility

        self.stable_wkt = Point(xoff, yoff).buffer(self.radius).wkt


class Rectangle(Shape):
    __mapper_args__ = {'polymorphic_identity': 'rectangle'}

    def __init__(self, material_code=None, rgb=[255, 255, 255], width=300, length=400, level=0, xoff=0, yoff=0, rotation=0, visibility=100):
        self.width = width
        self.length = length
        self.level = level
        self.material_code = material_code
        self.rgb = str(rgb)
        self.xoff = xoff
        self.yoff = yoff
        self.visibility = visibility

        self.stable_wkt = Polygon(
            [(xoff, yoff), (xoff, self.width), (self.length, self.width), (self.length, yoff)]).wkt
