#Simulacion Numerica de los casos simplificados

import numpy as np
import matplotlib.pyplot as plt
#from scipy.integrate import odeint

from Cond_Init import *
from IntegradoresCasos import *
from FunSimularDinamica import * 
from Errores import *

g = 9.81 #Aceleracion de gravedad cte

#Caso 1: Gravedad y masa cte
#no aplica parte angular

#no depende de t porque nada es variable
def der_gravedad_masa_cte(t, state):
    z, v = state
    derivs = np.array((v, -g))
    #print(derivs)
    return derivs

def sol_analitica_gravedad_masa_cte(state, t):
    z0, v0 = state
    z = z0 + (v0*t) - (0.5 * g * (t**2))
    v = v0 - (g*t)
    return z, v

##############################################################################
#Comparacion integradores
# Listas para guardar los resultados
tiempos_euler = []
pos_euler = []
vel_euler = []
pos_analitica_euler = []
vel_analitica_euler =[]

tiempos_rk4 = []
pos_rk4 = []
vel_rk4 = []
pos_analitica_rk4 = []
vel_analitica_rk4 =[]

tiempos_rk2 = []
pos_rk2 = []
vel_rk2 = []
pos_analitica_rk2 = []
vel_analitica_rk2 =[]

tiempos_rkf45 = []
pos_rkf45 = []
vel_rkf45 = []
pos_analitica_rkf45 = []
vel_analitica_rkf45 =[]

# Simulaciones con diferentes integradores
integradores = [Euler, RungeKutta4, RungeKutta2]#, RKF45]
labels = ['Euler', 'RK4', 'RK2'] #, 'RKF45']

for integrador, label in zip(integradores, labels):
    tiempos, sim = simular_dinamica(estado, t_max, dt, integrador, der_gravedad_masa_cte)
    pos = [sim[i][0] for i in range(len(sim))]
    vel = [sim[i][1] for i in range(len(sim))]

    # Solucion analitica
    posicion_analitica = []
    velocidad_analitica = []
    for t in tiempos:
        pos_analitica, vel_analitica = sol_analitica_gravedad_masa_cte(estado, t)
        posicion_analitica.append(pos_analitica)
        velocidad_analitica.append(vel_analitica)
    
    if label == 'Euler':
        tiempos_euler = tiempos
        pos_euler = pos
        vel_euler = vel
        pos_analitica_euler = posicion_analitica
        vel_analitica_euler = velocidad_analitica

    elif label == 'RK4':
        tiempos_rk4 = tiempos
        pos_rk4 = pos
        vel_rk4 = vel
        pos_analitica_rk4 = posicion_analitica
        vel_analitica_rk4 = velocidad_analitica

    elif label =='RK2':
        tiempos_rk2 = tiempos
        pos_rk2 = pos
        vel_rk2 = vel
        pos_analitica_rk2 = posicion_analitica
        vel_analitica_rk2 = velocidad_analitica

    elif label == 'RKF45':
        tiempos_rkf45 = tiempos
        pos_rkf45 = pos
        vel_rkf45 = vel
        pos_analitica_rkf45 = posicion_analitica
        vel_analitica_rkf45 = velocidad_analitica

'''
#Solucion analitica
pos_analitica = []
vel_analitica = []

#la solucion analitica se calcula para los tiempos de Euler
for t in tiempos_euler:
    pos, vel = sol_analitica_gravedad_masa_cte(estado, t)
    pos_analitica.append(pos)
    vel_analitica.append(vel)
'''

opacidad=0.5
# Graficar resultados
plt.figure(figsize=(8, 6))
#Analitica
plt.plot(tiempos_euler, pos_analitica_euler, label='Analitica', ls='-')
#Simulacion numerica
plt.plot(tiempos_euler, pos_euler, label='Euler',marker ='o', alpha=opacidad)
plt.plot(tiempos_rk4, pos_rk4, label='RK4', marker='*', alpha= opacidad)
plt.plot(tiempos_rk2, pos_rk2, label='RK2', marker='^', alpha=opacidad) #marker ='v', alpha= opacidad)
#plt.plot(tiempos_rkf45, pos_rkf45, label='RKF45', marker='X',alpha=opacidad)
plt.title('Posición vertical [m]')
plt.xlabel('Tiempo [s]')
plt.ylabel('Posición [m]')
plt.legend()


