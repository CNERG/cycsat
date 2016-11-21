'''

source.py

'''
from cycsat.archetypes import Facility


class SampleSource(Facility):
    __mapper_args__ = {'polymorphic_identity': 'Source'}

    def __init__(self,name='sample source', AgentId=None):

        self.AgentId = AgentId
        self.name = name
        self.width = 500
        self.length = 500

        self.features = [
        ]