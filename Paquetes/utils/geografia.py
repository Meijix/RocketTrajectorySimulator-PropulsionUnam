"""Conversión entre las coordenadas del simulador y coordenadas geográficas.

El simulador usa un sistema local con origen en el sitio de lanzamiento:
    x  horizontal, en la dirección hacia la que se inclina el riel (azimut del riel)
    y  horizontal, perpendicular, hacia la izquierda de esa dirección
    z  vertical
El azimut y las direcciones del viento "desde" se miden en grados desde el norte, en
sentido horario (convención de brújula y meteorológica).
"""
import math

R_TIERRA = 6371000.0  # [m]


def direccion_viento_simulador(direccion_desde, azimut_riel):
    """Convierte la dirección meteorológica del viento (de dónde viene, desde el norte)
    al ángulo que usa la clase Viento (hacia dónde sopla, medido desde el eje x hacia +y)."""
    hacia = direccion_desde + 180.0           # rumbo hacia el que sopla
    return (azimut_riel - hacia) % 360.0      # +y queda a la izquierda del eje x


def desplazamiento_este_norte(x, y, azimut_riel):
    """Desplazamiento (este, norte) en metros de un punto (x, y) del simulador."""
    a = math.radians(azimut_riel)
    este = x * math.sin(a) - y * math.cos(a)
    norte = x * math.cos(a) + y * math.sin(a)
    return este, norte


def a_geograficas(x, y, latitud_sitio, longitud_sitio, azimut_riel):
    """Latitud y longitud (grados) del punto (x, y) del simulador."""
    este, norte = desplazamiento_este_norte(x, y, azimut_riel)
    latitud = latitud_sitio + math.degrees(norte / R_TIERRA)
    longitud = longitud_sitio + math.degrees(este / (R_TIERRA * math.cos(math.radians(latitud_sitio))))
    return latitud, longitud


def distancia_y_rumbo(lat1, lon1, lat2, lon2):
    """Distancia (m) y rumbo (grados desde el norte) del punto 1 al punto 2 (aproximación plana local)."""
    norte = math.radians(lat2 - lat1) * R_TIERRA
    este = math.radians(lon2 - lon1) * R_TIERRA * math.cos(math.radians(lat1))
    return math.hypot(este, norte), math.degrees(math.atan2(este, norte)) % 360.0
