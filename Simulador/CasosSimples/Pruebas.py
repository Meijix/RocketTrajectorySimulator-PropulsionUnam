#Caso 2: Gravedad + Arrastre cuadratico y masa cte

import numpy as np
import matplotlib.pyplot as plt

# Importar tus módulos aquí
from Cond_Init import *
from IntegradoresCasos import *
from FunSimularDinamica import *
from Errores import *

def der_gravedad_masa_cte(t, state):
    z, v = state
    derivs = np.array((v, -g))
    #print(derivs)
    return derivs

def sol_analitica_gravedad_masa_cte(t, state):
    z0, v0 = state
    z = z0 + (v0*t) - (0.5 * g * (t**2))
    v = v0 - (g*t)
    return z, v

# Función auxiliar para graficar resultados
def graficar_resultados(dt_values, resultados, tipo='posición'):
    plt.figure(figsize=(12, 6))
    for dt in dt_values:
        tiempos = resultados[dt]["tiempos"]
        if tipo == 'posición':
            datos_sim = resultados[dt]["pos_sim"]
            datos_analitica = resultados[dt]["pos_analitica"]
            plt.plot(tiempos, datos_sim, label=f'dt={dt}', marker='o')
            #plt.plot(tiempos, datos_analitica, label=f'Pos. Analítica dt={dt}')
            plt.title('Comparación de Posiciones')
            plt.ylabel('Posición [m]')
        elif tipo == 'velocidad':
            datos_sim = resultados[dt]["vel_sim"]
            datos_analitica = resultados[dt]["vel_analitica"]
            plt.plot(tiempos, datos_sim, label=f'dt={dt}', marker='o')
            #plt.plot(tiempos, datos_analitica, label=f'Velocidad Analítica dt={dt}')
            plt.title('Comparación de Velocidades')
            plt.ylabel('Velocidad [m/s]')
        
        plt.xlabel('Tiempo [s]')
        plt.legend()
        plt.grid()
    plt.show()

# Graficar errores
def graficar_errores(dt_values, resultados, tipo='posicion'):
    opacidad=0.5
    plt.figure(figsize=(12, 6))
    plt.suptitle(f"Errores en {'posición' if tipo == 'posición' else 'velocidad'} para distintos dt")
    
    plt.subplot(1, 2, 1)
    for dt in dt_values:
        tiempos = resultados[dt]["tiempos"]
        error = resultados[dt][f"error_{tipo}"]
        plt.plot(tiempos, error, label=f"dt={dt}", marker='*', alpha = opacidad)

    plt.xlabel('Tiempo [s]')
    plt.ylabel('Error Absoluto')
    plt.title('Errores absolutos')
    plt.legend()
    
    plt.subplot(1, 2, 2)
    for dt in dt_values:
        tiempos = resultados[dt]["tiempos"]
        error_rel = resultados[dt][f"error_{tipo}_rel"]
        plt.plot(tiempos, error_rel, label=f"dt={dt}", marker='*', alpha = opacidad)

    plt.xlabel('Tiempo [s]')
    plt.ylabel('Error Relativo')
    plt.title('Errores relativos')
    plt.legend()
    plt.show()

def graficar_errores2(lista, resultados, tipo='posicion'):
    opacidad=0.5
    plt.figure(figsize=(12, 6))
    plt.suptitle(f"Errores en {'posición' if tipo == 'posicion' else 'velocidad'} para distintos integradores")
    
    plt.subplot(1, 2, 1)
    for integ in lista:
        tiempos = resultados[integ]["tiempos"]
        error = resultados[integ][f"error_{tipo}"]
        plt.plot(tiempos, error, label=f"{integ}", marker='p', alpha = opacidad)

    plt.xlabel('Tiempo [s]')
    plt.ylabel('Error Absoluto')
    plt.legend()
    
    plt.subplot(1, 2, 2)
    for integ in lista:
        tiempos = resultados[integ]["tiempos"]
        error_rel = resultados[integ][f"error_{tipo}_rel"]
        plt.plot(tiempos, error_rel, label=f"{integ}", marker='^', alpha = opacidad)

    plt.xlabel('Tiempo [s]')
    plt.ylabel('Error Relativo')
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
    'RK4': RungeKutta4
}

resultados = {}

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

# Graficar resultados de posiciones
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
plt.subplot(1, 2, 2)
plt.plot(lista_values, errores_pos_medabs, marker = 'o')
plt.title('Errores medio absoluto')
plt.xlabel('Integrador')
plt.ylabel('Error medio absoluto')

plt.figure(figsize=(12, 6))
plt.suptitle('Errores de la velocidad')
plt.subplot(1, 2, 1)
plt.plot(lista_values, errores_vel_L2, marker ='o')
plt.title('Errores L2')
plt.xlabel('Integrador')
plt.ylabel('Error L2')
plt.subplot(1, 2, 2)
plt.plot(lista_values, errores_vel_medabs, marker ='o')
plt.title('Errores medio absoluto')
plt.xlabel('Integrador')
plt.ylabel('Error medio absoluto')
plt.show()
