"""Configuración común de las pruebas: raíz del proyecto en el path y vuelos de referencia."""
import os
import sys

import pytest

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)

import matplotlib
matplotlib.use("Agg")   # sin ventanas durante las pruebas

from Simulador.GUI import backend  # noqa: E402


def volar(**cambios):
    """Simula el Xitle II con los valores por defecto de la GUI, modificando lo indicado."""
    params = dict(backend.PARAMS_XITLE, integrator="LSODA", wind_seed=1)   # viento reproducible
    params.update(cambios)
    return backend.ejecutar_simulacion(params, backend.RUTAS_XITLE)


@pytest.fixture(scope="session")
def vuelo_libre():
    return volar()


@pytest.fixture(scope="session")
def vuelo_paracaidas():
    return volar(recovery=backend.RECUPERACION[1])