plt.figure(figsize=(8, 6))
#Analitica
plt.plot(tiempos_euler, vel_analitica_euler, label='Analitica', ls='-')
#Simulacion numerica
plt.plot(tiempos_euler, vel_euler, label='Euler', marker='o')
plt.plot(tiempos_rk4, vel_rk4, label='RK4', marker='*')
plt.plot(tiempos_rk2, vel_rk2, label='RK2', marker='^', alpha=opacidad) 
#plt.plot(tiempos_rkf45, vel_rkf45, label='RKF45',marker='X')
plt.title('Velocidad vertical [m/s]')
plt.xlabel('Tiempo [s]')
plt.ylabel('Velocidad [m/s]')
plt.legend()

#plt.show()

#################################################

#Comparacion de errores
#Calcular y graficar el error numerico
#errores absolutos y relativos
error_pos_euler, error_pos_rel_euler = errores(pos_euler, pos_analitica_euler, tiempos_euler)
error_vel_euler, error_vel_rel_euler = errores(vel_euler, vel_analitica_euler, tiempos_euler)

error_pos_rk4, error_pos_rel_rk4 = errores(pos_rk4, pos_analitica_rk4, tiempos_rk4)
error_vel_rk4, error_vel_rel_rk4 = errores(vel_rk4, vel_analitica_rk4, tiempos_rk4)

error_pos_rk2, error_pos_rel_rk2 = errores(pos_rk2, pos_analitica_rk2, tiempos_rk2)
error_vel_rk2, error_vel_rel_rk2 = errores(vel_rk2, vel_analitica_rk2, tiempos_rk2)

error_pos_rkf45, error_pos_rel_rkf45 = errores(pos_rkf45, pos_analitica_rkf45, tiempos_rkf45)
error_vel_rkf45, error_vel_rel_rkf45 = errores(vel_rkf45, vel_analitica_rkf45, tiempos_rkf45)

# Graficar errores absolutos y relativos

plt.figure(figsize=(12, 6))
plt.title('Errores de la velocidad con distintos integradores')
plt.subplot(1, 2, 1)
plt.plot(tiempos_euler, error_vel_rel_euler, label='Error Euler', marker='o')
plt.plot(tiempos_rk4, error_vel_rel_rk4, label='Error RK4', marker='*')
plt.plot(tiempos_rk2, error_vel_rel_rk2, label='Error RK2', marker='^')
plt.plot(tiempos_rkf45, error_vel_rel_rkf45, label='Error RKF45', marker='X')
#plt.title("Errores relativos")
plt.xlabel('Tiempo [s]')
plt.ylabel('Errores relativos')
plt.legend()


plt.subplot(1, 2, 2)
plt.plot(tiempos_euler, error_vel_euler, label='Error Euler', marker='o')
plt.plot(tiempos_rk4, error_vel_rk4, label='Error RK4', marker='*')
plt.plot(tiempos_rk2, error_vel_rk2, label='Error RK2', marker='^')
plt.plot(tiempos_rkf45, error_vel_rkf45, label='Error RKF45', marker='X')
#plt.title("Errores absolutos")
plt.xlabel('Tiempo [s]')
plt.ylabel('Errorres absolutos [m/s]')
plt.legend()
#################################################
plt.figure(figsize=(12, 6))
plt.title('Errores de la posicion con distintos integradores')

plt.subplot(1, 2, 1)
plt.plot(tiempos_euler, error_pos_rel_euler, label='Error Euler', marker='o')
plt.plot(tiempos_rk4, error_pos_rel_rk4, label='Error RK4', marker='*')
plt.plot(tiempos_rk2, error_pos_rel_rk2, label='Error RK2', marker='^')
plt.plot(tiempos_rkf45, error_pos_rel_rkf45, label='Error RKF45', marker='X')
#plt.title("Errores relativos")
plt.xlabel('Tiempo [s]')
plt.ylabel('Errores relativos [1]')
plt.legend()

