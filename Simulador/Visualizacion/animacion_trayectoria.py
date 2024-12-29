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
datos_simulacion = pd.read_csv(r'C:\Users\Natalia\OneDrive\Archivos\Tesis\GithubCode\SimuladorVueloNat\3DOF-Rocket-PU\Simulador\src\datos_simulacion.csv')


# Extarer los datos del csv
(tiempos, posiciones, _, thetas, omegas, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, Gammas, _, _, _, _) = extraer_datoscsv(datos_simulacion)

#########################################
# Leer los datos de la simulación desde el archivo JSON
with open('datos_simulacion.json', 'r', encoding= 'utf-8') as f:
    datos = json.load(f)
# Extraer los datos del json
(_, t_MECO, tiempo_salida_riel, tiempo_apogeo, tiempo_impacto,
    max_altitude, _, _, _) = extraer_datosjson(datos)

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
for ts in t:
    if ts > t_MECO:
        t_MECO = ts
        break

for index in range(len(t)):
    if t[index] == t_MECO:
        MECO_index = index
        break


print('t_MECO:', t_MECO)
MECO_point = posiciones[MECO_index]
print('MECO:', MECO_point)

tiempo_salida_riel = int(tiempo_salida_riel)

alcance = x.max()
launch_point = posiciones[0]

impact_point = posiciones[-1]
tiempo_impacto = t[-1]

# Crear figura y ejes
fig = plt.figure(figsize=(10, 8))

# Eje 3D para la trayectoria del cohete
ax3d = fig.add_subplot(121, projection='3d')
ax3d.set_xlim([0, alcance+80])
ax3d.set_ylim([0, apogee[1]+80])
ax3d.set_zlim([0, apogee[2]+80])
ax3d.set_title('Trayectoria 3D')
ax3d.set_xlabel("Alcance(m)")
ax3d.set_ylabel("Desplazamiento(m)")
ax3d.set_zlabel("Altura(m)")
#Escribir lanazamiento, apogeo e impacto junto a los puntos 
sep=50 #separacion del punto
ax3d.text(launch_point[0]+sep, launch_point[1]+sep, launch_point[2]+sep, 'Lanzamiento', color='blue')
ax3d.text(impact_point[0]+sep, impact_point[1]+sep, impact_point[2]+sep, 'Impacto', color='red')
ax3d.text(apogee[0]+sep, apogee[1]+sep, apogee[2]+sep, 'Apogeo', color='deeppink')
ax3d.text(MECO_point[0]+sep, MECO_point[1]+sep, MECO_point[2]+sep, 'MECO', color='orangered')

# Plot the launch and impact points with different colors
ax3d.scatter(launch_point[0], launch_point[1], launch_point[2], c='blue', label='Punto de lanzamiento')
ax3d.scatter(impact_point[0], impact_point[1], impact_point[2], c='red', label='Punto de impacto')
ax3d.scatter(apogee[0], apogee[1], apogee[2], c='deeppink', label='Apogeo')
ax3d.scatter(MECO_point[0], MECO_point[1], MECO_point[2], c='orangered', label='MECO')
ax3d.set_box_aspect([1, 0.5, 2])  # Aspect ratio is 1:1:1

sap=150 #separacion de los puntos`
# Eje 2D para la visualización
ax2d = fig.add_subplot(122)
ax2d.set_xlim([-10, t_fin+15])
ax2d.set_ylim([-10, apogee[2]+400])
ax2d.set_title('Trayectoria 2D')
ax2d.set_xlabel("Tiempo(s)")
ax2d.set_ylabel("Altura(m)")
#Scatter del apogeo
ax2d.scatter(tiempo_apogeo, apogee[2], c='deeppink', label='Apogeo', s=200, marker='*')
#Scatter del MECO
ax2d.scatter(t_MECO, MECO_point[2], c='orangered', label='MECO', s=200, marker='*')
#Scatter del impacto y lanzamiento
ax2d.scatter(t[-1], impact_point[2], c='red', label='Impacto', s=200, marker='*')
ax2d.scatter(t[0], z[0], c='blue', label='Lanzamiento', s=200, marker='*')
ax2d.grid()
#ax2d.legend()
muestra_tiempos(tiempo_salida_riel,t_MECO, tiempo_apogeo, tiempo_impacto, ax2d)
#label a las lineas
#ax2d.text(tiempo_salida_riel, z[tiempo_salida_riel], 'Salida riel', color='pink')
ax2d.text(t_MECO+3, MECO_point[2]+sap,'MECO', color='orangered')
ax2d.text(tiempo_apogeo+3, apogee[2]+sap, 'Apogeo', color='deeppink')
ax2d.text(tiempo_impacto+3, impact_point[2]+sap, 'Impacto', color='red')
ax2d.text(t[0]+3, z[0]+sap, 'Lanzamiento', color='blue')

plt.tight_layout()
# Cada cuantos frames graficar
every = 500
y_max = max(y)
#print('y_max:', y_max)
# Función de actualización para la animación
def update(frame):

    #print(frame)
    ax3d.set_xlim([-50, alcance+50])
    ax3d.set_ylim([-50, y_max+50])
    ax3d.set_zlim([-50, apogee[2]+50])

    # Plot the trajectory
    ax3d.plot(x[:frame], y[:frame], z[:frame], 'darkblue')
    #ax3d.scatter(x[frame], y[frame], z[frame], 'g', s=20, marker='*')


    #ax3d.scatter(MECO_point[0], MECO_point[1], MECO_point[2], c='orangered', label='MECO')
    
    if frame == frames[-1]:
        #Create a circle in the xy plane with a diameter of 1000 meters around the impact point
        circle_radius = 500
        circle_points = np.linspace(0, 2*np.pi, 100)
        circle_x = impact_point[0] + circle_radius * np.cos(circle_points)
        circle_y = impact_point[1] + circle_radius * np.sin(circle_points)

        # Plot the circle in the xy plane
        ax3d.plot(circle_x, circle_y, 0, color='0.6', linestyle='--', label='1000 m radio de seguridad')

    #######################################
    ## Grafica 2D
    ax2d.set_xlim([-15, t_fin+15])
    ax2d.set_ylim([-500, apogee[2]+800])
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