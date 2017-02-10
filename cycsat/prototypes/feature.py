"""
prototpyes/feature.py
"""
from cycsat.archetypes import Shape, Feature, Rule
from cycsat.prototypes.shapes import Circle, Rectangle, Plume


class ConcretePad(Feature):
    __mapper_args__ = {'polymorphic_identity': 'concrete pad'}

    def __init__(self,name='concrete pad'):
        
        self.name = name
        self.visibility = 100
        self.rgb = [155,155,155]

        # define shapes
        self.shapes = [
        Rectangle(width=6000,length=6000)
        ]


# class Truck(Feature):
#     __mapper_args__ = {'polymorphic_identity': 'truck'}

#     def __init__(self,name='sample truck',visibility=100):
        
#         self.name = name
#         self.visibility = visibility

#         # define shapes
#         self.shapes = [
#         Rectangle(radius=900,material=materialize(rgb=[146,149,1]))
#         ]


class SampleCoolingTower1(Feature):
    __mapper_args__ = {'polymorphic_identity': 'sample cooling tower 1'}

    def __init__(self,name='sample cooling tower 1'):
        
        self.name = name
        self.rgb = [70,70,70]

        # define shapes
        self.shapes = [
        Circle(radius=900,material_code=23),
        Circle(level=1,radius=620,material_code=24),
        Plume(level=2,radius=800,rgb=[255,255,255],xoff=500,yoff=500)
        ]


class SampleCoolingTower2(Feature):
    __mapper_args__ = {'polymorphic_identity': 'sample cooling tower 2'}

    def __init__(self,name='sample cooling tower 2'):
        
        self.name = name
        self.rgb = [70,70,70]

        # define shapes
        self.shapes = [
        Circle(radius=900,material_code=23),
        Circle(level=1,radius=620,material_code=24),
        Plume(level=2,radius=800,rgb=[255,255,255],xoff=500,yoff=500)
        ]


class SampleContainment(Feature):
    __mapper_args__ = {'polymorphic_identity': 'sample containment'}

    def __init__(self,name='sample containement',visibility=100):
        
        self.name = name
        self.visibility = visibility
        self.rgb = [70,70,70]

        # define shapes
        self.shapes = [
        Circle(radius=520,rgb=[70,70,70])
        ]


class SampleTurbine(Feature):
    __mapper_args__ = {'polymorphic_identity': 'sample turbine'}

    def __init__(self,name='sample turbine',visibility=100):
        
        self.name = name
        self.visibility = visibility
        self.rgb = [70,70,70]

        # define shapes
        self.shapes = [
        Rectangle(width=580,length=2220,rgb=[208,40,14])
        ]



