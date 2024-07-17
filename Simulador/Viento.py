#En este SCRIPT: Clase Viento2D
import random
import numpy as np
from numpy import *
import matplotlib.pyplot as plt
import matplotlib.animation as animation

class Viento2D:

    def __init__(self, vel_mean=10, vel_var=2):
        self.vel_mean = vel_mean
        self.vel_var = vel_var


        self.magnitud = random.uniform(self.vel_mean - self.vel_var, self.vel_mean + self.vel_var)
        self.direccion = random.uniform(0, 180)
        self.vector = self.magnitud * np.array([np.cos(np.deg2rad(self.direccion)), 0, np.sin(np.deg2rad(self.direccion))])

    def __repr__(self):
        return f"Viento(magnitud={self.magnitud}, direccion={self.direccion})"
    
#Creacion del viento actual
viento_actual = Viento2D(vel_mean=10, vel_var=0.05)
print(viento_actual)
print(viento_actual.vector)

"""""Descomentar para graficar el vector viento 
# Get the x and z components of the wind vector
vx = viento_actual.vector[0]
vz = viento_actual.vector[2]

# Create a plot
fig, ax = plt.subplots()

# Plot the wind vector as an arrow
ax.arrow(0, 0, vx, vz, head_width=0.5, head_length=0.5, color='r', zorder=10)

# Set the limits of the plot
ax.set_xlim([-15, 15])
ax.set_ylim([-15, 15])

# Add labels and title
ax.set_xlabel('x (m)')
ax.set_ylabel('z (m)')
ax.set_title('Vector de viento')

# Show the plot
plt.show()
"""