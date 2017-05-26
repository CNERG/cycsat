import os
from shutil import copyfile
import random

# copying the test database (this is just for repeated testing)
src = 'C:/Users/Owen/Documents/Academic/CNERG/cycsat/simulations/four_reactors.sqlite'
dst = 'C:/Users/Owen/Documents/Academic/CNERG/cycsat/reactor_test_sample.sqlite'
copyfile(src, dst)

# =============================================================================
# TESTING CYCSAT STARTS HERE
# =============================================================================
from cycsat.simulation import Simulator
from cycsat.prototypes.ByronIL import ByronIL
from cycsat.laboratory import USGSMaterial
from cycsat.prototypes.instrument import Blue, Red, Green

from matplotlib import pyplot as plt

#------------------------------------------------------------------------
# Define a Reactor
#------------------------------------------------------------------------

db = Simulator('reactor_test_sample.sqlite')

temps = {'Reactor1': ByronIL}
b = db.create_build(temps)
s = b.simulate(end=6)
site = b.sites[0]

s.plot(5)

# # b = db.load_build(1)
# # s = b.simulations[0]
# # site = b.sites[0]

# fig, axes = plt.subplots(1, 5)
# axes = axes.flatten()

# for i in range(5):
#     site.assemble()
#     site.plot(ax=axes[i])

# fig, axes = plt.subplots(1, 3)
# for i, inst in enumerate([Blue, Green, Red]):
#     print('plotting', inst)
#     sensor = inst()
#     sensor.calibrate(site)
#     sensor.mmu = 150
#     sensor.plot(ax=axes[i], simulation=s, timestep=5)
#     sensor.write(str(i))

# axes[0].imshow(plt.imread('byronIL.PNG'))
