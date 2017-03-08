import os
from shutil import copyfile
import random

# # copying the test database (this is just for repeated testing)
# src = 'C:/Users/Owen/Documents/Academic/CNERG/cycsat/simulations/four_reactors.sqlite'
# dst = 'C:/Users/Owen/Documents/Academic/CNERG/cycsat/reactor_test_sample.sqlite'
# copyfile(src, dst)

# =============================================================================
# TESTING CYCSAT STARTS HERE
# =============================================================================
from descartes import PolygonPatch

from cycsat.simulation import Simulation
from cycsat.archetypes import Mission, Facility, Site, Satellite, Shape, Rule, Event
from cycsat.prototypes.satellite import LANDSAT8, RGB
from cycsat.prototypes.reactor import SampleReactor
from cycsat.prototypes.instrument import Blue, Red, Green
from cycsat.image import Sensor

from cycsat.geometry import build_facility, placement_bounds, Point, posit_point, place_feature
from cycsat.geometry import line_func, rotate_facility, near_rule, evaluate_rules

sim = Simulation('reactor_test_sample.sqlite')

# f = SampleReactor()
# f.build()

# fig, axes = plt.subplots(nrows=2,ncols=5,sharex=True,sharey=True,figsize=(15,5))
# for i, ax in enumerate(axes.flat,start=1):
# 	#ax.set_xticks([2000,4000,6000,8000,10000])
# 	#ax.set_yticks([2000,4000,6000,8000,10000])
# 	f.build()
# 	f.plot(ax,title=False,labels=False)


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

