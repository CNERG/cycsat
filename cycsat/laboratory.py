"""
laboratory.py
"""
import pandas as pd
import numpy as np

from scipy.ndimage import gaussian_filter
from scipy.interpolate import griddata, interp2d, bisplrep, Rbf

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

    def __init__(self, wavelengths=None, relectance=None, std=None):
        pass

    def plot(self):
        sample = self.measure()

        std = sample.describe().reflectance.loc['std']
        top = sample.describe().reflectance.loc['75%']
        bottom = sample.describe().reflectance.loc['25%']

        df = sample[(sample.reflectance > bottom) & (sample.reflectance < top)]
        if len(df) == 0:
            df = sample
        ax = df.plot(x='wavelength', y='reflectance')
        ax.set_title(self.name)
        return ax

    def measure(self):
        try:
            return self.observe()

        except:
            try:
                rgb = self.shape.get_rgb()
            except:
                rgb = [random.randint(0, 255) for i in range(3)]

            wavelength = (np.arange(281) / 100) + 0.20
            reflectance = np.zeros(281)
            reflectance[(wavelength >= 0.64) & (wavelength <= 0.67)] = rgb[0]
            reflectance[(wavelength >= 0.53) & (wavelength <= 0.59)] = rgb[1]
            reflectance[(wavelength >= 0.45) & (wavelength <= 0.51)] = rgb[2]
            std = np.zeros(281)

            return pd.DataFrame({'wavelength': wavelength,
                                 'reflectance': reflectance,
                                 'std': std})


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
