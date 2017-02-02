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

from cycsat.geometry import build_facility, placement_bounds, Point, posit_point, place_feature
from shapely.geometry import box

# sim = Cysat('reactor_test_sample.sqlite')

s = SampleReactor()
a = build_facility(s)

s.build_geometry()

c1 = s.features[0]
c2 = s.features[1]

def near(feature,target,distance):
	""""""
	# build geometry of both features
	target_geometry = target.build_geometry()
	feature_geometry = feature.build_geometry()
	
	# buffer the target geometry by the provided distance
	first_buffer = target_geometry.buffer(distance)

	bounds = feature_geometry.bounds
	diagaonal_dist = Point(bounds[0:2]).distance(Point(bounds[2:]))
	buffer_value = diagaonal_dist+(diagaonal_dist*0.50)
	second_buffer = first_buffer.buffer(buffer_value)

	final = second_buffer.difference(first_buffer)

	return final

buff = near(c1,c2,500)
p = PolygonPatch(buff)

fig, ax = plt.subplots(1,1,sharex=True,sharey=True)

ax.set_xlim([0,10000])
ax.set_ylim([0,10000])

p.set_color('blue')
ax.add_patch(p)

placed = place_feature(c1,buff,random=True)
print(placed)
placed = PolygonPatch(placed.build_geometry())
placed.set_color('green')
ax.add_patch(placed)