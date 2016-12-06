"""
prototpyes.instrument.py

"""
from cycsat.archetypes import Instrument


class CoastalAerosol(Instrument):
    __mapper_args__ = {'polymorphic_identity': 'CoastalAerosol'}

    def __init__(self,mmu=300,width=1000,length=1000):

        self.name = 'coastal aerosol'
        self.min_spectrum = 0.43
        self.max_spectrum = 0.45
        self.mmu = mmu
        self.width = width
        self.length = length

class Blue(Instrument):
    __mapper_args__ = {'polymorphic_identity': 'Blue'}

    def __init__(self,mmu=300,width=1000,length=1000):

        self.name = 'blue band'
        self.min_spectrum = 0.45
        self.max_spectrum = 0.51
        self.mmu = mmu
        self.width = width
        self.length = length


class Green(Instrument):
    __mapper_args__ = {'polymorphic_identity': 'Green'}

    def __init__(self,mmu=300,width=1000,length=1000):

        self.name = 'green band'
        self.min_spectrum = 0.53
        self.max_spectrum = 0.59
        self.mmu = mmu
        self.width = width
        self.length = length


class Red(Instrument):
    __mapper_args__ = {'polymorphic_identity': 'Red'}

    def __init__(self,mmu=300,width=1000,length=1000):

        self.name = 'red band'
        self.min_spectrum = 0.64
        self.max_spectrum = 0.67
        self.mmu = mmu
        self.width = width
        self.length = length


class NIR(Instrument):
    __mapper_args__ = {'polymorphic_identity': 'NIR'}

    def __init__(self,mmu=300,width=1000,length=1000):

        self.name = 'nir band'
        self.min_spectrum = 0.85
        self.max_spectrum = 0.88
        self.mmu = mmu
        self.width = width
        self.length = length


