#Simulacion sin paracaidas del Xitle2
import numpy as np
from math import pi

import sys
import os

# Agregar la ruta del directorio que contiene los paquetes al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

#Importar paquetes propios de carpeta superior Paquetes
from Paquetes.PaqueteFisica.vuelo import Vuelo
from Paquetes.PaqueteFisica.viento import Viento

import condiciones_init as c_init
import Xitle 

#input()
cohete_actual = Xitle.Xitle

#quitar el paracaidas
cohete_actual.parachute_added = False
#desactivar el paracaidas
cohete_actual.parachute_active1 = False

# Estado inicial
x0, y0, z0 = 0, 0, 0
vx0, vy0, vz0 = 0, 0, 0

theta0, omega0 = np.deg2rad(c_init.riel.angulo), 0
estado=np.array([x0, y0, z0, vx0, vy0, vz0, theta0, omega0])
#print(estado)
#estado=list(estado)
#print(estado)
#Parametros de la simulacion
dt = 0.1 #0.1 #[s]
t_max = 800 #[s]
dt_out =  0.01
integrador_actual = 'RungeKutta4'
#integrador_actual = 'RKF45'
#integrador_actual = 'AdaptiveEuler'
# t_max = 1200 #[s]
# t_max = 5 #[s]

#t=0
#it = 0

import time
inicio = time.time()
print("Simulando...")

viento_actual = Viento(vel_base=10, vel_mean=2, vel_var=0.01, var_ang=20)
#Sin viento
viento_actual = Viento(vel_base=0, vel_mean=0, vel_var=0, var_ang=0)
#viento_actual.actualizar_viento()
viento_actual.actualizar_viento3D()
#viento_actual = Viento(vel_mean=100, vel_var=0)
#print(viento_actual)
print("Viento actual",viento_actual.vector)

#Crear el vuelo
vuelo1 = Vuelo(cohete_actual, c_init.atmosfera_actual, viento_actual)

tiempos, sim, CPs, CGs, masavuelo, viento_vuelo_mags, viento_vuelo_dirs, viento_vuelo_vecs, Tvecs, Dvecs, Nvecs, accels, palancas, accangs, Gammas, Alphas, torcas, Cds, Machs = vuelo1.simular_vuelo(estado,t_max, dt, dt_out, integrador_actual)
#print(viento_vuelo_mags)
#Medir tiempo que tarda en correr la simulacion
fin = time.time()
print(f"Tiempo de ejecución: {fin-inicio:.1f}s")

posiciones = np.array([state[0:3] for state in sim])
velocidades = np.array([state[3:6] for state in sim])
thetas = np.array([state[6] for state in sim])
omegas = np.array([state[7] for state in sim])

Tmags = np.array([np.linalg.norm(Tvec) for Tvec in Tvecs])
Dmags = np.array([np.linalg.norm(Dvec) for Dvec in Dvecs])
Nmags = np.array([np.linalg.norm(Nvec) for Nvec in Nvecs])

Txs, Tys, Tzs = zip(*Tvecs)
Dxs, Dys, Dzs = zip(*Dvecs)
Nxs, Nys, Nzs = zip(*Nvecs)

wind_xs = [vec[0] for vec in viento_vuelo_vecs]
wind_ys = [vec[1] for vec in viento_vuelo_vecs]
wind_zs = [vec[2] for vec in viento_vuelo_vecs]

stability=[]

for i in range(len(tiempos)-1):
    stab= (CPs[i]-CGs[i])/Xitle.diam_ext
    stability.append(stab)

max_altitude = max(posiciones[:, 2])
max_speed = max(np.linalg.norm(velocidades, axis=1))
####################################
#print(tiempo)
#print(posiciones)
#print("Tiempo de salida del riel [s]",vuelo1.tiempo_salida_riel)
#print("Tiempo de MECO [s]",Xitle.t_MECO)
#print("Tiempo de apogeo [s]",vuelo1.tiempo_apogeo)
#print("Tiempo de impacto [s]",vuelo1.tiempo_impacto)

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
    'wind_xs': wind_xs,
    'wind_ys': wind_ys,
    'wind_zs': wind_zs,
    #'Tvecs': Tvecs,
    #'Dvecs': Dvecs,
    #'Nvecs': Nvecs,
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
#Crear un archivo csv con los datos de la simulación
# Guardar archivo en la carpeta Simulador/Resultados/OuputFiles
datos_simulados.to_csv('datos_simulacion.csv', index=False)
print('csv guardado')
############################
#Guardar datos importantes en un archivo json
import json

datos_a_guardar = {
    'd_ext': cohete_actual.d_ext,
    't_MECO': cohete_actual.t_MECO,
    'tiempo_salida_riel': vuelo1.tiempo_salida_riel,
    'tiempo_apogeo': vuelo1.tiempo_apogeo,
    'tiempo_impacto': vuelo1.tiempo_impacto,
    'max_altitude': max_altitude,
    'max_speed': max_speed,
    'max_acceleration_linear': np.max(accels),
    'max_acceleration_angular': np.max(accangs)
    #'velocidad de impacto': velocidades[-1]
}

# Guardar los datos en un archivo .json
# Guardar archivo en la carpeta Simulador/Resultados/OuputFiles
with open('datos_simulacion.json', 'w') as f:
    json.dump(datos_a_guardar, f, indent=4)

print('json guardado')