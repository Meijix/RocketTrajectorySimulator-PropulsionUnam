#Simulacion sin paracaidas del Xitle2

##no funciona la importacion de archivos

import numpy as np
#import matplotlib.pyplot as plt
#import pandas as pd
#from scipy.interpolate import interp1d
import math
from math import pi
#import random

#from Xitle import *
#from Vuelo import *
#from Integradores import *

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

#viento_actual = Viento2D(vel_mean=10, vel_var=0.05)
viento_actual = Viento2D(vel_mean=0, vel_var=0)
print(viento_actual)
print(viento_actual.vector)

vuelo1 = Vuelo(Xitle, atm_actual)
tiempos, sim, CPs, CGs, masavuelo, viento_vuelo_mags, viento_vuelo_dirs, viento_vuelo_vecs, Tvecs, Dvecs, Nvecs, accels, palancas, accangs, Gammas, Alphas, torcas, Cds, Machs = vuelo1.simular_vuelo(estado,t_max, dt)

#Medir tiempo que tarda en correr la simulacion
fin = time.time()
print(f"Tiempo de ejecución: {fin-inicio:.1f}s")

posiciones = np.array([state[0:3] for state in sim])
velocidades = np.array([state[3:6] for state in sim])
thetas = np.array([state[6] for state in sim])
omegas = np.array([state[7] for state in sim])

#print(tiempo)
#print(posiciones)
print("Tiempo de salida del riel [s]",vuelo1.tiempo_salida_riel)
print("Tiempo de MECO [s]",Xitle.t_MECO)
print("Tiempo de apogeo [s]",vuelo1.tiempo_apogeo)
print("Tiempo de impacto [s]",vuelo1.tiempo_impacto)


max_altitude = max(posiciones[:, 2])
max_speed = max(np.linalg.norm(velocidades, axis=1))

print("APOGEO:", max_altitude, "metros")
print("Máxima velocidad:", max_speed, "m/s")
print("Equivalente a:",max_speed/340, "Mach")