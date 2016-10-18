"""
geometry.py

"""
from shapely.geometry import Polygon, Point

building = Polygon([(300, 300), (480, 320), (380, 430), (220, 590)])

def build_site():
	'''
	Builds a site by fixing the placement of all it's features and giving them geometries.

	for feature in site.features:
		check if overlap
		place feature

	'''
	pass