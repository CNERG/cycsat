from cycsat.archetypes import Facility, Feature, Shape, Rule, Condition
from cycsat.prototypes.shape import Circle, Rectangle


class ByronIL(Facility):
    __mapper_args__ = {'polymorphic_identity': 'ByronIL'}

    def __init__(self):
        self.name = 'Byron, IL'
        self.maxx = 800 * 10
        self.maxy = 800 * 10

        self.features = [
            ConcretePad('concrete pad'),
            CoolingTower(name='cooling tower 1'),
            Containment(name='containment'),
            ContainmentSupport('containment support')
        ]


class ConcretePad(Feature):
    __mapper_args__ = {'polymorphic_identity': 'ByronIL.ConcretePad'}

    def __init__(self, name):
        self.name = name
        self.shapes = [Rectangle(5000, 5000)]


class CoolingTower(Feature):
    __mapper_args__ = {'polymorphic_identity': 'ByronIL.CoolingTower'}

    def __init__(self, name):
        self.name = name
        self.level = 1
        self.shapes = [Circle(radius=960, rgb='[90, 90, 90]')]
        self.rules = [Rule(target='concrete pad', oper='WITHIN')]


class Containment(Feature):
    __mapper_args__ = {'polymorphic_identity': 'ByronIL.Containment1'}

    def __init__(self, name):
        self.name = name
        self.level = 1
        self.shapes = [Circle(radius=280, rgb='[90, 90, 90]')]
        self.rules = [
            Rule(target='cooling tower 1', oper='NEAR', value=0),
            Rule(target='concrete pad', oper='WITHIN')
        ]


class ContainmentSupport(Feature):
    __mapper_args__ = {'polymorphic_identity': 'ByronIL.ContainmentSupport'}

    def __init__(self, name):
        self.name = name
        self.level = 1
        self.shapes = [Rectangle(500, 500)]
        self.rules = [
            Rule(target='cooling tower 1', oper='NEAR', value=0),
            Rule(target='concrete pad', oper='WITHIN'),
            Rule(target='concrete pad', oper='ROTATE', value=100)
        ]
