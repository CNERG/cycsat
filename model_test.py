from modeler.model import Simulation, Surface, Agent

surfaces = [Surface(np.ones((100, 100), dtype='int8'))]
agents = [Agent() for x in range(3)]
timesteps = pd.date_range('1/1/2015', '12/31/2015')

s = Simulation(surfaces, agents, timesteps)
s.run()
