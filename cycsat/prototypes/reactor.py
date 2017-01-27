"""
prototypes/reactor.py
"""
from cycsat.archetypes import Facility, Feature
from cycsat.prototypes.feature import SampleCoolingTower1, SampleContainment
from cycsat.prototypes.feature import SampleTurbine


class SampleReactor(Facility):
    __mapper_args__ = {'polymorphic_identity': 'Reactor'}

    def __init__(self,name='sample reactor',AgentId=None):

        self.AgentId = AgentId
        self.name = name
        self.width = 862
        self.length = 862

        self.features = [
        SampleCoolingTower1(),
        SampleCoolingTower1(),
        SampleContainment(),
        SampleContainment(),
        SampleTurbine()
        ]

