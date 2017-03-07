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

        self.rules = [
        #Rule(oper='ROTATE',value=0)
        ]


class SampleCoolingTower1(Feature):
    __mapper_args__ = {'polymorphic_identity': 'cooling tower 1'}

    def __init__(self,name='cooling tower 1'):
        
        self.name = name
        self.rgb = '[70,70,70]'
        self.level = 1
        self.visibility = 100

        # define shapes
        self.shapes = [
        Circle(radius=900,material_code=23),
        Circle(level=1,radius=620,material_code=24)
        ]


class SampleCoolingTower2(Feature):
    __mapper_args__ = {'polymorphic_identity': 'cooling tower 2'}

    def __init__(self,name='cooling tower 2'):
        
        self.name = name
        self.rgb = '[70,70,70]'
        self.level = 1
        self.visibility = 100


        # define shapes
        self.shapes = [
        Circle(radius=900,material_code=23),
        Circle(level=1,radius=620,material_code=24)
        ]

        self.rules = [
        #Rule(oper='NEAR',target='cooling tower 1',value=300),
        #Rule(oper='AXIS',target='cooling tower 1',direction='X'),
        ]


class SampleContainment1(Feature):
    __mapper_args__ = {'polymorphic_identity': 'containment1'}

    def __init__(self,name='containment1',visibility=100):
        
        self.name = name
        self.visibility = visibility
        self.rgb = '[70,70,70]'
        self.level = 1

        # define shapes
        self.shapes = [
        Circle(radius=520,rgb=[70,70,70])
        ]


class SampleContainment2(Feature):
    __mapper_args__ = {'polymorphic_identity': 'containment2'}

    def __init__(self,name='containment2',visibility=100):
        
        self.name = name
        self.visibility = visibility
        self.rgb = '[70,70,70]'
        self.level = 1

        # define shapes
        self.shapes = [
        Circle(radius=520,rgb=[70,70,70])
        ]

        self.rules = [
        #Rule(oper='NEAR',target='containment1',value=100),
        #Rule(oper='AXIS',target='containment1',direction='X')
        ]


class Turbine1(Feature):
    __mapper_args__ = {'polymorphic_identity': 'turbine1'}

    def __init__(self,name='turbine1',visibility=100):
        
        self.name = name
        self.visibility = visibility
        self.rgb = '[70,70,70]'
        self.level = 1

        # define shapes
        self.shapes = [
        Rectangle(width=580,length=2220,rgb=[208,40,14])
        ]
        
        self.rules = [
        #Rule(oper='ROTATE',value=0)
        #Rule(oper='ALINE',direction='Y',target='containment1'),
        #Rule(oper='NEAR',target='containment1',value=500)
        ]


class Turbine2(Feature):
    __mapper_args__ = {'polymorphic_identity': 'turbine2'}

    def __init__(self,name='turbine2',visibility=100):
        
        self.name = name
        self.visibility = visibility
        self.rgb = '[70,70,70]'
        self.level = 1

        # define shapes
        self.shapes = [
        Rectangle(width=580,length=2220,rgb=[208,40,14])
        ]
        
        self.rules = [
        #Rule(oper='AXIS',direction='X',target='turbine1'),
        #Rule(oper='ROTATE',value=0),
        #Rule(oper='NEAR',target='turbine1',value=10)
        ]



class SampleFuel(Feature):
    __mapper_args__ = {'polymorphic_identity': 'fuel building'}

    def __init__(self,name='pond',visibility=100):
        
        self.name = name
        self.visibility = visibility
        self.rgb = '[25,23,143]'
        self.level = 1

        # define shapes
        self.shapes = [
        Rectangle(width=1000,length=1000,rgb=[208,40,14])
        ]

        self.rules = [
        #Rule(oper='ROTATE',value=0)
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
        #Rule(oper='WITHIN',target='cooling tower 1',value=500)
        ]

        self.conditions = [
        Condition(table='TimeSeriesPower',oper='greater than',value=0)
        ]


