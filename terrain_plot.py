from mpl_toolkits.mplot3d import axes3d
import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np

from skimage.filters import sobel
from skimage.morphology import watershed
from cycsat.terrain import mpd, get_corners, floodFill
from cycsat.image import write_array

from scipy import ndimage as ndi
from scipy.stats import rankdata

from osgeo import ogr, gdal, osr
from geopandas import gpd

# generate terrain
print('generate')
data = mpd(5,0)

# set up surface
x = range(data.shape[0])	
y = range(data.shape[1])
X,Y = np.meshgrid(x,y)

# distance = ndi.distance_transform_edt(data)
#print('edges')
#sob = sobel(data)

print('filling')
x,y = np.unravel_index(data.argmin(),data.shape)
mask = np.where(data < data.mean(),1,0)
flood = floodFill(x,y,mask)
write_array(flood,'test')
write_array(data,'data')


ds = gdal.Open('test.tif')
band = ds.GetRasterBand(1)

drv = ogr.GetDriverByName("ESRI Shapefile")

srs = osr.SpatialReference()
srs.ImportFromWkt(ds.GetProjectionRef())

out = drv.CreateDataSource('test.shp')
out_layer = out.CreateLayer('new',srs=None)

fd = ogr.FieldDefn("DN",ogr.OFTInteger)
out_layer.CreateField(fd)

gdal.Polygonize(band,None,out_layer,0,[],callback=None)
out = None

gdf = gpd.read_file('test.shp')

# set up plot
fig1 = plt.figure(1)
ax1 = fig1.add_subplot(111, projection='3d')

fig2, axes = plt.subplots(1,2,sharex=True,sharey=True)
ax2, ax3 = axes

ax1.plot_surface(X, Y, data,cmap=cm.coolwarm,rstride=1, cstride=1,linewidth=0)

plt.show()

gdf.plot(ax=ax2)
flood = gdf[gdf.DN==1]
largest = flood.area.sort_values(ascending=False).head(5).index
gdf.ix[largest].plot(ax=ax3,column='DN')

plt.show()