from cycsat.agent import Agent
from cycsat.rules import NEAR, ALIGN, SET
from cycsat.geometry import grid, LoadFootprints
from cycsat.laboratory import Material

from shapely.geometry import Polygon, box, Point
import random
import matplotlib.pyplot as plt

from cycsat.laboratory import USGSMaterial


class CoolingTowerBlock(Agent):

    def __init__(self, **variables):
        Agent.__init__(self, **variables)
        self.__material__ = USGSMaterial('Concrete_WTC01-37A_ASDFRa_AREF')


class CoolingTower(Agent):

    def __init__(self, **variables):
        Agent.__init__(self, **variables)
        self.__material__ = USGSMaterial(
            'Brick_GDS354_Building_Lt_Gry_ASDFRa_AREF')

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
        Agent.__init__(self, name='Plume', **variables)
        self.__material__ = USGSMaterial('Melting_snow_mSnw01a_ASDFRa_AREF')

    def __run__(self):

        if self.parent.on == 1:
            self.place_in(self.parent.relative_geo.buffer(5))
            return True
        else:
            self.geometry = None
            return False


site = Agent(geometry=box(0, 0, 1000, 1000), name='Site', value=100)
site.set_material(USGSMaterial('Lawn_Grass_GDS91_green_BECKa_AREF'))

cblock = CoolingTowerBlock(geometry=box(0, 0, 500, 500), value=10)
cblock.add_rule(SET('CoolingTower 2', '$parent$', x=0.30, y=0.30, padding=10))
cblock.add_rule(NEAR('CoolingTower 1', 'CoolingTower 2', value=50))
cblock.add_rule(ALIGN('CoolingTower 1', 'CoolingTower 2', axis='x'))
cblock.add_rule(ALIGN('Turbine 3', 'CoolingTower 1', axis='y'))

buildings = LoadFootprints(
    'north-america-us-wisconsin', size=2, random_state=3)
buildings = Agent(geometry=buildings.iloc[0], value=10)
# buildings = buildings.apply(lambda x: Agent(geometry=x, value=10))
# buildings.apply(lambda x: x.set_material(
#     USGSMaterial('Asphalt_Tar_GDS346_Blck_Roof_ASDFRa_AREF')))
buildings.set_material(USGSMaterial(
    'Asphalt_Tar_GDS346_Blck_Roof_ASDFRa_AREF'))

turbine = Agent(name='Turbine', geometry=box(0, 0, 50, 100), value=0)
turbine.set_material(USGSMaterial('Asphalt_Tar_GDS346_Blck_Roof_ASDFRa_AREF'))

ctower1 = CoolingTower(on=0, geometry=Point(0, 0).buffer(75), value=20)
ctower2 = CoolingTower(on=0, geometry=Point(0, 0).buffer(75), value=20)
plume = Plume(geometry=Point(0, 0).buffer(50), value=100)

cblock.add_agents([ctower1, ctower2, turbine])
cblock.add_agent(buildings, scale=True, scale_ratio=0.20)
ctower1.add_agent(plume)
site.add_agent(cblock)

# # 25 test builds
# fig, axes = plt.subplots(5, 5)
# axes = axes.flatten()

# for ax in axes:
#     ax.set_aspect('equal')
#     site.place()
#     site.agenttree.plot(ax=ax)
