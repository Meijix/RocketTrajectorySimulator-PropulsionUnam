#Caso 1
#Movimiento vertical con gravedad y masa cte

import sys
import os
import numpy as np
import matplotlib.pyplot as plt

# Agregar la ruta del directorio que contiene los paquetes al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Importar modulos propios
from fun_simular_dinamica import *
from errores import *
from cond_iniciales import *
#Importar integradores del paquete Paquetes.PaqueteEDOs.integradores
from Paquetes.PaqueteEDOs.integradores import *

#Funciones de la derivada y solución analítica
def der_gravedad_masa_cte(t, state):
    _, v = state
    derivs = np.array((v, -g))
    #print(derivs)
    return derivs

def sol_analitica_gravedad_masa_cte(t, state):
    z0, v0 = state
    z = z0 + (v0*t) - (0.5 * g * (t**2))
    v = v0 - (g*t)
    return z, v

#Calculo de la solución analítica
t_apogeo = v0/g
apogeo = z0 + ((v0*v0)/(2*g))
#v_terminal = v0 - g*t_apogeo
t_impacto = 2*z0/(g-2*v0)

print("Tiempo de apogeo: ",t_apogeo, "[s]")
print("Apogeo: ", apogeo, "[m]")
#print("Velocidad terminal: ", v_terminal, "[m/s]")
print("Tiempo de impacto: ", t_impacto, "[s]")

#####################################################
# Simular la dinamica
# Diferentes pasos de tiempo y un mismo integrador
#####################################################
# Inicialización de parámetros
Integrador_oficial = RungeKutta4 
#Integrador_oficial = Euler
#dt_values = [0.005, 0.01, 0.02, 0.05, 0.1, 0.15, 0.2]
dt_values = [0.005, 0.01, 0.05, 0.1, 0.2, 0.5, 1]
resultados = {}

#Usar la funcion simular_dinamica y las condiciones iniciales de cond_iniciales.py
for dete in dt_values:
    tiempos, sim = simular_dinamica(estado, t_max, dete, Integrador_oficial, der_gravedad_masa_cte)
    pos_sim, vel_sim = zip(*[(s[0], s[1]) for s in sim])
    
    pos_analitica, vel_analitica = zip(*[sol_analitica_gravedad_masa_cte(t, estado) for t in tiempos])
    
    resultados[dete] = {
        "tiempos": list(tiempos),
        "pos_sim": list(pos_sim),
        "vel_sim": list(vel_sim),
        "pos_analitica": list(pos_analitica),
        "vel_analitica": list(vel_analitica)
    }


# Graficar posiciones y velocidades
graficar_resultados(dt_values, resultados, tipo='posición')
graficar_resultados(dt_values, resultados, tipo='velocidad')

# Cálculo de errores
for dit in dt_values:
    tiempos = resultados[dit]["tiempos"]
    pos_sim = resultados[dit]["pos_sim"]
    pos_analitica = resultados[dit]["pos_analitica"]
    vel_sim = resultados[dit]["vel_sim"]
    vel_analitica = resultados[dit]["vel_analitica"]

    error_pos = errores(pos_sim, pos_analitica, tiempos)
    error_vel = errores(vel_sim, vel_analitica, tiempos)

    resultados[dit]["error_posicion"] = error_pos[0]
    resultados[dit]["error_posicion_rel"] = error_pos[1]
    resultados[dit]["error_velocidad"] = error_vel[0]
    resultados[dit]["error_velocidad_rel"] = error_vel[1]


# Graficar errores de posición y velocidad
graficar_errores(dt_values, resultados, tipo='posicion')
graficar_errores(dt_values, resultados, tipo='velocidad')

# Calcular y graficar errores globales (L2 y medio absoluto)
errores_pos_L2 = []
errores_vel_L2 = []
errores_pos_medabs = []
errores_vel_medabs = []

