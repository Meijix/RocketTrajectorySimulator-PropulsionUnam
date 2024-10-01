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
    
    print("Tiempo de apogeo: ",t_apogeo)

    A = np.arctan(v0/v_terminal)
    B = np.arctanh(v0/v_terminal)

    apogeo = (v_terminal**2/g) *np.log(1/np.cos(A))

    if t<=t_apogeo:
        v = v_terminal * np.tan((-g*t / v_terminal)+ A)
        z = (v_terminal**2/g)* np.log(np.cos((-g*t/v_terminal)+A)/np.cos(A))
    else:
        v = v_terminal * np.tanh((-g / v_terminal)*(t-t_apogeo))
        z = apogeo + (v_terminal**2/-g)* np.log(np.cosh((-g/v_terminal)*(t-t_apogeo)))

    return z, v

'''
##############################
# Simulación con scipy
##############################
from scipy.integrate import odeint

def simular_dinamica_scipy(estado, t_max, dt):
    t = np.arange(0, t_max, dt)
    sol = odeint(der_gravedad_arrastre, estado, t)
    return t, sol

# ...

# Simulación con scipy
t_scipy, sol_scipy = simular_dinamica_scipy(estado, t_max, dt)

pos_scipy = sol_scipy[:, 0]
vel_scipy = sol_scipy[:, 1]

# Graficar resultados
plt.figure(figsize=(8, 6))
plt.plot(t_scipy, pos_scipy, label='Scipy')
plt.plot(tiempos, pos_analitica, label='Analítica')
plt.plot(tiempos, pos_simul, label='Simulación')
plt.title('Posición vertical [m/s]')
plt.xlabel('Tiempo [s]')
plt.ylabel('Posición [m]')
plt.legend()

plt.figure(figsize=(8, 6))
plt.plot(t_scipy, vel_scipy, label='Scipy')
plt.plot(tiempos, vel_analitica, label='Analítica')
plt.plot(tiempos, vel_simul, label='Simulación')
plt.title('Velocidad vertical [m/s]')
plt.xlabel('Tiempo [s]')
plt.ylabel('Velocidad [m/s]')
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


# Simulaciones numericas con diferentes integradores
integradores = [Euler, RungeKutta4, RungeKutta2]#, RKF45]
labels = ['Euler', 'RK4', 'RK2'] #, 'RKF45']

for integrador, label in zip(integradores, labels):
    tiempos, sim = simular_dinamica(estado, t_max, dt, integrador, der_gravedad_arrastre)
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
    pos, vel = sol_analitica_gravedad_arrastre(estado, t, m, g, D_mag)
    pos_analitica.append(pos)
    vel_analitica.append(vel)

#print(pos_analitica, pos_simul)
#print(vel_analitica, vel_simul)
#print(tiempos)



########################################################
####GRAFICAS
########################################################
opacidad=0.5
# Graficar resultados
plt.figure(figsize=(8, 6))
#Analitica
plt.plot(tiempos_euler, pos_analitica, label='Analitica', ls='-', alpha=opacidad)
#Simulacion numerica
plt.plot(tiempos_euler, pos_euler, label='Euler',marker ='o', alpha=opacidad)
#plt.plot(tiempos_rk4, pos_rk4, label='RK4', marker='*', alpha= opacidad)
#plt.plot(tiempos_rk2, pos_rk2, label='RK2', marker='^', alpha=opacidad) 
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
#plt.plot(tiempos_rk4, vel_rk4, label='RK4', marker='*', alpha=opacidad)
#plt.plot(tiempos_rk2, vel_rk2, label='RK2', marker= '^', alpha=opacidad) 
#plt.plot(tiempos_rkf45, vel_rkf45, label='RKF45',marker='X', alpha=opacidad)
plt.title('Velocidad vertical [m/s]')
plt.xlabel('Tiempo [s]')
plt.ylabel('Velocidad [m/s]')
plt.legend()

plt.show()
