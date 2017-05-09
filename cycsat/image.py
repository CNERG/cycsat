"""
image.py
"""
import shapely
import json
import ast

from skimage.transform import resize, downscale_local_mean
from skimage.draw import polygon
from shapely.geometry import Polygon, Point

import shapely
import numpy as np

import gdal


extensions = {
    'GTiff': '.tif'
}


class Sensor(object):

    def __init__(self, Instrument, method=''):
        """Initiate a sensor instance.

        Keyword arguments:
        InstrumentList -- List of instruments instance to draw the image
        method -- 'normal' (random normal distribution around mean) or 'mean'
        """
        self.Instrument = Instrument

        width = Instrument.width * 10
        length = Instrument.length * 10
        self.ifov = Instrument.geometry()

        self.name = Instrument.name
        self.mmu = Instrument.mmu
        self.min_spectrum = float(Instrument.min_spectrum)
        self.max_spectrum = float(Instrument.max_spectrum)

        self.foreground = self.background.copy()

        self.wavelength = (np.arange(281) / 100) + 0.20
        self.method = method

    def reset(self):
        """Resets the capture array to the background array"""
        self.foreground = self.background.copy()

    def calibrate(self, Site, method='normal'):
        """Generates a sensor with all the static shapes"""

        # for static shapes
        self.background = np.zeros((width, length), dtype=np.uint8)

        # add all the static (in level order) to the image
        for shape in self.shapes:
            if shape.visibility != 100:
                continue
            if shape.level in shape_stack:
                shape_stack[shape.level].append(shape)
            else:
                shape_stack[shape.level] = [shape]

        for level in sorted(shape_stack):
            for shape in shape_stack[level]:
                shape.materialize()
                add_shape(self, shape, background=True)

    def capture_shape(self, Shape, geometry='focused'):
        """Adds a shape to the foreground image"""
        add_shape(self, Shape, geometry=geometry, background=False)

    def write(self, path, img_format='GTiff'):
        """Writes an image using GDAL

        Keyword arguments:
        path -- the path to write the image
        img_format -- the GDAL format
        """
        origin = 0

        rows = round(self.foreground.shape[-2] / self.mmu)
        cols = round(self.foreground.shape[-1] / self.mmu)

        driver = gdal.GetDriverByName(img_format)

        outRaster = driver.Create(
            path + extensions[img_format], cols, rows, 1, gdal.GDT_Byte)
        outRaster.SetGeoTransform(
            (origin, self.mmu, 0, origin, 0, self.mmu * -1))

        outband = outRaster.GetRasterBand(1)
        if (self.mmu > 1):
            band_array = downscale_local_mean(
                self.foreground, (self.mmu, self.mmu))
            band_array = resize(band_array, (rows, cols), preserve_range=True)
        else:
            band_array = self.foreground

        outband.WriteArray(band_array)
        outband.FlushCache()


def add_shape(Sensor, Shape, background=True):
    """Adds a shape to the sensor objects image, by default the background image"""

    image = Sensor.foreground
    if background:
        image = Sensor.background

    geometry = Shape.geometry(placed=True)
    value = Shape.material.measure(
        wl_min=Sensor.min_spectrum, wl_max=Sensor.max_spectrum)

    # mask = (Sensor.wavelength >= Sensor.min_spectrum) & (Sensor.wavelength <= Sensor.max_spectrum)
    # spectrum = material[mask]
    # value = round(spectrum.mean())

    coords = np.array(list(geometry.exterior.coords))
    rr, cc = polygon(coords[:, 0], coords[:, 1], image.shape)

    image[rr, cc] = value


def write_array(array, path, mmu=1, img_format='GTiff'):
    """Writes an image using GDAL

    Keyword arguments:
    path -- the path to write the image
    img_format -- the GDAL format
    """
    origin = 0

    rows = round(array.shape[-2] / mmu)
    cols = round(array.shape[-1] / mmu)

    driver = gdal.GetDriverByName(img_format)

    outRaster = driver.Create(
        path + extensions[img_format], cols, rows, 1, gdal.GDT_Byte)
    outRaster.SetGeoTransform((origin, mmu, 0, origin, 0, mmu * -1))

    outband = outRaster.GetRasterBand(1)
    if (mmu > 1):
        band_array = downscale_local_mean(array, (mmu, mmu))
        band_array = resize(band_array, (rows, cols), preserve_range=True)
    else:
        band_array = array

    outband.WriteArray(band_array)
    outband.FlushCache()