for det in dt_values:
    error_pos = resultados[det]["error_posicion"]
    error_vel = resultados[det]["error_velocidad"]
    
    error_pos_L2, error_pos_medabs = calcular_errores_globales(error_pos, resultados[det]["tiempos"])
    error_vel_L2, error_vel_medabs = calcular_errores_globales(error_vel, resultados[det]["tiempos"])
    
    errores_pos_L2.append(error_pos_L2)
    errores_vel_L2.append(error_vel_L2)
    errores_pos_medabs.append(error_pos_medabs)
    errores_vel_medabs.append(error_vel_medabs)

# Graficar errores globales
plt.figure(figsize=(12, 6))
plt.subplot(1, 2, 1)
plt.title("Error L2")
plt.plot(dt_values, errores_pos_L2)
plt.scatter(dt_values, errores_pos_L2, label='Error Posición', marker='*', color='royalblue', s=100)
plt.plot(dt_values, errores_vel_L2)
plt.scatter(dt_values, errores_vel_L2, label='Error Velocidad', marker='x', color='salmon', s=100)
plt.xlabel('Paso de tiempo dt')
plt.ylabel('Error')
plt.legend()

plt.subplot(1, 2, 2)
plt.title("Error Medio Absoluto")
plt.plot(dt_values, errores_pos_medabs)
plt.scatter(dt_values, errores_pos_medabs, label='Error Posición', marker='*', color='royalblue', s=100)
plt.plot(dt_values, errores_vel_medabs)
plt.scatter(dt_values, errores_vel_medabs, label='Error Velocidad', marker='x', color='salmon', s=100)
plt.xlabel('Paso de tiempo dt')
plt.ylabel('Error')
plt.legend()

plt.show()

#####################################################
#################################################### 
### Un mismo paso de tiempo y diferentes integradores
####################################################

# Definir los integradores
integradores = {
    'Euler': Euler,
    'RK2': RungeKutta2,
    'RK4': RungeKutta4,
    #'RKF45': RKF45
}

resultados = {}
print("paso de tiempo: ",dt)
# Simulación con diferentes integradores
for label, integrador in integradores.items():
    tiempos_sim, sim = simular_dinamica(estado, t_max, dt, integrador, der_gravedad_masa_cte)
    pos = [s[0] for s in sim]
    vel = [s[1] for s in sim]
    
    # Calcular solución analítica para los tiempos de la simulación
    pos_analitica = []
    vel_analitica = []
    for t in tiempos_sim:
        pos_a, vel_a = sol_analitica_gravedad_masa_cte(t, estado)
        pos_analitica.append(pos_a)
        vel_analitica.append(vel_a)

    # Guardar resultados en el diccionario
    resultados[label] = {
        'tiempos': tiempos_sim,
        'posiciones': pos,
        'velocidades': vel,
        'posiciones_analiticas': pos_analitica,
        'velocidades_analiticas': vel_analitica
    }

