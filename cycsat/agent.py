from geopandas import GeoDataFrame
import random


class Agent:

    def __init__(self, **args):
        # clear the log and add init arguments
        self.data = GeoDataFrame()
        self.log(**args)

        # spatial rules
        self.rules = list()
        self.sub_agents = list()

    @property
    def subs(self):
        log = GeoDataFrame()
        for sa in self.sub_agents:
            log = log.append(sa.data.tail(1), ignore_index=True)
        return log

    def place(self, region, attempts=100):

        for i in range(attempts):
            posit_point(mask)

            typology_checks = list()

            loc = shape.place(posited_point, simulation, timestep)

            typology_checks.append(loc.geometry.within(results['restrict']))

            if False not in typology_checks:
                self.site.build.database.save(self)
                self.morph(simulation, timestep)
                return True

            print(
                self.name, 'placement failed after {', attempts, '} attempts.')
            return False

    print('point placement failed after {', attempts, '} attempts.')
    return False

    def log(self, **args):
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
