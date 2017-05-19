import os
from shutil import copyfile
import random

# copying the test database (this is just for repeated testing)
# src = 'C:/Users/Owen/Documents/Academic/CNERG/cycsat/simulations/four_reactors.sqlite'
# dst = 'C:/Users/Owen/Documents/Academic/CNERG/cycsat/reactor_test_sample.sqlite'
# copyfile(src, dst)

# =============================================================================
# TESTING CYCSAT STARTS HERE
# =============================================================================
from cycsat.simulation import Simulator
from cycsat.prototypes.ByronIL import ByronIL
from cycsat.laboratory import USGSMaterial
from cycsat.prototypes.instrument import Blue

from matplotlib import pyplot as plt

#------------------------------------------------------------------------
# Define a Reactor
#------------------------------------------------------------------------

db = Simulator('reactor_test_sample.sqlite')
b = db.load_build(1)
s = b.simulations[0]

# matplotlib.rcParams.update({'font.size': 18})
# fig, axes = plt.subplots(1, 3)
# for ax, ts in zip(axes, [1, 2, 3]):
#     s.plot(axes=ax, timestep=ts)

# temps = {'Reactor1': ByronIL}
# build = db.create_build(temps)
# s = build.simulate()

site = db.Site(1)
blue = Blue()
blue.calibrate(site)

fig, axes = plt.subplots(1, 2)

blue.mmu = 150
blue.plot(ax=axes[1], simulation=s, timestep=5)

axes[0].imshow(plt.imread('byronIL.PNG'))
