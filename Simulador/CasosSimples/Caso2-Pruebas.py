import numpy as np
import matplotlib.pyplot as plt

# Importar tus módulos aquí
from Cond_Init import *
from IntegradoresCasos import *
from FunSimularDinamica import *
from Errores import *

def der_gravedad_arrastre(t, state):
    v = state[1]
    Drag = (D_mag/m) * (v**2) * np.sign(v) if v != 0 else 0
    return np.array((v, -g - Drag))

def sol_analitica_gravedad_arrastre(state, t, m, g, D_mag):
    z0, v0 = state
    v_terminal = np.sqrt(m * g / D_mag)
    t_apogeo = (v_terminal/g) * np.arctan(v0/v_terminal)
    A = np.arctan(v0/v_terminal)
    apogeo = (v_terminal**2/g) * np.log(1/np.cos(A))

    if t <= t_apogeo:
        v = v_terminal * np.tan((-g*t / v_terminal) + A)
        z = z0 + (v_terminal**2/g) * np.log(np.cos((-g*t/v_terminal) + A) / np.cos(A))
    else:
        v = v_terminal * np.tanh((-g / v_terminal) * (t - t_apogeo))
        z = z0 + apogeo + (v_terminal**2/-g) * np.log(np.cosh((-g/v_terminal)*(t - t_apogeo)))

    return z, v

# Función auxiliar para graficar resultados
def graficar_resultados(dt_values, resultados, tipo='posición'):
    plt.figure(figsize=(12, 6))
    for dt in dt_values:
        tiempos = resultados[dt]["tiempos"]
        if tipo == 'posición':
            datos_sim = resultados[dt]["pos_sim"]
            datos_analitica = resultados[dt]["pos_analitica"]
            plt.plot(tiempos, datos_sim, label=f'Pos. Simulada dt={dt}', linestyle='--')
            plt.plot(tiempos, datos_analitica, label=f'Pos. Analítica dt={dt}')
            plt.title('Comparación de Posiciones')
            plt.ylabel('Posición [m]')
        elif tipo == 'velocidad':
            datos_sim = resultados[dt]["vel_sim"]
            datos_analitica = resultados[dt]["vel_analitica"]
            plt.plot(tiempos, datos_sim, label=f'Velocidad Simulada dt={dt}', linestyle='--')
            plt.plot(tiempos, datos_analitica, label=f'Velocidad Analítica dt={dt}')
            plt.title('Comparación de Velocidades')
            plt.ylabel('Velocidad [m/s]')
        
        plt.xlabel('Tiempo [s]')
        plt.legend()
        plt.grid()
    plt.show()

# Inicialización de parámetros
Integrador_oficial = RungeKutta2
dt_values = [0.005, 0.01, 0.02, 0.05, 0.1, 0.15, 0.2]
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
    pos_euler = resultados[dt]["pos_sim"]
    pos_analitica = resultados[dt]["pos_analitica"]
    vel_euler = resultados[dt]["vel_sim"]
    vel_analitica = resultados[dt]["vel_analitica"]

    error_pos = errores(pos_euler, pos_analitica, tiempos)
    error_vel = errores(vel_euler, vel_analitica, tiempos)

    resultados[dt]["error_pos"] = error_pos[0]
    resultados[dt]["error_pos_rel"] = error_pos[1]
    resultados[dt]["error_vel"] = error_vel[0]
    resultados[dt]["error_vel_rel"] = error_vel[1]

# Graficar errores
def graficar_errores(dt_values, resultados, tipo='posición'):
    plt.figure(figsize=(12, 6))
    plt.suptitle(f"Errores en {'posición' if tipo == 'posición' else 'velocidad'} para distintos dt")
    
    plt.subplot(1, 2, 1)
    for dt in dt_values:
        tiempos = resultados[dt]["tiempos"]
        error = resultados[dt][f"error_{tipo}"]
        plt.plot(tiempos, error, label=f"Error Absoluto dt={dt}")

    plt.xlabel('Tiempo [s]')
    plt.ylabel('Error Absoluto')
    plt.legend()
    
    plt.subplot(1, 2, 2)
    for dt in dt_values:
        tiempos = resultados[dt]["tiempos"]
        error_rel = resultados[dt][f"error_{tipo}_rel"]
        plt.plot(tiempos, error_rel, label=f"Error Relativo dt={dt}")

    plt.xlabel('Tiempo [s]')
    plt.ylabel('Error Relativo')
    plt.legend()
    plt.show()

# Graficar errores de posición y velocidad
graficar_errores(dt_values, resultados, tipo='posición')
graficar_errores(dt_values, resultados, tipo='velocidad')

# Calcular y graficar errores globales (L2 y medio absoluto)
errores_pos_L2 = []
errores_vel_L2 = []
errores_pos_medabs = []
errores_vel_medabs = []

for dt in dt_values:
    error_pos = resultados[dt]["error_pos"]
    error_vel = resultados[dt]["error_vel"]
    
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
