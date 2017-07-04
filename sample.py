from cycsat.agent import Agent
from cycsat.laboratory import Material, USGSMaterial

from shapely.geometry import Polygon, box, Point
import random


class CoolingTowerBlock(Agent):

    def __init__(self, **variables):
        Agent.__init__(self, **variables)


class CoolingTower(Agent):

    def __init__(self, **variables):
        Agent.__init__(self, **variables)

    def __run__(self):
        if random.choice([True, False]):
            self.on = 1
            self.value += 1
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


site = Agent(geometry=box(0, 0, 1000, 1000), value=0)
cblock = CoolingTowerBlock(geometry=box(0, 0, 500, 500), value=10)
ctower1 = CoolingTower(on=0, geometry=Point(0, 0).buffer(100), value=20)
ctower2 = CoolingTower(on=0, geometry=Point(0, 0).buffer(100), value=20)
plume = Plume(geometry=Point(0, 0).buffer(75), value=100)

cblock.add_agents([ctower1, ctower2])
ctower1.add_agents(plume)
site.add_agents(cblock)

site.place()
