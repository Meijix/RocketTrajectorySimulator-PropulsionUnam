####ESTA ANIMACION NO HA SIDO COMPLETADA
#NO SE MUESTRA EL COHETE GIRANDO EN LA TRAYECTORIA

import numpy as np
import pandas as pd
import json
import matplotlib.pyplot as plt
import sys
import os
from matplotlib.animation import FuncAnimation


# Agregar la ruta del directorio que contiene los paquetes al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from Paquetes.utils.funciones import extraer_datoscsv, extraer_datosjson, muestra_tiempos
from Paquetes.utils.dibujar_cohete2 import dibujar_cohete2  # Función para dibujar el cohete


ruta=r'C:\Users\Natalia\OneDrive\Archivos\Tesis\GithubCode\SimuladorVueloNat\3DOF-Rocket-PU\Simulador\Resultados\OutputFiles\VueloLibre-RungeKutta4-100\datos.csv'
# Leer datos de simulación
datos_simulacion = pd.read_csv(ruta)
(tiempos, posiciones, _, thetas, omegas, CPs, CGs, _,
            _, _, _, _, _, _,
            _, _, _, _, _, _, _, _, _, _, _, _, _, _, _,
            accels, _, accangs, Gammas, Alphas, torcas, _, _) = extraer_datoscsv(datos_simulacion)


ruta_json=r'C:\Users\Natalia\OneDrive\Archivos\Tesis\GithubCode\SimuladorVueloNat\3DOF-Rocket-PU\Simulador\Resultados\OutputFiles\VueloLibre-RungeKutta4-100\datos.json'
with open(ruta_json, 'r', encoding='utf-8') as f:
    datos = json.load(f)
(_, t_MECO, tiempo_salida_riel, tiempo_apogeo, tiempo_impacto, max_altitude, _, _, _) = extraer_datosjson(datos)

# Extraer datos de posición y tiempo
x = posiciones[:, 0]
y = posiciones[:, 1]
z = posiciones[:, 2]
t = tiempos[:]
t_fin = tiempos[-1]

# Puntos clave
apogee = [x[z.argmax()], y[z.argmax()], z[z.argmax()]]
MECO_index = np.argmax(t >= t_MECO)
MECO_point = posiciones[MECO_index]
launch_point = posiciones[0]
impact_point = posiciones[-1]

# Crear figura y ejes
fig = plt.figure(figsize=(12, 8))

# Eje 3D para la trayectoria del cohete
ax3d = fig.add_subplot(121, projection='3d')

# Eje 2D para Altura vs Tiempo
ax2d = fig.add_subplot(122)

# Configuración inicial de los límites
sep = 30
sap = 150
y_max = max(y)

# Crear la función de actualización
def update(frame):
    ax3d.clear()
    ax2d.clear()

    # Configurar límites para el eje 3D
    ax3d.set_xlim([-50, x.max() + 50])
    ax3d.set_ylim([-50, y_max + 50])
    ax3d.set_zlim([-50, apogee[2] + 50])

    # Dibujar la trayectoria
    ax3d.plot(x[:frame], y[:frame], z[:frame], 'darkblue')
    ax3d.scatter(x[frame], y[frame], z[frame], c='darkblue', s=80, marker='o')

    # Etiquetas y puntos clave
    ax3d.text(launch_point[0] + sep, launch_point[1] + sep, launch_point[2] + sep, 'Lanzamiento', color='blue')
    ax3d.text(impact_point[0] + sep, impact_point[1] + sep, impact_point[2] + sep, 'Impacto', color='red')
    ax3d.text(apogee[0] + sep, apogee[1] + sep, apogee[2] + sep, 'Apogeo', color='deeppink')
    ax3d.text(MECO_point[0] + sep, MECO_point[1] + sep, MECO_point[2] + sep, 'MECO', color='orangered')

    # Añadir puntos clave
    ax3d.scatter(launch_point[0], launch_point[1], launch_point[2], c='blue', label='Punto de lanzamiento', s=100, marker='*')
    ax3d.scatter(impact_point[0], impact_point[1], impact_point[2], c='red', label='Punto de impacto', s=100, marker='*')
    ax3d.scatter(apogee[0], apogee[1], apogee[2], c='deeppink', label='Apogeo', s=100, marker='*')
    ax3d.scatter(MECO_point[0], MECO_point[1], MECO_point[2], c='orangered', label='MECO', s=100, marker='*')

    # Configurar título y etiquetas del eje 3D
    ax3d.set_title('Trayectoria 3D')
    ax3d.set_xlabel("Desplazamiento (m)")
    ax3d.set_ylabel("Alcance (m)")
    ax3d.set_zlabel("Altura (m)")

    # Dibujar la altura vs tiempo en el eje 2D
    ax2d.set_xlim([-15, t_fin + 15])
    ax2d.set_ylim([-500, apogee[2] + 800])
    ax2d.plot(t[:frame], z[:frame], 'darkblue')
    ax2d.scatter(t[frame], z[frame], c='darkblue', s=80, marker='o')
    muestra_tiempos(tiempo_salida_riel, t_MECO, tiempo_apogeo, tiempo_impacto, ax2d)

    # Añadir el dibujo del cohete en la trayectoria
    theta_deg = np.degrees(thetas[frame])
    dibujar_cohete2(ax=ax2d, angle=theta_deg, x_cm=0, y_cm=z[frame])

    # Etiquetas y puntos clave en el gráfico 2D
    ax2d.set_title('Altura vs Tiempo')
    ax2d.set_xlabel("Tiempo (s)")
    ax2d.set_ylabel("Altura (m)")
    ax2d.scatter(tiempo_apogeo, apogee[2], c='deeppink', label='Apogeo', s=200, marker='*')
    ax2d.scatter(t_MECO, MECO_point[2], c='orangered', label='MECO', s=200, marker='*')
    ax2d.scatter(t[-1], impact_point[2], c='red', label='Impacto', s=200, marker='*')
    ax2d.scatter(t[0], z[0], c='blue', label='Lanzamiento', s=200, marker='*')
    ax2d.grid()

    return ax3d, ax2d

# Crear la animación
frames = np.arange(0, len(t), 30)  # Intervalos de frames
animation = FuncAnimation(fig, update, frames=frames, interval=100, repeat=False)

plt.show()
