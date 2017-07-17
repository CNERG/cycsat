"""
laboratory.py
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import os
import ast


class Material:
    """An instance for modeling spectral responses and textures."""

    def __init__(self):
        pass

    def observe(self, **args):
        try:
            self.response(**args)
        except:

    def __response__(self, **args):
        """DEFINED"""
        pass
