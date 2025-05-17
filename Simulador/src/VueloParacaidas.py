#Simulacion CON paracaidas del Xitle2
import numpy as np
import time
import sys
import os

# Agregar la ruta del directorio que contiene los paquetes al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

#Importar paquetes propios de carpeta superior Paquetes
from Paquetes.PaqueteFisica.vuelo import Vuelo
from Paquetes.PaqueteFisica.cohete import Parachute
from Paquetes.utils.funciones import guardar_datos_csv, guardar_datos_json

from Simulador.src import condiciones_init as c_init
from Simulador.src.XitleFile import Xitle

cohete_actual = Xitle
TipoVuelo = 'VueloParacaidas'

### EMPEZAR SIN PARACAIDAS
#quitar el paracaidas
cohete_actual.parachute_added = False
#desactivar el paracaidas
cohete_actual.parachute_active1 = False

######################################
#####Agregar paracaidas
Mainchute = Parachute(1.2, 0.802) #Crear paracaidas principal
print(Xitle.parachute_active1)
cohete_actual.agregar_paracaidas(Mainchute)
print("Paracaidas activado:",Xitle.parachute_active1)
print("Paracaidas agregado:", Xitle.parachute_added)
#########################################3

inicio = time.time()
print("Simulando...")
vuelo_paracaidas = Vuelo(cohete_actual, c_init.atmosfera_actual, c_init.viento_actual)
tiempos, sim, CPs, CGs, masavuelo, viento_vuelo_mags, viento_vuelo_dirs, viento_vuelo_vecs, Tvecs, Dvecs, Nvecs, accels, palancas, accangs, Gammas, Alphas, torcas, Cds, Machs = vuelo_paracaidas.simular_vuelo(c_init.estado, c_init.t_max, c_init.dt, c_init.dt_out, c_init.integrador_actual)
#Medir tiempo que tarda en correr la simulacion
fin = time.time()
print(f"Tiempo de ejecución: {fin-inicio:.1f}s")

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
# Guardar los datos de la simulación
print("Guardando datos...")
guardar_datos_csv(tiempos, posiciones, velocidades, thetas, omegas, CPs, CGs, masavuelo, viento_vuelo_mags, viento_vuelo_dirs, viento_vuelo_vecs, wind_xs, wind_ys, wind_zs, Tmags, Dmags, Nmags, Txs, Tys, Tzs, Dxs, Dys, Dzs, Nxs, Nys, Nzs, accels, palancas, accangs, Gammas, Alphas, torcas, Cds, Machs, TipoVuelo, c_init.integrador_actual)
########################################
guardar_datos_json(cohete_actual,vuelo_paracaidas, max_altitude, max_speed, accels, accangs, TipoVuelo, c_init.integrador_actual)