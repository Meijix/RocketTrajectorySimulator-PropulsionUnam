#Agregar condiciones iniciales

from Simulador.PaqueteFisica.riel import *
from Simulador.PaqueteFisica.atmosfera import *
from Simulador.PaqueteFisica.viento import *

#riel inicial
riel = Torrelanzamiento(10, 88)
#lugar de lanzamiento
latitud_cord = 19.5
longitud_cord = -98.8
altitud_cord = 20
#fecha
fecha = "2021-05-01"
#viento
#viento_actual = Viento( 10, 2, 0, 0)
#Sin viento
viento_actual = Viento( 0, 2, 0, 0)
#atmosfera
atmosfera_actual = atmosfera()
