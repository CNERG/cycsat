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
        self.level = 0

        # define shapes
        self.shapes = [
        Rectangle(width=6000,length=6000,rgb=[155,155,155])
        ]

        self.rules = [
        Rule(oper='ROTATE',value=120)
        ]


class Truck(Feature):
    __mapper_args__ = {'polymorphic_identity': 'truck'}

    def __init__(self,name='truck'): 
        self.name = name
<<<<<<< HEAD
        self.visibility = 35
=======
        self.visibility = 80
>>>>>>> exploratory
        self.level = 1

        # define shapes
        self.shapes = [
        Rectangle(width=20,length=50,rgb=[208,40,14])
        ]

        self.rules = [
        ]


class SampleCoolingTower1(Feature):
    __mapper_args__ = {'polymorphic_identity': 'cooling tower 1'}

    def __init__(self,name='cooling tower 1'):
        
        self.name = name
        self.level = 1
        self.visibility = 100

        # define shapes
        self.shapes = [
        Circle(radius=900,material_code=23,rgb=[70,70,70]),
        Circle(level=1,radius=620,material_code=24,rgb=[70,70,70])
        ]


class SampleCoolingTower2(Feature):
    __mapper_args__ = {'polymorphic_identity': 'cooling tower 2'}

    def __init__(self,name='cooling tower 2'):
        
        self.name = name
        self.level = 1
        self.visibility = 100

        # define shapes
        self.shapes = [
        Circle(radius=900,material_code=23,rgb=[70,70,70]),
        Circle(level=1,radius=620,material_code=24,rgb=[70,70,70])
        ]

        self.rules = [
        Rule(oper='NEAR',target='cooling tower 1',value=200),
        Rule(oper='AXIS',target='cooling tower 1',direction='X'),
        ]


class SampleContainment1(Feature):
    __mapper_args__ = {'polymorphic_identity': 'containment1'}

    def __init__(self,name='containment1',visibility=100):
        
        self.name = name
        self.visibility = visibility
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
        self.level = 1

        # define shapes
        self.shapes = [
        Circle(radius=520,rgb=[70,70,70])
        ]

        self.rules = [
        Rule(oper='NEAR',target='containment1',value=200),
        Rule(oper='AXIS',direction='Y',target='containment1')
        ]


class Turbine1(Feature):
    __mapper_args__ = {'polymorphic_identity': 'turbine1'}

    def __init__(self,name='turbine1',visibility=100):
        
        self.name = name
        self.visibility = visibility
        self.level = 1

        # define shapes
        self.shapes = [
        Rectangle(width=580,length=2220,rgb=[208,40,14])
        ]
        
        self.rules = [
        Rule(oper='ROTATE',value=0),
        Rule(oper='AXIS',direction='X',target='containment1'),
        Rule(oper='NEAR',target='containment1',value=500)
        ]


class Turbine2(Feature):
    __mapper_args__ = {'polymorphic_identity': 'turbine2'}

    def __init__(self,name='turbine2',visibility=100):
        
        self.name = name
        self.visibility = visibility
        self.level = 1

        # define shapes
        self.shapes = [
        Rectangle(width=580,length=2220,rgb=[208,40,14])
        ]
        
        self.rules = [
        Rule(oper='ROTATE',value=0),
        Rule(oper='AXIS',direction='X',target='containment2'),
        Rule(oper='NEAR',target='containment1',value=500)
        ]



class SampleFuel(Feature):
    __mapper_args__ = {'polymorphic_identity': 'fuel building'}

    def __init__(self,name='pond',visibility=100):
        
        self.name = name
        self.visibility = visibility
        self.level = 1

        # define shapes
        self.shapes = [
        Rectangle(width=1000,length=1000,rgb=[208,40,14])
        ]

        self.rules = [
        Rule(oper='ROTATE',target='concrete pad',value=0)
        ]


class Plume(Feature):
    __mapper_args__ = {'polymorphic_identity': 'plume'}

    def __init__(self,material_code=None,rgb=[255,255,255],radius=800,level=3,xoff=500,yoff=500,visibility=5):
        self.name = 'Plume'
        self.level = 2
        self.visibility = 99

        # define shapes
        self.shapes = [
        Circle(level=3,radius=800,rgb=[255,255,255])
        ]

        self.rules = [
        Rule(oper='WITHIN',target='cooling tower 1',value=600)
        ]

        self.conditions = [
        Condition(table='TimeSeriesPower',oper='greater than',value=0)
        ]


