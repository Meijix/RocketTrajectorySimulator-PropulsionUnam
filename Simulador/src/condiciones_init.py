#Agregar condiciones iniciales

from PaqueteFisica.riel import *
from PaqueteFisica.atmosfera import *
from PaqueteFisica.viento import *

#riel inicial
riel = Torrelanzamiento(10, 88)
#lugar de lanzamiento
latitud_cord = 19.5
longitud_cord = -98.8
altitud_cord = 20
#Indicar fecha actual
fecha = "2024-11-06"

#viento
#viento_actual = Viento( 10, 2, 0, 0)
#Sin viento
viento_actual = Viento( 0, 2, 0, 0)
#atmosfera
atmosfera_actual = atmosfera()
