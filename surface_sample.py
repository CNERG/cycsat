from cycsat.agent import Agent
from cycsat.laboratory import Material, USGSMaterial

from shapely.geometry import Polygon, box, Point
import random


class CtrlPt(Agent):

    def __init__(self):
        geo = Point(0, 0).buffer(5)
        val = random.randint(-500, 500)

        Agent.__init__(self, geometry=geo, value=val)

    def __run__(self):
        self.value += (np.random.normal(self.value) * random.choice([-1, 1]))

surface = Agent(geometry=box(0, 0, 500, 500), value=0)
pts = [CtrlPt() for i in range(200)]

surface.add_agents(pts)
surface.place()

# from scipy.ndimage.filters import gaussian_filter
# out = surface.render('value')

# a = gaussian_filter(out, sigma=10)

w = np.arange(10)
m = Material(w, w * 2, np.random.rand(10))
