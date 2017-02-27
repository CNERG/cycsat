"""
prototpyes/feature.py
"""
import random
from cycsat.archetypes import Shape, Feature, Rule, Condition
from cycsat.prototypes.shapes import Circle, Rectangle, Plume


class ConcretePad(Feature):
    __mapper_args__ = {'polymorphic_identity': 'concrete pad'}

    def __init__(self,name='concrete pad'):
        
        self.name = name
        self.visibility = 100
        self.rgb = '[155,155,155]'
        self.level = 0

        # define shapes
        self.shapes = [
        Rectangle(width=6000,length=6000)
        ]


class SampleCoolingTower1(Feature):
    __mapper_args__ = {'polymorphic_identity': 'sample cooling tower 1'}

    def __init__(self,name='sample cooling tower 1'):
        
        self.name = name
        self.rgb = '[70,70,70]'
        self.level = 0
        self.visibility = 100

        # define shapes
        self.shapes = [
        Circle(radius=900,material_code=23),
        Circle(level=1,radius=620,material_code=24)
        ]


class SampleCoolingTower2(Feature):
    __mapper_args__ = {'polymorphic_identity': 'sample cooling tower 2'}

    def __init__(self,name='sample cooling tower 2'):
        
        self.name = name
        self.rgb = '[70,70,70]'
        self.level = 0
        self.visibility = 100


        # define shapes
        self.shapes = [
        Circle(radius=900,material_code=23),
        Circle(level=1,radius=620,material_code=24)
        ]


class SampleContainment(Feature):
    __mapper_args__ = {'polymorphic_identity': 'sample containment'}

    def __init__(self,name='sample containment 1',visibility=100):
        
        self.name = name
        self.visibility = visibility
        self.rgb = '[70,70,70]'
        self.level = 0

        # define shapes
        self.shapes = [
        Circle(radius=520,rgb=[70,70,70])
        ]


class SampleTurbine(Feature):
    __mapper_args__ = {'polymorphic_identity': 'sample turbine'}

    def __init__(self,name='sample turbine',visibility=100):
        
        self.name = name
        self.visibility = visibility
        self.rgb = '[70,70,70]'
        self.level = 0

        # define shapes
        self.shapes = [
        Rectangle(width=580,length=2220,rgb=[208,40,14])
        ]
        
        self.rules = [
        Rule(oper='axis_offset',value=600)
        ]


class SampleFuel(Feature):
    __mapper_args__ = {'polymorphic_identity': 'sample fuel building'}

    def __init__(self,name='sample fuel building',visibility=100):
        
        self.name = name
        self.visibility = visibility
        self.rgb = '[70,70,70]'
        self.level = 0

        # define shapes
        self.shapes = [
        Rectangle(width=1000,length=1000,rgb=[208,40,14])
        ]



class Plume(Feature):
    __mapper_args__ = {'polymorphic_identity': 'plume'}

    def __init__(self,material_code=None,rgb=[255,255,255],radius=800,level=3,xoff=500,yoff=500,visibility=5):
        self.name = 'Plume'
        self.level = 1
        self.rgb = '[255,255,255]'
        self.visibility = 99

        # define shapes
        self.shapes = [
        Circle(radius=800,rgb=[255,255,255])
        ]

        self.rules = [
        Rule(oper='within',target='sample cooling tower 1',value=500)
        ]

        self.conditions = [
        Condition(table='TimeSeriesPower',oper='greater than',value=0)
        ]


