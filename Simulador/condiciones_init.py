#Agregar condiciones iniciales

from riel import *
from Atmosfera1 import *
from Viento import *

#riel inicial
riel = Torrelanzamiento(10, 80)
#lugar de lanzamiento
latitud_cord = 19.5
longitud_cord = -98.8
altitud_cord = 20
#fecha
fecha = "2021-05-01"
#viento
viento_actual = Viento2D(10,0)
#atmosfera
atmosfera_actual = atmosfera(0, 0, 0)
