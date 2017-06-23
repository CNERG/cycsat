from cycsat.agent import Agent
from cycsat.laboratory import Material

from shapely.geometry import Polygon, box, Point
import random


class Site(Agent):

    def __init__(self, variables):
        Agent.__init__(self, **variables)


class CoolingTower(Agent):

    def __init__(self, **variables):
        Agent.__init__(self, **variables)

    def __run__(self):
        if random.choice([True, False]):
            self.on = 1
            print('on')
        else:
            print('off')
            self.on = 0
        return True


class Plume(Agent):

    def __init__(self, **variables):
        Agent.__init__(self, **variables)

    def __run__(self):

        if self.parent.on == 1:
            self.place_in(self.parent.geometry.buffer(100))
            return True
        else:
            return False


site = Agent(geometry=box(0, 0, 500, 500))
ctower = CoolingTower(on=0, geometry=Point(0, 0).buffer(100))
plume = Plume(geometry=Point(0, 0).buffer(75))

ctower.add_agents(plume)
site.add_agents(ctower)
