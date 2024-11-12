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
