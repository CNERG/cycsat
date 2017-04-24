from cycsat.archetypes import Facility, Feature, Shape, Rule, Condition
from cycsat.prototypes.shape import Circle, Rectangle
from cycsat.prototypes.rule import WITHIN, ROTATE, NEAR
import random

# -----------------------------------------------------------------------------------------------
# Site and feature definitions
# -----------------------------------------------------------------------------------------------


class ByronIL(Facility):
    __mapper_args__ = {'polymorphic_identity': 'ByronIL'}

    def __init__(self):
        self.name = 'Byron, IL'
        self.maxx = 700 * 10
        self.maxy = 700 * 10

        self.features = [
            ConcretePad('concrete pad'),
            CoolingTower('1 cooling tower'),
            Containment('1 containment'),
            Containment('2 containment'),
            ContainmentSupport('support containment 1',
                               '1 containment', 500, 500),
            ContainmentSupport('support containment 2',
                               '2 containment', 500, 700),
            ParkingLot('parking lot'),
            Plume('plume 1')
        ]

        for x in range(5):
            t = Truck('truck ' + str(x + 1))
            self.features.append(t)


class ConcretePad(Feature):
    __mapper_args__ = {'polymorphic_identity': 'ByronIL.ConcretePad'}

    def __init__(self, name):
        self.name = name
        self.shapes = [Rectangle(4000, 4000, rgb='[209,209,209]')]

        self.rules = [ROTATE()]


class CoolingTower(Feature):
    __mapper_args__ = {'polymorphic_identity': 'ByronIL.CoolingTower'}

    def __init__(self, name):
        self.name = name
        self.level = 1
        self.shapes = [Circle(radius=350, rgb='[88, 88, 88]', level=1),
                       Circle(radius=750, rgb='[96, 96, 96]', level=0)]

        self.rules = [WITHIN(pattern='concrete', value=-300)]


class Containment(Feature):
    __mapper_args__ = {'polymorphic_identity': 'ByronIL.Containment1'}

    def __init__(self, name):
        self.name = name
        self.level = 1
        self.shapes = [Circle(radius=280, rgb='[90, 90, 90]')]
        self.rules = [
            NEAR(pattern='1 cooling tower', value=-50),
            WITHIN(pattern='concrete')
        ]


class ContainmentSupport(Feature):
    __mapper_args__ = {'polymorphic_identity': 'ByronIL.ContainmentSupport'}

    def __init__(self, name, support, w, l):
        self.name = name
        self.level = 1
        self.shapes = [Rectangle(w, l, rgb='[85,85,85]')]
        self.rules = [
            NEAR(pattern=support, value=0),
            WITHIN(pattern='concrete'),
            ROTATE(pattern='concrete')
        ]


class ParkingLot(Feature):
    __mapper_args__ = {'polymorphic_identity': 'ByronIL.ParkingLot'}

    def __init__(self, name):
        self.name = name
        self.level = 1
        self.shapes = [
            Rectangle(1000, 800, rgb='[150,150,150]'),
        ]
        self.rules = [WITHIN(pattern='concrete pad'),
                      ROTATE(pattern='concrete pad'),
                      NEAR(pattern='1 cooling tower', value=0)
                      ]


class Plume(Feature):
    __mapper_args__ = {'polymorphic_identity': 'ByronIL.Plume'}

    def __init__(self, name):
        self.name = name
        self.level = 4
        self.visibility = 98
        self.shapes = [
            Circle(650, level=4)
        ]
        self.rules = [
            WITHIN(pattern='1 cooling tower', value=300)
        ]

        self.conditions = [
            Condition(table='TimeSeriesPower', oper='greater than', value=0)
        ]


class Truck(Feature):
    __mapper_args__ = {'polymorphic_identity': 'ByronIL.Truck'}

    def __init__(self, name):
        self.name = name
        self.level = 2
        self.visibility = 50
        rgb = random.choice(['[22,29,163]', '[163,43,22]'])
        self.shapes = [
            Rectangle(30, 15, rgb=rgb),
        ]
        self.rules = [
            WITHIN(pattern='parking lot')
        ]


# -----------------------------------------------------------------------------------------------
# Spatial Rule defintions
# -----------------------------------------------------------------------------------------------


# -----------------------------------------------------------------------------------------------
# Condition defintions
# -----------------------------------------------------------------------------------------------
