"""
rule.py

A library of default rule definitions. Rules need a "run" function that returns the
a mask of location it can be placed.
"""
from cycsat.archetypes import Rule2 as Rule

from shapely.ops import cascaded_union


class WITHIN(Rule):
    __mapper_args__ = {'polymorphic_identity': 'WITHIN'}

    def __init__(self, pattern, value=0):
        """Returns a Feature by "placing it."""
        self.name = 'WITHIN'
        self.pattern = pattern
        self.value = value

    def run(self, Simulator):
        targets = self.depends_on(Simulator)['obj'].tolist()
        mask = cascaded_union(
            [target.footprint(placed=True) for target in targets])

        return {'mask': mask.buffer(int(self.value))}
