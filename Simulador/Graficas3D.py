import numpy as np
import matplotlib.pyplot as plt

from angulos import *
from simulacion1 import *
#from simulacion2 import *

vuelo_graficar=vuelo1
#vuelo_graficar=vuelo_paracaidas

# Extract the positions of the trajectory
posiciones = np.array([state[0:3] for state in sim])

# Extract the launch and impact points
launch_point = posiciones[0]
impact_point = posiciones[-1]

# Create the figure and 3D axes
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection="3d")

# Plot the trajectory
ax.plot(posiciones[:, 0], posiciones[:, 1], posiciones[:, 2])

# Plot the launch and impact points with different colors
ax.scatter(launch_point[0], launch_point[1], launch_point[2], c='blue', label='Punto de lanzamiento')
ax.scatter(impact_point[0], impact_point[1], impact_point[2], c='red', label='Punto de impacto')

# Create a circle in the xy plane with a diameter of 1000 meters around the impact point
circle_radius = 1000
circle_points = np.linspace(0, 2*np.pi, 100)
circle_x = impact_point[0] + circle_radius * np.cos(circle_points)
circle_y = impact_point[1] + circle_radius * np.sin(circle_points)

# Plot the circle in the xy plane
ax.plot(circle_x, circle_y, 0, color='gray', linestyle='--', label='1000 m radio de seguridad')

# Set labels, title, and limits
ax.set_xlabel("Alcance (m)")
ax.set_ylabel("Desplazamiento (m)")
ax.set_zlabel("Altura (m)")
ax.set_title("Trayectoria del cohete Xitle en el tiempo")
#ax.set_xlim(0, 10000)
#ax.set_ylim(0, 10000)
#ax.set_zlim(0, 10000)

# Add legend and show plot
ax.legend()
plt.show()


###GRAFICA 3D
posiciones = np.array([state[0:3] for state in sim])

# Extract the launch and impact points
launch_point = posiciones[0]
impact_point = posiciones[-1]

# Create the figure and 3D axes
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection="3d")

# Plot the trajectory
ax.plot(posiciones[:, 0], posiciones[:, 1], posiciones[:, 2])

# Plot the launch and impact points with different colors
ax.scatter(launch_point[0], launch_point[1], launch_point[2], c='blue', label='Punto de lanzamiento')
ax.scatter(impact_point[0], impact_point[1], impact_point[2], c='red', label='Punto de impacto')

# Create a circle in the xy plane with a diameter of 1000 meters around the impact point
circle_radius = 1000
circle_points = np.linspace(0, 2*np.pi, 100)
circle_x = impact_point[0] + circle_radius * np.cos(circle_points)
circle_y = impact_point[1] + circle_radius * np.sin(circle_points)

# Plot the circle in the xy plane
ax.plot(circle_x, circle_y, 0, color='gray', linestyle='--', label='1000 m radio de seguridad')

# Set labels, title, and limits
ax.set_xlabel("Alcance (m)")
ax.set_ylabel("Desplazamiento (m)")
ax.set_zlabel("Altura (m)")
ax.set_title("Trayectoria y orientaciones del cohete Xitle en el tiempo")

# Add legend and show plot
ax.legend()

# Add an arrow indicating the launch angle
# Create a rotation matrix
theta_rad = np.deg2rad(riel.angulo)
#rotation_matrixY = np.array([[np.cos(theta_rad),0, np.sin(theta_rad)],
#                               [0,1,0],
#                            [-np.sin(theta_rad), 0, np.cos(theta_rad)]])

rotation_matrix = np.array([[np.cos(theta_rad), -np.sin(theta_rad), 0],
                            [np.sin(theta_rad), np.cos(theta_rad), 0],
                            [0, 0, 1]])


launch_vector = rotation_matrix @ np.array([800, 0, 0])
ax.quiver(launch_point[0], launch_point[1], launch_point[2], launch_vector[0], launch_vector[1], launch_vector[2], color='green', arrow_length_ratio=0.1)

# Add projections of the trajectory onto the xy, xz, and yz planes
ax.plot(posiciones[:, 0], posiciones[:, 1], 0, color='black', linestyle='--', alpha=0.5)
ax.plot(posiciones[:, 0], posiciones[:, 2], 0, color='black', linestyle='--', alpha=0.7)
ax.plot(posiciones[:, 1], posiciones[:, 2], 0, color='black', linestyle='--', alpha=0.5)

# Set limits for each plane
#ax.set_xlim(0, 10000)
#ax.set_ylim(0, 10000)
#ax.set_zlim(0, 10000)

# Show the plot
plt.show()
###

#  grafica sobre el mapa el punto dado por las coordenadas de lanzamiento y grafica la trayectoria del vuelo

import numpy as np
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt

factor = 0.0005
# Define the launch coordinates
launch_latitude = 32
launch_longitude = -106

# Create a Basemap instance
m = Basemap(projection='cyl', llcrnrlat=launch_latitude-factor, urcrnrlat=launch_latitude+factor,
            llcrnrlon=launch_longitude+factor, urcrnrlon=launch_longitude-factor, resolution='h')

# Draw the coastlines and fill the continents
m.drawcoastlines(color='#135')
m.fillcontinents(color='#eee', lake_color='#aaa')

# Draw the launch point
x_im, y_im = m(posiciones[-1,0], posiciones[-1,1])
m.scatter(x_im, y_im, latlon=True, s=50, c='black', marker='o')

# Draw the impact point

xpt, ypt = m(launch_longitude, launch_latitude)
m.scatter(xpt, ypt, latlon=True, s=50, c='r', marker='o')

# Convert the positions to latitude and longitude
latitudes = posiciones[:, 1]
longitudes = posiciones[:, 0]

# Transform the coordinates to the map projection
x, y = m(longitudes, latitudes)

# Plot the trajectory
m.plot(x, y, latlon=True, color='b', linewidth=2)

# Add labels and title
m.drawparallels(np.arange(32, 32.05, 0.5), labels=[True, True, True, True], size=10)
m.drawmeridians(np.arange(-106, -106.05, 0.5), labels=[True, True, True, True], size=10)
plt.title("Trayectoria del cohete Xitle")

# Show the plot
plt.show()