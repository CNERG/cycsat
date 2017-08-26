from cycsat.agent import Agent
from cycsat.rules import NEAR, ALIGN, SET, SIDE
from cycsat.geometry import grid, LoadFootprints
from cycsat.laboratory import Material
from cycsat.laboratory import USGSMaterial

from shapely.geometry import Polygon, box, Point
import geopandas as gpd


class CoolingTowerBlock(Agent):

    def __init__(self, **variables):
        Agent.__init__(self, **variables)
        self._material = USGSMaterial('Concrete_WTC01-37A_ASDFRa_AREF')


class CoolingTower(Agent):

    def __init__(self, **variables):
        Agent.__init__(self, **variables)
        self._material = USGSMaterial(
            'Brick_GDS354_Building_Lt_Gry_ASDFRa_AREF')

    def _run(self, state):
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
        self._material = USGSMaterial('Melting_snow_mSnw01a_ASDFRa_AREF')
        self.level = 1

    def _run(self, state):

        if self.parent.on == 1:
            self.place_in(self.parent.relative_geo.buffer(5), restrict=False)
            return True
        else:
            self.geometry = None
            return False


water = Agent(name='Water', floating=True,
              geometry=Point(0, 0).buffer(100), value=0)
water.set_material(USGSMaterial('Marsh_water55%..._CRMS121v47_ASDFRa_AREF'))

site = Agent(geometry=box(0, 0, 1000, 1000), name='Site', value=100)
site.set_material(USGSMaterial('Lawn_Grass_GDS91_green_BECKa_AREF'))
site.add_rule(SIDE('Water', value=0))

cblock = CoolingTowerBlock(geometry=box(0, 0, 500, 500), value=10)
cblock.add_rule(SET('CoolingTower', x=0.30, y=0.30, padding=10))
cblock.add_rule(NEAR('CoolingTower 1', 'CoolingTower', value=50))
cblock.add_rule(ALIGN('CoolingTower 1', 'CoolingTower', axis='x'))
cblock.add_rule(ALIGN('Turbine', 'CoolingTower', axis='y'))

buildings = gpd.read_file('samples/sample.shp').head(8)
buildings = buildings.geometry.apply(lambda x: Agent(geometry=x, value=10))

buildings.apply(lambda x: x.set_material(
    USGSMaterial('Asphalt_Tar_GDS346_Blck_Roof_ASDFRa_AREF')))

turbine = Agent(name='Turbine', geometry=box(0, 0, 50, 100), value=0)
turbine.set_material(USGSMaterial('Asphalt_Tar_GDS346_Blck_Roof_ASDFRa_AREF'))

ctower1 = CoolingTower(on=0, geometry=Point(0, 0).buffer(75), value=20)
ctower2 = CoolingTower(on=0, geometry=Point(0, 0).buffer(75), value=20)
plume = Plume(geometry=Point(0, 0).buffer(50), value=100)

cblock.add_agents([water, ctower1, ctower2, turbine])
cblock.add_agents(buildings.tolist(), scale_ratio=0.10)
ctower1.add_agent(plume)
site.add_agents([cblock])
