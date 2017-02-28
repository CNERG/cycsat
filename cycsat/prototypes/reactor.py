"""
prototypes/reactor.py
"""
from cycsat.archetypes import Facility, Feature, Rule
from cycsat.prototypes.feature import SampleCoolingTower1, SampleContainment, SampleCoolingTower2
from cycsat.prototypes.feature import SampleTurbine, ConcretePad, Plume, SampleFuel


class SampleReactor(Facility):
    __mapper_args__ = {'polymorphic_identity': 'Reactor'}

    def __init__(self,name='sample reactor',AgentId=None):

        self.AgentId = AgentId
        self.name = name
        self.width = 862
        self.length = 862

        self.features = [
        ConcretePad(),
        SampleContainment(name='containment1'),
        SampleContainment(name='containment2'),
        SampleTurbine(),
        SampleTurbine(),
        SampleCoolingTower1(),
        SampleCoolingTower2(),
        SampleFuel(),
        Plume()
        ]

        for f in self.features:
            f.rules.append(Rule(oper='WITHIN',target='concrete pad',value=0))

