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

v_terminal = np.sqrt(m*g/D_mag)
t_apogeo = (v_terminal/g) * np.arctan(v0/v_terminal)
A = np.arctan(v0/v_terminal)
apogeo = (v_terminal**2/g) *np.log(1/np.cos(A))

print("Tiempo de apogeo: ",t_apogeo, "[s]")
print("Velocidad terminal: ", v_terminal, "[m/s]")
print("Apogeo: ", apogeo, "[m]")

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

tiempos_rk2 = []
pos_rk2 = []
vel_rk2 = []

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
#porque tienen diferentes longitudes en los distintos integradores?

# Calcular solucion analitica
#Solucion analitica
pos_analitica = []
vel_analitica = []

#la solucion analitica se calcula para los tiempos de Euler
for t in tiempos_rk4:
    pos, vel = sol_analitica_gravedad_arrastre(estado, t, m, g, D_mag)
    pos_analitica.append(pos)
    vel_analitica.append(vel)

#print(pos_analitica, pos_simul)
#print(vel_analitica, vel_simul)
#print(tiempos)


#################################


########################################################
####GRAFICAS
########################################################
opacidad=0.5
# Graficar resultados
plt.figure(figsize=(8, 6))
#Analitica
plt.plot(tiempos_rk4, pos_analitica, label='Analitica', ls='-', alpha=opacidad)
#Simulacion numerica
plt.plot(tiempos_euler, pos_euler, label='Euler',marker ='o', alpha=opacidad)
plt.plot(tiempos_rk4, pos_rk4, label='RK4', marker='*', alpha= opacidad)
plt.plot(tiempos_rk2, pos_rk2, label='RK2', marker='^', alpha=opacidad) 
plt.plot(tiempos_rkf45, pos_rkf45, label='RKF45', marker='X',alpha=opacidad)
plt.axvline(x=t_apogeo, color='k', linestyle='--', label='t_apogeo')  # <--- Agregue esta línea
plt.axvline(x=tiempos_euler[-1], color='r', linestyle='--', label='t_rompe')  # <--- Agregue esta línea



plt.title('Posición vertical [m]')
plt.xlabel('Tiempo [s]')
plt.ylabel('Posición [m]')
plt.legend()

plt.figure(figsize=(8, 6))
#Analitica
plt.plot(tiempos_rk4, vel_analitica, label='Analitica', ls='-', alpha = opacidad)
#Simulacion numerica
plt.plot(tiempos_euler, vel_euler, label='Euler', marker='o', alpha= opacidad)
plt.plot(tiempos_rk4, vel_rk4, label='RK4', marker='*', alpha=opacidad)
plt.plot(tiempos_rk2, vel_rk2, label='RK2', marker= '^', alpha=opacidad) 
plt.plot(tiempos_rkf45, vel_rkf45, label='RKF45',marker='X', alpha=opacidad)
plt.axvline(x=t_apogeo, color='k', linestyle='--', label='t_apogeo')  # <--- Agregue esta línea
plt.axvline(x=tiempos_euler[-1], color='r', linestyle='--', label='t_rompe')  # <--- Agregue esta línea

plt.title('Velocidad vertical [m/s]')
plt.xlabel('Tiempo [s]')
plt.ylabel('Velocidad [m/s]')
plt.legend()

#plt.show()


###########################################
#Comparacion de errores
#Calcular y graficar el error numerico
#errores absolutos y relativos

error_pos_euler, error_pos_rel_euler = errores(pos_euler, pos_analitica, tiempos_euler)
error_vel_euler, error_vel_rel_euler = errores(vel_euler, vel_analitica, tiempos_euler)

error_pos_rk4, error_pos_rel_rk4 = errores(pos_rk4, pos_analitica, tiempos_rk4)
error_vel_rk4, error_vel_rel_rk4 = errores(vel_rk4, vel_analitica, tiempos_rk4)

error_pos_rk2, error_pos_rel_rk2 = errores(pos_rk2, pos_analitica, tiempos_rk2)
error_vel_rk2, error_vel_rel_rk2 = errores(vel_rk2, vel_analitica, tiempos_rk2)

