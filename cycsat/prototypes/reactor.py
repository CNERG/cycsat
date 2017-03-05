"""
prototypes/reactor.py
"""
from cycsat.archetypes import Facility, Feature, Rule
from cycsat.prototypes.feature import SampleCoolingTower1, SampleContainment, SampleCoolingTower2
from cycsat.prototypes.feature import Turbine1, ConcretePad, Plume, SampleFuel, Turbine2


class SampleReactor(Facility):
    __mapper_args__ = {'polymorphic_identity': 'Reactor'}

    def __init__(self,name='sample reactor',AgentId=None):

        self.AgentId = AgentId
        self.name = name
        self.width = 862
        self.length = 862

        self.features = [
        ConcretePad(),
        SampleContainment(),
        SampleContainment(name='containment1'),
        Turbine1(),
        Turbine2(),
        SampleCoolingTower1(),
        SampleCoolingTower2(),
        SampleFuel(),
        #Plume()
        ]

        for f in self.features[1:]:
           f.rules.append(Rule(oper='WITHIN',target='concrete pad',value=0))

