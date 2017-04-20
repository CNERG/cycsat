"""
rule.py

A library of default rule definitions. Rules need a "run" function that returns the
a mask of location it can be placed.
"""
from cycsat.archetypes import Rule2 as Rule


class WITHIN(Rule):
    __mapper_args__ = {'polymorphic_identity': 'WITHIN'}

    def __init__(self, value):
        """Returns a Feature by "placing it."""
        self.name = 'WITHIN'

    def run(self):

        return self.feature.facility.bounds()
