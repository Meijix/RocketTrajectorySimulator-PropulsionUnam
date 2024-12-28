import numpy as np
from math import pi
import pandas as pd
import json
import time
import random  # Para variar las condiciones en cada simulación

from Simulador.src.condiciones_init import *
from Simulador.src.XitleFile import *
from Simulador.PaqueteFisica.Vuelo import *
from Simulador.PaqueteFisica.Viento import Viento

# Variable para el número de simulaciones
n_simulaciones = 5  # Cambia este valor para el número de simulaciones deseadas

# Parámetros de la simulación
dt = 0.01  # Intervalo de tiempo
t_max = 800  # Tiempo máximo
dt_out = 0.01  # Intervalo de salida

masa_inicial_variada = [30,35,40,45,50]
# Bucle para múltiples simulaciones
for sim_num in range(1, n_simulaciones + 1):
    print(f"Simulación {sim_num} de {n_simulaciones}")
    
    # Asignar el valor de la lista a la masa inicial variada
    XitleFile.masa = masa_inicial_variada[sim_num - 1]
    print(f"Masa inicial para la simulación {sim_num}: {XitleFile.masa} kg")

    # Configuración inicial para cada simulación
    XitleFile.parachute_added = False
    XitleFile.parachute_active1 = False

    # Estado inicial
    x0, y0, z0 = 0, 0, 0
    vx0, vy0, vz0 = 0, 0, 0

    theta0, omega0 = np.deg2rad(riel.angulo), 0
    estado = np.array([x0, y0, z0, vx0, vy0, vz0, theta0, omega0])

    # Tiempo inicial
    inicio = time.time()

    # Variar el viento en cada simulación
    viento_actual = Viento(vel_base=10, vel_mean=2 + random.uniform(-1, 1), vel_var=0.01, var_ang=20)
    viento_actual.actualizar_viento3D()

    vuelo1 = Vuelo(XitleFile, atmosfera_actual, viento_actual)
    tiempos, sim, CPs, CGs, masavuelo, viento_vuelo_mags, viento_vuelo_dirs, viento_vuelo_vecs, Tvecs, Dvecs, Nvecs, accels, palancas, accangs, Gammas, Alphas, torcas, Cds, Machs = vuelo1.simular_vuelo(estado, t_max, dt, dt_out)

    # Resultados de posiciones y velocidades
    posiciones = np.array([state[0:3] for state in sim])
    velocidades = np.array([state[3:6] for state in sim])
    thetas = np.array([state[6] for state in sim])
    omegas = np.array([state[7] for state in sim])

    # Magnitudes de las fuerzas
    Tmags = np.array([np.linalg.norm(Tvec) for Tvec in Tvecs])
    Dmags = np.array([np.linalg.norm(Dvec) for Dvec in Dvecs])
    Nmags = np.array([np.linalg.norm(Nvec) for Nvec in Nvecs])

    Txs, Tys, Tzs = zip(*Tvecs)
    Dxs, Dys, Dzs = zip(*Dvecs)
    Nxs, Nys, Nzs = zip(*Nvecs)

    wind_xs = [vec[0] for vec in viento_vuelo_vecs]
    wind_ys = [vec[1] for vec in viento_vuelo_vecs]
    wind_zs = [vec[2] for vec in viento_vuelo_vecs]

    stability = [(CPs[i] - CGs[i]) / diam_ext for i in range(len(tiempos) - 1)]

    # Datos importantes
    max_altitude = max(posiciones[:, 2])
    max_speed = max(np.linalg.norm(velocidades, axis=1))

    # Guardar los datos de la simulación en un archivo CSV
    datos_simulados = pd.DataFrame({
        'tiempos': tiempos[1:],
        'posiciones_x': posiciones[1:, 0],
        'posiciones_y': posiciones[1:, 1],
        'posiciones_z': posiciones[1:, 2],
        'velocidades_x': velocidades[1:, 0],
        'velocidades_y': velocidades[1:, 1],
        'velocidades_z': velocidades[1:, 2],
        'thetas': thetas[1:],
        'omegas': omegas[1:],
        'CPs': CPs,
        'CGs': CGs,
        'masavuelo': masavuelo[1:],
        'viento_vuelo_mags': viento_vuelo_mags,
        'viento_vuelo_dirs': viento_vuelo_dirs,
        'viento_vuelo_vecs': viento_vuelo_vecs,
        'wind_xs': wind_xs,
        'wind_ys': wind_ys,
        'wind_zs': wind_zs,
        'Tmags': Tmags,
        'Dmags': Dmags,
        'Nmags': Nmags,
        'Txs': Txs,
        'Tys': Tys,
        'Tzs': Tzs,
        'Dxs': Dxs,
        'Dys': Dys,
        'Dzs': Dzs,
        'Nxs': Nxs,
        'Nys': Nys,
        'Nzs': Nzs,
        'accels': accels,
        'palancas': palancas,
        'accangs': accangs,
        'Gammas': Gammas,
        'Alphas': Alphas,
        'torcas': torcas,
        'Cds': Cds,
        'Machs': Machs,
        'estabilidad': stability
    })

    # Guardar CSV numerado por simulación
    csv_filename = f'datos_simulacion_{sim_num}.csv'
    datos_simulados.to_csv(csv_filename, index=False)
    print(f'CSV guardado: {csv_filename}')

    # Guardar los datos importantes en un archivo JSON
    datos_a_guardar = {
        'd_ext': XitleFile.d_ext,
        't_MECO': XitleFile.t_MECO,
        'tiempo_salida_riel': vuelo1.tiempo_salida_riel,
        'tiempo_apogeo': vuelo1.tiempo_apogeo,
        'tiempo_impacto': vuelo1.tiempo_impacto,
        'max_altitude': max_altitude,
        'max_speed': max_speed,
        'max_acceleration_linear': np.max(accels),
        'max_acceleration_angular': np.max(accangs),
        'masa_inicial': masa_inicial_variada  # Agregar la masa inicial usada en esta simulación
    }

    json_filename = f'datos_simulacion_{sim_num}.json'
    with open(json_filename, 'w') as f:
        json.dump(datos_a_guardar, f, indent=4)
    print(f'JSON guardado: {json_filename}')

    # Tiempo de ejecución por simulación
    fin = time.time()
    print(f"Tiempo de ejecución de simulación {sim_num}: {fin - inicio:.1f}s\n")
