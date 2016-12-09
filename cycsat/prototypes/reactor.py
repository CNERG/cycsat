"""
prototypes/reactor.py

"""
from cycsat.archetypes import Facility, Feature
from cycsat.prototypes.feature import SampleCoolingTower, SampleContainment
from cycsat.prototypes.feature import SampleTurbine, Lawn


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
        SampleTurbine(),
        Lawn()
        ]

