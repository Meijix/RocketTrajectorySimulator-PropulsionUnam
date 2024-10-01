import numpy as np

def errores(numerico,analitico,tiempos):
    error_abs = [numerico[i] - analitico[i] for i in range(len(tiempos))]
    error_rel = [abs(error_abs[i]/analitico[i]) for i in range(len(tiempos))]
    #for i in range(len(tiempos)):
        #print(i, numerico[i], analitico[i])
    return error_abs, error_rel