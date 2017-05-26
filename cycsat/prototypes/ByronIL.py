from cycsat.archetypes import Site, Observable, Shape, Rule, Condition
from cycsat.prototypes.shape import Circle, Rectangle
from cycsat.prototypes.rule import WITHIN, ROTATE, NEAR
from cycsat.prototypes.rule import OUTSIDE, XALIGN, YALIGN, DISPURSE_PLUME
from cycsat.laboratory import USGSMaterial
import random

from cycsat.terrain import simple

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
            Water(maxx=self.maxx, maxy=self.maxy),
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
            self.observables.append(t)


class Water(Observable):
    __mapper_args__ = {'polymorphic_identity': 'ByronIL.Water'}

    def __init__(self, maxx, maxy,  name='terrain'):
        self.name = name
        self.level = -1
        self.shapes = [simple(maxx, maxy)]

        self.rules = [
        ]


class ConcretePad(Observable):
    __mapper_args__ = {'polymorphic_identity': 'ByronIL.ConcretePad'}

    def __init__(self, name):
        self.name = name

        building = Rectangle(4000, 4000, rgb='[209,209,209]')
        building.materials.append(USGSMaterial('concrete_wtc01-37a.27883.asc'))
        self.shapes = [building]

        self.rules = [
        ]


class CoolingTower(Observable):
    __mapper_args__ = {'polymorphic_identity': 'ByronIL.CoolingTower'}

    def __init__(self, name):
        self.name = name
        self.level = 1

        building = Circle(radius=750, rgb='[96, 96, 96]', level=1)
        building.materials.append(USGSMaterial('concrete_gds375.27862.asc'))
        self.shapes = [building]

        self.rules = [WITHIN(pattern='concrete', value=0)]


class Containment(Observable):
    __mapper_args__ = {'polymorphic_identity': 'ByronIL.Containment1'}

    def __init__(self, name):
        self.name = name
        self.level = 1

        building = Circle(radius=280, rgb='[90, 90, 90]')
        building.materials.append(USGSMaterial('concrete_gds375.27862.asc'))
        self.shapes = [building]

        self.shapes = [building]
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

        building = Rectangle(w, l, rgb='[85,85,85]')
        building.materials.append(USGSMaterial('concrete_gds375.27862.asc'))
        self.shapes = [building]

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

        parking_lot = Rectangle(1000, 800, rgb='[150,150,150]')
        parking_lot.materials.append(USGSMaterial('concrete_gds375.27862.asc'))

        self.shapes = [parking_lot]
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