plt.subplot(1, 2, 2)
plt.plot(tiempos_euler, error_pos_euler, label='Error Euler', marker='o')
plt.plot(tiempos_rk4, error_pos_rk4, label='Error RK4', marker='*') 
plt.plot(tiempos_rk2, error_pos_rk2, label='Error RK2', marker='^')
plt.plot(tiempos_rkf45, error_pos_rkf45, label='Error RKF45', marker='X')
#plt.title("Errores absolutos")
plt.xlabel('Tiempo [s]')
plt.ylabel('Errorres absolutos [m]')
plt.legend()

#plt.show()
#####################################################
#####################################################
###Diferentes pasos de tiempo y un mismo integrador
#####################################################
Integrador_oficial= Euler
tiempos_euler_dt1 = []
pos_euler_dt1 = []
vel_euler_dt1 = []
pos_analitica_dt1 = []
vel_analitica_dt1 = []

tiempos_euler_dt2 = []
pos_euler_dt2 = []
vel_euler_dt2 = []
pos_analitica_dt2 = []
vel_analitica_dt2 = []

tiempos_euler_dt3 = []
pos_euler_dt3 = []
vel_euler_dt3 = []
pos_analitica_dt3 = []
vel_analitica_dt3 = []

tiempos_euler_dt4 = []
pos_euler_dt4 = []
vel_euler_dt4 = []
pos_analitica_dt4 = []
vel_analitica_dt4 = []

tiempos_euler_dt5 = []
pos_euler_dt5 = []
vel_euler_dt5 = []
pos_analitica_dt5 = []
vel_analitica_dt5 = []

# Simulaciones con diferentes pasos de tiempo
dt_values = [0.005, 0.01, 0.05, 0.1, 0.2]
labels = ['dt=0.005', 'dt=0.01', 'dt=0.05', 'dt=0.1', 'dt=0.2']

for dt, label in zip(dt_values, labels):
    tiempos, sim = simular_dinamica(estado, t_max, dt, Integrador_oficial, der_gravedad_masa_cte)
    pos = [sim[i][0] for i in range(len(sim))]
    vel = [sim[i][1] for i in range(len(sim))]

    pos_analitica_lista=[]
    vel_analitica_lista=[]
    for t in tiempos:
        pos_analitica, vel_analitica = sol_analitica_gravedad_masa_cte(estado, t)
        pos_analitica_lista.append(pos_analitica)
        vel_analitica_lista.append(vel_analitica)
    
    if label == 'dt=0.005':
        tiempos_euler_dt1 = tiempos
        pos_euler_dt1 = pos
        vel_euler_dt1 = vel
        pos_analitica_dt1 = pos_analitica_lista
        vel_analitica_dt1 = vel_analitica_lista

    elif label == 'dt=0.01':
        tiempos_euler_dt2 = tiempos
        pos_euler_dt2 = pos
        vel_euler_dt2 = vel
        pos_analitica_dt2 = pos_analitica_lista
        vel_analitica_dt2 = vel_analitica_lista

    elif label == 'dt=0.05':
        tiempos_euler_dt3 = tiempos
        pos_euler_dt3 = pos
        vel_euler_dt3 = vel
        pos_analitica_dt3 = pos_analitica_lista
        vel_analitica_dt3 = vel_analitica_lista

    elif label == 'dt=0.1':
        tiempos_euler_dt4 = tiempos
        pos_euler_dt4 = pos
        vel_euler_dt4 = vel
        pos_analitica_dt4 = pos_analitica_lista
        vel_analitica_dt4 = vel_analitica_lista

    elif label == 'dt=0.2':
        tiempos_euler_dt5 = tiempos
        pos_euler_dt5 = pos
        vel_euler_dt5 = vel
        pos_analitica_dt5 = pos_analitica_lista
        vel_analitica_dt5 = vel_analitica_lista

