import numpy as np
import pandas as pd
import json
import matplotlib.pyplot as plt

from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation

from funciones import *

###############################################
# Leer los datos de la simulación desde el archivo CSV
datos_simulacion = pd.read_csv('datos_simulacion.csv')
# Extarer los datos del csv
(tiempos, posiciones, velocidades, thetas, omegas, CPs, CGs, masavuelo,estabilidad,
viento_vuelo_mags, viento_vuelo_dirs, viento_vuelo_vecs, wind_xs, wind_ys, wind_zs,
Dmags, Nmags, Tmags, Dxs, Dys, Dzs, Nxs, Nys, Nzs, Txs, Tys, Tzs, Tvecs, Dvecs, Nvecs,
accels, palancas, accangs, Gammas, Alphas, torcas, Cds, Machs) = extraer_datoscsv(datos_simulacion)

#########################################
# Leer los datos de la simulación desde el archivo JSON
with open('datos_simulacion.json', 'r') as f:
    datos = json.load(f)
# Extraer los datos del json
(d_ext, t_MECO, tiempo_salida_riel, tiempo_apogeo, tiempo_impacto,
    max_altitude, max_speed, max_acceleration_linear, max_acceleration_angular) = extraer_datosjson(datos)

############################################

x = posiciones[:, 0]
y = posiciones[:, 1]
z = posiciones[:, 2]
t = tiempos[::20]

launch_point = posiciones[0]
impact_point = posiciones[-1]

# Crear figura y ejes
fig = plt.figure(figsize=(12, 6))

# Eje 3D para la trayectoria del cohete
ax3d = fig.add_subplot(121, projection='3d')
ax3d.set_xlim([-500, 2000])
ax3d.set_ylim([-1000, 5000])
ax3d.set_zlim([0, 8000])
ax3d.set_title('Trayectoria 3D del cohete')
ax3d.set_xlabel("Alcance (m)")
ax3d.set_ylabel("Desplazamiento (m)")
ax3d.set_zlabel("Altura (m)")

#ax3d.plot(x[:100], y[:100], z[:100], 'b')


# Eje 2D para la visualización
ax2d = fig.add_subplot(122)
ax2d.set_xlim([0, 80])
ax2d.set_ylim([-10, 5000])
ax2d.set_title('Trayectoria 2D del cohete')
ax2d.grid()

# Función de actualización para la animación
def update(frame):
    ax3d.clear()
    ax3d.set_xlim([-500, 5000])
    ax3d.set_ylim([-1000, 2000])
    ax3d.set_zlim([-1000, 8000])
    ax3d.set_title('Trayectoria 3D del cohete')
    ax3d.set_xlabel("Alcance (m)")
    ax3d.set_ylabel("Desplazamiento (m)")
    ax3d.set_zlabel("Altura (m)")

    # Plot the trajectory
    ax3d.plot(x[:frame], y[:frame], z[:frame], 'b')
    #ax3d.plot(posiciones[:frame, 0], posiciones[:frame, 1], posiciones[:frame, 2])
    # Plot the launch and impact points with different colors
    ax3d.scatter(launch_point[0], launch_point[1], launch_point[2], c='blue', label='Punto de lanzamiento')
    ax3d.scatter(impact_point[0], impact_point[1], impact_point[2], c='red', label='Punto de impacto')
    
    # Create a circle in the xy plane with a diameter of 1000 meters around the impact point
    #circle_radius = 1000
    #circle_points = np.linspace(0, 2*np.pi, 100)
    #circle_x = impact_point[0] + circle_radius * np.cos(circle_points)
    #circle_y = impact_point[1] + circle_radius * np.sin(circle_points)

    # Plot the circle in the xy plane
    #ax3d.plot(circle_x, circle_y, 0, color='gray', linestyle='--', label='1000 m radio de seguridad')

  
    ax3d.scatter(x[frame], y[frame], z[frame], 'g', size= 20)
    ax3d.legend()

    ax2d.clear()
    ax2d.set_xlim([0, 80])
    ax2d.set_ylim([-10, 8000])
    #ax2d.plot(t[:frame], z[:frame], 'b-')
    ax2d.plot(t[:],x[:], 'purple')
    #ax2d.scatter(t[frame], z[frame], 'r')

    return ax3d, ax2d

# Crear la animación
animation = FuncAnimation(fig, update, frames=len(t), interval=1)

plt.show()
plt.savefig("TrayectoriaAnimada.gif")