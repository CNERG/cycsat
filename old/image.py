import os

import numpy as np

import gdal, ogr, os, osr
from osgeo import ogr

extensions = {
    'GTiff':'.tif'
}

def array_to_image(path,array,image_format='GTiff'):

    cols = array.shape[1]
    rows = array.shape[0]

    driver = gdal.GetDriverByName(image_format)

    # add file extension based on driver
    outRaster = driver.Create(path+extensions[image_format], cols, rows, 1, gdal.GDT_Int32)

    outband = outRaster.GetRasterBand(1)
    outband.WriteArray(array)
    
    outband.FlushCache()