# Graficar resultados
plt.figure(figsize=(8, 6))
plt.plot(tiempos_euler_dt1, pos_euler_dt1, label='dt=0.005', marker='*')
plt.plot(tiempos_euler_dt2, pos_euler_dt2, label='dt=0.01', marker='*')
plt.plot(tiempos_euler_dt3, pos_euler_dt3, label='dt=0.05', marker='*')
plt.plot(tiempos_euler_dt4, pos_euler_dt4, label='dt=0.1', marker='*')
plt.plot(tiempos_euler_dt5, pos_euler_dt5, label='dt=0.2', marker='*')


plt.title('Posición vertical[m] con distintos dt ')
plt.xlabel('Tiempo [s]')
plt.ylabel('Posición [m]')
plt.legend()

#Para la velocidad la solucion va a ser igual pues e sun metodo de segundo orden? (Preguntar dr Claudio)

plt.figure(figsize=(8, 6))
plt.plot(tiempos_euler_dt1, vel_euler_dt1, label='dt=0.005')
plt.plot(tiempos_euler_dt2, vel_euler_dt2, label='dt=0.01')
plt.plot(tiempos_euler_dt3, vel_euler_dt3, label='dt=0.05')
plt.plot(tiempos_euler_dt4, vel_euler_dt4, label='dt=0.1')
plt.plot(tiempos_euler_dt5, vel_euler_dt5, label='dt=0.2')

plt.title('Velocidad vertical [m/s]')
plt.xlabel('Tiempo [s]')
plt.ylabel('Velocidad [m/s]')
plt.legend()
#plt.show()

'''
print("Longitud tiempos dt1", len(tiempos_euler_dt1))
print("Longitud tiempos dt2", len(tiempos_euler_dt2))
print("Longitud tiempos dt3", len(tiempos_euler_dt3))
print("Longitud tiempos dt4", len(tiempos_euler_dt4))
print("Longitud tiempos dt5", len(tiempos_euler_dt5))

print("Longitud posiciones dt1", len(pos_euler_dt1))
print("Longitud posiciones dt2", len(pos_euler_dt2))
print("Longitud posiciones dt3", len(pos_euler_dt3))
print("Longitud posiciones dt4", len(pos_euler_dt4))
print("Longitud posiciones dt5", len(pos_euler_dt5))

print("Longitud velocidades dt1", len(vel_euler_dt1))
print("Longitud velocidades dt2", len(vel_euler_dt2))
print("Longitud velocidades dt3", len(vel_euler_dt3))
print("Longitud velocidades dt4", len(vel_euler_dt4))
print("Longitud velocidades dt5", len(vel_euler_dt5))

print("Longitud posiciones analiticas dt1", len(pos_analitica_dt1))
print("Longitud posiciones analiticas dt2", len(pos_analitica_dt2))
print("Longitud posiciones analiticas dt3", len(pos_analitica_dt3))
print("Longitud posiciones analiticas dt4", len(pos_analitica_dt4))
print("Longitud posiciones analiticas dt5", len(pos_analitica_dt5))

print("Longitud velocidades analiticas dt1", len(vel_analitica_dt1))
print("Longitud velocidades analiticas dt2", len(vel_analitica_dt2))
print("Longitud velocidades analiticas dt3", len(vel_analitica_dt3))
print("Longitud velocidades analiticas dt4", len(vel_analitica_dt4))
print("Longitud velocidades analiticas dt5", len(vel_analitica_dt5))
'''
################################################
# Calcula errores absolutos y relativos para cada dt
error_pos_dt1, error_pos_rel_dt1 = errores(pos_euler_dt1, pos_analitica_dt1, tiempos_euler_dt1)
error_vel_dt1, error_vel_rel_dt1 = errores(vel_euler_dt1, vel_analitica_dt1, tiempos_euler_dt1)
error_pos_dt2, error_pos_rel_dt2 = errores(pos_euler_dt2, pos_analitica_dt2, tiempos_euler_dt2)
error_vel_dt2, error_vel_rel_dt2 = errores(vel_euler_dt2, vel_analitica_dt2, tiempos_euler_dt2)
error_pos_dt3, error_pos_rel_dt3 = errores(pos_euler_dt3, pos_analitica_dt3, tiempos_euler_dt3)
error_vel_dt3, error_vel_rel_dt3 = errores(vel_euler_dt3, vel_analitica_dt3, tiempos_euler_dt3)
error_pos_dt4, error_pos_rel_dt4 = errores(pos_euler_dt4, pos_analitica_dt4, tiempos_euler_dt4)
error_vel_dt4, error_vel_rel_dt4 = errores(vel_euler_dt4, vel_analitica_dt4, tiempos_euler_dt4)
error_pos_dt5, error_pos_rel_dt5 = errores(pos_euler_dt5, pos_analitica_dt5, tiempos_euler_dt5)
error_vel_dt5, error_vel_rel_dt5 = errores(vel_euler_dt5, vel_analitica_dt5, tiempos_euler_dt5)


