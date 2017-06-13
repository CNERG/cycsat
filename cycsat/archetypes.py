from geopandas import GeoDataFrame


class Agent:

    def __init__(self, **args):
        # clear log
        self.data = GeoDataFrame()
        self.log(**args)

    def log(self, **args):
        # set current attributes
        for arg in args:
            setattr(self, arg, args[arg])

        # archive attributes
        self.data = self.data.append(args, ignore_index=True)

    def run(self, **args):
        self.log(**args)
