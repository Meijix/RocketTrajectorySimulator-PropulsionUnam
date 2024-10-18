import numpy as np
import pandas as pd
import json
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from Simulador.utils.funciones import *
from Simulador.utils.dibujar_cohete import dibujar_cohete
from Simulador.utils.angulos import nice_angle

# Leer los datos de la simulación desde el archivo CSV
datos_simulacion = pd.read_csv('datos_simulacion.csv')

print(datos_simulacion.columns)
# Extraer los datos del CSV
(tiempos, posiciones, velocidades, thetas, omegas, CPs, CGs, masavuelo, estabilidad,
 viento_vuelo_mags, viento_vuelo_dirs, viento_vuelo_vecs, wind_xs, wind_ys, wind_zs,
 Dmags, Nmags, Tmags, Dxs, Dys, Dzs, Nxs, Nys, Nzs, Txs, Tys, Tzs, Tvecs, Dvecs, Nvecs,
 accels, palancas, accangs, Gammas, Alphas, torcas, Cds, Machs) = extraer_datoscsv(datos_simulacion)

# Leer los datos de la simulación desde el archivo JSON
with open('datos_simulacion.json', 'r') as f:
    datos = json.load(f)

# Extraer los datos del JSON
(d_ext, t_MECO, tiempo_salida_riel, tiempo_apogeo, tiempo_impacto,
    max_altitude, max_speed, max_acceleration_linear, max_acceleration_angular) = extraer_datosjson(datos)

# Configuración inicial
t = tiempos[:]
t_fin = tiempos[-1]
tamaño = 10

# Crear figura y ejes
fig = plt.figure(figsize=(12, 6))
axcohete = fig.add_subplot(121)
ax2d = fig.add_subplot(122)

# Configurar el gráfico del cohete
axcohete.set_aspect("equal")
axcohete.set_title('Dibujo del Cohete')

# Eje 2D para la visualización
ax2d.set_xlim([0, t_fin + 1])
ax2d.set_ylim([-95, 95])
ax2d.set_title('Ángulos del Cohete')
ax2d.set_xlabel("Tiempo (s)")
ax2d.set_ylabel("Grados")
ax2d.grid()

# Cada cuántos frames graficar
every = 40

print(nice_angle(thetas))

# Función de actualización para la animación
def update(frame):
    axcohete.clear()
    axcohete.set_xlim([-15, 15])
    axcohete.set_ylim([-15, 15])
    dibujar_cohete(0, 0, np.degrees(thetas[frame]), tamaño, ax=axcohete)  # Dibujar el cohete inclinado
    #ax.set_xlim(-10, 10)
    #ax.set_ylim(-10, 10)
    axcohete.set_aspect("equal")
    axcohete.set_title('Dibujo del Cohete')

    ax2d.plot(t[:frame + 1], np.degrees(thetas[:frame + 1]), 'b-')  # Graficar hasta el frame actual
    ax2d.scatter(t[frame], np.degrees(thetas[frame]), color='red')  # Puntos en el gráfico

    return ax2d, axcohete

# Crear la animación
fps = 30
frames = np.arange(0, len(t), every)
animation = FuncAnimation(fig, update, frames=frames, interval=1000/fps, repeat=False)

plt.show()

fps=fps/3
print('Guardando animacion...')
# Guardar la animación como mp4
animation.save("AngulosAnimacionPrueba.gif")
#animation.save("AngulosAnimados.mp4", fps=fps)
print("mp4 Guardado")