''' 
#Graficar resultados de posiciones
plt.figure(figsize=(12, 6))
for label, res in resultados.items():
    plt.plot(res['tiempos'], res['posiciones'], label=f'{label}', marker='o')

# Graficar solo la posición analítica de RK4
plt.plot(resultados['RK4']['tiempos'], resultados['RK4']['posiciones_analiticas'], label='Sol. Analítica', ls='--')
plt.title('Comparación de posiciones con distintos integradores')
plt.xlabel('Tiempo [s]')
plt.ylabel('Posición [m]')
plt.legend()
plt.grid()

# Graficar resultados de velocidades
plt.figure(figsize=(12, 6))
for label, res in resultados.items():
    plt.plot(res['tiempos'], res['velocidades'], label=f'{label}', marker='o')

# Graficar solo la velocidad analítica de RK4
plt.plot(resultados['RK4']['tiempos'], resultados['RK4']['velocidades_analiticas'], label='Sol. Analítica', ls='--')
plt.title('Comparación de velocidades con distintos integradores')
plt.xlabel('Tiempo [s]')
plt.ylabel('Velocidad [m/s]')
plt.legend()
plt.grid()
plt.show()

# Calcular y graficar errores
for label, res in resultados.items():
    error_pos = errores(res['posiciones'], res['posiciones_analiticas'], res['tiempos'])
    error_vel = errores(res['velocidades'], res['velocidades_analiticas'], res['tiempos'])
    
    resultados[label]["error_posicion"] = error_pos[0]
    resultados[label]["error_posicion_rel"] = error_pos[1]
    resultados[label]["error_velocidad"] = error_vel[0]
    resultados[label]["error_velocidad_rel"] = error_vel[1]

# Graficar errores de posición
lista_values = list(integradores.keys())
graficar_errores2(lista_values, resultados, tipo='posicion')
# Graficar errores de velocidad
graficar_errores2(lista_values, resultados, tipo='velocidad')


##########################################
#print(lista_values)
# Cálculo de errores globales
errores_pos_L2 = []
errores_vel_L2 = []
errores_pos_medabs = []
errores_vel_medabs = []

for integ in integradores.keys():
    error_pos = resultados[integ]["error_posicion"]
    error_vel = resultados[integ]["error_velocidad"]
    tiempos = resultados[integ]["tiempos"]
    
    # Calcular errores globales para posición y velocidad
    error_pos_L2, error_pos_medabs = calcular_errores_globales(error_pos, tiempos)
    error_vel_L2, error_vel_medabs = calcular_errores_globales(error_vel, tiempos)
    
    # Guardar los errores
    errores_pos_L2.append(error_pos_L2)
    errores_vel_L2.append(error_vel_L2)
    errores_pos_medabs.append(error_pos_medabs)
    errores_vel_medabs.append(error_vel_medabs)

# Resultados de errores globales
print('Error L2 de la posición:', errores_pos_L2)
print('Error L2 de la velocidad:', errores_vel_L2)
print('Error medio absoluto de la posición:', errores_pos_medabs)
print('Error medio absoluto de la velocidad:', errores_vel_medabs)

# Graficar errores globales
plt.figure(figsize=(12, 6))
plt.suptitle('Errores de la posición')

plt.subplot(1, 2, 1)
plt.plot(lista_values, errores_pos_L2, marker='o')
plt.title('Errores L2 ')
plt.xlabel('Integrador')
plt.ylabel('Error L2')
# Agregar valores L2 sobre los puntos
for i, value in enumerate(errores_pos_L2):
    plt.text(i, value, f"{value:.2e}", ha='center', va='bottom')


plt.subplot(1, 2, 2)
plt.plot(lista_values, errores_pos_medabs, marker = 'o')
plt.title('Errores medio absoluto')
plt.xlabel('Integrador')
plt.ylabel('Error medio absoluto')
# Agregar valores de error medio absoluto sobre los puntos
for i, value in enumerate(errores_pos_medabs):
    plt.text(i, value, f"{value:.2e}", ha='center', va='bottom')


plt.figure(figsize=(12, 6))
plt.suptitle('Errores de la velocidad')
plt.subplot(1, 2, 1)
plt.plot(lista_values, errores_vel_L2, marker ='o')
plt.title('Errores L2')
plt.xlabel('Integrador')
plt.ylabel('Error L2')
# Agregar valores L2 sobre los puntos
for i, value in enumerate(errores_vel_L2):
    plt.text(i, value, f"{value:.2e}", ha='center', va='bottom')


plt.subplot(1, 2, 2)
plt.plot(lista_values, errores_vel_medabs, marker ='o')
plt.title('Errores medio absoluto')
plt.xlabel('Integrador')
plt.ylabel('Error medio absoluto')
# Agregar valores de error medio absoluto sobre los puntos
for i, value in enumerate(errores_vel_medabs):
    plt.text(i, value, f"{value:.2e}", ha='center', va='bottom')

plt.show()
'''
#####################################################
###Simular con solve_ivp
print('dt:',dt)
dt=0.1
#####################################################
tiempos_py_RK45, sim_py_RK45 = simular_python(estado, t_max, dt, 'RK45', der_gravedad_masa_cte)
tiempos_py_RK23, sim_py_RK23 = simular_python(estado, t_max, dt, 'RK23', der_gravedad_masa_cte)
tiempos_py_BDF, sim_py_BDF = simular_python(estado, t_max, dt, 'BDF', der_gravedad_masa_cte)
tiempos_py_LSODA, sim_py_LSODA = simular_python(estado, t_max, dt, 'LSODA', der_gravedad_masa_cte)
tiempos_py_DOP853, sim_py_DOP853 = simular_python(estado, t_max, dt, 'DOP853', der_gravedad_masa_cte)

