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


# Función auxiliar para graficar resultados
def graficar_resultados(dt_values, resultados, tipo='posición'):
    plt.figure(figsize=(12, 6))
    for dt in dt_values:
        tiempos = resultados[dt]["tiempos"]
        if tipo == 'posición':
            datos_sim = resultados[dt]["pos_sim"]
            datos_analitica = resultados[dt]["pos_analitica"]
            plt.plot(tiempos, datos_sim, label=f'Posicion dt={dt}', marker='o')
            #plt.plot(tiempos, datos_analitica, label=f'Pos. Analítica dt={dt}')
            plt.title('Comparación de Posiciones')
            plt.ylabel('Posición [m]')
        elif tipo == 'velocidad':
            datos_sim = resultados[dt]["vel_sim"]
            datos_analitica = resultados[dt]["vel_analitica"]
            plt.plot(tiempos, datos_sim, label=f'Velocidad dt={dt}', marker='o')
            #plt.plot(tiempos, datos_analitica, label=f'Velocidad Analítica dt={dt}')
            plt.title('Comparación de Velocidades')
            plt.ylabel('Velocidad [m/s]')
        
        plt.xlabel('Tiempo [s]')
        plt.legend()
        plt.grid()
    plt.show()

# Graficar errores
def graficar_errores(dt_values, resultados, tipo='posicion'):
    plt.figure(figsize=(12, 6))
    plt.suptitle(f"Errores en {'posición' if tipo == 'posición' else 'velocidad'} para distintos dt")
    
    plt.subplot(1, 2, 1)
    for dt in dt_values:
        tiempos = resultados[dt]["tiempos"]
        error = resultados[dt][f"error_{tipo}"]
        plt.plot(tiempos, error, label=f"Error Absoluto dt={dt}", marker='*')

    plt.xlabel('Tiempo [s]')
    plt.ylabel('Error Absoluto')
    plt.legend()
    
    plt.subplot(1, 2, 2)
    for dt in dt_values:
        tiempos = resultados[dt]["tiempos"]
        error_rel = resultados[dt][f"error_{tipo}_rel"]
        plt.plot(tiempos, error_rel, label=f"Error Relativo dt={dt}", marker='*')

    plt.xlabel('Tiempo [s]')
    plt.ylabel('Error Relativo')
    plt.legend()
    plt.show()


####################################################################
v_terminal = np.sqrt(m*g/D_mag)
t_apogeo = (v_terminal/g) * np.arctan(v0/v_terminal)
A = np.arctan(v0/v_terminal)
apogeo = (v_terminal**2/g) *np.log(1/np.cos(A))

print("Tiempo de apogeo: ",t_apogeo, "[s]")
print("Velocidad terminal: ", v_terminal, "[m/s]")
print("Apogeo: ", apogeo, "[m]")

#####################################################
#####################################################
###Diferentes pasos de tiempo y un mismo integrador
#####################################################
# Inicialización de parámetros
#Integrador_oficial = RungeKutta4 #RungeKutta2
Integrador_oficial = Euler
#dt_values = [0.005, 0.01, 0.02, 0.05, 0.1, 0.15, 0.2]
dt_values = [0.005, 0.01, 0.02, 0.03, 0.04, 0.05, 0.1, 0.125, 0.15, 0.175, 0.2]
resultados = {}

