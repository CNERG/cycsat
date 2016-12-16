from mpl_toolkits.mplot3d import axes3d
import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np

from cycsat.terrain import mpd

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

data = mpd(5,0)
x = range(data.shape[0])	
y = range(data.shape[1])

X,Y = np.meshgrid(x,y)

ax.plot_surface(X, Y, data,cmap=cm.coolwarm,rstride=1, cstride=1,linewidth=0)
plt.show()

# mlab.figure(size=(640, 800), bgcolor=(0.16, 0.28, 0.46))
# mlab.surf(data, warp_scale=0.2) 
# mlab.show()
