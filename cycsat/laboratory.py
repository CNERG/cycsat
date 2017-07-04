"""
laboratory.py
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import os
import ast

# opens the USGS library of spectra
cdir, cfile = os.path.split(__file__)
f = os.walk(cdir + '/materials/ASCII')
samples = list()
for path, subdirs, files in f:
    for name in files:
        samples.append(
            [os.path.join(cdir, path.replace('/', '\\'), name), path, name]
        )

Library = pd.DataFrame(samples,
                       columns=['path', 'subdir', 'name']).sort_values('name')


class Material:

    def __init__(self, wavelengths, response, variation, points=10):

        self.wavelengths = wavelengths
        self.response = response
        self.variation = variation
        self.points = points

    def measure(self, band=None):
        values = self.response[
            (self.wavelengths > band[0]) & (self.wavelengths < band[1])]
        variation = self.variation[
            (self.wavelengths > band[0]) & (self.wavelengths < band[1])]

        return [values, variation]

    def plot(self):
        plt.plot(self.wavelengths, self.response)


class USGSMaterial(Material):

    def __init__(self, name):
        path = Library[Library['name'] == name]['path'].iloc[0]
        df = pd.read_table(path, sep='\s+', skiprows=16, header=None,
                           names=['wavelength', 'response', 'variation'])

        Material.__init__(self, df.wavelength, df.response, df.variation)
