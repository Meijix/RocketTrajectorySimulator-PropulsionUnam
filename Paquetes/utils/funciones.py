
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy.interpolate import interp1d
import math
from math import pi
import random


# Constantes universales
GravUn = 6.67430E-11  # m^3/kg/s^2 Constante de gravitación universal
Rg = 8.31447   #[J/(mol·K)] Constante universal de los gases
R_Tierra = 6371000 #[m] Radio de la Tierra
M_tierra = 5.972168e24  #[kg] Masa de la Tierra

# Funciones
#Funcion para normalizar vectores
def normalized(vec):
  assert np.linalg.norm(vec) > 0
  return vec / np.linalg.norm(vec)

def calc_gravedad(altura_z):
  return GravUn * M_tierra / (altura_z + R_Tierra)**2

#Calcular la gravedad en la superficie
g0 = calc_gravedad(0)
#print(g0)

#Funciones que extraen datos de los archivos 
def extraer_datoscsv(datos_simulacion):
    # Convertir los datos a arrays de numpy
    tiempos = datos_simulacion['tiempos'].values

    posiciones = datos_simulacion[['posiciones_x', 'posiciones_y', 'posiciones_z']].values
    velocidades = datos_simulacion[['velocidades_x', 'velocidades_y', 'velocidades_z']].values
    thetas = datos_simulacion['thetas'].values
    omegas = datos_simulacion['omegas'].values

    CPs = datos_simulacion['CPs'].values
    CGs = datos_simulacion['CGs'].values
    masavuelo = datos_simulacion['masavuelo'].values
    estabilidad = datos_simulacion['estabilidad'].values

    viento_vuelo_mags = datos_simulacion['viento_vuelo_mags'].values
    viento_vuelo_dirs = datos_simulacion['viento_vuelo_dirs'].values
    viento_vuelo_vecs = datos_simulacion['viento_vuelo_vecs'].values
    wind_xs = datos_simulacion['wind_xs'].values
    wind_ys = datos_simulacion['wind_ys'].values
    wind_zs = datos_simulacion['wind_zs'].values

    Tmags = datos_simulacion['Tmags'].values
    Dmags = datos_simulacion['Dmags'].values
    Nmags = datos_simulacion['Nmags'].values
    Txs = datos_simulacion['Txs'].values
    Tys = datos_simulacion['Tys'].values
    Tzs = datos_simulacion['Tzs'].values
    Dxs = datos_simulacion['Dxs'].values
    Dys = datos_simulacion['Dys'].values
    Dzs = datos_simulacion['Dzs'].values
    Nxs = datos_simulacion['Nxs'].values
    Nys = datos_simulacion['Nys'].values
    Nzs = datos_simulacion['Nzs'].values

    accels = datos_simulacion['accels'].values
    palancas = datos_simulacion['palancas'].values
    accangs = datos_simulacion['accangs'].values

    Gammas = datos_simulacion['Gammas'].values
    Alphas = datos_simulacion['Alphas'].values
    torcas = datos_simulacion['torcas'].values

    Cds = datos_simulacion['Cds'].values
    Machs = datos_simulacion['Machs'].values
    #########################################
    #Obtener magnitudes y separar coordenadas
    Tvecs = np.column_stack((Txs, Tys, Tzs))
    Dvecs = np.column_stack((Dxs, Dys, Dzs))
    Nvecs = np.column_stack((Nxs, Nys, Nzs))
    #print(Tvecs)

    CGs = np.array(CGs)
    CPs = np.array(CPs)
    return (tiempos, posiciones, velocidades, thetas, omegas, CPs, CGs, masavuelo,estabilidad,
            viento_vuelo_mags, viento_vuelo_dirs, viento_vuelo_vecs, wind_xs, wind_ys, wind_zs,
            Dmags, Nmags, Tmags, Dxs, Dys, Dzs, Nxs, Nys, Nzs, Txs, Tys, Tzs, Tvecs, Dvecs, Nvecs,
            accels, palancas, accangs, Gammas, Alphas, torcas, Cds, Machs)

def extraer_datosjson(datos):
    #print(datos)
    diam_ext = datos['d_ext']
    t_MECO = datos["t_MECO"]
    tiempo_salida_riel = datos["tiempo_salida_riel"]
    tiempo_apogeo = datos["tiempo_apogeo"]
    tiempo_impacto = datos["tiempo_impacto"]
    max_altitude = datos["max_altitude"]
    max_speed = datos["max_speed"]
    max_acceleration_linear = datos["max_acceleration_linear"]
    max_acceleration_angular = datos["max_acceleration_angular"]
    return (diam_ext, t_MECO, tiempo_salida_riel, tiempo_apogeo, tiempo_impacto, 
            max_altitude, max_speed, max_acceleration_linear, max_acceleration_angular)
