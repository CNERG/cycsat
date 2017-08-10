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


class Material:
    """An instance for modeling spectral responses and textures."""

    def __init__(self):
        pass

    def observe(self, wavelength):
        try:
            return self.__response__(wavelength)
        except:
            pass


class USGSMaterial(Material):

    def __init__(self, name):
        self.model = pickle.load(
            open('{}/data/spectra/{}.txt'.format(DIR, name), 'rb'))

    def __response__(self, wavelength):
        return list(self.model.predict(wavelength))[0]
