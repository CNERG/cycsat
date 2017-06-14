from cycsat.archetypes import Agent
from shapely.geometry import Polygon, box, Point

# initalize agents with random values
site = Agent(geometry=box(0, 0, 100, 100))
site.sub_agents = [Agent(geometry=Point(0, 0).buffer(10))]
