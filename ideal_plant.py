import os

from osgeo import ogr
from osgeo import gdal

import rasterio
from rasterio import features

from skimage import io
from skimage.segmentation import quickshift

import fiona
from shapely.geometry import mapping, shape

############################################################################################################

images = os.listdir('test_data/images')
images = ['test_data/images/'+x for x in images if '_clip.tif' in x]

# image = rasterio.open(images[0])
# data = image.read(1)
# image.close()

img = io.imread(images[0])
segments = quickshift(img, kernel_size=20, convert2lab=False, max_dist=20, ratio=0.5)
print("Quickshift number of segments: %d" % len(np.unique(segments)))



# band1.fill(10)

# new_dataset = rasterio.open('test_data/test.tif', 'w', driver='GTiff',height=band1.shape[0], width=band1.shape[1],
# 							count=1, dtype=band1.dtype,crs=image.crs, transform=image.affine)
# new_dataset.close()

# mask = rasterio.open('test_data/test.tif')
# band1 = mask.read(1)

#new_dataset.close()







# with collection("some.shp", "r") as input:
#     # schema = input.schema.copy()
#     schema = { 'geometry': 'Polygon', 'properties': { 'name': 'str' } }
#     with collection(
#         "some_buffer.shp", "w", "ESRI Shapefile", schema) as output:
#         for point in input:
#             output.write({
#                 'properties': {
#                     'name': point['properties']['name']
#                 },
#                 'geometry': mapping(shape(point['geometry']).buffer(5.0))
#             })

