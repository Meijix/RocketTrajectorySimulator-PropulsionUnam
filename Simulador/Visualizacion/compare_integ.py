#Comparar los resultados de los diferentes métodos de integración en el vuelo completo
#
# Simula el mismo vuelo (mismo cohete, mismas condiciones y mismo viento) con todos los
# métodos del catálogo (Paquetes/PaqueteEDOs/metodos.py), guarda una tabla de resultados
# y grafica las trayectorias. Ejecutar desde la raíz:
#     python -m Simulador.Visualizacion.compare_integ

# Importar librerías
import contextlib
import io
import os
import sys
import time

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Agregar la ruta del directorio que contiene los paquetes al sys.path
RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(RAIZ)

#Importar paquetes propios de carpeta superior Paquetes
from Paquetes.utils.angulos import nice_angle
from Paquetes.utils.figuras import guardar_figuras_al_mostrar
from Paquetes.PaqueteEDOs.metodos import METODOS
from Paquetes.PaqueteFisica.vuelo import Vuelo
from Simulador.src import condiciones_init as c_init
from Simulador.src.XitleFile import Xitle

CARPETA = os.path.join(RAIZ, 'Simulador', 'Resultados', 'OutputFiles', 'ComparacionIntegradores')
guardar_figuras_al_mostrar(os.path.join(CARPETA, 'figuras'))

#Indicar el tipo de vuelo
TipoVuelo = 'VueloLibre'
#Integradores a comparar: todos los del catálogo, con su nombre corto
integradores = list(METODOS)
dt = c_init.dt              # paso (métodos de paso fijo) o paso máximo (adaptativos)
dt_referencia = dt / 5      # la solución de referencia usa DOP853 con un paso cinco veces menor


def simular(clave, paso):
    """Vuelo libre del Xitle II con el integrador indicado. Devuelve el objeto Vuelo, tiempos, estados y el tiempo de cómputo."""
    Xitle.parachute_added = False
    vuelo = Vuelo(Xitle, c_init.atmosfera_actual, c_init.viento_actual)
    inicio = time.perf_counter()
    with contextlib.redirect_stdout(io.StringIO()):
        salida = vuelo.simular_vuelo(c_init.estado.copy(), c_init.t_max, paso, paso, clave)
    return vuelo, np.array(salida[0]), np.array(salida[1]), time.perf_counter() - inicio


print(f"Solución de referencia: DOP853 con paso máximo {dt_referencia:g} s ...")
_, t_ref, sim_ref, _ = simular('DOP853', dt_referencia)
apogeo_ref = sim_ref[:, 2].max()
t_impacto_ref = t_ref[-1]

#Iniciar un diccionario para guardar los datos de los diferentes integradores
#Cada integrador tiene un diccionario con los datos de la simulación
info = {}
filas = []
for integrador in integradores:
    m = METODOS[integrador]
    print(f"Simulando con {m.corto} ({m.nombre}) ...")
    vuelo, tiempos, sim, t_computo = simular(m.clave, dt)
    posiciones, velocidades = sim[:, 0:3], sim[:, 3:6]
    rapidez = np.linalg.norm(velocidades, axis=1)

    info[integrador] = {
        'tiempos': tiempos,
        'posiciones': posiciones,
        'velocidades': velocidades,
        'thetas': sim[:, 6],
        'omegas': sim[:, 7],
        'apogeo': posiciones[:, 2].max(),
        'velocidad_max': rapidez.max(),
        'tiempo_impacto': vuelo.tiempo_impacto,
        'tiempo_apogeo': vuelo.tiempo_apogeo,
        'tiempo_salida_riel': vuelo.tiempo_salida_riel,
    }

    # Diferencia con la referencia a lo largo de todo el vuelo (altitud interpolada en los mismos tiempos)
    comunes = tiempos[tiempos <= t_ref[-1]]
    diferencia = np.interp(comunes, tiempos, posiciones[:, 2]) - np.interp(comunes, t_ref, sim_ref[:, 2])
    filas.append({
        'Método': m.corto,
        'Nombre': m.nombre,
        'Implementación': m.origen,
        'Paso': m.paso,
        'Apogeo [m]': info[integrador]['apogeo'],
        't apogeo [s]': vuelo.tiempo_apogeo,
        't impacto [s]': vuelo.tiempo_impacto,
        'Vel. máxima [m/s]': rapidez.max(),
        'Pasos': vuelo.pasos,
        'Evaluaciones de f': vuelo.evaluaciones,
        'Tiempo de cómputo [s]': t_computo,
        'Dif. apogeo vs ref. [m]': info[integrador]['apogeo'] - apogeo_ref,
        'Dif. t impacto vs ref. [s]': vuelo.tiempo_impacto - t_impacto_ref,
        'RMS altitud vs ref. [m]': np.sqrt(np.mean(diferencia**2)),
    })

# Tabla de resultados con todos los métodos
tabla = pd.DataFrame(filas)
os.makedirs(CARPETA, exist_ok=True)
ruta_tabla = os.path.join(CARPETA, 'tabla_integradores.csv')
tabla.to_csv(ruta_tabla, index=False)
print()
print(f"{TipoVuelo} del Xitle II, dt = {dt:g} s. Referencia: DOP853 con paso máximo {dt_referencia:g} s "
      f"(apogeo {apogeo_ref:.2f} m, impacto {t_impacto_ref:.3f} s)")