# Graficar resultados de la simulación con solve_ivp
# Gráfica de posición
plt.figure(figsize=(10, 5))
plt.plot(tiempos_py_RK45, sim_py_RK45[0], label='RK45-py', marker='o', linestyle='-.')
plt.plot(tiempos_py_RK23, sim_py_RK23[0], label='RK23-py', marker='o', linestyle='-.')
plt.plot(tiempos_py_BDF, sim_py_BDF[0], label='BDF-py', marker='o', linestyle='-.')
plt.plot(tiempos_py_LSODA, sim_py_LSODA[0], label='LSODA-py', marker='o', linestyle='-.')
plt.plot(tiempos_py_DOP853, sim_py_DOP853[0], label='DOP853-py', marker='o', linestyle='-.')
# Agregar resultados de la simulación con integradores propios
for label, res in resultados.items():
    plt.plot(res['tiempos'], res['posiciones'], label=f'{label}', marker='o', linestyle='-.')
# Agregar solución analítica
plt.plot(resultados['RK4']['tiempos'], resultados['RK4']['posiciones_analiticas'], label='Sol. Analítica', color='darkblue')
#linea vertical cada dt
#dts=np.linspace(0,t_max,round(t_max/dt)+1)
#for i in range(1,len(resultados['RK4']['tiempos'])):
    #plt.axvline(x=dts[i], color='k', linestyle='--', alpha=0.2)
#linea en el tiempo del apogeo y punto del apogeo
#Cambiar a los valores analiticos
plt.axvline(x=resultados['RK4']['tiempos'][resultados['RK4']['posiciones'].index(max(resultados['RK4']['posiciones']))], color='r', linestyle='--', alpha=0.5)
plt.scatter(resultados['RK4']['tiempos'][resultados['RK4']['posiciones'].index(max(resultados['RK4']['posiciones']))],max(resultados['RK4']['posiciones']),color='r',label='Apogeo', s=100)

plt.title('Simulación de Posición')
plt.xlabel('Tiempo [s]')
plt.ylabel('Posición [m]')
plt.legend()
plt.grid()


# Gráfica de velocidad
plt.figure(figsize=(10, 5))
plt.plot(tiempos_py_RK45, sim_py_RK45[1], label='RK45', marker='o')
plt.plot(tiempos_py_RK23, sim_py_RK23[1], label='RK23', marker='o')
plt.plot(tiempos_py_BDF, sim_py_BDF[1], label='BDF', marker='o')
plt.plot(tiempos_py_LSODA, sim_py_LSODA[1], label='LSODA', marker='o')
plt.plot(tiempos_py_DOP853, sim_py_DOP853[1], label='DOP853', marker='o')
# Agregar resultados de la simulación con integradores propios
for label, res in resultados.items():
    plt.plot(res['tiempos'], res['velocidades'], label=f'{label}', marker='o')
# Agregar solución analítica
plt.plot(resultados['RK4']['tiempos'], resultados['RK4']['velocidades_analiticas'], label='Sol. Analítica', ls='--')


plt.title('Simulación de Velocidad')
plt.xlabel('Tiempo [s]')
plt.ylabel('Velocidad [m/s]')
plt.legend()
plt.grid()
plt.show()


