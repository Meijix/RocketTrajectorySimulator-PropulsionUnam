#Funciones utiles para el guardar y extraer datos de los archivos
import pandas as pd
import numpy as np
import os
import json
import tqdm
from tqdm import tqdm
import sys

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
    tiempos = datos_simulacion['t'].values

    posiciones = datos_simulacion[['x', 'y', 'z']].values
    velocidades = datos_simulacion[['vx', 'vy', 'vz']].values
    thetas = datos_simulacion['thetas'].values
    omegas = datos_simulacion['omegas'].values

    CPs = datos_simulacion['CPs'].values
    CGs = datos_simulacion['CGs'].values
    masavuelo = datos_simulacion['masavuelo'].values

    viento_vuelo_mags = datos_simulacion['viento_mags'].values
    viento_vuelo_dirs = datos_simulacion['viento_dirs'].values
    viento_vuelo_vecs = datos_simulacion['viento_vecs'].values
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
    return (tiempos, posiciones, velocidades, thetas, omegas, CPs, CGs, masavuelo,
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
def guardar_datos_csv(tiempos, posiciones, velocidades, thetas, omegas, CPs, CGs, masavuelo, viento_vuelo_mags, viento_vuelo_dirs, viento_vuelo_vecs, wind_xs, wind_ys, wind_zs, Tmags, Dmags, Nmags, Txs, Tys, Tzs, Dxs, Dys, Dzs, Nxs, Nys, Nzs, accels, palancas, accangs, Gammas, Alphas, torcas, Cds, Machs, TipoVuelo, integrador_actual, eficiencia=100):
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

    nombre_carpeta = f'{TipoVuelo}-{integrador_actual}-{eficiencia}'
    ruta_carpeta = f'Simulador/Resultados/OutputFiles/{nombre_carpeta}'

    # Crear la carpeta si no existe
    if not os.path.exists(ruta_carpeta):
        os.makedirs(ruta_carpeta)

    # Guardar archivo CSV en la carpeta
    ruta_archivo_csv = f'{ruta_carpeta}/datos.csv'
    datos_simulados.to_csv(ruta_archivo_csv, index=False)
    print(f'Archivo CSV guardado en: {ruta_archivo_csv}')

def guardar_datos_json(cohete_actual,vuelo1, max_altitude, max_speed, accels, accangs, TipoVuelo, integrador_actual, eficiencia=100):
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

    nombre_carpeta = f'{TipoVuelo}-{integrador_actual}-{eficiencia}'
    ruta_carpeta = f'Simulador/Resultados/OutputFiles/{nombre_carpeta}'

    # Crear la carpeta si no existe
    if not os.path.exists(ruta_carpeta):
        os.makedirs(ruta_carpeta)

    # Guardar los datos en un archivo .json
    ruta_archivo_json = f'{ruta_carpeta}/datos.json'
    with open(ruta_archivo_json, 'w', encoding='utf-8') as f:
        json.dump(datos_a_guardar, f, indent=4)
    print(f'Archivo JSON guardado en: {ruta_archivo_json}')


def guardar_animacion(animation, nombre_archivo, formato='mp4', fps=30):
    """
    Guarda la animación con una barra de progreso.

    :param animation: Objeto de animación de Matplotlib.
    :param nombre_archivo: Nombre del archivo de salida.
    :param formato: Formato de salida ('mp4' o 'gif').
    :param fps: Fotogramas por segundo.
    """
    print("Guardando animación...")
    #ruta_archivo
    ruta_archivo = f'Simulador/Resultados/OutputFiles/{nombre_archivo}'
    if formato == 'mp4':
        with tqdm(total=100, file=sys.stdout, desc="Progreso") as pbar:
            def progress_callback(i, n):
                pbar.update(int(100 * i / n) - pbar.n)

            animation.save(
                ruta_archivo, 
                writer='ffmpeg', 
                fps=fps, 
                progress_callback=progress_callback
            )
    elif formato == 'gif':
        with tqdm(total=100, file=sys.stdout, desc="Progreso") as pbar:
            def progress_callback(i, n):
                pbar.update(int(100 * i / n) - pbar.n)

            animation.save(
                nombre_archivo, 
                writer='imagemagick', 
                fps=fps, 
                progress_callback=progress_callback
            )
    else:
        raise ValueError("Formato no soportado. Use 'mp4' o 'gif'.")

    print("Animación guardada con éxito")

import os
# Función para obtener la ruta del archivo

def obtener_path_archivo(*subrutas):
    ruta_base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    ruta_final = os.path.join(ruta_base, *subrutas)
    return ruta_final
