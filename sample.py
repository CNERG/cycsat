from cycsat.agent import Agent
from cycsat.laboratory import Material

from shapely.geometry import Polygon, box, Point
import random

site = Agent(geometry=box(0, 0, 500, 500), value=100)

circle = Agent(geometry=Point(0, 0).buffer(50), value=50)
circle.agents = [Agent(geometry=Point(0, 0).buffer(5), value=0)
                 for i in range(50)]

site.agents = [circle]


# class CoolingTower(Agent):

#     def __init__(self):
#         self.geometry = Point(0, 0).buffer(10)
#         self.name = 'cooling tower'

#     def run(self, **args):
#         last = self.data.plume[-1]
#         if last == 1:
#             pass
#         else:


# class ConcretePad(Agent):

#     def __init__(self):
#         self.geometry = box(0, 0, 100, 100)
#         self.name = 'concrete pad'
