"""
laboratory.py
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import os
import ast
import pickle

DIR = os.path.dirname(__file__)

USGSLibrary = pd.Series(os.listdir(DIR + '/data/spectra/')
                        ).apply(lambda x: x.replace('.txt', ''))


class Material:
    """An instance for modeling spectral responses and textures."""

    def __init__(self, name, **args):
        self.name = name

    def observe(self, wavelength):
        try:
            relectance = self.__response__(wavelength)
            if relectance < 0:
                return 0
            else:
                return relectance
        except:
            pass


class USGSMaterial(Material):

    def __init__(self, name):
        Material.__init__(self, name)
        self.model = pickle.load(
            open('{}/data/spectra/{}.txt'.format(DIR, name), 'rb'))

    def __response__(self, wavelength):
        return list(self.model.predict(wavelength))[0]
