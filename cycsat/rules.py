
class Rule:

    def __init__(self, target, dep, **args):
        self.__target__ = target
        self.__dep__ = dep
        self.args = args
        self.agent = False

    def __str__(self):
        return '{} {} {} ARGS: {}'.format(self.__target__,
                                          self.__class__.__name__,
                                          self.__dep__,
                                          self.args)

    @property
    def target(self):
        try:
            return [i for i in self.agent.agents if i.name == self.__target__][0]
        except:
            return False

    @property
    def depend(self):
        try:
            return [i for i in self.agent.agents if i.name == self.__dep__][0]
        except:
            return False

    def evaluate(self):
        try:
            return self.__evaluate__()
        except:
            return False


class NEAR(Rule):

    def __evaluate__(self):
        inner_buffer = mask.buffer(int(self.value))

        diagaonal_dist = Point(mask[0:2]).distance(Point(mask[2:]))

        buffer_value = diagaonal_dist * 2
        second_buffer = inner_buffer.buffer(buffer_value)

        return self.depend.geometry.buffer(self.args['value'])
