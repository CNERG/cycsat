'''
prototypes/reactor.py

'''

from cycsat.archetypes import Facility, Feature
from cycsat.prototypes.shapes import Circle, Rectangle, Plume

from cycsat.image import materialize

'''
facility prototypes
'''

class SampleReactor(Facility):
    __mapper_args__ = {'polymorphic_identity': 'Reactor'}

    def __init__(self,name='sample reactor',AgentId=None):

        self.AgentId = AgentId
        self.name = name
        self.width = 862
        self.length = 877

        self.features = [
        SampleCoolingTower(),
        SampleCoolingTower(),
        SampleContainment(),
        SampleContainment(),
        SampleTurbine()
        ]


'''
feature prototypes
'''

class SampleCoolingTower(Feature):
    '''
    '''
    __mapper_args__ = {'polymorphic_identity': 'sample cooling tower'}

    def __init__(self,name='sample cooling tower',visibility=100):
        
        self.name = name
        self.visibility = visibility

        # define shapes
        self.shapes = [
        Circle(radius=900,material=materialize(rgb=[146,149,1])),
        Circle(level=1,radius=620,material=materialize(rgb=[79,81,84])),
        Plume(level=2,radius=800,material=materialize(rgb=[255,255,255]),xoff=500,yoff=500)
        ]


class SampleContainment(Feature):
    '''
    '''
    __mapper_args__ = {'polymorphic_identity': 'sample containment'}

    def __init__(self,name='sample containement',visibility=100):
        
        self.name = name
        self.visibility = visibility

        # define shapes
        self.shapes = [
        Circle(radius=520,material=materialize(rgb=[70,70,70]))
        ]


class SampleTurbine(Feature):
    '''
    '''
    __mapper_args__ = {'polymorphic_identity': 'sample turbine'}

    def __init__(self,name='sample turbine',visibility=100):
        
        self.name = name
        self.visibility = visibility

        # define shapes
        self.shapes = [
        Rectangle(width=580,length=2220,material=materialize(rgb=[208,40,14]))
        ]


