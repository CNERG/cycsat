"""
prototypes/reactor.py
"""
from cycsat.archetypes import Facility, Feature, Rule
from cycsat.prototypes.feature import SampleCoolingTower1, SampleContainment2, SampleCoolingTower2,Truck
from cycsat.prototypes.feature import Turbine1, ConcretePad, Plume, SampleFuel, Turbine2, SampleContainment1


class SampleReactor(Facility):
    __mapper_args__ = {'polymorphic_identity': 'Reactor'}

    def __init__(self,name='sample reactor',AgentId=None):

        self.AgentId = AgentId
        self.name = name
        self.width = 862
        self.length = 862

        self.features = [
        ConcretePad(),
        Truck(),
        SampleContainment1(),
        SampleContainment2(),
        Turbine1(),
        Turbine2(),
        SampleCoolingTower1(),
        SampleCoolingTower2(),
        SampleFuel(),
        Plume()
        ]

        for f in self.features[1:]:
           f.rules.append(Rule(oper='WITHIN',target='concrete pad',value=0))
           f.rules.append(Rule(oper='ROTATE',target='concrete pad'))

