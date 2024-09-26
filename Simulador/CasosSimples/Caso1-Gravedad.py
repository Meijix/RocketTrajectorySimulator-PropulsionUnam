#Simulacion Numerica de los casos simplificados

import numpy as np
import matplotlib.pyplot as plt
#from scipy.integrate import odeint

from Cond_Init import *
from IntegradoresCasos import *
from FunSimularDinamica import * 

g = 9.81 #Aceleracion de gravedad cte

#Caso 1: Gravedad y masa cte
#no aplica parte angular

#no depende de t porque nada es variable
def der_gravedad_masa_cte(t, state):
    z, v = state
    derivs = np.array((v, -g))
    #print(derivs)
    return derivs

def sol_analitica_gravedad_masa_cte(z0, v0, t):
    z = z0 + (v0*t) - (0.5 * g * (t**2))
    v = v0 - (g*t)
    return z, v


'''
#Calcular y graficar el error numerico
#error en metros
error_pos = [pos_simul[i] - pos_analitica[i] for i in range(len(tiempos))]
error_vel = [vel_simul[i] - vel_analitica[i] for i in range(len(tiempos))]

#error relativo
error_pos_rel = [abs(error_pos[i]/pos_analitica[i]) for i in range(len(tiempos))]
error_vel_rel = [abs(error_vel[i]/vel_analitica[i]) for i in range(len(tiempos))]

plt.figure(figsize=(8, 6))
plt.plot(tiempos, error_pos, label='Error z(t)')
plt.plot(tiempos, error_vel, label='Error v(t)')
plt.title("Error absoluto")
plt.xlabel('Tiempo [s]')
plt.ylabel('Errorres absolutos [m],[m/s]')
plt.legend()

plt.figure(figsize=(8, 6))
plt.plot(tiempos, error_pos_rel, label='Error z(t)')
plt.plot(tiempos, error_vel_rel, label='Error v(t)')
plt.title("Error relativo")
plt.xlabel('Tiempo [s]')
plt.ylabel('Errores relativos')
plt.legend()

plt.show()
'''


##############################################################################
#Comparacion integradores
# Listas para guardar los resultados
tiempos_euler = []
pos_euler = []
vel_euler = []

tiempos_rk4 = []
pos_rk4 = []
vel_rk4 = []

tiempos_rkf45 = []
pos_rkf45 = []
vel_rkf45 = []

# Simulaciones con diferentes integradores
integradores = [Euler, RungeKutta4, RungeKutta2]#, RKF45]
labels = ['Euler', 'RK4', 'RK2'] #, 'RKF45']

for integrador, label in zip(integradores, labels):
    tiempos, sim = simular_dinamica(estado, t_max, dt, integrador, der_gravedad_masa_cte)
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

#Solucion analitica
pos_analitica = []
vel_analitica = []

#la solucion analitica se calcula para los tiempos de Euler
for t in tiempos_euler:
    pos, vel = sol_analitica_gravedad_masa_cte(estado, t, g)
    pos_analitica.append(pos)
    vel_analitica.append(vel)

opacidad=1
# Graficar resultados
plt.figure(figsize=(8, 6))
#Analitica
#plt.plot(tiempos_euler, pos_analitica, label='Analitica', ls='-')
#Simulacion numerica
plt.plot(tiempos_euler, pos_euler, label='Euler',marker ='o', alpha=opacidad)
plt.plot(tiempos_rk4, pos_rk4, label='RK4', marker='*', alpha= opacidad)
plt.plot(tiempos_rk2, pos_rk2, label='RK2', linestyle='dashed', alpha=opacidad) #marker ='v', alpha= opacidad)
plt.plot(tiempos_rkf45, pos_rkf45, label='RKF45', marker='X',alpha=opacidad)

plt.title('Posición vertical [m]')
plt.xlabel('Tiempo [s]')
plt.ylabel('Posición [m]')
plt.legend()


