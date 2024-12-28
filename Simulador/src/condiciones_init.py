#Agregar condiciones iniciales

import sys
import os
import numpy as np

# Agregar la ruta del directorio que contiene los paquetes al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
#Importar paquetes propios de carpeta superior Paquetes
from Paquetes.PaqueteFisica.riel import Torrelanzamiento
from Paquetes.PaqueteFisica.atmosfera import atmosfera
from Paquetes.PaqueteFisica.viento import Viento


#riel inicial
riel = Torrelanzamiento(10, 87)
#lugar de lanzamiento
latitud_cord = 19.5
longitud_cord = -98.8
altitud_cord = 20
#Indicar fecha actual
fecha = "2024-11-06" #año-mes-dia

#viento
#viento_actual = Viento( 10, 2, 0, 0)
#Sin viento
viento_actual = Viento( 0, 2, 0, 0)
#atmosfera
atmosfera_actual = atmosfera()
#cohete



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
t_max = 800 #[s]
dt_out =  0.01
integrador_actual = 'RungeKutta4'
#integrador_actual = 'RKF45'
#integrador_actual = 'AdaptiveEuler'
# t_max = 1200 #[s]
# t_max = 5 #[s]

viento_actual = Viento(vel_base=20, vel_mean=5, vel_var=5, var_ang=5)
viento_actual.actualizar_viento3D()
#print(viento_actual)
#print(viento_actual.vector)