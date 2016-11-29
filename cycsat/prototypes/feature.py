"""
prototpyes.feature.py

"""
from cycsat.archetypes import Shape, Feature

class Truck(Feature):
    __mapper_args__ = {'polymorphic_identity': 'truck'}

    def __init__(self,name='sample truck',visibility=100):
        
        self.name = name
        self.visibility = visibility

        # define shapes
        self.shapes = [
        Rectangle(radius=900,material=materialize(rgb=[146,149,1]))
        ]