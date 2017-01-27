import os
from shutil import copyfile

# # copying the test database (this is just for repeated testing)
src = 'C:/Users/Owen/Documents/Academic/CNERG/cycsat/simulations/four_reactors.sqlite'
dst = 'C:/Users/Owen/Documents/Academic/CNERG/cycsat/reactor_test_sample.sqlite'
copyfile(src, dst)

# =============================================================================
# TESTING CYCSAT STARTS HERE
# =============================================================================
from descartes import PolygonPatch

from cycsat.simulation import Cysat
from cycsat.archetypes import Mission, Facility, Site, Satellite, Shape
from cycsat.prototypes.satellite import LANDSAT8, RGB
from cycsat.prototypes.reactor import SampleReactor
from cycsat.image import Sensor

from cycsat.geometry import build_facility, placement_bounds

# sim = Cysat('reactor_test_sample.sqlite')

s = SampleReactor()
a = build_facility(s)

s.build_geometry()

fig, axes = plt.subplots(2,3,sharex=True,sharey=True)

axes[0,0].set_xlim([0,10000])
axes[0,0].set_ylim([0,10000])

ax_l = axes.flatten()

for patch,ax in zip(a,ax_l[1:]):
	p = PolygonPatch(patch)
	ax.add_patch(p)






