#Agregar condiciones iniciales para el vuelo
import sys
import os
import numpy as np

# Agregar la ruta del directorio que contiene los paquetes al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
#Importar paquetes propios de carpeta superior Paquetes
from Paquetes.PaqueteFisica.riel import Torrelanzamiento
from Paquetes.PaqueteFisica.atmosfera import atmosfera
from Paquetes.PaqueteFisica.viento import Viento

from Simulador.src.dia_de_vuelo import cargar_condiciones, crear_atmosfera, crear_viento

# Sitio y condiciones del vuelo real del Xitle II (Spaceport America, 22 de junio de 2024).
# Los valores y sus fuentes están en Archivos/DatosVuelo/condiciones_2024-06-22.json
condiciones = cargar_condiciones()

#riel inicial
# Angulo de elevacion de 83 grados: es el que reproduce la trayectoria GPS del vuelo real
# (apogeo a 2.5 km del sitio y caida a unos 4.6 km; con 87 grados caeria a 2 km)
riel = Torrelanzamiento(10, 83)
azimut_riel = condiciones['lanzamiento']['azimut_riel_grados']  # rumbo hacia el que se inclina el riel (grados desde el norte)
#lugar de lanzamiento
latitud_cord = condiciones['sitio']['latitud']
longitud_cord = condiciones['sitio']['longitud']
altitud_cord = condiciones['sitio']['altitud_m']   # metros sobre el nivel del mar
#Fecha del lanzamiento
fecha = condiciones['lanzamiento']['fecha'] #año-mes-dia

#viento del dia: perfil con la altura mas rafagas
# Semilla de las rafagas: resultados reproducibles (None = aleatorio en cada corrida)
viento_actual = crear_viento(condiciones, azimut_riel, semilla=2024)
# Para un viento constante (sin perfil), por ejemplo 5 m/s de frente con rafagas:
#viento_actual = Viento(vel_base=5, vel_mean=3, vel_var=2, ang_base=180, var_ang=10.0, semilla=2024)
# (ang_base: direccion horizontal hacia la que sopla, desde el eje x: 0 = de cola, 180 = de frente, 90/270 = cruzado)
viento_actual.actualizar_viento3D()

#atmosfera del dia: ISA ajustada a la altitud del sitio, la temperatura y la presion
atmosfera_actual = crear_atmosfera(condiciones)
#Atmosfera estandar al nivel del mar:
#atmosfera_actual = atmosfera()

# Estado inicial
x0, y0, z0 = 0, 0, 0
vx0, vy0, vz0 = 0, 0, 0

theta0, omega0 = np.deg2rad(riel.angulo), 0
estado=np.array([x0, y0, z0, vx0, vy0, vz0, theta0, omega0])
#print(estado)
#estado=list(estado)
#print(estado)
#Parametros de la simulacion
dt = 0.01 #0.1 #[s]
t_max = 1000 #[s] tiempo maximo; la simulacion termina antes si hay impacto
dt_out = dt  # intervalo de guardado; debe ser multiplo de dt (si es menor, limita el paso de los integradores propios)
integrador_actual = 'RungeKutta4'
#integrador_actual = 'Euler'
#integrador_actual = 'RK45'
integrador_actual = 'DOP853'
#integrador_actual = 'LSODA'
#integrador_actual = 'BDF'
