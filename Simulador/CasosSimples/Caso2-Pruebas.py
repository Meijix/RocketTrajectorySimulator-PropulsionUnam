#Caso 2: Gravedad + Arrastre cuadratico y masa cte

import numpy as np
import matplotlib.pyplot as plt
#from scipy.integrate import odeint

from Cond_Init import *
from IntegradoresCasos import *
from FunSimularDinamica import *
from Errores import *

def der_gravedad_arrastre(t, state):
    v = state[1]
    if v == 0:
        Drag = 0
    else:
        Drag = (D_mag/m) * (v**2) * np.sign(v)
    
    derivs = np.array((v, -g - Drag))
    #print(derivs)
    return derivs
import numpy as np

def sol_analitica_gravedad_arrastre(state, t, m, g, D_mag):
    z0= state[0]
    v0= state[1]

    v_terminal = np.sqrt(m*g/D_mag)
    t_apogeo = (v_terminal/g) * np.arctan(v0/v_terminal)
    A = np.arctan(v0/v_terminal)
    apogeo = (v_terminal**2/g) *np.log(1/np.cos(A))

    if t<=t_apogeo:
        v = v_terminal * np.tan((-g*t / v_terminal)+ A)
        z = z0+ (v_terminal**2/g)* np.log(np.cos((-g*t/v_terminal)+A)/np.cos(A))
    else:
        v = v_terminal * np.tanh((-g / v_terminal)*(t-t_apogeo))
        z = z0 + apogeo + (v_terminal**2/-g)* np.log(np.cosh((-g/v_terminal)*(t-t_apogeo)))

    return z, v



#####################################################
#####################################################
###Diferentes pasos de tiempo y un mismo integrador
#####################################################
Integrador_oficial= RungeKutta2
#Integrador_oficial= Euler

# Simulaciones con diferentes pasos de tiempo
dt_values = [0.005, 0.01, 0.05, 0.1, 0.2]
labels = ['dt=0.005', 'dt=0.01', 'dt=0.05', 'dt=0.1', 'dt=0.2']

n = len(dt_values)  # numero de dt's a probar

for i in range(1, n + 1):
    globals()[f"tiempos_euler_dt{i}"] = []
    globals()[f"pos_euler_dt{i}"] = []
    globals()[f"vel_euler_dt{i}"] = []
    globals()[f"pos_analitica_euler_dt{i}"] = []
    globals()[f"vel_analitica_euler_dt{i}"] = []
    globals()[f"error_pos_rel_dt{i}"] = []
    globals()[f"error_vel_rel_dt{i}"] = []
    globals()[f"error_pos_dt{i}"] = []
    globals()[f"error_vel_dt{i}"] = []


pos_lista=[]
vel_lista=[]

for i, dt in enumerate(dt_values, start=1):
    tiempos, sim = simular_dinamica(estado, t_max, dt, Integrador_oficial, der_gravedad_arrastre)
    pos_sim, vel_sim = zip(*[(s[0], s[1]) for s in sim])

    pos_analitica, vel_analitica = zip(*[sol_analitica_gravedad_arrastre(estado, t, m, g, D_mag) for t in tiempos])
    pos_lista.extend(pos_analitica)
    vel_lista.extend(vel_analitica)

globals()[f"tiempos_euler_dt{i}"] = tiempos
globals()[f"pos_euler_dt{i}"] = pos_sim
globals()[f"vel_euler_dt{i}"] = vel_sim
globals()[f"pos_analitica_euler_dt{i}"] = pos_lista
globals()[f"vel_analitica_euler_dt{i}"] = vel_lista

# Graficar resultados
plt.figure(figsize=(8, 6))
for i, dt in enumerate(dt_values, start=1):
    tiempos = globals()[f"tiempos_euler_dt{i}"]
    pos_euler = globals()[f"pos_euler_dt{i}"]
    plt.plot(tiempos, pos_euler, label=f"dt={dt}")

plt.title('Posición vertical [m]')
plt.xlabel('Tiempo [s]')
plt.ylabel('Posición [m]')
plt.legend()

plt.figure(figsize=(8, 6))
for i, dt in enumerate(dt_values, start=1):
    tiempos = globals()[f"tiempos_euler_dt{i}"]
    vel_euler = globals()[f"vel_euler_dt{i}"]
    plt.plot(tiempos, vel_euler, label=f"dt={dt}")

plt.title('Velocidad vertical [m/s]')
plt.xlabel('Tiempo [s]')
plt.ylabel('Velocidad [m/s]')
plt.legend()