print(tabla.drop(columns=['Nombre']).to_string(index=False, float_format=lambda v: f"{v:.4g}"))
print(f"Tabla guardada en: {ruta_tabla}")

###########################################################

#Graficar las posiciones de los diferentes integradores
plt.figure()
for integrador in integradores:
    plt.plot(info[integrador]['tiempos'], info[integrador]['posiciones'][:, 2], label=integrador)
    #scatter de apogeo
    #plt.scatter(info[integrador]['tiempo_apogeo'], info[integrador]['apogeo'], color='red', label='Apogeo') 
plt.xlabel('Tiempo [s]')
plt.ylabel('Altura [m]')
plt.title('Altura vs Tiempo')
plt.xlim(0, 85)
plt.ylim(0, 10000)
plt.legend()
plt.grid()
plt.show()

#Graficar las velocidades de los diferentes integradores
plt.figure()
for integrador in integradores:
    plt.plot(info[integrador]['tiempos'], info[integrador]['velocidades'][:, 2], label=integrador)
plt.xlabel('Tiempo [s]')
plt.ylabel('Velocidad [m/s]')
plt.title('Velocidad vs Tiempo')
#linea horizontal en 0
plt.axhline(y=0, color='k', linestyle='--')
plt.legend()
plt.grid()
plt.ylim(-325, 550)
plt.xlim(0, 85)
plt.show()

#Graficar thetas de los diferentes integradores
plt.figure()
for integrador in integradores:
    plt.plot(info[integrador]['tiempos'], nice_angle(info[integrador]['thetas']), label=integrador)
plt.xlabel('Tiempo [s]')
plt.ylabel('Theta [deg]')
plt.title('Theta vs Tiempo')
#lineas en 90 y -90
plt.axhline(y=90, color='darkslategray', linestyle='--')
plt.axhline(y=-90, color='darkslategray', linestyle='--')
plt.axhline(y=0, color='k', linestyle='--')
plt.xlim(0, 85)
plt.legend()
plt.grid()
plt.show()

#Graficar omegas de los diferentes integradores
plt.figure()
for integrador in integradores:
    plt.plot(info[integrador]['tiempos'], info[integrador]['omegas'], label=integrador)
plt.xlabel('Tiempo [s]')
plt.ylabel('Omega [rad/s]')
plt.title('Omega vs Tiempo')
plt.xlim(0, 85)
plt.ylim(-8,8)
plt.legend()
plt.grid()
plt.show()

###########################################
# Comparar el apogeo de los diferentes integradores
num_integradores = len(integradores)
x_positions = range(1, num_integradores + 1)  # Posiciones únicas en el eje x

plt.figure(figsize=(8, 6))
for i, integrador in enumerate(integradores):
    plt.scatter(x_positions[i], info[integrador]['apogeo'], label=integrador)
    #agregar el valor de apogeo junto a cada scatter
    plt.annotate(f"{info[integrador]['apogeo']:.2f}", (x_positions[i], info[integrador]['apogeo']))

plt.xticks(x_positions, integradores)  # Nombres de los integradores en el eje x
plt.xlabel('Integrador')
plt.ylabel('Altura [m]')
plt.title('Altura de Apogeo')
plt.legend(title="Integradores")
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()

# Comparar el tiempo de apogeo de los diferentes integradores
plt.figure(figsize=(8, 6))
for i, integrador in enumerate(integradores):
    plt.scatter(x_positions[i], info[integrador]['tiempo_apogeo'], label=integrador)
    #agregar el valor de tiempo de apogeo junto a cada scatter
    plt.annotate(f"{info[integrador]['tiempo_apogeo']:.2f}", (x_positions[i], info[integrador]['tiempo_apogeo']))
plt.xticks(x_positions, integradores)  # Nombres de los integradores en el ej
plt.xlabel('Integrador')
plt.ylabel('Tiempo [s]')
plt.title('Tiempo de Apogeo')
plt.legend(title="Integradores")
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()

# Comparar el tiempo de impacto de los diferentes integradores
plt.figure(figsize=(8, 6))
for i, integrador in enumerate(integradores):
    plt.scatter(x_positions[i], info[integrador]['tiempo_impacto'], label=integrador)
    #agregar el valor de tiempo de impacto junto a cada scatter
    plt.annotate(f"{info[integrador]['tiempo_impacto']:.2f}", (x_positions[i], info[integrador]['tiempo_impacto']))
plt.xticks(x_positions, integradores)  # Nombres de los integradores en el ej
plt.xlabel('Integrador')
plt.ylabel('Tiempo [s]')
plt.title('Tiempo de Impacto')
plt.legend(title="Integradores")
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()

# Comparar la velocidad máxima de los diferentes integradores
plt.figure(figsize=(8, 6))
for i, integrador in enumerate(integradores):
    plt.scatter(x_positions[i], info[integrador]['velocidad_max'], label=integrador)
    #agregar el valor de velocidad máxima junto a cada scatter
    plt.annotate(f"{info[integrador]['velocidad_max']:.2f}", (x_positions[i], info[integrador]['velocidad_max']))
plt.xticks(x_positions, integradores)  # Nombres de los integradores en el ej
plt.xlabel('Integrador')
plt.ylabel('Velocidad [m/s]')
plt.title('Velocidad Máxima')
plt.legend(title="Integradores")
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()