# Grafica errores absolutos y relativos
#Para la posicion
plt.figure(figsize=(12, 6))
plt.title("Errores en posición para distintos dt")

plt.subplot(1, 2, 1)
plt.plot(tiempos_euler_dt1, error_pos_dt1, label='dt=0.005', marker='*')
plt.plot(tiempos_euler_dt2, error_pos_dt2, label='dt=0.01', marker='*')
plt.plot(tiempos_euler_dt3, error_pos_dt3, label='dt=0.05', marker='*')
plt.plot(tiempos_euler_dt4, error_pos_dt4, label='dt=0.1', marker='*')
plt.plot(tiempos_euler_dt5, error_pos_dt5, label='dt=0.2', marker='*')
#plt.title("Errores absolutos")
plt.xlabel('Tiempo [s]')
plt.ylabel('Error absoluto [m]')
plt.legend()

plt.subplot(1, 2, 2)
plt.plot(tiempos_euler_dt1, error_pos_rel_dt1, label='dt=0.005', marker='*')
plt.plot(tiempos_euler_dt2, error_pos_rel_dt2, label='dt=0.01', marker='*')
plt.plot(tiempos_euler_dt3, error_pos_rel_dt3, label='dt=0.05', marker='*')
plt.plot(tiempos_euler_dt4, error_pos_dt4, label='dt=0.1', marker='*')
plt.plot(tiempos_euler_dt5, error_pos_rel_dt5, label='dt=0.2', marker='*')
#plt.title("Errores relativos")
plt.xlabel('Tiempo [s]')
plt.ylabel('Error relativo')
plt.legend()
#plt.show()

#Para la velocidad
plt.figure(figsize=(12, 6))
plt.title("Errores en velocidad para distintos dt")

plt.subplot(1, 2, 1)
plt.plot(tiempos_euler_dt1, error_vel_dt1, label='dt=0.005', marker='*')
plt.plot(tiempos_euler_dt2, error_vel_dt2, label='dt=0.01', marker='*')
plt.plot(tiempos_euler_dt3, error_vel_dt3, label='dt=0.05', marker='*')
plt.plot(tiempos_euler_dt4, error_vel_dt4, label='dt=0.1', marker='*')
plt.plot(tiempos_euler_dt5, error_vel_dt5, label='dt=0.2', marker='*')
#plt.title("Errores absolutos")
plt.xlabel('Tiempo [s]')
plt.ylabel('Error absoluto [m/s]')
plt.legend()


plt.subplot(1, 2, 2)
plt.plot(tiempos_euler_dt1, error_vel_rel_dt1, label='dt=0.005', marker='*')
plt.plot(tiempos_euler_dt2, error_vel_rel_dt2, label='dt=0.01', marker='*')
plt.plot(tiempos_euler_dt3, error_vel_rel_dt3, label='dt=0.05', marker='*')
plt.plot(tiempos_euler_dt4, error_vel_rel_dt4, label='dt=0.1', marker='*')
plt.plot(tiempos_euler_dt5, error_vel_rel_dt5, label='dt=0.2', marker='*')
#plt.title("Errores relativos")
plt.xlabel('Tiempo [s]')
plt.ylabel('Error relativo')
plt.legend()
plt.show()
