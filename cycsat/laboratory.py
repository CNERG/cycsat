"""
laboratory.py

Defines the material class for modeling the response of surfaces.
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

    def __init__(self, name, **args):
        """The Material class.

        This class is for modeling the response of materials.
        """
        self.name = name

    def observe(self, **args):
        """Attempts to return the user-defined _response function.
        """
        try:
            relectance = self._response(**args)
            if relectance < 0:
                return 0
            else:
                return relectance
        except:
            print('error rendering material.')
            pass

# -------------------------------------------------
# Material library
# -------------------------------------------------


class USGSMaterial(Material):

    def __init__(self, name):
        """Uses the USGS Spectral Library to model the reflectance response
        to wavelengths.

        Parameters:
        ----------
        name - the name of the material model
        ----------
        """
        Material.__init__(self, name)
        self.model = pickle.load(
            open('{}/data/spectra/{}.txt'.format(DIR, name), 'rb'))

    def _response(self, wavelength, **args):
        return list(self.model.predict(wavelength))[0]
