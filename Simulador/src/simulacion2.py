#Simulacion CON paracaidas del Xitle2
import numpy as np
from math import pi

import sys
import os

# Agregar la ruta del directorio que contiene los paquetes al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

#Importar paquetes propios de carpeta superior Paquetes
from Paquetes.PaqueteFisica.vuelo import Vuelo
from Paquetes.PaqueteFisica.viento import Viento
from Paquetes.PaqueteFisica.cohete import Parachute

from Simulador.src import condiciones_init as c_init
from Simulador.src import XitleFile

cohete_actual = XitleFile.Xitle

#####EMPEZAR SIN PARACAIDAS
#quitar el paracaidas
cohete_actual.parachute_added = False
#desactivar el paracaidas
cohete_actual.parachute_active1 = False


# Estado inicial
x0, y0, z0 = 0, 0, 0
vx0, vy0, vz0 = 0, 0, 0
theta0, omega0 = np.deg2rad(c_init.riel.angulo), 0
estado=np.array([x0, y0, z0, vx0, vy0, vz0, theta0, omega0])

#Parametros de la simulacion
dt=0.01 #[s]
t_max = 1000 #[s]
dt_out = dt

#Permitir cambiar de integrador
integrador_actual = 'Euler'
integrador_actual = 'RungeKutta4'

######################################
#####Agregar paracaidas
Mainchute = Parachute(1.2, 0.802) #Crear paracaidas principal
#print(Xitle.parachute_active1)
cohete_actual.agregar_paracaidas(Mainchute)
#print(Xitle.parachute_active1)
#print(Xitle.parachute_added)
#########################################3

#como le hago para agregar dos paracaidas??? el drogue y el main

import time
inicio = time.time()

print("Simulando...")
viento_actual = Viento(vel_base=20, vel_mean=5, vel_var=5, var_ang=5)
viento_actual.actualizar_viento3D()
#viento_actual = Viento2D(vel_mean=30, vel_var=0)
#print(viento_actual)
#print(viento_actual.vector)

vuelo_paracaidas = Vuelo(cohete_actual, c_init.atmosfera_actual, viento_actual)
tiempos, sim, CPs, CGs, masavuelo, viento_vuelo_mags, viento_vuelo_dirs, viento_vuelo_vecs, Tvecs, Dvecs, Nvecs, accels, palancas, accangs, Gammas, Alphas, torcas, Cds, Machs = vuelo_paracaidas.simular_vuelo(estado,t_max, dt, dt_out, integrador_actual)

# Guardar los datos de la simulación
#datos_simulados = (tiempos, sim, CPs, CGs, masavuelo, viento_vuelo_mags, viento_vuelo_dirs, viento_vuelo_vecs, Tvecs, Dvecs, Nvecs, accels, palancas, accangs, Gammas, Alphas, torcas, Cds, Machs)

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
    stab= (CPs[i]-CGs[i])/cohete_actual.d_ext
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
print("Guardando datos...")
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

datos_simulados.to_csv('datos_sim_paracaidas.csv', index=False)

############################
#Guardar datos importantes en un archivo json
import json
datos_a_guardar = {
    'd_ext': cohete_actual.d_ext,
    't_MECO': cohete_actual.t_MECO,
    'tiempo_salida_riel': vuelo_paracaidas.tiempo_salida_riel,
    'tiempo_apogeo': vuelo_paracaidas.tiempo_apogeo,
    'tiempo_impacto': vuelo_paracaidas.tiempo_impacto,
    'max_altitude': max_altitude,
    'max_speed': max_speed,
    'max_acceleration_linear': np.max(accels),
    'max_acceleration_angular': np.max(accangs)
    #'velocidad de impacto': velocidades[-1]
}
print("csv guardado")

with open('datos_sim_paracaidas.json', 'w', encoding='utf-8') as f:
    json.dump(datos_a_guardar, f, indent=4)
print("json guardado")

print("LISTO")