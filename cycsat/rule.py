"""
rules.py

Defines the Rule class for placing agents according to rules.
"""
from shapely.ops import nearest_points
from shapely.geometry import LineString, Point, box

from .geometry import calulate_shift, longest_side


class Rule:

    def __init__(self, target, dep='parent', **args):
        """Rule class.

        This class represents a method for placing a
        "target" agent in relation to a "dependent" agent. Rule intances are
        added to agents for the placement of their sub-agents. Evaluating the rule
        instance returns a valid area for placement.

        Parameter
        ---------
        target : string
                The name of the target agent to apply the rule to

        dep : string or 'parent', default: 'parent'
                The name of the dependent agent to use to evaluate the rule.
                The default ('parent') sets the dependent agent to the parent agent itself.
        ---------
        """
        self._target = target
        self._dep = dep
        self.agent = False
        self.args = args
        for arg in args:
            setattr(self, arg, args[arg])

    def __repr__(self):
        return '<"{}" {} "{}" {}>'.format(self._target,
                                          self.__class__.__name__,
                                          self._dep,
                                          self.args)

    @property
    def target(self):
        try:
            return [i for i in self.agent.agents if i.name == self._target][0]
        except:
            return False

    @property
    def dependent_on(self):
        try:
            if self._dep == 'parent':
                if self.target.parent:
                    return self.target.parent
        except:
            pass
        try:
            return [i for i in self.agent.agents if i.name == self._dep][0]
        except:
            return False

    def evaluate(self):
        """Evaluates the rule and returns a valid region for placement."""
        try:
            return self._evaluate()
        except BaseException as e:
            print(e)
            return False

# -------------------------------------------------
# DEFINED RULES
# -------------------------------------------------


class SET(Rule):

    def __init__(self, target, dep='parent', x=0, y=0, padding=10):
        """Returns a relative position within the target agent's parent.

        Parameter
        ---------
        x : float, 1 >= x >= -1, default: 0
                The relative x position. 0 means the center 1
                means the far right and -1 means the far left of the
                parent.

        y : float, 1 >= x >= -1, default: 0
                The relative y postion (see above).

        padding : float, default: 10
                The padding for placement
        ---------
        """
        Rule.__init__(self, target, dep, x=x, y=y, padding=padding)

    def _evaluate(self):
        parent = self.dependent_on.relative_geo
        minx, miny, maxx, maxy = parent.bounds
        parent_bounds = box(minx, miny, maxx, maxy)
        shift_x = (maxx - minx) * self.x
        shift_y = (maxy - miny) * self.y
        center_x, center_y = parent_bounds.centroid.x, parent_bounds.centroid.y
        center_x += shift_x
        center_y += shift_y
        return Point(center_x, center_y).buffer(self.padding)


class SIDE(Rule):

    def __init__(self, target, dep='parent', value=100):
        """Returns the side area from within a parent agent.

        Parameter
        ---------
        value : float, default: 100
                Buffer value
        ---------
        """
        Rule.__init__(self, target, dep, value=value)

    def _evaluate(self):
        parent = self.dependent_on.relative_geo
        outer_buffer = parent.buffer(self.value * -1)
        band_width = longest_side(self.target.geometry) * 0.10
        inner_buffer = outer_buffer.buffer(band_width * -1)
        return outer_buffer.difference(inner_buffer)


class NEAR(Rule):

    def __init__(self, target, dep='parent', value=100):
        """Returns a valid area near a dependent agent to place the target agent.

        Parameter
        ---------
        value : float, default: 100
                Buffer value
        ---------
        """
        Rule.__init__(self, target, dep, value=value)

    def _evaluate(self):
        inner_buffer = self.dependent_on.geometry.buffer(self.value)
        outer_buffer = inner_buffer.buffer(100)
        return outer_buffer.difference(inner_buffer)


class ALIGN(Rule):

    def __init__(self, target, dep='parent', axis='x'):
        """Align the target agent to the same axis as the dependent agent.

        Parameter
        ---------
        axis : {'x', 'y'}, default: 'x'
                The axis to align by, i.e. 'x' or 'y'
        ---------
        """
        Rule.__init__(self, target, dep, axis=axis)

    def _evaluate(self):
        value = getattr(self.dependent_on.geometry.centroid, self.axis)
        if self.axis == 'x':
            maxy = self.target.parent.geometry.bounds[-1]
            line = LineString([[value, 0], [value, maxy]])
        else:
            maxx = self.target.parent.geometry.bounds[-1]
            line = LineString([[0, value], [maxx, value]])
        return line.buffer(10)
