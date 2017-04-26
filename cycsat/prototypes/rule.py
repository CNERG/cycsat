"""
rule.py

A library of default rule definitions. Rules need a "run" function that returns the
a mask of location it can be placed.
"""
from cycsat.archetypes import Rule
from shapely.ops import cascaded_union
from shapely.geometry import Point, LineString
from shapely.affinity import translate
from shapely.affinity import rotate

import random


class OUTSIDE(Rule):
    """Allows a feature to appear outside the facility bounds."""
    __mapper_args__ = {'polymorphic_identity': 'OUTSIDE'}

    def __init__(self, value=10000):
        """Returns a Feature by "placing it."""
        self.kind = 'restrict'
        self.pattern = None
        self.value = value

    def run(self, Simulator):
        return self.feature.facility.bounds().buffer(int(self.value))


class NEAR(Rule):
    __mapper_args__ = {'polymorphic_identity': 'NEAR'}

    def __init__(self, pattern, value=100):
        """Returns a Feature by "placing it."""
        self.kind = 'restrict'
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
        self.kind = 'restrict'
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


class XALIGN(Rule):
    __mapper_args__ = {'polymorphic_identity': 'XALIGN'}

    def __init__(self, pattern=None, value=None):
        """Returns a Feature by "placing it."""
        self.kind = 'place'
        self.pattern = pattern
        self.value = value

    def run(self, Simulator):
        # get targets
        maxy = self.feature.facility.maxy
        if self.value:
            line = LineString([[int(self.value), 0], [int(self.value), maxy]])

        else:
            targets = self.depends_on(Simulator)['obj'].tolist()
            if not targets:
                return self.feature.facility.bounds()

            mask = cascaded_union(
                [target.footprint(placed=True) for target in targets])
            x_min, y_min, x_max, y_max = mask.bounds

            value = (x_max - x_min) + x_min
            line = LineString([[value, 0], [value, maxy]])

        return line.buffer(10)


class ROTATE(Rule):
    __mapper_args__ = {'polymorphic_identity': 'ROTATE'}

    def __init__(self, pattern=None, value='random'):
        """Returns a Feature by "placing it."""
        self.kind = 'transform'
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
