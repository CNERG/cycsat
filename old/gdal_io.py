import os

import gdal, ogr, os, osr
from osgeo import ogr

import numpy as np

extensions = {
    'GTiff':'.tif'
}

def open_shape(in_file):
    '''reads in a shapefile.'''
    driver = ogr.GetDriverByName('ESRI Shapefile')
    dataSource = driver.Open(in_file, 0)
    return dataSource

def get_bounds(in_file):
    '''return the bounds of a raster dataset.'''

    image = gdal.Open(in_file)

    return image

#############################################################################################################
# Raster data model
############################################################################################################

def raster2array(rasterfn):
    raster = gdal.Open(rasterfn)
    band = raster.GetRasterBand(1)
    array = band.ReadAsArray()
    return array

def array2image(path,array,image_format='GTiff'):

    cols = array.shape[1]
    rows = array.shape[0]

    driver = gdal.GetDriverByName(image_format)

    # add file extension based on driver
    outRaster = driver.Create(path+extensions[image_format], cols, rows, 1, gdal.GDT_Int32)

    outband = outRaster.GetRasterBand(1)
    outband.WriteArray(array)
    
    outband.FlushCache()


