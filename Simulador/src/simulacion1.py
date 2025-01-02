#Simulacion sin paracaidas del Xitle2
import numpy as np
import pandas as pd
import sys
import os
import time
import json

# Agregar la ruta del directorio que contiene los paquetes al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

#Importar paquetes propios de carpeta superior Paquetes
from Paquetes.PaqueteFisica.vuelo import Vuelo
from Simulador.src import condiciones_init as c_init
from Simulador.src.XitleFile import Xitle, diam_ext


cohete_actual = Xitle

#quitar el paracaidas
cohete_actual.parachute_added = False
#desactivar el paracaidas
cohete_actual.parachute_active1 = False

#Crear el vuelo
vuelo1 = Vuelo(cohete_actual, c_init.atmosfera_actual, c_init.viento_actual)

print("Inicio de la simulación")
inicio = time.time()
#Simular el vuelo
tiempos, sim, CPs, CGs, masavuelo, viento_vuelo_mags, viento_vuelo_dirs, viento_vuelo_vecs, Tvecs, Dvecs, Nvecs, accels, palancas, accangs, Gammas, Alphas, torcas, Cds, Machs = vuelo1.simular_vuelo(c_init.estado,c_init.t_max, c_init.dt, c_init.dt_out, c_init.integrador_actual)
#print(viento_vuelo_mags)
#Medir tiempo que tarda en correr la simulacion
fin = time.time()
print(f"Tiempo de ejecución: {fin-inicio:.1f}s")

print("Simulación terminada")

#Extraer datos de la simulación
posiciones = np.array([state[0:3] for state in sim])
velocidades = np.array([state[3:6] for state in sim])
thetas = np.array([state[6] for state in sim])
omegas = np.array([state[7] for state in sim])

Tmags = np.array([np.linalg.norm(Tvec) for Tvec in Tvecs])
Dmags = np.array([np.linalg.norm(Dvec) for Dvec in Dvecs])
Nmags = np.array([np.linalg.norm(Nvec) for Nvec in Nvecs])

Txs, Tys, Tzs = zip(*Tvecs)
Dxs, Dys, Dzs = zip(*Dvecs)
Nxs, Nys, Nzs = zip(*Nvecs)

wind_xs = [vec[0] for vec in viento_vuelo_vecs]
wind_ys = [vec[1] for vec in viento_vuelo_vecs]
wind_zs = [vec[2] for vec in viento_vuelo_vecs]

max_altitude = max(posiciones[:, 2])
max_speed = max(np.linalg.norm(velocidades, axis=1))
####################################
#print(tiempo)
#print(posiciones)
#print("Tiempo de salida del riel [s]",vuelo1.tiempo_salida_riel)
#print("Tiempo de MECO [s]",Xitle.t_MECO)
#print("Tiempo de apogeo [s]",vuelo1.tiempo_apogeo)
#print("Tiempo de impacto [s]",vuelo1.tiempo_impacto)

#print("APOGEO:", max_altitude, "metros")
#print("Máxima velocidad:", max_speed, "m/s")
#print("Equivalente a:",max_speed/340, "Mach")
#########################################
print("Guardando datos de la simulación")
print("Tiempos", len(tiempos))
print("Sim ", len(sim))
print("CPs", len(CPs))
print("CGs", len(CGs))
print("masavuelo", len(masavuelo))
print("viento_vuelo_mags", len(viento_vuelo_mags))
print("viento_vuelo_dirs", len(viento_vuelo_dirs))
print("viento_vuelo_vecs", len(viento_vuelo_vecs))
print("Tvecs", len(Tvecs))
print("Dvecs", len(Dvecs))
print("Nvecs", len(Nvecs))
print("viento_vuelo_vecs", len(viento_vuelo_vecs))




# Guardar los datos de la simulación en un archivo .csv
datos_simulados = pd.DataFrame({
    #En los integradores propios se debe cambiar el tamano de los estados para que coincida con el número de tiempos
    'tiempos': tiempos[:],#Se quita el primer tiempo para que coincida con el número de estados
    'posiciones_x': posiciones[:, 0], #Se quita el primer estado para que coincida con el número de tiempos
    'posiciones_y': posiciones[:, 1], #Se quita el primer estado para que coincida con el número de tiempos
    'posiciones_z': posiciones[:, 2], #Se quita el primer estado para que coincida con el número de tiempos
    'velocidades_x': velocidades[:, 0], #Se quita el primer estado para que coincida con el número de tiempos
    'velocidades_y': velocidades[:, 1], #Se quita el primer estado para que coincida con el número de tiempos
    'velocidades_z': velocidades[:, 2], #Se quita el primer estado para que coincida con el número de tiempos
    'thetas': thetas[:], #Se quita el primer estado para que coincida con el número de tiempos
    'omegas': omegas[:], #Se quita el primer estado para que coincida con el número de tiempos
    'CPs': CPs,
    'CGs': CGs,
    'masavuelo': masavuelo[:], #Se quita el primer estado para que coincida con el número de tiempos
    'viento_vuelo_mags': viento_vuelo_mags,
    'viento_vuelo_dirs': viento_vuelo_dirs,
    'viento_vuelo_vecs': viento_vuelo_vecs,
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
#Crear un archivo csv con los datos de la simulación
# Guardar archivo en la carpeta Simulador/Resultados/OuputFiles
datos_simulados.to_csv('datos_simulacion.csv', index=False)
print('csv guardado')
############################
#Guardar datos importantes en un archivo json

datos_a_guardar = {
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

# Guardar los datos en un archivo .json
# Guardar archivo en la carpeta Simulador/Resultados/OuputFiles
with open('././datos_simulacion.json', 'w', encoding='utf-8') as f:
    json.dump(datos_a_guardar, f, indent=4)

print('json guardado')