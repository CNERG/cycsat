import os

import gdal, ogr, os, osr

from osgeo import ogr

import shapefile
import numpy as np

import fiona
import shapely

import rasterio

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

def array2GTiff(newRasterfn,rasterOrigin,pixelWidth,pixelHeight,array):

    cols = array.shape[1]
    rows = array.shape[0]
    
    originX = rasterOrigin[0]
    originY = rasterOrigin[1]

    driver = gdal.GetDriverByName('GTiff')

    outRaster = driver.Create(newRasterfn, cols, rows, 1, gdal.GDT_Byte)

    outRaster.SetGeoTransform((originX, pixelWidth, 0, originY, 0, pixelHeight))

    outband = outRaster.GetRasterBand(1)
    outband.WriteArray(array)
    
    outRasterSRS = osr.SpatialReference()
    outRasterSRS.ImportFromEPSG(4326)
    outRaster.SetProjection(outRasterSRS.ExportToWkt())
    
    outband.FlushCache()

