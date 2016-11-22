"""
prototypes.satellite.py

"""
from cycsat.archetypes import Satellite, Instrument
from cycsat.prototypes.instrument import CoastalAerosol, Blue, Green, Red, NIR


class RGB(Satellite):
	"""Simple RGB satellite"""
	__mapper_args__ = {'polymorphic_identity': 'RGB'}

	def __init__(self,name='simple RGB',mmu=150):

		self.name = name
		self.mmu = mmu

		self.instruments = [
    	Blue(mmu=mmu),
    	Green(mmu=mmu),
    	Red(mmu=mmu)
        ]


class LANDSAT8(Satellite):
	"""Model Landsat 8 with first 6 bands"""
	__mapper_args__ = {'polymorphic_identity': 'LANDSAT8'}

	def __init__(self,name='mock LANDSAT 8',mmu=300):
		self.name = name
		self.mmu = mmu

		self.instruments = [
    	CoastalAerosol(mmu=mmu),
    	Blue(mmu=mmu),
    	Green(mmu=mmu),
    	Red(mmu=mmu),
    	NIR(mmu=mmu)
        ]
