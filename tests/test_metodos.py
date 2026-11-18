"""Catálogo de métodos: mismos nombres en todas partes y todos resuelven bien un problema conocido."""
import numpy as np
import pytest

from Paquetes.PaqueteEDOs.metodos import ADAPTATIVOS, CLAVES_VUELO, FIJOS, METODOS, etiqueta, metodo, resolver
from Simulador.GUI import backend

G = 9.81


def caida(t, y):
    return np.array([y[1], -G])


def impacto(t, y):
    return y[0]
impacto.terminal = True
impacto.direction = -1


def test_el_catalogo_tiene_los_nueve_metodos():
    assert list(METODOS) == ["Euler", "RK2", "RK4", "RKF45", "RK23", "RK45", "DOP853", "BDF", "LSODA"]
    assert FIJOS == ["Euler", "RK2", "RK4"]
    assert ADAPTATIVOS == ["RKF45", "RK23", "RK45", "DOP853", "BDF", "LSODA"]


def test_los_nombres_teoricos_son_los_correctos():
    assert METODOS["RK45"].nombre == "Dormand-Prince 5(4)"        # el RK45 de SciPy no es Fehlberg
    assert METODOS["RKF45"].nombre == "Runge-Kutta-Fehlberg 4(5)"
    assert METODOS["RKF45"].origen == "propio"
    assert METODOS["RK23"].nombre == "Bogacki-Shampine 3(2)"
    assert metodo("RungeKutta4") is METODOS["RK4"]
    assert etiqueta("RK45") == "RK45 · Dormand-Prince 5(4)"


def test_el_simulador_y_la_gui_ofrecen_los_mismos_metodos():
    assert sorted(backend.INTEGRADORES) == sorted(CLAVES_VUELO)


@pytest.mark.parametrize("nombre", ADAPTATIVOS)
def test_adaptativos_paso_libre_con_evento(nombre):
    # Tiro vertical: v0 = 50 m/s. Impacto en t = 2*v0/g con velocidad -v0
    sol = resolver(nombre, caida, (0, 20), [0.0, 50.0], events=impacto, repeticiones=1)
    assert sol.termino_por_evento
    assert sol.t[-1] == pytest.approx(2 * 50 / G, rel=1e-4)
    assert sol.y[0, -1] == pytest.approx(0.0, abs=1e-3)
    assert sol.y[1, -1] == pytest.approx(-50.0, rel=1e-3)
    assert sol.pasos == len(sol.t) - 1 and sol.nfev > 0 and sol.tiempo > 0


@pytest.mark.parametrize("nombre", ADAPTATIVOS)
def test_adaptativos_respetan_el_paso_maximo(nombre):
    sol = resolver(nombre, caida, (0, 5), [0.0, 50.0], dt=0.1, repeticiones=1)
    assert np.diff(sol.t).max() <= 0.1 + 1e-12
    assert sol.t[-1] == pytest.approx(5.0)


@pytest.mark.parametrize("nombre", FIJOS)
def test_paso_fijo(nombre):
    sol = resolver(nombre, caida, (0, 5), [0.0, 50.0], dt=0.1, repeticiones=1)
    assert sol.pasos == 50
    assert np.diff(sol.t) == pytest.approx(0.1)
    assert sol.nfev == 50 * {"Euler": 1, "RK2": 2, "RK4": 4}[nombre]
    assert sol.y[1, -1] == pytest.approx(50 - G * 5)
    with pytest.raises(ValueError, match="paso fijo"):
        resolver(nombre, caida, (0, 5), [0.0, 50.0])


def test_paso_fijo_termina_antes_del_evento():
    sol = resolver("RK4", caida, (0, 20), [0.0, 50.0], dt=0.1, events=impacto, repeticiones=1)
    assert sol.termino_por_evento
    assert sol.y[0, -1] > 0 and sol.t[-1] == pytest.approx(10.1, abs=0.11)
