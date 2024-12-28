import numpy as np
import pandas as pd
import json
import matplotlib.pyplot as plt
import sys
import os

#from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation

# Agregar la ruta del directorio que contiene los paquetes al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
#from Paquetes.utils.funciones import *
from Paquetes.utils.funciones import extraer_datoscsv, extraer_datosjson, muestra_tiempos


###############################################
# Leer los datos de la simulación desde el archivo CSV
datos_simulacion = pd.read_csv('datos_simulacion.csv')
datos_simulacion = pd.read_csv(r'C:\Users\Natalia\OneDrive\Archivos\Tesis\GithubCode\SimuladorVueloNat\3DOF-Rocket-PU\Simulador\src\datos_sim_paracaidas.csv')


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
#Apogeo
apogee = [x[z.argmax()], y[z.argmax()], z[z.argmax()]]
tiempo_apogeo = t[z.argmax()]
print('Apogeo:', apogee)

#MECO
print('t_MECO:', t_MECO)
t_MECO = int(t_MECO)
MECO_point = posiciones[t_MECO]
print('MECO:', MECO_point)

alcance = x.max()
launch_point = posiciones[0]

impact_point = posiciones[-1]
tiempo_impacto = t[-1]

# Crear figura y ejes
fig = plt.figure(figsize=(12, 6))

# Eje 3D para la trayectoria del cohete
ax3d = fig.add_subplot(121, projection='3d')
ax3d.set_xlim([-100, alcance+200])
ax3d.set_ylim([-100, 2000])
ax3d.set_zlim([0, apogee[2]+200])
ax3d.set_title('Trayectoria 3D del cohete')
ax3d.set_xlabel("Alcance (m)")
ax3d.set_ylabel("Desplazamiento (m)")
ax3d.set_zlabel("Altura (m)")
#Escribir lanazamiento, apogeo e impacto junto a los puntos 
sep=100 #separacion del punto
ax3d.text(launch_point[0]+sep, launch_point[1]+sep, launch_point[2]+sep, 'Lanzamiento', color='blue')
ax3d.text(impact_point[0]+sep, impact_point[1]+sep, impact_point[2]+sep, 'Impacto', color='red')
ax3d.text(apogee[0]+sep, apogee[1]+sep, apogee[2]+sep, 'Apogeo', color='purple')
ax3d.set_box_aspect([1, 1, 1])  # Aspect ratio is 1:1:1

# Eje 2D para la visualización
ax2d = fig.add_subplot(122)
ax2d.set_xlim([0, t_fin])
ax2d.set_ylim([-10, apogee[2]+200])
ax2d.set_title('Trayectoria 2D del cohete')
ax2d.set_xlabel("Tiempo (s)")
ax2d.set_ylabel("Altura (m)")
#Scatter del apogeo
ax2d.scatter(tiempo_apogeo, apogee[2], c='c', label='Apogeo', s=200, marker='*')
#Scatter del MECO
ax2d.scatter(t_MECO, z[t_MECO], c='orange', label='MECO', s=200, marker='*')
ax2d.grid()
ax2d.legend()
muestra_tiempos(tiempo_salida_riel,t_MECO, tiempo_apogeo, tiempo_impacto, ax2d)

# Cada cuantos frames graficar
every = 700

# Función de actualización para la animación
def update(frame):

    #print(frame)
    ax3d.set_xlim([-500, alcance+200])
    ax3d.set_ylim([-1000, 2000])
    ax3d.set_zlim([-1000, apogee[2]+200])

    # Plot the trajectory
    ax3d.plot(x[:frame], y[:frame], z[:frame], 'darkblue')
    #ax3d.scatter(x[frame], y[frame], z[frame], 'g', s=20, marker='*')

    # Plot the launch and impact points with different colors
    ax3d.scatter(launch_point[0], launch_point[1], launch_point[2], c='blue', label='Punto de lanzamiento')
    ax3d.scatter(impact_point[0], impact_point[1], impact_point[2], c='red', label='Punto de impacto')
    ax3d.scatter(apogee[0], apogee[1], apogee[2], c='purple', label='Apogeo')
    
    if frame == frames[-1]:
        #Create a circle in the xy plane with a diameter of 1000 meters around the impact point
        circle_radius = 1000
        circle_points = np.linspace(0, 2*np.pi, 100)
        circle_x = impact_point[0] + circle_radius * np.cos(circle_points)
        circle_y = impact_point[1] + circle_radius * np.sin(circle_points)

        # Plot the circle in the xy plane
        ax3d.plot(circle_x, circle_y, 0, color='0.6', linestyle='--', label='1000 m radio de seguridad')

    #######################################
    ## Grafica 2D
    ax2d.set_xlim([0, t_fin])
    ax2d.set_ylim([0, apogee[2]+200])
    ax2d.plot(t[:frame], z[:frame], 'darkblue')



    return ax3d, ax2d

# Crear la animación
frames = np.arange(0, len(t)+every, every)
if frames[-1] > len(t): 
    frames[-1] = len(t)-1
#print(frames)

fps=40
animation = FuncAnimation(fig, update, frames=frames, interval=1000/fps, repeat=False)
plt.show()

#animation.save("TrayectoriaAnimada.gif")
#animation.save("Trayectoria-pelicula.mp4", fps)
#print("Mp4 Guardado")