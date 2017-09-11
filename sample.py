"""
This sample file demonstrates how to set up a cycsat simulation.
"""
# import the Agent class
from cycsat.agent import Agent

# import the Rule classes that will be used for placing sub-agents
from cycsat.rules import NEAR, ALIGN, SET, SIDE

# import the LoadFootprints function for loading building footprints
from cycsat.geometry import LoadFootprints

# import the USGS material class for modeling materials (i.e. grass, cement)
from cycsat.laboratory import USGSMaterial

# import Shapely, Gsieopandas libraries for creating geometry for agents
# and plotting.
from shapely.geometry import Polygon, box, Point
import geopandas as gpd

# There are a two options for creating Agents.
# The simplest way is to create an Agent instance. The site agent will
# contain all other agents.
site = Agent(geometry=box(0, 0, 1000, 1000), name='Site', value=100)

# This sets the material of the site.
site.set_material(USGSMaterial('Lawn_Grass_GDS91_green_BECKa_AREF'))

# add a placement rule that places the sub-agent named 'Water' along the
# side of the site agent
site.add_rule(SIDE('Water', value=0))

# The other way to create Agents is define new Agent classes that inherit
# the Agent class (see below). This is useful for creating Agent
# templates when several Agents with the same properties are needed and
# for defining an Agent's _run function (see CoolingTower).


class CoolingTowerBlock(Agent):

    def __init__(self, **variables):
        Agent.__init__(self, **variables)
        self._material = USGSMaterial('Concrete_WTC01-37A_ASDFRa_AREF')


class CoolingTower(Agent):

    def __init__(self, **variables):
        Agent.__init__(self, **variables)
        self._material = USGSMaterial(
            'Brick_GDS354_Building_Lt_Gry_ASDFRa_AREF')

    # Defining the _run function of an Agent will define what this Agent will do when it is
    # run. The _run function does not need to return anything.
    def _run(self, state):
        if random.choice([True, False]):
            self.on = 1
            self.value += 1
        else:
            self.on = 0


class Plume(Agent):

    def __init__(self, **variables):
        Agent.__init__(self, name='Plume', **variables)
        self._material = USGSMaterial('Melting_snow_mSnw01a_ASDFRa_AREF')
        self.level = 1

    # the Plume Agent will "turn on" or "turn off" depending on if its parent
    # Agent (the CoolingTower) has an attribute of on that is equal to 1 or 0.
    def _run(self, state):
        if self.parent.on == 1:
            self.turn_on()  # This makes the Agent visible
            self.place_in(self.parent.relative_geo.buffer(5), restrict=False)
        else:
            self.turn_off()  # This hides the Agent

# Here a shapefile of building footprints is loaded and 8 footprints are
# selected. Using GeoPandas the shapes are converted to Agents with a
# material of asphalt.
buildings = gpd.read_file('samples/sample.shp').head(8)
buildings = buildings.geometry.apply(lambda x: Agent(geometry=x, value=10))
buildings.apply(lambda x: x.set_material(
    USGSMaterial('Asphalt_Tar_GDS346_Blck_Roof_ASDFRa_AREF')))

water = Agent(name='Water',
              geometry=Point(0, 0).buffer(100), value=0)
water.set_material(USGSMaterial('Marsh_water55%..._CRMS121v47_ASDFRa_AREF'))

cblock = CoolingTowerBlock(geometry=box(0, 0, 500, 500), value=10)
cblock.add_rule(SET('CoolingTower', x=0.30, y=0.30, padding=10))
cblock.add_rule(NEAR('CoolingTower 1', 'CoolingTower', value=50))
cblock.add_rule(ALIGN('CoolingTower 1', 'CoolingTower', axis='x'))
cblock.add_rule(ALIGN('Turbine', 'CoolingTower', axis='y'))

turbine = Agent(name='Turbine', geometry=box(0, 0, 50, 100), value=0)
turbine.set_material(USGSMaterial('Asphalt_Tar_GDS346_Blck_Roof_ASDFRa_AREF'))

ctower1 = CoolingTower(on=0, geometry=Point(0, 0).buffer(75), value=20)
ctower2 = CoolingTower(on=0, geometry=Point(0, 0).buffer(75), value=20)
plume = Plume(geometry=Point(0, 0).buffer(50), value=100)

# Here agents are added to their parents the CoolingTowerBlock contains
# several agents
cblock.add_agents([water, ctower1, ctower2, turbine])
cblock.add_agents(buildings.tolist(), scale_ratio=0.10)

# CoolingTower 1 Agent has a plume
ctower1.add_agent(plume)

# Add the CoolingTowerBlock (which contains all the Agents) to the site.
site.add_agents([cblock])

# Build the site (place all the agents according to rules) with
# detailed information.
site.build(verbose=True)
