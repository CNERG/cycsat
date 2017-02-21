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
from cycsat.prototypes.feature import SampleTurbine
from cycsat.image import Sensor

from cycsat.geometry import build_facility, placement_bounds, Point, posit_point, place_feature
from cycsat.geometry import pointilize
from shapely.geometry import box
from shapely.affinity import translate as shift_shape

sim = Cycsat('reactor_test_sample.sqlite')

# s2 = SampleReactor()
# s2.features.pop(0s)

# fig, ax = plt.subplots(3,2, sharex=True,sharey=True)
# for x in ax[:,0]:
# 	s1.build()

# ims = os.listdir('temp')

# import imageio
# images = []
# for filename in filenames:
#     images.append(imageio.imread(filename))
# imageio.mimsave('/path/to/movie.gif', images)

# def plot_facilities():


def plot_features(features):
	fig, ax = plt.subplots(1,1,sharex=True,sharey=True)
	ax.set_xlim([0,10000])
	ax.set_ylim([0,10000])

	patches = [PolygonPatch(feat) for feat in features]
	for patch in patches:
		ax.add_patch(patch)

