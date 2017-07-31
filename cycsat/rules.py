
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
        buf = self.depend.geometry.buffer(self.args['value'])
        self.target.place_in(buf, strict=False)
        print(self.target.geometry.distance(self.depend.geometry))
