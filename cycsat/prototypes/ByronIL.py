from cycsat.archetypes import Facility, Feature, Shape, Rule, Condition
from cycsat.prototypes.shape import Circle, Rectangle


class ByronIL(Facility):
    __mapper_args__ = {'polymorphic_identity': 'ByronIL'}

    def __init__(self):
        self.name = 'Byron, IL'
        self.maxx = 914 * 10
        self.maxy = 1149 * 10

        self.features = [
            CoolingTower(name='test'),
            CoolingTower(name='test2')]


class CoolingTower(Feature):
    __mapper_args__ = {'polymorphic_identity': 'ByronIL.CoolingTower'}

    def __init__(self, name):
        self.name = name
        self.shapes = [Circle(radius=960, rgb='[90, 90, 90]')]


class Containment1(Feature):
    __mapper_args__ = {'polymorphic_identity': 'ByronIL.Containment1'}

    def __init__(self):
        self.name = 'containment 1'
        self.shapes = [Circle(radius=960, rgb='[90, 90, 90]')]
        self.rules = [Rule(target='cooling tower 1', oper='NEAR', value=100)]
