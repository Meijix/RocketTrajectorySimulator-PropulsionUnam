"""Sitio de lanzamiento y condiciones atmosféricas del vuelo real del Xitle II.

Lee Archivos/DatosVuelo/condiciones_2024-06-22.json (ahí están los valores y sus fuentes)
y construye con ellos la atmósfera y el viento del simulador.
"""
import json
import os

from Paquetes.PaqueteFisica.atmosfera import atmosfera
from Paquetes.PaqueteFisica.viento import Viento
from Paquetes.utils.geografia import direccion_viento_simulador

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
RUTA_CONDICIONES = os.path.join(RAIZ, 'Archivos', 'DatosVuelo', 'condiciones_2024-06-22.json')


def cargar_condiciones(ruta=RUTA_CONDICIONES):
    with open(ruta, 'r', encoding='utf-8') as f:
        return json.load(f)


def crear_atmosfera(condiciones):
    """Atmósfera ISA ajustada a la altitud del sitio y a la temperatura y presión del día."""
    return atmosfera(altitud_sitio=condiciones['sitio']['altitud_m'],
                     delta_T=condiciones['atmosfera']['delta_T_ISA_K'],
                     presion_sitio=condiciones['atmosfera']['presion_sitio_Pa'])


def perfil_de_viento(condiciones, azimut_riel):
    """Niveles de viento como (altura sobre el sitio, rapidez, dirección en la convención del simulador)."""
    altitud_sitio = condiciones['sitio']['altitud_m']
    return [(max(n['altitud_msnm'] - altitud_sitio, 0.0), n['rapidez_ms'],
             direccion_viento_simulador(n['direccion_desde_grados'], azimut_riel))
            for n in condiciones['viento']['niveles']]


def crear_viento(condiciones, azimut_riel=None, semilla=None):
    """Viento del día: perfil con la altura más ráfagas."""
    if azimut_riel is None:
        azimut_riel = condiciones['lanzamiento']['azimut_riel_grados']
    perfil = perfil_de_viento(condiciones, azimut_riel)
    v = condiciones['viento']
    return Viento(vel_base=perfil[0][1], ang_base=perfil[0][2],
                  vel_mean=v['rafaga_media_ms'], vel_var=v['rafaga_desviacion_ms'],
                  var_ang=v['variacion_direccion_grados'], perfil=perfil, semilla=semilla)
