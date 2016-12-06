"""
prototypes.satellite.py

"""
from cycsat.archetypes import Satellite, Instrument
from cycsat.prototypes.instrument import CoastalAerosol, Blue, Green, Red, NIR


class RGB(Satellite):
	"""Simple RGB satellite"""
	__mapper_args__ = {'polymorphic_identity': 'RGB'}

	def __init__(self,name='simple RGB',mmu=150,width=1000,length=1000):
		self.name = name
		self.mmu = mmu
		self.width = width
		self.length = length

		self.instruments = [
    	Blue(mmu=mmu,width=width,length=length),
    	Green(mmu=mmu,width=width,length=length),
    	Red(mmu=mmu,width=width,length=length)
        ]


class LANDSAT8(Satellite):
	"""Model Landsat 8 with first 6 bands"""
	__mapper_args__ = {'polymorphic_identity': 'LANDSAT8'}

	def __init__(self,name='landsat 8',mmu=150,width=1000,length=1000):
		self.name = name
		self.mmu = mmu
		self.width = width
		self.length = length

		self.instruments = [
    	CoastalAerosol(mmu=mmu,width=width,length=length),
    	Blue(mmu=mmu,width=width,length=length),
    	Green(mmu=mmu,width=width,length=length),
    	Red(mmu=mmu,width=width,length=length),
    	NIR(mmu=mmu,width=width,length=length)
        ]
