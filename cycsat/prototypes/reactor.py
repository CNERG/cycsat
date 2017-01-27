"""
prototypes/reactor.py
"""
from cycsat.archetypes import Facility, Feature
from cycsat.prototypes.feature import SampleCoolingTower, SampleContainment
from cycsat.prototypes.feature import SampleTurbine, Lawn, SitePad


class SampleReactor(Facility):
    __mapper_args__ = {'polymorphic_identity': 'Reactor'}

    def __init__(self,name='sample reactor',AgentId=None):

        self.AgentId = AgentId
        self.name = name
        self.width = 862
        self.length = 862

        self.features = [
        SitePad(order=1),
        SampleCoolingTower(order=2),
        SampleCoolingTower(order=2),
        SampleContainment(order=2),
        SampleContainment(order=2),
        SampleTurbine(order=2)
        ]

