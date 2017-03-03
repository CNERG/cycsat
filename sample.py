import os
from shutil import copyfile
import random

# # copying the test database (this is just for repeated testing)
src = 'C:/Users/Owen/Documents/Academic/CNERG/cycsat/simulations/four_reactors.sqlite'
dst = 'C:/Users/Owen/Documents/Academic/CNERG/cycsat/reactor_test_sample.sqlite'
copyfile(src, dst)

# =============================================================================
# TESTING CYCSAT STARTS HERE
# =============================================================================
from descartes import PolygonPatch

from cycsat.simulation import Cycsat
from cycsat.archetypes import Mission, Facility, Site, Satellite, Shape, Rule
from cycsat.prototypes.satellite import LANDSAT8, RGB
from cycsat.prototypes.reactor import SampleReactor
from cycsat.image import Sensor

from cycsat.geometry import build_facility, placement_bounds, Point, posit_point, place_feature
from cycsat.geometry import line_func, rotate_facility, near_rule, evaluate_rules


#sim = Cycsat('reactor_test_sample.sqlite')

s = SampleReactor()
#s.build()
# t = s.features[3]

# fig, ax = plt.subplots(3,2, sharex=True,sharey=True)
# for x in ax[:,0]:
# 	s1.build()

# ims = os.listdir('temp')

# import imageio
# images = []
# for filename in filenames:
#     images.append(imageio.imread(filename))
# imageio.mimsave('/path/to/movie.gif', images)

#fig, ax = plt.subplots(1,1,sharex=True,sharey=True)


def plot_features(features):
	fig, ax = plt.subplots(1,1,sharex=True,sharey=True)
	ax.set_xlim([0,10000])
	ax.set_ylim([0,10000])
	ax.set_aspect('equal')

	patches = [PolygonPatch(feat) for feat in features]
	for patch in patches:
		ax.add_patch(patch)

