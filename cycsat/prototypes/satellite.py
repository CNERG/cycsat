"""
prototypes.satellite.py

"""
from cycsat.archetypes import Satellite, Instrument
from cycsat.prototypes.instrument import CoastalAerosol, Blue, Green, Red, NIR


class RGB(Satellite):
	"""Simple RGB satellite"""
	__mapper_args__ = {'polymorphic_identity': 'RGB'}

	def __init__(self,name='simple RGB',mmu=150,ifov_width=1000,ifov_length=1000):
		self.name = name
		self.mmu = mmu
		self.ifov_width = ifov_width
		self.ifov_length = ifov_length

		self.instruments = [
    	Blue(mmu=mmu,ifov_width=ifov_width,ifov_length=ifov_length),
    	Green(mmu=mmu,ifov_width=ifov_width,ifov_length=ifov_length),
    	Red(mmu=mmu,ifov_width=ifov_width,ifov_length=ifov_length)
        ]


class LANDSAT8(Satellite):
	"""Model Landsat 8 with first 6 bands"""
	__mapper_args__ = {'polymorphic_identity': 'LANDSAT8'}

	def __init__(self,name='landsat 8',mmu=150,ifov_width=1000,ifov_length=1000):
		self.name = name
		self.mmu = mmu
		self.ifov_width = ifov_width
		self.ifov_length = ifov_length

		self.instruments = [
    	CoastalAerosol(mmu=mmu,ifov_width=ifov_width,ifov_length=ifov_length),
    	Blue(mmu=mmu,ifov_width=ifov_width,ifov_length=ifov_length),
    	Green(mmu=mmu,ifov_width=ifov_width,ifov_length=ifov_length),
    	Red(mmu=mmu,ifov_width=ifov_width,ifov_length=ifov_length),
    	NIR(mmu=mmu,ifov_width=ifov_width,ifov_length=ifov_length)
        ]
