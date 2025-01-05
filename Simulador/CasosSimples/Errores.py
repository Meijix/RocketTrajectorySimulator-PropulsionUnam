#Funciones utiles para calcular errores y graficarlos
import numpy as np
import matplotlib.pyplot as plt


def errores(numerico,analitico,tiempos):
    error_abs = [numerico[i] - analitico[i] for i in range(len(tiempos))]
    error_rel = [abs(error_abs[i]/analitico[i]) for i in range(len(tiempos))]
    #for i in range(len(tiempos)):
        #print(i, numerico[i], analitico[i])
    return error_abs, error_rel

def calcular_errores_globales(error_abs, tiempos):
    # Calcular error global L2
    error_L2 = np.sqrt(sum([e**2 for e in error_abs])) / len(tiempos)
    
    # Calcular error global medio absoluto
    error_medio_abs = sum([abs(e) for e in error_abs]) / len(tiempos)
    
    return error_L2, error_medio_abs

def graficar_resultados(dt_values, resultados, tipo='posición'):
    """
    Función para graficar resultados analíticos y numéricos para diferentes valores de dt.

    :param dt_values: Lista de valores de dt utilizados en las simulaciones.
    :param resultados: Diccionario con resultados para cada dt.
                       Debe contener "tiempos", "pos_analitica", "vel_analitica",
                       "pos_sim" y "vel_sim" para cada dt.
    :param tipo: Tipo de gráfico ('posición' o 'velocidad').
    """
    # Configuración inicial de la figura
    plt.figure(figsize=(12, 6))

    # Seleccionar datos analíticos del primer dt como referencia
    primer_dt = dt_values[0]
    tiempos_analiticos = resultados[primer_dt]["tiempos"]
    if tipo == 'posición':
        datos_analiticos = resultados[primer_dt]["pos_analitica"]
        titulo = 'Comparación de Posiciones'
        ylabel = 'Posición [m]'
    elif tipo == 'velocidad':
        datos_analiticos = resultados[primer_dt]["vel_analitica"]
        titulo = 'Comparación de Velocidades'
        ylabel = 'Velocidad [m/s]'
    else:
        raise ValueError("El tipo debe ser 'posición' o 'velocidad'.")

    # Graficar resultados analíticos
    plt.plot(tiempos_analiticos, datos_analiticos, label="Analítica", linestyle='solid',color='darkblue' ,linewidth=2)

    # Graficar resultados numéricos para cada dt
    for dt in dt_values:
        tiempos = resultados[dt]["tiempos"]
        if tipo == 'posición':
            datos_sim = resultados[dt]["pos_sim"]
        elif tipo == 'velocidad':
            datos_sim = resultados[dt]["vel_sim"]
        plt.plot(tiempos, datos_sim, label=f'dt={dt}', marker='o', linestyle='-.', alpha=0.8)

    # Configuración de etiquetas y título
    plt.title(titulo, fontsize=14)
    plt.xlabel('Tiempo [s]', fontsize=12)
    plt.ylabel(ylabel, fontsize=12)
    plt.legend(title="Método", fontsize=10)
    plt.grid(True, linestyle='--', alpha=0.7)

    # Mostrar el gráfico
    plt.tight_layout()
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
