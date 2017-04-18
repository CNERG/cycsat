from cycsat.archetypes import Facility, Feature, Shape, Rule, Condition
from cycsat.prototypes.shape import Circle, Rectangle


class ByronIL(Facility):
    __mapper_args__ = {'polymorphic_identity': 'ByronIL'}

    def __init__(self):
        self.name = 'Byron, IL'
        self.width = 914 * 10
        self.length = 1149 * 10

        self.features = [
            CoolingTower1(),
            CoolingTower2()]


class CoolingTower1(Feature):
    __mapper_args__ = {'polymorphic_identity': 'ByronIL.CoolingTower1'}

    def __init__(self):
        self.name = 'cooling tower 1'
        self.shapes = [Circle(radius=960, rgb='[90, 90, 90]')]


class CoolingTower2(Feature):
    __mapper_args__ = {'polymorphic_identity': 'ByronIL.CoolingTower2'}

    def __init__(self):
        self.name = 'cooling tower 2'
        self.shapes = [Circle(radius=960, rgb='[90, 90, 90]')]
        self.rules = [Rule(target='cooling tower 1', oper='NEAR', value=100)]
