#Funciones utiles para el guardar y extraer datos de los archivos
import pandas as pd
import numpy as np
import os
import json

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


##########################################
# Funcion para graficar los tiempos importantes
def muestra_tiempos(tiempo_salida_riel,t_MECO,tiempo_apogeo, tiempo_impacto, ax):
    ax.axvline(tiempo_salida_riel, color="darkred", ls="--")
    ax.axvline(t_MECO, color="orange", ls="--")
    if tiempo_apogeo is not None:
        ax.axvline(tiempo_apogeo, color="darkgreen", ls="--")
    if tiempo_impacto is not None:
        ax.axvline(tiempo_impacto, color="0.5", ls="--")
    #if tiempo_despliegue is not None:
        #ax.axvline(tiempo_despliegue, color="green", ls="--")
    #ax.legend()

###############################################
def guardar_datos_csv(tiempos, posiciones, velocidades, thetas, omegas, CPs, CGs, masavuelo, viento_vuelo_mags, viento_vuelo_dirs, viento_vuelo_vecs, wind_xs, wind_ys, wind_zs, Tmags, Dmags, Nmags, Txs, Tys, Tzs, Dxs, Dys, Dzs, Nxs, Nys, Nzs, accels, palancas, accangs, Gammas, Alphas, torcas, Cds, Machs, TipoVuelo, integrador_actual):
    # Guardar los datos de la simulación en un archivo .csv
    datos_simulados = pd.DataFrame({
        #En los integradores propios se debe cambiar el tamano de los estados para que coincida con el número de tiempos
        't': tiempos[:],#Se quita el primer tiempo para que coincida con el número de estados
        'x': posiciones[:, 0], #Se quita el primer estado para que coincida con el número de tiempos
        'y': posiciones[:, 1], #Se quita el primer estado para que coincida con el número de tiempos
        'z': posiciones[:, 2], #Se quita el primer estado para que coincida con el número de tiempos
        'vx': velocidades[:, 0], #Se quita el primer estado para que coincida con el número de tiempos
        'vy': velocidades[:, 1], #Se quita el primer estado para que coincida con el número de tiempos
        'vz': velocidades[:, 2], #Se quita el primer estado para que coincida con el número de tiempos
        'thetas': thetas[:], #Se quita el primer estado para que coincida con el número de tiempos
        'omegas': omegas[:], #Se quita el primer estado para que coincida con el número de tiempos
        'CPs': CPs,
        'CGs': CGs,
        'masavuelo': masavuelo[:], #Se quita el primer estado para que coincida con el número de tiempos
        'viento_mags': viento_vuelo_mags,
        'viento_dirs': viento_vuelo_dirs,
        'viento_vecs': viento_vuelo_vecs,
        'wind_xs': wind_xs,
        'wind_ys': wind_ys,
        'wind_zs': wind_zs,
        #'Tvecs': Tvecs,
        #'Dvecs': Dvecs,
        #'Nvecs': Nvecs,
        'Tmags': Tmags,
        'Dmags': Dmags,
        'Nmags': Nmags,
        'Txs': Txs,
        'Tys': Tys,
        'Tzs': Tzs,
        'Dxs': Dxs,
        'Dys': Dys,
        'Dzs': Dzs,
        'Nxs': Nxs,
        'Nys': Nys,
        'Nzs': Nzs,
        'accels': accels,
        'palancas': palancas,
        'accangs': accangs,
        'Gammas': Gammas,
        'Alphas': Alphas,
        'torcas': torcas,
        'Cds': Cds,
        'Machs': Machs
    })

    nombre_carpeta = f'{TipoVuelo}-{integrador_actual}'
    ruta_carpeta = f'Simulador/Resultados/OutputFiles/{nombre_carpeta}'

    # Crear la carpeta si no existe
    if not os.path.exists(ruta_carpeta):
        os.makedirs(ruta_carpeta)

    # Guardar archivo CSV en la carpeta
    ruta_archivo_csv = f'{ruta_carpeta}/datos.csv'
    datos_simulados.to_csv(ruta_archivo_csv, index=False)
    print(f'Archivo CSV guardado en: {ruta_archivo_csv}')

def guardar_datos_json(cohete_actual,vuelo1, max_altitude, max_speed, accels, accangs, TipoVuelo, integrador_actual):
    #Guardar datos importantes en un archivo json
    datos_a_guardar = {
        'nombre cohete': cohete_actual.nombre,
        'd_ext': cohete_actual.d_ext,
        't_MECO': cohete_actual.t_MECO,
        'tiempo_salida_riel': vuelo1.tiempo_salida_riel,
        'tiempo_apogeo': vuelo1.tiempo_apogeo,
        'tiempo_impacto': vuelo1.tiempo_impacto,
        'max_altitude': max_altitude,
        'max_speed': max_speed,
        'max_acceleration_linear': np.max(accels),
        'max_acceleration_angular': np.max(accangs)
        #'velocidad de impacto': velocidades[-1]
    }

    nombre_carpeta = f'{TipoVuelo}-{integrador_actual}'
    ruta_carpeta = f'Simulador/Resultados/OutputFiles/{nombre_carpeta}'

    # Crear la carpeta si no existe
    if not os.path.exists(ruta_carpeta):
        os.makedirs(ruta_carpeta)

    # Guardar los datos en un archivo .json
    ruta_archivo_json = f'{ruta_carpeta}/datos.json'
    with open(ruta_archivo_json, 'w', encoding='utf-8') as f:
        json.dump(datos_a_guardar, f, indent=4)
    print(f'Archivo JSON guardado en: {ruta_archivo_json}')
