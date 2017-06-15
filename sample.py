from cycsat.agent import Agent
from shapely.geometry import Polygon, box, Point
import random

# initalize agents with random values
site = Agent(geometry=box(0, 0, 500, 500), value=1)

parking_lot1 = Agent(geometry=Point(0, 0).buffer(100), value=10)
parking_lot2 = Agent(geometry=box(0, 0, 100, 100), value=10)

site.agents = [parking_lot1, parking_lot2]

for pl in site.agents:
    pl.place(site.geometry)

parking_lot1.agents = [
    Agent(geometry=Point(0, 0).buffer(10), value=random.randint(45, 50)) for i in range(20)]

for a in parking_lot1.agents:
    a.place(parking_lot1.geometry)

parking_lot2.agents = [
    Agent(geometry=Point(0, 0).buffer(10), value=random.randint(45, 50)) for i in range(20)]

for a in parking_lot2.agents:
    a.place(parking_lot2.geometry)
