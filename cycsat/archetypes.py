from geopandas import GeoDataFrame
import random


class Agent:

    def __init__(self, **args):
        # clear log
        self.data = GeoDataFrame()
        self.log(**args)

    def log(self, **args):
        # set and log initial attributes
        for arg in args:
            setattr(self, arg, args[arg])

        # archive attributes
        self.data = self.data.append(args, ignore_index=True)

    def run(self, **args):
        # update attributes
        value = self.value + random.randint(-5., 5)

        # record attributes
        self.log(value=value)
