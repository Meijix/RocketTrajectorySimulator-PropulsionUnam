#Comparacion de simulaciones
#Leer y graficar las diferentes simulaciones

import pandas as pd
import json
import numpy as np
import matplotlib.pyplot as plt

from funciones import extraer_datoscsv, extraer_datosjson

# Variable para el número de simulaciones
n_simulaciones = 5  # Cambia este valor al número de simulaciones deseadas

# Inicializamos listas para almacenar los datos de cada simulación
lista_archivos_csv = [f'datos_simulacion_{i+1}.csv' for i in range(n_simulaciones)]
lista_archivos_json = [f'datos_simulacion_{i+1}.json' for i in range(n_simulaciones)]

# Leer y extraer los datos de todos los archivos CSV y JSON
datos_simulaciones_csv = []
datos_simulaciones_json = []

for i in range(n_simulaciones):
    # Leer el archivo CSV
    archivo_csv = lista_archivos_csv[i]
    datos_simulacion_csv = pd.read_csv(archivo_csv)
    
    # Extraer los datos del CSV
    (tiempos, posiciones, velocidades, thetas, omegas, CPs, CGs, masavuelo, estabilidad,
    viento_vuelo_mags, viento_vuelo_dirs, viento_vuelo_vecs, wind_xs, wind_ys, wind_zs,
    Dmags, Nmags, Tmags, Dxs, Dys, Dzs, Nxs, Nys, Nzs, Txs, Tys, Tzs, Tvecs, Dvecs, Nvecs,
    accels, palancas, accangs, Gammas, Alphas, torcas, Cds, Machs) = extraer_datoscsv(datos_simulacion_csv)

    # Guardar los datos extraídos del CSV en una lista
    datos_simulaciones_csv.append({
        'tiempos': tiempos,
        'posiciones': posiciones,
        'velocidades': velocidades,
        'thetas': thetas,
        'omegas': omegas,
        'CPs': CPs,
        'CGs': CGs,
        'masavuelo': masavuelo,
        'estabilidad': estabilidad,
        'viento_vuelo_mags': viento_vuelo_mags,
        'viento_vuelo_dirs': viento_vuelo_dirs,
        'viento_vuelo_vecs': viento_vuelo_vecs,
        'wind_xs': wind_xs,
        'wind_ys': wind_ys,
        'wind_zs': wind_zs,
        'Dmags': Dmags,
        'Nmags': Nmags,
        'Tmags': Tmags,
        'Dxs': Dxs,
        'Dys': Dys,
        'Dzs': Dzs,
        'Nxs': Nxs,
        'Nys': Nys,
        'Nzs': Nzs,
        'Txs': Txs,
        'Tys': Tys,
        'Tzs': Tzs,
        'Tvecs': Tvecs,
        'Dvecs': Dvecs,
        'Nvecs': Nvecs,
        'accels': accels,
        'palancas': palancas,
        'accangs': accangs,
        'Gammas': Gammas,
        'Alphas': Alphas,
        'torcas': torcas,
        'Cds': Cds,
        'Machs': Machs
    })

    # Leer el archivo JSON
    archivo_json = lista_archivos_json[i]
    with open(archivo_json, 'r') as f:
        datos_simulacion_json = json.load(f)
    
    # Extraer los datos del JSON
    (d_ext, t_MECO, tiempo_salida_riel, tiempo_apogeo, tiempo_impacto,
    max_altitude, max_speed, max_acceleration_linear, max_acceleration_angular) = extraer_datosjson(datos_simulacion_json)

    # Guardar los datos extraídos del JSON en una lista
    datos_simulaciones_json.append({
        'd_ext': d_ext,
        't_MECO': t_MECO,
        'tiempo_salida_riel': tiempo_salida_riel,
        'tiempo_apogeo': tiempo_apogeo,
        'tiempo_impacto': tiempo_impacto,
        'max_altitude': max_altitude,
        'max_speed': max_speed,
        'max_acceleration_linear': max_acceleration_linear,
        'max_acceleration_angular': max_acceleration_angular
    })

# Comparación de simulaciones (ejemplo básico de cómo podrías graficar o comparar)
# Aquí podrías empezar a graficar o analizar las diferencias entre las simulaciones
for i in range(n_simulaciones):
    print(f"Simulación {i+1}:")
    print(f" - Tiempo de apogeo: {datos_simulaciones_json[i]['tiempo_apogeo']} s")
    print(f" - Altitud máxima: {datos_simulaciones_json[i]['max_altitude']} m")
    print(f" - Velocidad máxima: {datos_simulaciones_json[i]['max_speed']} m/s")
    print(f" - Masa inicial: {datos_simulaciones_csv[i]['masavuelo'][0]} kg")  # Usamos la primera masa del CSV como la masa inicial
    print()

# Aquí puedes agregar código para generar gráficos o comparaciones detalladas
# entre las diferentes simulaciones

# Por ejemplo, podrías graficar la altitud máxima de cada simulación

# Comparación de Altitud máxima
altitudes_maximas = [datos_simulaciones_json[i]['max_altitude'] for i in range(n_simulaciones)]

plt.figure(figsize=(10, 6))
plt.scatter(range(1, n_simulaciones + 1), altitudes_maximas, color='skyblue')
plt.title('Comparación de Altitud Máxima entre Simulaciones')
plt.xlabel('Simulación')
plt.ylabel('Altitud Máxima (m)')
plt.xticks(range(1, n_simulaciones + 1))
#plt.show()

# Comparación de Velocidad máxima
velocidades_maximas = [datos_simulaciones_json[i]['max_speed'] for i in range(n_simulaciones)]

plt.figure(figsize=(10, 6))
plt.scatter(range(1, n_simulaciones + 1), velocidades_maximas, color='lightgreen')
plt.title('Comparación de Velocidad Máxima entre Simulaciones')
plt.xlabel('Simulación')
plt.ylabel('Velocidad Máxima (m/s)')
plt.xticks(range(1, n_simulaciones + 1))
#plt.show()

# Comparación de Aceleración lineal máxima
aceleraciones_maximas = [datos_simulaciones_json[i]['max_acceleration_linear'] for i in range(n_simulaciones)]

plt.figure(figsize=(10, 6))
plt.scatter(range(1, n_simulaciones + 1), aceleraciones_maximas, color='salmon')
plt.title('Comparación de Aceleración Lineal Máxima entre Simulaciones')
plt.xlabel('Simulación')
plt.ylabel('Aceleración Lineal Máxima (m/s²)')
plt.xticks(range(1, n_simulaciones + 1))
plt.show()

