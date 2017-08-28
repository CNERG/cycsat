
class AgentState(Agent):

    def __init__(self, agent, time):
        self.agent = agent
        self.time = time

    @property
    def data(self):
        data = {'time': self.time}
        for attr in self.agent.attrs:
            data[attr] = getattr(self, attr)
        return data