plt.figure(figsize=(8, 6))
#Analitica
#plt.plot(tiempos_euler, vel_analitica, label='Analitica', ls='-')
#Simulacion numerica
plt.plot(tiempos_euler, vel_euler, label='Euler', marker='o')
plt.plot(tiempos_rk4, vel_rk4, label='RK4', marker='*')
plt.plot(tiempos_rk2, vel_rk2, label='RK2', linestyle='dashed', alpha=opacidad) 
plt.plot(tiempos_rkf45, vel_rkf45, label='RKF45',marker='X')

plt.title('Velocidad vertical [m/s]')
plt.xlabel('Tiempo [s]')
plt.ylabel('Velocidad [m/s]')
plt.legend()

plt.show()


#####################################################
###Diferentes pasos de tiempo
# Listas para guardar los resultados
# Listas para guardar los resultados
tiempos_euler_dt1 = []
pos_euler_dt1 = []
vel_euler_dt1 = []

tiempos_euler_dt2 = []
pos_euler_dt2 = []
vel_euler_dt2 = []

tiempos_euler_dt3 = []
pos_euler_dt3 = []
vel_euler_dt3 = []

tiempos_euler_dt4 = []
pos_euler_dt4 = []
vel_euler_dt4 = []

tiempos_euler_dt5 = []
pos_euler_dt5 = []
vel_euler_dt5 = []

# Simulaciones con diferentes pasos de tiempo
dt_values = [0.005, 0.01, 0.05, 0.1, 0.25]
labels = ['dt=0.005', 'dt=0.01', 'dt=0.05', 'dt=0.1', 'dt=0.25']

for dt, label in zip(dt_values, labels):
    tiempos, sim = simular_dinamica(estado, t_max, dt, Euler, der_gravedad_masa_cte)
    pos = [sim[i][0] for i in range(len(sim))]
    vel = [sim[i][1] for i in range(len(sim))]
    
    if label == 'dt=0.005':
        tiempos_euler_dt1 = tiempos
        pos_euler_dt1 = pos
        vel_euler_dt1 = vel
    elif label == 'dt=0.01':
        tiempos_euler_dt2 = tiempos
        pos_euler_dt2 = pos
        vel_euler_dt2 = vel
    elif label == 'dt=0.05':
        tiempos_euler_dt3 = tiempos
        pos_euler_dt3 = pos
        vel_euler_dt3 = vel
    elif label == 'dt=0.1':
        tiempos_euler_dt4 = tiempos
        pos_euler_dt4 = pos
        vel_euler_dt4 = vel
    elif label == 'dt=0.25':
        tiempos_euler_dt5 = tiempos
        pos_euler_dt5 = pos
        vel_euler_dt5 = vel

# Graficar resultados
plt.figure(figsize=(8, 6))
plt.plot(tiempos_euler_dt1, pos_euler_dt1, label='dt=0.005')
plt.plot(tiempos_euler_dt2, pos_euler_dt2, label='dt=0.01')
plt.plot(tiempos_euler_dt3, pos_euler_dt3, label='dt=0.05')
plt.plot(tiempos_euler_dt4, pos_euler_dt4, label='dt=0.1')
plt.plot(tiempos_euler_dt5, pos_euler_dt5, label='dt=0.25')

plt.title('Posición vertical [m]')
plt.xlabel('Tiempo [s]')
plt.ylabel('Posición [m]')
plt.legend()

plt.figure(figsize=(8, 6))
plt.plot(tiempos_euler_dt1, vel_euler_dt1, label='dt=0.005')
plt.plot(tiempos_euler_dt2, vel_euler_dt2, label='dt=0.01')
plt.plot(tiempos_euler_dt3, vel_euler_dt3, label='dt=0.05')
plt.plot(tiempos_euler_dt4, vel_euler_dt4, label='dt=0.1')
plt.plot(tiempos_euler_dt5, vel_euler_dt5, label='dt=0.25')

plt.title('Velocidad vertical [m/s]')
plt.xlabel('Tiempo [s]')
plt.ylabel('Velocidad [m/s]')
plt.legend()

plt.show()