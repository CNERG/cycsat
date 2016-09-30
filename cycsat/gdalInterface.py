import gdal, ogr, os, osr
import numpy as np

def array2GTiff(newRasterfn,rasterOrigin,pixelWidth,pixelHeight,array):
	'''Writes a single array to a raster.'''

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

def raster2array(rasterfn):
    raster = gdal.Open(rasterfn)
    band = raster.GetRasterBand(1)
    array = band.ReadAsArray()
    return array