error_pos_rkf45, error_pos_rel_rkf45 = errores(pos_rkf45[:-1], pos_analitica, tiempos_rkf45)
error_vel_rkf45, error_vel_rel_rkf45 = errores(vel_rkf45[:-1], vel_analitica, tiempos_rkf45)

# Graficar errores globales
error_pos_euler_L2, error_pos_euler_medioabs=calcular_errores_globales(error_pos_euler, tiempos_euler)
error_vel_euler_L2, error_vel_euler_medioabs=calcular_errores_globales(error_vel_euler, tiempos_euler)

error_pos_rk4_L2, error_pos_rk4_medioabs=calcular_errores_globales(error_pos_rk4, tiempos_rk4)
error_vel_rk4_L2, error_vel_rk4_medioabs=calcular_errores_globales(error_vel_rk4, tiempos_rk4)

error_pos_rk2_L2, error_pos_rk2_medioabs=calcular_errores_globales(error_pos_rk2, tiempos_rk2)
error_vel_rk2_L2, error_vel_rk2_medioabs=calcular_errores_globales(error_vel_rk2, tiempos_rk2)

#error_pos_rkf45_L2, error_pos_rkf45_medioabs=calcular_errores_globales(error_pos_rkf45, tiempos_rkf45)
#error_vel_rkf45_L2, error_vel_rkf45_medioabs=calcular_errores_globales(error_vel_rkf45, tiempos_rkf45)

plt.figure(figsize=(12, 6))
plt.suptitle('Errores de la velocidad con distintos integradores')
plt.subplot(1, 2, 1)
plt.plot(tiempos_euler, error_vel_rel_euler, label='Error Euler', marker='o')
plt.plot(tiempos_rk4, error_vel_rel_rk4, label='Error RK4', marker='*')
plt.plot(tiempos_rk2, error_vel_rel_rk2, label='Error RK2', marker='^')
plt.plot(tiempos_rkf45, error_vel_rel_rkf45, label='Error RKF45', marker='X')
plt.axvline(x=t_apogeo, color='k', linestyle='--', label='t_apogeo')  # <--- Agregue esta línea
plt.axvline(x=tiempos_euler[-1], color='r', linestyle='--', label='t_rompe')  # <--- Agregue esta línea

#plt.title("Errores relativos")
plt.xlabel('Tiempo [s]')
plt.ylabel('Errores relativos')
plt.legend()


plt.subplot(1, 2, 2)
plt.plot(tiempos_euler, error_vel_euler, label='Error Euler', marker='o')
plt.plot(tiempos_rk4, error_vel_rk4, label='Error RK4', marker='*')
plt.plot(tiempos_rk2, error_vel_rk2, label='Error RK2', marker='^')
plt.plot(tiempos_rkf45, error_vel_rkf45, label='Error RKF45', marker='X')
plt.axvline(x=t_apogeo, color='k', linestyle='--', label='t_apogeo')  # <--- Agregue esta línea
plt.axvline(x=tiempos_euler[-1], color='r', linestyle='--', label='t_rompe')  # <--- Agregue esta línea

#plt.title("Errores absolutos")
plt.xlabel('Tiempo [s]')
plt.ylabel('Errorres absolutos [m/s]')
plt.legend()

#plt.show()
#################################################
plt.figure(figsize=(12, 6))
plt.suptitle('Errores de la posicion con distintos integradores')

plt.subplot(1, 2, 1)
plt.plot(tiempos_euler, error_pos_rel_euler, label='Error Euler', marker='o')
plt.plot(tiempos_rk4, error_pos_rel_rk4, label='Error RK4', marker='*')
plt.plot(tiempos_rk2, error_pos_rel_rk2, label='Error RK2', marker='^')
plt.plot(tiempos_rkf45, error_pos_rel_rkf45, label='Error RKF45', marker='X')
plt.axvline(x=t_apogeo, color='k', linestyle='--', label='t_apogeo')  # <--- Agregue esta línea
plt.axvline(x=tiempos_euler[-1], color='r', linestyle='--', label='t_rompe')  # <--- Agregue esta línea

#plt.title("Errores relativos")
plt.xlabel('Tiempo [s]')
plt.ylabel('Errores relativos [1]')
plt.legend()