#########################################
#Errores
for i, dt in enumerate(dt_values, start=1):
    tiempos = globals()[f"tiempos_euler_dt{i}"]
    vel_euler = globals()[f"vel_euler_dt{i}"]
    pos_euler = globals()[f"pos_euler_dt{i}"]
    pos_analitica = globals()[f"pos_analitica_euler_dt{i}"]
    vel_analitica = globals()[f"vel_analitica_euler_dt{i}"]

    globals()[f"error_pos_dt{i}"], globals()[f"error_pos_rel_dt{i}"] = errores(pos_euler, pos_analitica, tiempos)
    globals()[f"error_vel_dt{i}"], globals()[f"error_vel_rel_dt{i}"] = errores(vel_euler, vel_analitica, tiempos)


#Errores globales
for i, dt in enumerate(dt_values, start=1):
    tiempos = globals()[f"tiempos_euler_dt{i}"]
    error_pos = globals()[f"error_pos_dt{i}"]
    error_vel = globals()[f"error_vel_dt{i}"]

    errores_pos_L2=[]
    errores_vel_L2=[]
    errores_pos_medabs=[]
    errores_vel_medabs=[]

    error_pos_L2, error_pos_medabs = calcular_errores_globales(error_pos, tiempos)
    error_vel_L2, error_vel__medabs = calcular_errores_globales(error_vel, tiempos)
    errores_pos_L2.append(error_pos_L2)
    errores_vel_L2.append(error_vel_L2)
    errores_pos_medabs.append(error_pos_medabs)
    errores_vel_medabs.append(error_vel__medabs)



# Graficar errores absolutos y relativos
plt.figure(figsize=(12, 6))
plt.suptitle("Errores en posición para distintos dt")
plt.subplot(1, 2, 1)
for i, dt in enumerate(dt_values, start=1):
    tiempos = globals()[f"tiempos_euler_dt{i}"]
    error = globals()[f"error_pos_dt{i}"]
    plt.plot(tiempos, error, label=f"dt={dt}")

plt.xlabel('Tiempo [s]')
plt.ylabel('Error absoluto [m]')
plt.legend()

plt.subplot(1, 2, 2)
for i, dt in enumerate(dt_values, start=1):
    tiempos = globals()[f"tiempos_euler_dt{i}"]
    error = globals()[f"error_pos_rel_dt{i}"]

    plt.plot(tiempos, error, label=f"dt={dt}")

plt.xlabel('Tiempo [s]')
plt.ylabel('Error relativo')
plt.legend()

plt.figure(figsize=(12, 6))
plt.suptitle("Errores en velocidad para distintos dt")
plt.subplot(1, 2, 1)
for i, dt in enumerate(dt_values, start=1):
    tiempos = globals()[f"tiempos_euler_dt{i}"]
    error = globals()[f"error_vel_dt{i}"]
    plt.plot(tiempos, error, label=f"dt={dt}")

plt.xlabel('Tiempo [s]')
plt.ylabel('Error absoluto [m/s]')
plt.legend()

plt.subplot(1, 2, 2)
for i, dt in enumerate(dt_values, start=1):
    tiempos = globals()[f"tiempos_euler_dt{i}"]
    error = globals()[f"error_vel_rel_dt{i}"]
    plt.plot(tiempos, error, label=f"dt={dt}")

plt.xlabel('Tiempo [s]')
plt.ylabel('Error relativo')
plt.legend()

plt.show()

##################################################
# Grafica el error L2 y el error medio absoluto
plt.figure(figsize=(8, 6))

plt.subplot(1,2,1)
plt.title("Error L2")
plt.plot(dt_values, errores_pos_L2, label='Error posicion', marker='*')
plt.plot(dt_values, errores_vel_L2, label='Error velocidad', marker='o')
plt.xlabel('Paso de tiempo dt')
plt.ylabel('Error')
plt.legend()

plt.subplot(1,2,2)
plt.title("Error medio absoluto")
#plt.scatter([error_pos_dt1_medabs, error_pos_dt2_medabs, error_pos_dt3_medabs, error_pos_dt4_medabs, error_pos_dt5_medabs])
plt.plot(dt_values, errores_pos_medabs , label='Error posicion', marker='*')
#plt.scatter([error_vel_dt1_medabs, error_vel_dt2_medabs, error_vel_dt3_medabs, error_vel_dt4_medabs, error_vel_dt5_medabs])
plt.plot(dt_values, errores_vel_medabs, label='Error velocidad', marker='o')

plt.xlabel('Paso de tiempo dt')
plt.ylabel('Error')
plt.legend()


plt.show()
'''

