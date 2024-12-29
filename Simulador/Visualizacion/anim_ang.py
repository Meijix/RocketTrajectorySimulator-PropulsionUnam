import numpy as np
import pandas as pd
import json
import sys
import os
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Agregar la ruta del directorio que contiene los paquetes al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
# Supongamos que estas funciones ya están definidas
from Paquetes.utils.funciones import extraer_datoscsv, extraer_datosjson, muestra_tiempos
from Paquetes.utils.dibujar_cohete2 import dibujar_cohete2, actualizar

# Leer datos de simulación
datos_simulacion = pd.read_csv(r'C:\Users\Natalia\OneDrive\Archivos\Tesis\GithubCode\SimuladorVueloNat\3DOF-Rocket-PU\Simulador\src\datos_simulacion.csv')
(tiempos, _, _, thetas, omegas, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _) = extraer_datoscsv(datos_simulacion)

# Leer los datos de la simulación desde el archivo JSON
with open('datos_simulacion.json', 'r', encoding= 'utf-8') as f:
    datos = json.load(f)
# Extraer los datos del json
(_, t_MECO, tiempo_salida_riel, tiempo_apogeo, tiempo_impacto,
    max_altitude, _, _, _) = extraer_datosjson(datos)

# Crear figura y ejes
fig = plt.figure(figsize=(14, 7))

# Subgráfico 1: Cohete rotado
ax_cohete = fig.add_subplot(121)
ax_cohete.set_xlim(-10, 10)
ax_cohete.set_ylim(-10, 10)
ax_cohete.set_aspect('equal')

# Subgráfico 2: Theta y Omega vs Tiempo
ax_theta_omega = fig.add_subplot(122)
ax_theta_omega.set_xlim([0, tiempos[-1]])
ax_theta_omega.set_ylim([min(thetas.min(), omegas.min())-0.2, max(thetas.max(), omegas.max())+0.2])
ax_theta_omega.set_xlabel("Tiempo (s)")
ax_theta_omega.set_ylabel("Ángulo (rad) / Velocidad Angular (rad/s)")
ax_theta_omega.set_title("Theta y Omega vs Tiempo")

# Función de actualización de la animación
def update(frame):
    # Limpieza y configuración del subgráfico del cohete
    ax_cohete.clear()
    ax_cohete.set_xlim(-4, 4)
    ax_cohete.set_ylim(-5, 5)
    ax_cohete.set_aspect('equal')
    theta_deg = np.degrees(thetas[frame])
    
    # Dibujar el cohete actualizado
    dibujar_cohete2(ax=ax_cohete, angle=theta_deg, x_cm=0, y_cm=0, long=4.5)
    ax_cohete.set_title(f"Ángulo: {theta_deg:.2f}°")
    #linea vertical para el cohete
    ax_cohete.axvline(x=0, color='0.5', linestyle='--')

    # Limpieza y configuración del subgráfico Theta y Omega vs Tiempo
    ax_theta_omega.clear()
    ax_theta_omega.set_title("Theta y Omega vs Tiempo")
    ax_theta_omega.set_xlim([0, tiempos[-1]])
    ax_theta_omega.set_ylim([min(thetas.min(), omegas.min()), max(thetas.max(), omegas.max())])
    ax_theta_omega.plot(tiempos[:frame], thetas[:frame], color="yellowgreen")
    ax_theta_omega.plot(tiempos[:frame], omegas[:frame], color="tomato")

    # Etiquetas dinámicas para valores actuales
    ax_theta_omega.scatter(tiempos[frame], thetas[frame], color="yellowgreen", label=f"Theta: {thetas[frame]:.2f} rad")
    ax_theta_omega.scatter(tiempos[frame], omegas[frame], color="tomato", label=f"Omega: {omegas[frame]:.2f} rad/s")
    
    # Mostrar tiempos importantes
    muestra_tiempos(tiempo_salida_riel, t_MECO, tiempo_apogeo, tiempo_impacto, ax_theta_omega)

    # Configurar leyenda y etiquetas
    ax_theta_omega.legend()
    ax_theta_omega.set_xlabel("Tiempo (s)")
    return ax_cohete, ax_theta_omega

# Crear la animación
frames = np.arange(0, len(tiempos), 10)  # Intervalos optimizados
animation = FuncAnimation(fig, update, frames=frames, interval=100, repeat=False)

plt.show()