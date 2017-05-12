from cycsat.archetypes import Site, Observable, Shape, Rule, Condition
from cycsat.prototypes.shape import Circle, Rectangle
from cycsat.prototypes.rule import WITHIN, ROTATE, NEAR
from cycsat.prototypes.rule import OUTSIDE, XALIGN, YALIGN, DISPURSE_PLUME
import random

from cycsat.terrain import simple_land

# -----------------------------------------------------------------------------------------------
# Site and feature definitions
# -----------------------------------------------------------------------------------------------


class ByronIL(Site):
    __mapper_args__ = {'polymorphic_identity': 'ByronIL'}

    def __init__(self):
        self.name = 'Byron, IL'
        self.maxx = 700 * 10
        self.maxy = 700 * 10

        self.observables = [
            Land(maxx=self.maxx, maxy=self.maxy),
            ConcretePad('concrete pad'), ]
        #     CoolingTower('1 cooling tower'),
        #     Containment('1 containment'),
        #     Containment('2 containment'),
        #     ContainmentSupport('support containment 1',
        #                        '1 containment', 500, 500),
        #     ContainmentSupport('support containment 2',
        #                        '2 containment', 500, 700),
        #     ParkingLot('parking lot'),
        #     Plume('plume 1')
        # ]

        # for x in range(5):
        #     t = Truck('truck ' + str(x + 1))
        #     self.observables.append(t)


class Land(Observable):
    __mapper_args__ = {'polymorphic_identity': 'ByronIL.Land'}

    def __init__(self, maxx, maxy,  name='land'):
        self.name = name
        self.level = -1
        self.shapes = [simple_land(maxx, maxy)]

        self.rules = [
        ]


class ConcretePad(Observable):
    __mapper_args__ = {'polymorphic_identity': 'ByronIL.ConcretePad'}

    def __init__(self, name):
        self.name = name
        self.shapes = [Rectangle(4000, 4000, rgb='[209,209,209]')]

        self.rules = [
        ]


class CoolingTower(Observable):
    __mapper_args__ = {'polymorphic_identity': 'ByronIL.CoolingTower'}

    def __init__(self, name):
        self.name = name
        self.level = 1
        self.shapes = [Circle(radius=350, rgb='[88, 88, 88]', level=2),
                       Circle(radius=750, rgb='[96, 96, 96]', level=1)]

        self.rules = [WITHIN(pattern='concrete', value=0)]


class Containment(Observable):
    __mapper_args__ = {'polymorphic_identity': 'ByronIL.Containment1'}

    def __init__(self, name):
        self.name = name
        self.level = 1
        self.shapes = [Circle(radius=280, rgb='[90, 90, 90]')]
        self.rules = [WITHIN(pattern='concrete', value=0)
                      ]

        if name == '2 containment':
            self.rules += [
                NEAR(pattern='1 containment', value=0),
                YALIGN(pattern='1 containment')
            ]


class ContainmentSupport(Observable):
    __mapper_args__ = {'polymorphic_identity': 'ByronIL.ContainmentSupport'}

    def __init__(self, name, support, w, l):
        self.name = name
        self.level = 1
        self.shapes = [Rectangle(w, l, rgb='[85,85,85]')]
        self.rules = [
            WITHIN(pattern='concrete')
        ]

        if name == 'support containment 1':
            self.rules.append(
                XALIGN(pattern='1 containment')
            )
        else:
            self.rules.append(
                XALIGN(pattern='2 containment')
            )


class ParkingLot(Observable):
    __mapper_args__ = {'polymorphic_identity': 'ByronIL.ParkingLot'}

    def __init__(self, name):
        self.name = name
        self.level = 1
        self.shapes = [
            Rectangle(1000, 800, rgb='[150,150,150]'),
        ]
        self.rules = [WITHIN(pattern='concrete pad')]


class Plume(Observable):
    __mapper_args__ = {'polymorphic_identity': 'ByronIL.Plume'}

    def __init__(self, name):
        self.name = name
        self.level = 4
        self.visibility = 95
        self.shapes = [
            Circle(500, level=4)
        ]
        self.rules = [
            XALIGN(pattern='1 cooling tower'),
            YALIGN(pattern='1 cooling tower'),
            DISPURSE_PLUME()
        ]

        self.conditions = [
            Condition(table='TimeSeriesPower', oper='greater than', value=0)
        ]


class Truck(Observable):
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
