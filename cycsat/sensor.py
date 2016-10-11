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

def array_to_image(path,array,image_format='GTiff'):

    cols = array.shape[1]
    rows = array.shape[0]

    driver = gdal.GetDriverByName(image_format)

    # add file extension based on driver
    outRaster = driver.Create(path+extensions[image_format], cols, rows, 1, gdal.GDT_Int32)

    outband = outRaster.GetRasterBand(1)
    outband.WriteArray(array)
    
    outband.FlushCache()


class Basemap(object):
    '''
    The canvas object.

    Attributes:
        name: A descriptive name.
        width: The with of the canvas in pixels

    '''
    def __init__(self,name,w,l,mmu=1):
        self.name = name
        self.mmu = mmu
        
        self.data = np.zeros((w,l),dtype=np.int32)

    def change_mmu(self,mmu):
        '''Change the minimim mapping unit (pixel size in meters).'''
        self.mmu = mmu

    def draw(self,path,image_format='GTiff'):
        '''Draws the canvas saving it as an image.'''
        array_to_image(path,self.data,image_format=image_format)

    def add_circle(self,x,y,radius,value):

        rr, cc = circle(x,y,radius)
        set_color(self.data, (rr, cc), 2)