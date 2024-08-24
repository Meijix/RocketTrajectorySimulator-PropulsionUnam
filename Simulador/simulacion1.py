#Simulacion sin paracaidas del Xitle2

import numpy as np
from math import pi

from condiciones_init import *
from Xitle import *
from Vuelo import *
from Viento import Viento2D


#quitar el paracaidas
Xitle.parachute_added = False
#desactivar el paracaidas
Xitle.parachute_active1 = False

# Estado inicial
x0, y0, z0 = 0, 0, 0
vx0, vy0, vz0 = 0, 0, 0

theta0, omega0 = np.deg2rad(riel.angulo), 0
estado=np.array([x0, y0, z0, vx0, vy0, vz0, theta0, omega0])
#print(estado)
#estado=list(estado)
#print(estado)
#Parametros de la simulacion
dt=0.01 #0.1 #[s]
t_max = 120 #[s]

#t=0
#it = 0

import time
inicio = time.time()
print("Simulando...")

viento_actual = Viento2D(vel_mean=10, vel_var=2)
viento_actual.actualizar_viento()
#viento_actual = Viento2D(vel_mean=100, vel_var=0)
#print(viento_actual)
print("Viento actual",viento_actual.vector)

vuelo1 = Vuelo(Xitle, atmosfera_actual, viento_actual)
tiempos, sim, CPs, CGs, masavuelo, viento_vuelo_mags, viento_vuelo_dirs, viento_vuelo_vecs, Tvecs, Dvecs, Nvecs, accels, palancas, accangs, Gammas, Alphas, torcas, Cds, Machs = vuelo1.simular_vuelo(estado,t_max, dt)

#Medir tiempo que tarda en correr la simulacion
fin = time.time()
print(f"Tiempo de ejecución: {fin-inicio:.1f}s")

posiciones = np.array([state[0:3] for state in sim])
velocidades = np.array([state[3:6] for state in sim])
thetas = np.array([state[6] for state in sim])
omegas = np.array([state[7] for state in sim])

####################################
#print(tiempo)
#print(posiciones)
#print("Tiempo de salida del riel [s]",vuelo1.tiempo_salida_riel)
#print("Tiempo de MECO [s]",Xitle.t_MECO)
#print("Tiempo de apogeo [s]",vuelo1.tiempo_apogeo)
#print("Tiempo de impacto [s]",vuelo1.tiempo_impacto)

max_altitude = max(posiciones[:, 2])
max_speed = max(np.linalg.norm(velocidades, axis=1))

#print("APOGEO:", max_altitude, "metros")
#print("Máxima velocidad:", max_speed, "m/s")
#print("Equivalente a:",max_speed/340, "Mach")
#########################################
import pandas as pd
# Guardar los datos de la simulación en un archivo .csv
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

datos_simulados.to_csv('datos_simulacion.csv', index=False)

############################
#Guardar datos importantes en un archivo json
import json
datos_a_guardar = {
    'd_ext': Xitle.d_ext,
    't_MECO': Xitle.t_MECO,
    'tiempo_salida_riel': vuelo1.tiempo_salida_riel,
    'tiempo_apogeo': vuelo1.tiempo_apogeo,
    'tiempo_impacto': vuelo1.tiempo_impacto,
    'max_altitude': max_altitude,
    'max_speed': max_speed,
    'max_acceleration_linear': np.max(accels),
    'max_acceleration_angular': np.max(accangs)
}

with open('datos_simulacion.json', 'w') as f:
    json.dump(datos_a_guardar, f, indent=4)