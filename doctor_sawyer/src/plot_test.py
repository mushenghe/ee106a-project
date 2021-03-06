#!/usr/bin/env python
#import matplotlib.pyplot as plt
#import numpy as np
#from matplotlib import cm
#from matplotlib.ticker import LinearLocator, FormatStrFormatter
#
data = {(-1, 2): (-0.29021055535686702, 12.605169778226989), (-2, 0): (-0.270210555356867, 19.43707202707103), (2, 1): (-0.270210555356867, 7.543417470198903), (0, 0): (-0.23021055535686699, 11.422650259812091), (2, -1): (-0.25021055535686698, 5.491962326879429), (1, -1): (-0.25021055535686698, 6.968586102999278), (-1, 0): (-0.210210555356867, 6.570329755477597), (1, 2): (-0.13021055535686704, 8.073481148587701), (-2, 1): (-0.270210555356867, 9.851596649124554), (1, -2): (-0.25021055535686698, 8.65811482572064), (-1, -1): (-0.17021055535686702, 5.324382485243624), (1, 1): (-0.13021055535686704, 11.305178522616867), (2, -2): (-0.25021055535686698, 12.13932117418799), (2, 2): (-0.210210555356867, 7.359608092886553), (-2, -2): (-0.19021055535686701, 7.478034636248098), (-2, 2): (-0.29021055535686702, 12.332088526731617), (-1, 1): (-0.270210555356867, 11.45294266080062), (-1, -2): (-0.17021055535686702, 7.849827925809371), (0, -2): (-0.17021055535686702, 5.396258946798993), (1, 0): (-0.270210555356867, 19.157912575305186), (0, 1): (-0.270210555356867, 9.384339581374817), (-2, -1): (-0.19021055535686701, 7.85222127820874), (2, 0): (-0.210210555356867, 5.719675760045892), (0, -1): (-0.210210555356867, 9.62425749437009), (0, 2): (-0.29021055535686702, 17.318891712844316)}
#fig = plt.figure()
#x = np.arange(-2, 3, 1)
#y = np.arange(-2, 3, 1)
#x2d, y2d = np.meshgrid(x, y)
#x, y = x2d.ravel(), y2d.ravel()
##R = np.sqrt(X**2 + Y**2)
#Z = np.zeros((5, 5))
#for x in np.arange(-2, 3, 1):
#    for y in np.arange(-2, 3, 1):
#        Z[x, y] = data[(x, y)][0]
#
#ax1 = fig.add_subplot(1, 1, 1, projection = '3d')
#
print(data[(0,0)][0])
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

x = np.arange(-2, 3, 1)
y = np.arange(-2, 3, 1)
x2d, y2d = np.meshgrid(x, y)
x, y = x2d.ravel(), y2d.ravel()
z = np.zeros_like(x) * 0.0
for i in range(x.shape[0]):
	print(data[(x[i], y[i])][0])
	z[i] = data[(x[i], y[i])][0]
print(z)
fig = plt.figure(figsize=(4, 6))
ax1 = fig.add_subplot(1, 1, 1, projection='3d')
ax1.bar3d(x, y, 0, 1, 1, z - np.min(z), shade=True)
ax1.set_title('Shading On')


plt.show()