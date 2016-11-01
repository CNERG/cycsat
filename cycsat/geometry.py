"""

features.py

units in centimeters

"""

from .database import Shape

from sqlalchemy import Column, Integer, String

from sqlalchemy.ext.declarative import declared_attr

from random import randint

import numpy as np
from shapely.geometry import Polygon, Point
from shapely.wkt import loads as load_wkt
from shapely.affinity import translate as shift_shape
from shapely.ops import cascaded_union

'''
a blueprint object is a copy of all the shapes placed onto the footprint of a facility

'''

class Blueprint(object):

	def __init__(self,Facility):

		self.features = Facility.features

		# convert centimeters to meters and define footprint
		width = Facility.width*100
		length = Facility.length*100
		self.footprint = Polygon([(0,0),(0,width),(length,width),(length,0)])

	def create_draft(self):
		'''
		Posits (or proposes) locations for all the features at a facility
		
		'''
		self.draft = list()

		features = self.features.copy()

		for feature in features:

			posited_feature = dict()

			# posit (or propose) the feature
			posited_shape_stack = posit_feature(feature,self.footprint)
			posited_feature['posited_shape_stack'] = posited_shape_stack
			posited_feature['feature'] = feature

			# create a copy
			posit_stack = posited_feature.copy()

			self.draft.append(posit_stack)


	def assess(self):

		assessment = dict()
		assessment['success'] = []
		assessment['conflict'] = []

		draft = self.draft.copy()

		posited_shape_stacks = [x['posited_shape_stack'] for x in draft]

		merged_shape_stacks = dict()

		# combine all the posited shape stacks
		for shape_stack in posited_shape_stacks:
			for level in shape_stack:
				if level in merged_shape_stacks:
					merged_shape_stacks[level]+=shape_stack[level]
				else:
					merged_shape_stacks[level] = shape_stack[level]

		overlaps = []

		for level in merged_shape_stacks:
			for shape in merged_shape_stacks[level]:
				overlaps = [shape.disjoint(x) for x in merged_shape_stacks[level]]
				
				if False in overlaps:
					assessment['conflict'].append(shape)
				else:
					assessment['success'].append(shape)

		if len(assessment['conflict'])>0:
			assessment['result'] = False
		else:
			assessment['result'] = True

		self.assessment = assessment

	def design(self,attempts=10):
		fails = 0
		while fails<attempts:
			self.create_draft()
			self.assess()

			if self.assessment['result']:
				break
			else:
				fails+=1

def stack_shapes(Feature):
	'''
	Returns a dictionary of shapes sorted and merged by their levels
	'''
	shape_stack = dict()

	# stack shapes by level
	for shape in Feature.shapes:
		if shape.level in shape_stack:
			shape_stack[shape.level].append(load_wkt(shape.geometry))
		else:
			shape_stack[shape.level] = [load_wkt(shape.geometry)]

	return shape_stack


def posit_feature(Feature,footprint):
	'''
	Posits (or proposes) a random placement for a feature within a facility footprint, returns
	a shape stack with proposed locations
	'''
	
	length = footprint.bounds[-2]
	width = footprint.bounds[-1]

	shape_stack = stack_shapes(Feature)

	posit = Point(randint(0,width+1), randint(0,length+1))
	posit_x = posit.coords.xy[0][0]
	posit_y = posit.coords.xy[1][0]

	posited_shape_stack = dict()

	for level in shape_stack:
		for shape in shape_stack[level]:

			placed = 0
			while (placed < 10): 

				shape_x = shape.centroid.coords.xy[0][0]
				shape_y = shape.centroid.coords.xy[1][0]
				shift_x = posit_x - shape_x
				shift_y = posit_y - shape_y

				posited = shift_shape(shape,xoff=shift_x,yoff=shift_y)

				if posited.within(footprint):
					if level in posited_shape_stack:
						posited_shape_stack[level].append(posited)
					else:
						posited_shape_stack[level] = [posited]
					placed = 15
				else:
					placed+=1
					continue

			if (placed < 15):
				# shape cannot be placed
				break

	return posited_shape_stack


'''
basic shapely shape templates

'''

class Circle(Shape):
    __mapper_args__ = {'polymorphic_identity': 'circle'}

    def __init__(self,radius=4000,level=0):
    	self.radius = radius
    	self.geometry = Point(0,0).buffer(self.radius).wkt
    	self.level = level

    @declared_attr
    def geometry(self):
    	return Shape.__table__.c.get('geometry', Column(String))

class Rectangle(Shape):
    __mapper_args__ = {'polymorphic_identity': 'rectangle'}

    def __init__(self,width=3000,length=4000,level=0):
    	self.width = width
    	self.length = length
    	self.geometry = Polygon([(0,0),(0,self.width),(self.length,self.width),(self.length,0)]).wkt
    	self.level = level

    @declared_attr
    def geometry(self):
    	return Shape.__table__.c.get('geometry', Column(String))