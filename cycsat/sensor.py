"""
sensor.py

Contains tools for writing scenes.

"""

import gdal
import numpy as np
from skimage.draw import circle, set_color

extensions = {
    'GTiff':'.tif'
}

# draw a site
# 1. take a site's dems and draw a basemap
# 2. get all the features from the site that are "static"


def array_to_image(path,array,image_format='GTiff'):

    rows = array.shape[-2]
    cols = array.shape[-1]

    driver = gdal.GetDriverByName(image_format)

    # add file extension based on driver
    outRaster = driver.Create(path+extensions[image_format], cols, rows, 1, gdal.GDT_Int32)

    # write bands
    outband = outRaster.GetRasterBand(1)
    outband.WriteArray(array)
    outband.FlushCache()




