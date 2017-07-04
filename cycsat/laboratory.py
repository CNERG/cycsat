"""
laboratory.py
"""
import pandas as pd
import numpy as np

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

    def __init__(self, wavelengths, relectance, std):

        self.__wavelengths__ = wavelengths
        self.__relectance__ = relectance
        self.__std__ = std

    def measure(self, band=None):
        wavelengths

    def plot(self):
        self.measure()

        std = sample.describe().reflectance.loc['std']
        top = sample.describe().reflectance.loc['75%']
        bottom = sample.describe().reflectance.loc['25%']

        df = sample[(sample.reflectance > bottom) & (sample.reflectance < top)]
        if len(df) == 0:
            df = sample
        ax = df.plot(x='wavelength', y='reflectance')
        ax.set_title(self.name)
        return ax


class USGSMaterial(Material):
    __mapper_args__ = {'polymorphic_identity': 'USGSMaterial'}

    def __init__(self, name, mass=1):
        self.name = name
        self.mass = mass

    def observe(self):
        global Library
        path = Library[Library['name'] == self.name]['path'].iloc[0]
        df = pd.read_table(path, sep='\s+', skiprows=16, header=None,
                           names=['wavelength', 'reflectance', 'std'])

        return df
