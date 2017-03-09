"""

DEMO input file for cysat.

"""
from cysat.geometry import Polygon, Point
from cycsat.archetypes import Facility, Feature, Rule, Condition

tower_1 = Feature()
tower_1.name = 'cooling_tower 1'
tower_1.level = 1

reactor = Facility()
reactor.name = 'demo reactor'
reactor.features = [tower_1]

