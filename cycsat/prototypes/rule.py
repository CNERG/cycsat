"""
rule.py

A library of default rule definitions. Rules need a "run" function that returns the
a mask of location it can be placed.
"""
from cycsat.archetypes import Rule2 as Rule
from shapely.ops import cascaded_union

# masks return possible locations, modifiers return modified shapes to place


class WITHIN(Rule):
    __mapper_args__ = {'polymorphic_identity': 'WITHIN'}

    def __init__(self, pattern, value=0):
        """Returns a Feature by "placing it."""
        self.kind = 'mask'
        self.name = 'WITHIN'
        self.pattern = pattern
        self.value = value

    def run(self, Simulator):
        # get targets
        targets = self.depends_on(Simulator)['obj'].tolist()
        mask = cascaded_union(
            [target.footprint(placed=True) for target in targets])

        return {'mask': mask.buffer(int(self.value))}


# class ROTATE(Rule):
#     __mapper_args__ = {'polymorphic_identity': 'ROTATE'}

#     def __init__(self, pattern=None, value=0):
#         """Returns a Feature by "placing it."""
#         self.kind = 'modifier'
#         self.name = 'ROTATE'
#         self.pattern = pattern
#         self.value = value

#     def run(self, Simulator):
#         # get the first found target
#         if pattern
#             targets = self.depends_on(Simulator)['obj'].tolist()
#             if not targets:
#                 return self.feature

#         return None
