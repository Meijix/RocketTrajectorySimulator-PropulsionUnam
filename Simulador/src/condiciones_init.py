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
viento_actual.actualizar_viento3D()
#print(viento_actual.vector)

#atmosfera
atmosfera_actual = atmosfera()

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
t_max = 400 #[s]
dt_out =  0.01
integrador_actual = 'RungeKutta4'
integrador_actual = 'Euler'
#integrador_actual = 'BDF'
#integrador_actual = 'RKF45'
