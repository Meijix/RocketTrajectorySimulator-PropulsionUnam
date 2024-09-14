import numpy as np
import pandas as pd
import json
import matplotlib.pyplot as plt

from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation

from funciones import *
from dibujarCohete import *

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

t = tiempos[:]
t_fin = tiempos[-1]
theta0 = thetas[0]
theta_fin = thetas[-1]
tamaño = 5

# Crear figura y ejes
fig = plt.figure(figsize=(12, 6))
ax = fig.add_subplot(121)
ax2d = fig.add_subplot(122)

# Dibujo cohete inclinado
dibujar_cohete(0, 0, theta0, tamaño)
ax.set_aspect("equal")

# Eje 2D para la visualización
ax2d.set_xlim([0, t_fin+10])
ax2d.set_ylim([-10,10])
ax2d.set_title('Angulos del cohete')
ax2d.set_xlabel("Tiempo (s)")
ax2d.set_ylabel("Grados ()")
ax2d.grid()

# Cada cuantos frames graficar
every = 100

# Función de actualización para la animación
def update(frame):

    #######################################
    ## Dibujo cohete inclinado
    dibujar_cohete(0, 0, thetas[frame], tamaño)
    ax.set_aspect("equal")

    #ax2d.clear()
    ax2d.set_xlim([0, t_fin+10])
    ax2d.set_ylim([-15,15])
    ax2d.plot(t[:frame], thetas[:frame], 'b-')
    ax2d.scatter(t[frame], thetas[frame])

    return ax, ax2d

# Crear la animación
frames = np.arange(0, len(t)+every, every)
if frames[-1] > len(t): frames[-1] = len(t)-1
#print(frames)
animation = FuncAnimation(fig, update, frames=frames, interval=5, repeat=False)

plt.show()

animation.save("AngulosAnimados.gif")
print("GIF Guardado")