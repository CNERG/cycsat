'''

sink.py

'''
from cycsat.archetypes import Facility


class SampleSink(Facility):
    __mapper_args__ = {'polymorphic_identity': 'Sink'}

    def __init__(self,name='sample sink', AgentId=None):

    	self.AgentId = AgentId
    	self.name = name
    	self.width = 500
    	self.length = 500

    	self.features = [
        ]