plt.subplot(1, 2, 2)
plt.plot(tiempos_euler, error_pos_euler, label='Error Euler', marker='o')
plt.plot(tiempos_rk4, error_pos_rk4, label='Error RK4', marker='*') 
plt.plot(tiempos_rk2, error_pos_rk2, label='Error RK2', marker='^')
plt.plot(tiempos_rkf45, error_pos_rkf45, label='Error RKF45', marker='X')
plt.axvline(x=t_apogeo, color='k', linestyle='--', label='t_apogeo')  # <--- Agregue esta línea
plt.axvline(x=tiempos_euler[-1], color='r', linestyle='--', label='t_rompe')  # <--- Agregue esta línea

#plt.title("Errores absolutos")
plt.xlabel('Tiempo [s]')
plt.ylabel('Errorres absolutos [m]')
plt.legend()

'''

#####################################################
#####################################################
###Diferentes pasos de tiempo y un mismo integrador
#####################################################
Integrador_oficial= RungeKutta2
#Integrador_oficial= Euler

# Simulaciones con diferentes pasos de tiempo
dt_values = [0.005, 0.01, 0.05, 0.1, 0.2]
labels = ['dt=0.005', 'dt=0.01', 'dt=0.05', 'dt=0.1', 'dt=0.2']

tiempos_euler_dt1=[]
pos_euler_dt1=[]
vel_euler_dt1=[]
pos_analitica_dt1=[]
vel_analitica_dt1=[]

tiempos_euler_dt2=[]
pos_euler_dt2=[]
vel_euler_dt2=[]
pos_analitica_dt2=[]
vel_analitica_dt2=[]

tiempos_euler_dt3=[]
pos_euler_dt3=[]
vel_euler_dt3=[]
pos_analitica_dt3=[]
vel_analitica_dt3=[]

tiempos_euler_dt4=[]
pos_euler_dt4=[]
vel_euler_dt4=[]
pos_analitica_dt4=[]
vel_analitica_dt4=[]

tiempos_euler_dt5=[]
pos_euler_dt5=[]
vel_euler_dt5=[]
pos_analitica_dt5=[]
vel_analitica_dt5=[]

for dt, label in zip(dt_values, labels):
    tiempos, sim = simular_dinamica(estado, t_max, dt, Integrador_oficial, der_gravedad_arrastre)
    pos = [sim[i][0] for i in range(len(sim))]
    vel = [sim[i][1] for i in range(len(sim))]

    pos_analitica = []
    vel_analitica = []
    for t in tiempos:
        pos, vel = sol_analitica_gravedad_arrastre(estado, t, m, g, D_mag)
        pos_analitica.append(pos)
        vel_analitica.append(vel)
    
    if label == 'dt=0.005':
        tiempos_euler_dt1 = tiempos
        pos_euler_dt1 = pos
        vel_euler_dt1 = vel
        pos_analitica_dt1 = pos_analitica
        vel_analitica_dt1 = vel_analitica
    elif label == 'dt=0.01':
        tiempos_euler_dt2 = tiempos
        pos_euler_dt2 = pos
        vel_euler_dt2 = vel
        pos_analitica_dt2 = pos_analitica
        vel_analitica_dt2 = vel_analitica
    elif label == 'dt=0.05':
        tiempos_euler_dt3 = tiempos
        pos_euler_dt3 = pos
        vel_euler_dt3 = vel
        pos_analitica_dt3 = pos_analitica
        vel_analitica_dt3 = vel_analitica
    elif label == 'dt=0.1':
        tiempos_euler_dt4 = tiempos
        pos_euler_dt4 = pos
        vel_euler_dt4 = vel
        pos_analitica_dt4 = pos_analitica
        vel_analitica_dt4 = vel

    elif label == 'dt=0.2':
        tiempos_euler_dt5 = tiempos
        pos_euler_dt5 = pos
        vel_euler_dt5 = vel
        pos_analitica_dt5 = pos_analitica
        vel_analitica_dt5 = vel

# Graficar resultados
plt.figure(figsize=(8, 6))
plt.plot(tiempos_euler_dt1, pos_analitica_dt1, label='analitica', marker='^')
plt.plot(tiempos_euler_dt1, pos_euler_dt1, label='dt=0.005', marker='*')
plt.plot(tiempos_euler_dt2, pos_euler_dt2, label='dt=0.01', marker='*')
plt.plot(tiempos_euler_dt3, pos_euler_dt3, label='dt=0.05', marker='*')
plt.plot(tiempos_euler_dt4, pos_euler_dt4, label='dt=0.1', marker='*')
plt.plot(tiempos_euler_dt5, pos_euler_dt5, label='dt=0.2', marker='*')
plt.axvline(x=t_apogeo, color='k', linestyle='--', label='t_apogeo')  # <--- Agregue esta línea
plt.axvline(x=tiempos_euler_dt5[-1], color='r', linestyle='--', label='t_rompe')  # <--- Agregue esta línea


plt.title('Posición vertical con distintos dt ')
plt.xlabel('Tiempo [s]')
plt.ylabel('Posición [m]')
plt.legend()

#Para la velocidad la solucion va a ser igual pues e sun metodo de segundo orden? (Preguntar dr Claudio)

plt.figure(figsize=(8, 6))
plt.plot(tiempos_euler_dt1, vel_analitica_dt1, label='analitica', marker='^')
plt.plot(tiempos_euler_dt1, vel_euler_dt1, label='dt=0.005')
plt.plot(tiempos_euler_dt2, vel_euler_dt2, label='dt=0.01')
plt.plot(tiempos_euler_dt3, vel_euler_dt3, label='dt=0.05')
plt.plot(tiempos_euler_dt4, vel_euler_dt4, label='dt=0.1')
plt.plot(tiempos_euler_dt5, vel_euler_dt5, label='dt=0.2')
plt.axvline(x=t_apogeo, color='k', linestyle='--', label='t_apogeo')  # <--- Agregue esta línea
plt.axvline(x=tiempos_euler_dt5[-1], color='r', linestyle='--', label='t_rompe')  # <--- Agregue esta línea

plt.title('Velocidad vertical con distintos dt')
plt.xlabel('Tiempo [s]')
plt.ylabel('Velocidad [m/s]')
plt.legend()
#plt.show()
#plt.savefig('pos_vel_dt.png')

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

error_pos_dt1_L2, error_pos_dt1_medabs=calcular_errores_globales(pos_euler_dt1, tiempos_euler_dt1)
error_vel_dt1_L2, error_vel_dt1_medabs=calcular_errores_globales(vel_euler_dt1, tiempos_euler_dt1)
error_pos_dt2_L2, error_pos_dt2_medabs=calcular_errores_globales(pos_euler_dt2, tiempos_euler_dt2)
error_vel_dt2_L2, error_vel_dt2_medabs=calcular_errores_globales(vel_euler_dt2, tiempos_euler_dt2)
error_pos_dt3_L2, error_pos_dt3_medabs=calcular_errores_globales(pos_euler_dt3, tiempos_euler_dt3)
error_vel_dt3_L2, error_vel_dt3_medabs=calcular_errores_globales(vel_euler_dt3, tiempos_euler_dt3)
error_pos_dt4_L2, error_pos_dt4_medabs=calcular_errores_globales(pos_euler_dt4, tiempos_euler_dt4)
error_vel_dt4_L2, error_vel_dt4_medabs=calcular_errores_globales(vel_euler_dt4, tiempos_euler_dt4)
error_pos_dt5_L2, error_pos_dt5_medabs=calcular_errores_globales(pos_euler_dt5, tiempos_euler_dt5)
error_vel_dt5_L2, error_vel_dt5_medabs=calcular_errores_globales(vel_euler_dt5, tiempos_euler_dt5)

################################################
# Grafica errores absolutos y relativos
#Para la posicion
plt.figure(figsize=(12, 6))
plt.suptitle("Errores en posición para distintos dt")

plt.subplot(1, 2, 1)
plt.plot(tiempos_euler_dt1, error_pos_dt1, label='dt=0.005', marker='*')
plt.plot(tiempos_euler_dt2, error_pos_dt2, label='dt=0.01', marker='*')
plt.plot(tiempos_euler_dt3, error_pos_dt3, label='dt=0.05', marker='*')
plt.plot(tiempos_euler_dt4, error_pos_dt4, label='dt=0.1', marker='*')
plt.plot(tiempos_euler_dt5, error_pos_dt5, label='dt=0.2', marker='*')
plt.axvline(x=t_apogeo, color='k', linestyle='--', label='t_apogeo')  # <--- Agregue esta línea
plt.axvline(x=tiempos_euler_dt5[-1], color='r', linestyle='--', label='t_rompe')  # <--- Agregue esta línea

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
plt.axvline(x=t_apogeo, color='k', linestyle='--', label='t_apogeo')  # <--- Agregue esta línea
plt.axvline(x=tiempos_euler_dt5[-1], color='r', linestyle='--', label='t_rompe')  # <--- Agregue esta línea

#plt.title("Errores relativos")
plt.xlabel('Tiempo [s]')
plt.ylabel('Error relativo')
plt.legend()
#plt.show()

#Para la velocidad
plt.figure(figsize=(12, 6))
plt.suptitle("Errores en velocidad para distintos dt")

plt.subplot(1, 2, 1)
plt.plot(tiempos_euler_dt1, error_vel_dt1, label='dt=0.005', marker='*')
plt.plot(tiempos_euler_dt2, error_vel_dt2, label='dt=0.01', marker='*')
plt.plot(tiempos_euler_dt3, error_vel_dt3, label='dt=0.05', marker='*')
plt.plot(tiempos_euler_dt4, error_vel_dt4, label='dt=0.1', marker='*')
plt.plot(tiempos_euler_dt5, error_vel_dt5, label='dt=0.2', marker='*')
plt.axvline(x=t_apogeo, color='k', linestyle='--', label='t_apogeo')  # <--- Agregue esta línea
plt.axvline(x=tiempos_euler_dt5[-1], color='r', linestyle='--', label='t_rompe')  # <--- Agregue esta línea

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
plt.axvline(x=t_apogeo, color='k', linestyle='--', label='t_apogeo')  # <--- Agregue esta línea
plt.axvline(x=tiempos_euler_dt5[-1], color='r', linestyle='--', label='t_rompe')  # <--- Agregue esta línea

#plt.title("Errores relativos")
plt.xlabel('Tiempo [s]')
plt.ylabel('Error relativo')
plt.legend()
plt.show()
##################################################
# Grafica el error L2 y el error medio absoluto
lista_errores_pos_L2 = [error_pos_dt1_L2, error_pos_dt2_L2, error_pos_dt3_L2, error_pos_dt4_L2, error_pos_dt5_L2]
lista_errores_vel_L2 = [error_vel_dt1_L2, error_vel_dt2_L2, error_vel_dt3_L2, error_vel_dt4_L2, error_vel_dt5_L2]
lista_errores_pos_medabs = [error_pos_dt1_medabs, error_pos_dt2_medabs, error_pos_dt3_medabs, error_pos_dt4_medabs, error_pos_dt5_medabs]
lista_errores_vel_medabs = [error_vel_dt1_medabs, error_vel_dt2_medabs, error_vel_dt3_medabs, error_vel_dt4_medabs, error_vel_dt5_medabs]

plt.figure(figsize=(8, 6))

plt.subplot(1,2,1)
plt.title("Error L2")
plt.plot(dt_values, lista_errores_pos_L2, label='Error posicion', marker='*')
plt.plot(dt_values, lista_errores_vel_L2, label='Error velocidad', marker='o')
plt.xlabel('Paso de tiempo dt')
plt.ylabel('Error')
plt.legend()

plt.subplot(1,2,2)
plt.title("Error medio absoluto")
#plt.scatter([error_pos_dt1_medabs, error_pos_dt2_medabs, error_pos_dt3_medabs, error_pos_dt4_medabs, error_pos_dt5_medabs])
plt.plot(dt_values, lista_errores_pos_medabs , label='Error posicion', marker='*')
#plt.scatter([error_vel_dt1_medabs, error_vel_dt2_medabs, error_vel_dt3_medabs, error_vel_dt4_medabs, error_vel_dt5_medabs])
plt.plot(dt_values, lista_errores_vel_medabs, label='Error velocidad', marker='o')

plt.xlabel('Paso de tiempo dt')
plt.ylabel('Error')
plt.legend()


plt.show()
