# Comparacion de simulaciones
# Leer y graficar las diferentes simulaciones

import pandas as pd
import json
import numpy as np
import matplotlib.pyplot as plt

from funciones import extraer_datoscsv, extraer_datosjson

# Variable para el número de simulaciones
n_simulaciones = 5  # Cambia este valor al número de simulaciones deseadas

# Inicializamos listas para almacenar los archivos CSV y JSON
lista_archivos_csv = [f'datos_simulacion_{i+1}.csv' for i in range(n_simulaciones)]
lista_archivos_json = [f'datos_simulacion_{i+1}.json' for i in range(n_simulaciones)]

# Inicializamos una lista para almacenar los diccionarios con datos de cada simulación
simulaciones = []

for i in range(n_simulaciones):
    # Diccionario para almacenar la simulación i
    dic_i = {}

    # Leer y extraer los datos del CSV
    archivo_csv = lista_archivos_csv[i]
    datos_simulacion_csv = pd.read_csv(archivo_csv)
    
    (tiempos, posiciones, velocidades, thetas, omegas, CPs, CGs, masavuelo, estabilidad,
    viento_vuelo_mags, viento_vuelo_dirs, viento_vuelo_vecs, wind_xs, wind_ys, wind_zs,
    Dmags, Nmags, Tmags, Dxs, Dys, Dzs, Nxs, Nys, Nzs, Txs, Tys, Tzs, Tvecs, Dvecs, Nvecs,
    accels, palancas, accangs, Gammas, Alphas, torcas, Cds, Machs) = extraer_datoscsv(datos_simulacion_csv)

    # Almacenamos los datos del CSV en el diccionario
    dic_i.update({
        "tiempos": tiempos,
        "posiciones": posiciones,
        "velocidades": velocidades,
        "thetas": thetas,
        "omegas": omegas,
        "CPs": CPs,
        "CGs": CGs,
        "masavuelo": masavuelo,
        "estabilidad": estabilidad,
        "viento_vuelo_mags": viento_vuelo_mags,
        "viento_vuelo_dirs": viento_vuelo_dirs,
        "viento_vuelo_vecs": viento_vuelo_vecs,
        "wind_xs": wind_xs,
        "wind_ys": wind_ys,
        "wind_zs": wind_zs,
        "Dmags": Dmags,
        "Nmags": Nmags,
        "Tmags": Tmags,
        "Dxs": Dxs,
        "Dys": Dys,
        "Dzs": Dzs,
        "Nxs": Nxs,
        "Nys": Nys,
        "Nzs": Nzs,
        "Txs": Txs,
        "Tys": Tys,
        "Tzs": Tzs,
        "Tvecs": Tvecs,
        "Dvecs": Dvecs,
        "Nvecs": Nvecs,
        "accels": accels,
        "palancas": palancas,
        "accangs": accangs,
        "Gammas": Gammas,
        "Alphas": Alphas,
        "torcas": torcas,
        "Cds": Cds,
        "Machs": Machs
    })

    # Leer y extraer los datos del JSON
    archivo_json = lista_archivos_json[i]
    with open(archivo_json, 'r') as f:
        datos_simulacion_json = json.load(f)
    
    (d_ext, t_MECO, tiempo_salida_riel, tiempo_apogeo, tiempo_impacto,
    max_altitude, max_speed, max_acceleration_linear, max_acceleration_angular) = extraer_datosjson(datos_simulacion_json)

    # Almacenamos los datos del JSON en el diccionario
    dic_i.update({
        "d_ext": d_ext,
        "t_MECO": t_MECO,
        "tiempo_salida_riel": tiempo_salida_riel,
        "tiempo_apogeo": tiempo_apogeo,
        "tiempo_impacto": tiempo_impacto,
        "max_altitude": max_altitude,
        "max_speed": max_speed,
        "max_acceleration_linear": max_acceleration_linear,
        "max_acceleration_angular": max_acceleration_angular
    })

    # Añadir la simulación actual a la lista de simulaciones
    simulaciones.append(dic_i)

# Imprimir ejemplo de simulación para verificar que los datos se guardaron correctamente
#print(f"Simulaciones: {simulaciones}")
#print(f"Una sim: {simulaciones[0]}")

# Graficar todas las trayectorias en una misma gráfica
plt.figure(figsize=(10, 6))

for i, simulacion in enumerate(simulaciones):
    tiempos = simulacion["tiempos"]
    posiciones = simulacion["posiciones"]
    plt.plot(tiempos, posiciones, label=f'Sim {i+1}', ls='--', marker='*')

plt.xlabel('Tiempo')
plt.ylabel('Posición')
plt.title('Trayectorias de las simulaciones')
plt.legend()
plt.grid(True)

#plt.show()

# Graficar todas las velocidades en una misma gráfica
plt.figure(figsize=(10, 6))
for i, simulacion in enumerate(simulaciones):
    tiempos = simulacion["tiempos"]
    velocidades = simulacion["velocidades"]
    plt.plot(tiempos, velocidades, label=f'Sim {i+1}')

plt.xlabel('Tiempo')
plt.ylabel('Velocidad')
plt.title('Velocidades de las simulaciones')
plt.legend()
plt.grid(True)
#plt.show()

# Graficar todas las aceleraciones en una misma gráfica
plt.figure(figsize=(10, 6))
for i, simulacion in enumerate(simulaciones):
    tiempos = simulacion["tiempos"]
    accels = simulacion["accels"]
    plt.plot(tiempos, accels, label=f'Sim {i+1}')

plt.xlabel('Tiempo')
plt.ylabel('Aceleración')
plt.title('Aceleraciones de las simulaciones')
plt.legend()
plt.grid(True)
plt.show()

'''
altitudes_maximas = [datos_simulaciones_json[i]['max_altitude'] for i in range(n_simulaciones)]
velocidades_maximas = [datos_simulaciones_json[i]['max_speed'] for i in range(n_simulaciones)]
masas_iniciales = [datos_simulaciones_csv[i]['masavuelo'][0] for i in range(n_simulaciones)]
'''