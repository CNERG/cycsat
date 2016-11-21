'''

satellite.py

'''
from cycsat.archetypes import Satellite, Instrument
from cycsat.prototypes.instrument import RedBand, GreenBand, BlueBand


class StandardRGB(Satellite):
    __mapper_args__ = {'polymorphic_identity': 'StandardRGB'}

    def __init__(self,name='standard RGB satellite'):

    	self.name = name
    	self.instruments = [
    	RedBand(),
    	GreenBand(),
    	BlueBand()
        ]

