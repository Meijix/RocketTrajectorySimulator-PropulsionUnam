#Comparacion de simulaciones
#Leer y graficar las diferentes simulaciones

import pandas as pd
import json
import numpy as np

from funciones import extraer_datoscsv, extraer_datosjson

#Lista de n-archivos csv de simulaciones
lista_archivos_csv=['datos_simulacion.csv','datos_simulacion.csv']

#Leer y extraer los datos de todos los archivos
for i in range (len(lista_archivos_csv)):
    archivo_i=lista_archivos_csv[i]
    datos_simulacion_i = pd.read_csv(archivo_i)
    # Extarer los datos del csv
    (tiempos, posiciones, velocidades, thetas, omegas, CPs, CGs, masavuelo,estabilidad,
    viento_vuelo_mags, viento_vuelo_dirs, viento_vuelo_vecs, wind_xs, wind_ys, wind_zs,
    Dmags, Nmags, Tmags, Dxs, Dys, Dzs, Nxs, Nys, Nzs, Txs, Tys, Tzs, Tvecs, Dvecs, Nvecs,
    accels, palancas, accangs, Gammas, Alphas, torcas, Cds, Machs) = extraer_datoscsv(datos_simulacion_i)
    
