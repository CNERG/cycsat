'''

enrichment.py

'''
from cycsat.archetypes import Facility

class SampleEnrichment(Facility):
    __mapper_args__ = {'polymorphic_identity': 'Enrichment'}

    def __init__(self,name='sample enrichment',AgentId=None):

        self.AgentId = AgentId
        self.name = name
        self.width = 500
        self.length = 500

        self.features = [
        ]
