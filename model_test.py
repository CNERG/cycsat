from modeler.model import Simulation, Surface, Agent, collect

# must be a list of Surface objects
surfaces = [Surface(np.ones((100, 100), dtype='int8'))]

# a list of Agent objects
agents = [Agent() for x in range(500)]

# times steps
timesteps = pd.Series([0, 1, 2])

s = Simulation(surfaces, agents, timesteps)
s.run()

s.data.apply(collect, image=s.surfaces[0].data, axis=1)
s.surfaces[0].plot()
