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

from cycsat.simulation import Cysat
from cycsat.archetypes import Mission, Facility, Site, Satellite, Shape
from cycsat.prototypes.satellite import LANDSAT8, RGB
from cycsat.prototypes.reactor import SampleReactor
from cycsat.image import Sensor

from cycsat.geometry import build_facility, placement_bounds, Point
from shapely.geometry import box

# sim = Cysat('reactor_test_sample.sqlite')

s = SampleReactor()
a = build_facility(s)

s.build_geometry()


# fig, axes = plt.subplots(2,3,sharex=True,sharey=True)
# axes[0,0].set_xlim([0,10000])
# axes[0,0].set_ylim([0,10000])
# ax_l = axes.flatten()
# for patch,ax in zip(a,ax_l):
# 	p = PolygonPatch(patch)
# 	ax.add_patch(p)

c1 = s.features[0]
c2 = s.features[1]

def near(feature,target,distance):
	""""""
	# build geometry of both features
	target_geometry = target.build_geometry()
	feature_geometry = feature.build_geometry()
	
	# buffer the target geometry by the provided distance
	buff = target_geometry.buffer(distance)

	bounds = feature_geometry.bounds
	bound_box = box(bounds[0],bounds[1],bounds[2],bounds[3])

	# find all coords in feature to be placed
	# coords = list(feature_geometry.exterior.coords)
	# feature_center = buff.centroid()

	xs = buff.exterior.xy[0]
	ys = buff.exterior.xy[1]
	index = random.randint(0,len(xs)-1)

	x = xs[index]
	y = ys[index]

	p = Point(x,y)

	return [buff, p, bound_box]




buff, point, bbox = near(c1,c2,100)

p = PolygonPatch(buff)

fig, ax = plt.subplots(1,1,sharex=True,sharey=True)

ax.set_xlim([0,10000])
ax.set_ylim([0,10000])

c1p = PolygonPatch(c1.build_geometry())
c2p = PolygonPatch(c2.build_geometry())

p.set_color('red')
ax.add_patch(p)

ax.add_patch(PolygonPatch(bbox))

ax.add_patch(c1p)
ax.add_patch(c2p)