# Simulaciones
for dt in dt_values:
    tiempos, sim = simular_dinamica(estado, t_max, dt, Integrador_oficial, der_gravedad_arrastre)
    pos_sim, vel_sim = zip(*[(s[0], s[1]) for s in sim])
    
    pos_analitica, vel_analitica = zip(*[sol_analitica_gravedad_arrastre(estado, t, m, g, D_mag) for t in tiempos])
    
    resultados[dt] = {
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
for dt in dt_values:
    tiempos = resultados[dt]["tiempos"]
    pos_sim = resultados[dt]["pos_sim"]
    pos_analitica = resultados[dt]["pos_analitica"]
    vel_sim = resultados[dt]["vel_sim"]
    vel_analitica = resultados[dt]["vel_analitica"]

    error_pos = errores(pos_sim, pos_analitica, tiempos)
    error_vel = errores(vel_sim, vel_analitica, tiempos)

    resultados[dt]["error_posicion"] = error_pos[0]
    resultados[dt]["error_posicion_rel"] = error_pos[1]
    resultados[dt]["error_velocidad"] = error_vel[0]
    resultados[dt]["error_velocidad_rel"] = error_vel[1]


# Graficar errores de posición y velocidad
graficar_errores(dt_values, resultados, tipo='posicion')
graficar_errores(dt_values, resultados, tipo='velocidad')

# Calcular y graficar errores globales (L2 y medio absoluto)
errores_pos_L2 = []
errores_vel_L2 = []
errores_pos_medabs = []
errores_vel_medabs = []

for dt in dt_values:
    error_pos = resultados[dt]["error_posicion"]
    error_vel = resultados[dt]["error_velocidad"]
    
    error_pos_L2, error_pos_medabs = calcular_errores_globales(error_pos, resultados[dt]["tiempos"])
    error_vel_L2, error_vel_medabs = calcular_errores_globales(error_vel, resultados[dt]["tiempos"])
    
    errores_pos_L2.append(error_pos_L2)
    errores_vel_L2.append(error_vel_L2)
    errores_pos_medabs.append(error_pos_medabs)
    errores_vel_medabs.append(error_vel_medabs)

# Graficar errores globales
plt.figure(figsize=(12, 6))
plt.subplot(1, 2, 1)
plt.title("Error L2")
plt.plot(dt_values, errores_pos_L2, label='Error Posición', marker='*')
plt.plot(dt_values, errores_vel_L2, label='Error Velocidad', marker='o')
plt.xlabel('Paso de tiempo dt')
plt.ylabel('Error')
plt.legend()

plt.subplot(1, 2, 2)
plt.title("Error Medio Absoluto")
plt.plot(dt_values, errores_pos_medabs, label='Error Posición', marker='*')
plt.plot(dt_values, errores_vel_medabs, label='Error Velocidad', marker='o')
plt.xlabel('Paso de tiempo dt')
plt.ylabel('Error')
plt.legend()

plt.show()

#####################################################
####################################################
###Un mismo paso de tiempo y diferentes integradores
####################################################
# Definir los integradores
integradores = {
    'Euler': Euler,
    'RK2': RungeKutta2,
    'RK4': RungeKutta4
}

resultados = {}

# Simulación con diferentes integradores
for label, integrador in integradores.items():
    tiempos_sim, sim = simular_dinamica(estado, t_max, dt, integrador, der_gravedad_arrastre)
    pos = [s[0] for s in sim]
    vel = [s[1] for s in sim]
    
    # Guardar resultados en el diccionario
    resultados[label] = {
        'tiempos': tiempos_sim,
        'posiciones': pos,
        'velocidades': vel
    }

# Calcular solución analítica para los tiempos del integrador RK4
pos_analitica = []
vel_analitica = []
for t in resultados['RK4']['tiempos']:  # Usando RK4
    pos, vel = sol_analitica_gravedad_arrastre(estado, t, m, g, D_mag)
    pos_analitica.append(pos)
    vel_analitica.append(vel)

# Graficar resultados de posiciones
plt.figure(figsize=(12, 6))
for label, res in resultados.items():
    plt.plot(res['tiempos'], res['posiciones'], label=f'Posición - {label}', marker='o', markersize=4)

plt.plot(resultados['RK4']['tiempos'], pos_analitica, label='Posición Analítica', ls='--')
plt.title('Comparación de posiciones con distintos integradores')
plt.xlabel('Tiempo [s]')
plt.ylabel('Posición [m]')
plt.legend()
plt.grid()

# Graficar resultados de velocidades
plt.figure(figsize=(12, 6))
for label, res in resultados.items():
    plt.plot(res['tiempos'], res['velocidades'], label=f'Velocidad - {label}', marker='o', markersize=4)

plt.plot(resultados['RK4']['tiempos'], vel_analitica, label='Velocidad Analítica', ls='--')
plt.title('Comparación de velocidades con distintos integradores')
plt.xlabel('Tiempo [s]')
plt.ylabel('Velocidad [m/s]')
plt.legend()
plt.grid()
plt.show()

# Calcular y graficar errores
for label, res in resultados.items():
    error_pos = errores(res['posiciones'], pos_analitica, res['tiempos'])
    error_vel = errores(res['velocidades'], vel_analitica, res['tiempos'])
    
    resultados[label]["error_posicion"] = error_pos[0]
    resultados[label]["error_posicion_rel"] = error_pos[1]
    resultados[label]["error_velocidad"] = error_vel[0]
    resultados[label]["error_velocidad_rel"] = error_vel[1]

# Graficar errores de posición
lista_values = list(integradores.keys())
graficar_errores(lista_values, resultados, tipo='posicion')
# Graficar errores de velocidad
graficar_errores(lista_values, resultados, tipo='velocidad')
