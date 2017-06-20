from geopandas import GeoDataFrame
import numpy as np
import random
import rasterio

from skimage.draw import polygon

from shapely.geometry import Point
from shapely.affinity import rotate, translate


class Agent:

    def __init__(self, **args):
        # clear the log and add init arguments
        self.data = GeoDataFrame()
        self.log(**args)

        # spatial rules
        self.rules = list()
        self.agents = list()

    @property
    def subdata(self):
        """Collects the current attributes of all agents by cascading."""
        log = self.data.tail(1)
        for agent in self.agents:
            log = log.append(agent.subdata, ignore_index=True)
        return log

    def surface(self, value_field):
        """Generates a blank raster surface."""
        minx, miny, maxx, maxy = [round(coord)
                                  for coord in self.geometry.bounds]

        image = np.zeros((maxx - minx, maxy - miny)) + \
            getattr(self, value_field)

        return image

    def collect_surfaces(self, value_field, image=[], res=1):

        # if no image is provided create a blank
        if len(image) == 0:
            image = self.surface(value_field)
            # else add the agent to the image
        else:
            coords = np.array(list(self.geometry.exterior.coords))
            rr, cc = polygon(coords[:, 0], coords[:, 1], image.shape)
            image[rr, cc] = getattr(self, value_field)

        # if there are agents add their surfaces too
        if self.agents:
            for agent in self.agents:
                image = agent.collect_surfaces(value_field, image=image)

        return image

    def place(self, region, attempts=100):
        """Places the agent randomly into a region."""
        for i in range(attempts):
            placement = posit_point(region, attempts=attempts)
            if placement:
                x, y = [placement.coords.xy[0][0], placement.coords.xy[1][0]]
                _x, _y = [self.geometry.centroid.coords.xy[0][
                    0], self.geometry.centroid.coords.xy[1][0]]
                shift_x = x - _x
                shift_y = y - _y

                geometry = translate(self.geometry, xoff=shift_x, yoff=shift_y)
                if geometry.within(region):
                    self.log(geometry=translate(
                        self.geometry, xoff=shift_x, yoff=shift_y))
                    return True
        return False

    def log(self, **args):
        """Record information about the agent."""

        # set and log initial attributes
        for arg in args:
            setattr(self, arg, args[arg])

        # archive attributes
        self.data = self.data.append(args, ignore_index=True)

    def run(self, **args):
        # update attributes
        value = self.value + random.randint(-5., 5)
        self.log(value=value)


def posit_point(mask, attempts=1000):
    """Generates a random point within a mask."""
    x_min, y_min, x_max, y_max = mask.bounds

    for i in range(attempts):
        x = random.uniform(x_min, x_max + 1)
        y = random.uniform(y_min, y_max + 1)
        posited_point = Point(x, y)

        if posited_point.within(mask):
            return posited_point
