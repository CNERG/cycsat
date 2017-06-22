from cycsat.agent import Agent
from cycsat.laboratory import Material

from shapely.geometry import Polygon, box, Point
import random

a = Agent()

# class Site(Agent):

#     def __init__(self):
#         Agent.__init__(self)
#         self.geometry = box(0, 0, 500, 500)


# class CoolingTower(Agent):

#     def __init__(self):
#         Agent.__init__(self)
#         self.geometry = Point(0, 0).buffer(50)
#         self.name = 'cooling tower'


# class Plume(Agent):

#     def __init__(self):
#         Agent.__init__(self)
#         self.geometry = Point(0, 0).buffer(25)
#         self.name = 'plume'

#     def __evaluate__(self, **args):

#         if args['parent_agent'].on:
#             return args['parent_agent'].geometry.buffer(100)

#     def __run__(self, **args):
#         valid = self.evaluate(args['parent_agent'])
#         spawn_zone = valid.centroid.buffer(50)


# site = Site()
# ctower = CoolingTower()
# plume = Plume()

# ctower.agents = [plume]
# site.agents = [ctower]
