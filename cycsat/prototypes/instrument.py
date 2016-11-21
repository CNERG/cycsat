'''

instrument.py

'''
from cycsat.archetypes import Instrument


class RedBand(Instrument):
    __mapper_args__ = {'polymorphic_identity': 'RedBand'}

    def __init__(self,mmu=1):

        self.name = 'red band'
        self.min_spectrum = 0.64
        self.max_spectrum = 0.67
        self.mmu = mmu

class BlueBand(Instrument):
    __mapper_args__ = {'polymorphic_identity': 'BlueBand'}

    def __init__(self,mmu=1):

        self.name = 'blue band'
        self.min_spectrum = 0.45
        self.max_spectrum = 0.51
        self.mmu = mmu

class GreenBand(Instrument):
    __mapper_args__ = {'polymorphic_identity': 'GreenBand'}

    def __init__(self,mmu=1):

        self.name = 'green band'
        self.min_spectrum = 0.53
        self.max_spectrum = 0.59
        self.mmu = mmu
