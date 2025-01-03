#Comparar los resultados de los diferentes métodos de integración

# Importar librerías
#Graficar los resultados de la simulacion
import matplotlib.pyplot as plt
import pandas as pd
import json
import sys
import os

# Agregar la ruta del directorio que contiene los paquetes al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

#Importar paquetes propios de carpeta superior Paquetes
from Paquetes.utils.angulos import nice_angle
from Paquetes.utils.funciones import extraer_datoscsv, extraer_datosjson
#from Simulador.src.condiciones_init import *

#Indicar el tipo de vuelo
TipoVuelo = 'VueloLibre'
#TipoVuelo = 'VueloParacaidas'
#Integradores a comparar
integradores = ['Euler', 'RungeKutta2', 'RungeKutta4', 'RK45', 'RK23', 'DOP853', 'BDF', 'LSODA']

#Iniciar un diccionario para guardar los datos de los diferentes integradores
#Cada integrador tiene un diccionario con los datos de la simulación
#Ejemplos de datos: posiciones, velocidades, aceleraciones, etc.
info = {}

#Acceder a las carpetas de ese tipo de vuelo
for integrador in integradores:
    carpeta = f'C:/Users/Natalia/OneDrive/Archivos/Tesis/GithubCode/SimuladorVueloNat/3DOF-Rocket-PU/Simulador/Resultados/OutputFiles/{TipoVuelo}-{integrador}'
    archivo_csv = f'{carpeta}/datos.csv'
    archivo_json = f'{carpeta}/datos.json'

    # Leer los datos de la simulación desde el archivo CSV
    datos_csv = pd.read_csv(archivo_csv)
    # Extraer los datos del csv
    (tiempos, posiciones, velocidades, thetas, omegas, CPs, CGs, _,
    viento_vuelo_mags, viento_vuelo_dirs, viento_vuelo_vecs, wind_xs, wind_ys, wind_zs,
    Dmags, Nmags, Tmags, Dxs, Dys, Dzs, Nxs, Nys, Nzs, Txs, Tys, Tzs, Tvecs, Dvecs, Nvecs,
    accels, palancas, accangs, Gammas, Alphas, torcas, Cds, Machs) = extraer_datoscsv(datos_csv)

    #########################################
    # Leer los datos de la simulación desde el archivo JSON
    with open(archivo_json, 'r', encoding='utf-8') as f:
        datos_json = json.load(f)
    # Extraer los datos del json
    (d_ext, t_MECO, tiempo_salida_riel, tiempo_apogeo, tiempo_impacto,
        max_altitude, max_speed, max_acceleration_linear, max_acceleration_angular) = extraer_datosjson(datos_json)
    #Guardar los datos en el diccionario
    info[integrador] = {}
    #del csv
    info[integrador]['tiempos'] = tiempos
    info[integrador]['posiciones'] = posiciones
    info[integrador]['velocidades'] = velocidades
    info[integrador]['thetas'] = thetas
    info[integrador]['omegas'] = omegas
    #del json
    info[integrador]['apogeo'] = max_altitude
    info[integrador]['velocidad_max'] = max_speed
    info[integrador]['aceleracion_max'] = max_acceleration_linear
    info[integrador]['aceleracion_max_angular'] = max_acceleration_angular
    info[integrador]['tiempo_impacto'] = tiempo_impacto
    info[integrador]['tiempo_apogeo'] = tiempo_apogeo
    #info[integrador]['tiempo_MECO'] = t_MECO
    info[integrador]['tiempo_salida_riel'] = tiempo_salida_riel


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
