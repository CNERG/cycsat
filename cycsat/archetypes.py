
class Agent:

    def __init__(self, **args):
        for arg in args:
            setattr(self, arg, args[arg])

    def run(self, **args):
        print(*args)
        print('run')
