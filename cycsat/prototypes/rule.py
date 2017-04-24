"""
rule.py

A library of default rule definitions. Rules need a "run" function that returns the
a mask of location it can be placed.
"""
from cycsat.archetypes import Rule
from shapely.ops import cascaded_union
from shapely.geometry import Point
from shapely.affinity import translate
from shapely.affinity import rotate

import random

# masks return possible locations, modifiers return modified shapes to place


class NEAR(Rule):
    __mapper_args__ = {'polymorphic_identity': 'NEAR'}

    def __init__(self, pattern, value=100):
        """Returns a Feature by "placing it."""
        self.kind = 'mask'
        self.pattern = pattern
        self.value = value

    def run(self, Simulator):
        # get targets
        targets = self.depends_on(Simulator)['obj'].tolist()
        if not targets:
            return self.feature.facility.bounds()
        mask = cascaded_union(
            [target.footprint(placed=True) for target in targets])

        inner_buffer = mask.buffer(int(self.value))
        mask = self.feature.footprint().bounds

        diagaonal_dist = Point(mask[0:2]).distance(Point(mask[2:]))

        buffer_value = diagaonal_dist * 2
        second_buffer = inner_buffer.buffer(buffer_value)
        mask = second_buffer.difference(inner_buffer)

        return mask


class WITHIN(Rule):
    __mapper_args__ = {'polymorphic_identity': 'WITHIN'}

    def __init__(self, pattern, value=0):
        """Returns a Feature by "placing it."""
        self.kind = 'mask'
        self.pattern = pattern
        self.value = value

    def run(self, Simulator):
        # get targets
        targets = self.depends_on(Simulator)['obj'].tolist()
        if not targets:
            return self.feature.facility.bounds()
        mask = cascaded_union(
            [target.footprint(placed=True) for target in targets])

        return mask.buffer(int(self.value))


# class ALIGN(Rule):
#     __mapper_args__ = {'polymorphic_identity': 'ALIGN'}

#     def __init__(self, pattern, value, axis='X'):
#         """Returns a Feature by "placing it."""
#         self.kind = 'mask'
#         self.pattern = pattern
#         self.value = value
#         self.axis = axis

#     def run(self, Simulator):
#         # get targets
#         if self.value:

#         targets = self.depends_on(Simulator)['obj'].tolist()
#         if not targets:
#             return self.feature.facility.bounds()

#         mask = cascaded_union(
#             [target.footprint(placed=True) for target in targets])

#         x_min, y_min, x_max, y_max = mask.bounds

#         site_axis = LineString([[-maxx, 0], [maxx * 2, 0]])

#         if

#         return mask.buffer(int(self.value))


class ROTATE(Rule):
    __mapper_args__ = {'polymorphic_identity': 'ROTATE'}

    def __init__(self, pattern=None, value='random'):
        """Returns a Feature by "placing it."""
        self.kind = 'modifier'
        self.pattern = pattern
        self.value = value

    def run(self, Simulator):
        # if there are any targets get the first angle
        angle = self.rotation = random.randint(-180, 180)
        try:
            angle = int(self.value)
        except:
            if self.pattern:
                targets = self.depends_on(Simulator)['obj'].tolist()
                if targets:
                    angle = targets[0].rotation

        for shape in self.feature.shapes:
            geometry = shape.geometry(placed=True)
            rotated = rotate(geometry, angle,
                             origin='center', use_radians=False)
            shape.placed_wkt = rotated.wkt

        self.feature.rotation = angle
