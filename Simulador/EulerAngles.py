
import numpy as np
import math as m
  
def Rx(theta):
  return np.matrix([[ 1, 0           , 0           ],
                   [ 0, m.cos(theta),-m.sin(theta)],
                   [ 0, m.sin(theta), m.cos(theta)]])
  
def Ry(theta):
  return np.matrix([[ m.cos(theta), 0, m.sin(theta)],
                   [ 0           , 1, 0           ],
                   [-m.sin(theta), 0, m.cos(theta)]])
  
def Rz(theta):
  return np.matrix([[ m.cos(theta), -m.sin(theta), 0 ],
                   [ m.sin(theta), m.cos(theta) , 0 ],
                   [ 0           , 0            , 1 ]])

phi = m.pi/2
theta = m.pi/4
psi = m.pi/2
print("phi =", phi)
print("theta  =", theta)
print("psi =", psi)
  
  
R = Rz(psi) * Ry(theta) * Rx(phi)
print(np.round(R, decimals=2))


import sys
tol = sys.float_info.epsilon * 10
  
if abs(R.item(0,0))< tol and abs(R.item(1,0)) < tol:
   eul1 = 0
   eul2 = m.atan2(-R.item(2,0), R.item(0,0))
   eul3 = m.atan2(-R.item(1,2), R.item(1,1))
else:   
   eul1 = m.atan2(R.item(1,0),R.item(0,0))
   sp = m.sin(eul1)
   cp = m.cos(eul1)
   eul2 = m.atan2(-R.item(2,0),cp*R.item(0,0)+sp*R.item(1,0))
   eul3 = m.atan2(sp*R.item(0,2)-cp*R.item(1,2),cp*R.item(1,1)-sp*R.item(0,1))
  
print("phi =", eul1)
print("theta  =", eul2)
print("psi =", eul3)



v1 = np.array([[1],[0],[0]])
v2 = R * v1
print(np.round(v2, decimals=2))

####Grafica
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.quiver(0, 0, 0, v1[0], v1[1], v1[2], color='r')
ax.quiver(0, 0, 0, v2[0], v2[1], v2[2], color='b')
ax.set_xlim([-1, 1])
ax.set_ylim([-1, 1])
ax.set_zlim([-1, 1])
plt.show()
