import numpy as np
import pandas as pd
import json
import matplotlib.pyplot as plt
#from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation

#from Paquetes.utils.funciones import *
from Paquetes.utils.funciones import extraer_datoscsv, extraer_datosjson

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
with open('datos_simulacion.json', 'r', encoding= 'utf-8') as f:
    datos = json.load(f)
# Extraer los datos del json
(d_ext, t_MECO, tiempo_salida_riel, tiempo_apogeo, tiempo_impacto,
    max_altitude, max_speed, max_acceleration_linear, max_acceleration_angular) = extraer_datosjson(datos)

############################################

x = posiciones[:, 0]
y = posiciones[:, 1]
z = posiciones[:, 2]
t = tiempos[:]

t_fin = tiempos[-1]
apogeo = z.max()
alcance = x.max()
launch_point = posiciones[0]
impact_point = posiciones[-1]

# Crear figura y ejes
fig = plt.figure(figsize=(12, 6))

# Eje 3D para la trayectoria del cohete
ax3d = fig.add_subplot(121, projection='3d')
ax3d.set_xlim([-500, alcance+200])
ax3d.set_ylim([-1000, 2000])
ax3d.set_zlim([0, apogeo+200])
ax3d.set_title('Trayectoria 3D del cohete')
ax3d.set_xlabel("Alcance (m)")
ax3d.set_ylabel("Desplazamiento (m)")
ax3d.set_zlabel("Altura (m)")

# Eje 2D para la visualización
ax2d = fig.add_subplot(122)
ax2d.set_xlim([0, t_fin])
ax2d.set_ylim([-10, apogeo+200])
ax2d.set_title('Trayectoria 2D del cohete')
ax2d.set_xlabel("Tiempo (s)")
ax2d.set_ylabel("Altura (m)")
ax2d.grid()

# Cada cuantos frames graficar
every = 500

# Función de actualización para la animación
def update(frame):

    #print(frame)
    ax3d.set_xlim([-500, alcance+200])
    ax3d.set_ylim([-1000, 2000])
    ax3d.set_zlim([-1000, apogeo+200])

    # Plot the trajectory
    ax3d.plot(x[:frame], y[:frame], z[:frame], 'b')
    ax3d.scatter(x[frame], y[frame], z[frame], 'g', s=20, marker='*')

    # Plot the launch and impact points with different colors
    ax3d.scatter(launch_point[0], launch_point[1], launch_point[2], c='blue', label='Punto de lanzamiento')
    ax3d.scatter(impact_point[0], impact_point[1], impact_point[2], c='red', label='Punto de impacto')
    
    if frame == frames[-1]:
        #Create a circle in the xy plane with a diameter of 1000 meters around the impact point
        circle_radius = 1000
        circle_points = np.linspace(0, 2*np.pi, 100)
        circle_x = impact_point[0] + circle_radius * np.cos(circle_points)
        circle_y = impact_point[1] + circle_radius * np.sin(circle_points)

        # Plot the circle in the xy plane
        ax3d.plot(circle_x, circle_y, 0, color='gray', linestyle='--', label='1000 m radio de seguridad')

    #######################################
    ## Grafica 2D

    #ax2d.clear()
    ax2d.set_xlim([0, t_fin])
    ax2d.set_ylim([0, apogeo+200])
    ax2d.plot(t[:frame], z[:frame], 'b-')
    ax2d.scatter(t[frame], z[frame])

    return ax3d, ax2d

# Crear la animación
frames = np.arange(0, len(t)+every, every)
if frames[-1] > len(t): frames[-1] = len(t)-1
#print(frames)

fps=30
animation = FuncAnimation(fig, update, frames=frames, interval=1000/fps, repeat=False)

plt.show()


fps=fps
#animation.save("TrayectoriaAnimada.gif")
animation.save("Trayectoria-pelicula.mp4", fps=fps)
print("Mp4 Guardado")