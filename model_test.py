from modeler.model import Simulation, Surface, Agent

# must be a list of Surface objects
surfaces = [Surface(np.ones((100, 100), dtype='int8'))]

# a list of agents
agents = [Agent() for x in range(5000)]

# times steps
timesteps = [1]  # pd.date_range('1/1/2015', '1/31/2015')

s = Simulation(surfaces, agents, timesteps)
s.run()
