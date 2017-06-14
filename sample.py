from cycsat.agent import Agent
from shapely.geometry import Polygon, box, Point

# initalize agents with random values
site = Agent(geometry=box(0, 0, 500, 500))

parking_lot1 = Agent(geometry=box(0, 0, 100, 100))
parking_lot2 = Agent(geometry=box(0, 0, 100, 100))

site.sub_agents = [parking_lot1, parking_lot2]

for pl in site.sub_agents:
    pl.place(site.geometry)

parking_lot1.sub_agents = [
    Agent(geometry=Point(0, 0).buffer(5)) for i in range(100)]

for a in parking_lot1.sub_agents:
    a.place(parking_lot1.geometry)

parking_lot2.sub_agents = [
    Agent(geometry=Point(0, 0).buffer(5)) for i in range(100)]

for a in parking_lot2.sub_agents:
    a.place(parking_lot2.geometry)
