from geopandas import GeoSeries
from pandas import pandas


class RowObj(GeoSeries):

    def __init__(self):
        GeoSeries.__init__(self)

r = RowObj()
