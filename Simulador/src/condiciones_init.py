#Agregar condiciones iniciales

import sys
import os

# Agregar la ruta del directorio que contiene los paquetes al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
#Importar paquetes propios de carpeta superior Paquetes
from Paquetes.PaqueteFisica.riel import Torrelanzamiento
from Paquetes.PaqueteFisica.atmosfera import atmosfera
from Paquetes.PaqueteFisica.viento import Viento

#riel inicial
riel = Torrelanzamiento(10, 88)
""" #lugar de lanzamiento
latitud_cord = 19.5
longitud_cord = -98.8
altitud_cord = 20
#Indicar fecha actual
fecha = "2024-11-06" """

#viento
#viento_actual = Viento( 10, 2, 0, 0)
#Sin viento
viento_actual = Viento( 0, 2, 0, 0)
#atmosfera
atmosfera_actual = atmosfera()
