# Caso 3: Gravedad + Empuje constante y masa variable

import numpy as np
import matplotlib.pyplot as plt

from Cond_Init import *
from IntegradoresCasos import *
from FunSimularDinamica import *

# Función para la masa variable
def masa_variable(t, m0, beta):
    return m0 * np.exp(-beta * t)

# Función para la derivada del sistema
def der_gravedad_empuje_masa_var(t, state):
    z, v = state
    m = masa_variable(t, m0, beta)
    F_empuje = F0
    Drag = (D_mag/m) * (v**2)
    derivs = np.array((v, F_empuje/m - g - Drag))
    return derivs

# Función para la solución analítica
def sol_analitica_gravedad_empuje_masa_var(z0, v0, t, m0, beta, F0):
    m = masa_variable(t, m0, beta)
    v = v0 + np.log(m0/(m0-beta*t))
    z = z0 + v0 * t + 0
    return z, v


##############################################################
# Simulaciones numericas con diferentes integradores
integradores = [Euler, RungeKutta4, RungeKutta2]#, RKF45]
labels = ['Euler', 'RK4', 'RK2'] #, 'RKF45']

for integrador, label in zip(integradores, labels):
    tiempos, sim = simular_dinamica(estado, t_max, dt, integrador, der_gravedad_empuje_masa_var)
    pos = [sim[i][0] for i in range(len(sim))]
    vel = [sim[i][1] for i in range(len(sim))]
    
    if label == 'Euler':
        tiempos_euler = tiempos
        pos_euler = pos
        vel_euler = vel
    elif label == 'RK4':
        tiempos_rk4 = tiempos
        pos_rk4 = pos
        vel_rk4 = vel
    elif label =='RK2':
        tiempos_rk2 = tiempos
        pos_rk2 = pos
        vel_rk2 = vel
    elif label == 'RKF45':
        tiempos_rkf45 = tiempos
        pos_rkf45 = pos
        vel_rkf45 = vel

# Solución analítica
pos_analitica = []
vel_analitica = []

for t in tiempos_euler:
    pos, vel = sol_analitica_gravedad_empuje_masa_var(z0, v0, t, m0, beta, F0)
    pos_analitica.append(pos)
    vel_analitica.append(vel)

########################################################
####GRAFICAS
########################################################
opacidad=1
# Graficar resultados
plt.figure(figsize=(8, 6))
#Analitica
plt.plot(tiempos_euler, pos_analitica, label='Analitica', ls='-', alpha=opacidad)
#Simulacion numerica
plt.plot(tiempos_euler, pos_euler, label='Euler',marker ='o', alpha=opacidad)
plt.plot(tiempos_rk4, pos_rk4, label='RK4', marker='*', alpha= opacidad)
plt.plot(tiempos_rk2, pos_rk2, label='RK2', linestyle='dashed', alpha=opacidad) #marker ='v', alpha= opacidad)
#plt.plot(tiempos_rkf45, pos_rkf45, label='RKF45', marker='X',alpha=opacidad)
plt.title('Posición vertical [m]')
plt.xlabel('Tiempo [s]')
plt.ylabel('Posición [m]')
plt.legend()

plt.figure(figsize=(8, 6))
#Analitica
plt.plot(tiempos_euler, vel_analitica, label='Analitica', ls='-', alpha = opacidad)
#Simulacion numerica
plt.plot(tiempos_euler, vel_euler, label='Euler', marker='o', alpha= opacidad)
plt.plot(tiempos_rk4, vel_rk4, label='RK4', marker='*', alpha=opacidad)
plt.plot(tiempos_rk2, vel_rk2, label='RK2', linestyle='dashed', alpha=opacidad) 
#plt.plot(tiempos_rkf45, vel_rkf45, label='RKF45',marker='X', alpha=opacidad)
plt.title('Velocidad vertical [m/s]')
plt.xlabel('Tiempo [s]')
plt.ylabel('Velocidad [m/s]')
plt.legend()

plt.show()
