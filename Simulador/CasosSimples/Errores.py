import numpy as np


def errores(numerico,analitico,tiempos):
    error_abs = [numerico[i] - analitico[i] for i in range(len(tiempos))]
    error_rel = [abs(error_abs[i]/analitico[i]) for i in range(len(tiempos))]
    #for i in range(len(tiempos)):
        #print(i, numerico[i], analitico[i])
    return error_abs, error_rel

'''
def graficar_errores(tiempos1, tiempos2, tiempos3, tiempos4, tiempos5, errorpos1, errorpos2, errorpos3,errorpos4, errorpos5, errorpos_rel1, errorpos_rel2, errorpos_rel3, errorpos_rel4, errorpos_rel5, errorvel1, errorvel2, errorvel3,errorvel4, errorvel5, errorvel_rel1, errorvel_rel2, errorvel_rel3, errorvel_rel4, errorvel_rel5):
    # Grafica errores absolutos y relativos
    #Para la posicion
    plt.figure(figsize=(12, 6))
    #plt.title("Errores en posición para distintos dt")

    plt.subplot(1, 2, 1)
    plt.plot(tiempos1, errorpos1, label='dt=0.005', marker='*')
    plt.plot(tiempos2, errorpos2, label='dt=0.01', marker='*')
    plt.plot(tiempos3, errorpos3, label='dt=0.05', marker='*')
    plt.plot(tiempos4, errorpos4, label='dt=0.1', marker='*')
    plt.plot(tiempos5, errorpos5, label='dt=0.2', marker='*')
    #plt.title("Errores absolutos")
    plt.xlabel('Tiempo [s]')
    plt.ylabel('Error absoluto [m]')
    plt.legend()

    plt.subplot(1, 2, 2)
    plt.plot(tiempos1, errorpos_rel1, label='dt=0.005', marker='*')
    plt.plot(tiempos2, errorpos_rel2, label='dt=0.01', marker='*')
    plt.plot(tiempos3, errorpos_rel3, label='dt=0.05', marker='*')
    plt.plot(tiempos4, errorpos_rel4, label='dt=0.1', marker='*')
    plt.plot(tiempos5, errorpos_rel5, label='dt=0.2', marker='*')
    #plt.title("Errores relativos")
    plt.xlabel('Tiempo [s]')
    plt.ylabel('Error relativo')
    plt.legend()
    #plt.show()

    #Para la velocidad
    plt.figure(figsize=(12, 6))
    plt.title("Errores en velocidad para distintos dt")

    plt.subplot(1, 2, 1)
    plt.plot(tiempos1, errorvel1, label='dt=0.005', marker='*')
    plt.plot(tiempos2, errorvel2, label='dt=0.01', marker='*')
    plt.plot(tiempos3, errorvel3, label='dt=0.05', marker='*')
    plt.plot(tiempos4, errorvel4, label='dt=0.1', marker='*')
    plt.plot(tiempos5, errorvel5, label='dt=0.2', marker='*')
    #plt.title("Errores absolutos")
    plt.xlabel('Tiempo [s]')
    plt.ylabel('Error absoluto [m/s]')
    plt.legend()


    plt.subplot(1, 2, 2)
    plt.plot(tiempos1, errorvel_rel1, label='dt=0.005', marker='*')
    plt.plot(tiempos2, errorvel_rel2, label='dt=0.01', marker='*')
    plt.plot(tiempos3, errorvel_rel3, label='dt=0.05', marker='*')
    plt.plot(tiempos4, errorvel_rel4, label='dt=0.1', marker='*')
    plt.plot(tiempos5, errorvel_rel5, label='dt=0.2', marker='*')
    #plt.title("Errores relativos")
    plt.xlabel('Tiempo [s]')
    plt.ylabel('Error relativo')
    plt.legend()
    plt.show()
'''
