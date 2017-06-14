from cycsat.archetypes import Agent

# initalize agents with random values
agents = pd.Series([Agent(value=i) for i in range(100)])

# generate 100 steps of test data
for i in range(100):
    i = agents.apply(lambda x: x.run())
