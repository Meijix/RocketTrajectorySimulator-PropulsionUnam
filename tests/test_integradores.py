"""Integradores propios contra soluciones analíticas."""
import numpy as np
import pytest

from Paquetes.PaqueteEDOs.integradores import Euler, RungeKutta2, RungeKutta4

G = 9.81


def tiro_parabolico(t, estado):
    """Estado = [x, z, vx, vz] bajo gravedad constante, sin arrastre."""
    return np.array([estado[2], estado[3], 0.0, -G])


def integrar(clase, f, estado, t_final, dt):
    integrador, t = clase(f), 0.0
    for _ in range(round(t_final / dt)):
        estado, _ = integrador.step(t, estado, dt)
        t += dt
    return estado


@pytest.mark.parametrize("clase", [RungeKutta2, RungeKutta4])
def test_tiro_parabolico_exacto(clase):
    # La solución es un polinomio de grado 2 en t: RK2 y RK4 deben reproducirla exactamente
    x, z, vx, vz = integrar(clase, tiro_parabolico, np.array([0.0, 0.0, 30.0, 40.0]), 5.0, 0.1)
    assert x == pytest.approx(30.0 * 5.0)
    assert z == pytest.approx(40.0 * 5.0 - 0.5 * G * 25.0)
    assert (vx, vz) == pytest.approx((30.0, 40.0 - G * 5.0))


def test_tiro_parabolico_conserva_energia():
    # Energía mecánica por unidad de masa: v²/2 + g·z
    energia = lambda e: 0.5 * (e[2] ** 2 + e[3] ** 2) + G * e[1]
    inicial = np.array([0.0, 0.0, 30.0, 40.0])
    final = integrar(RungeKutta4, tiro_parabolico, inicial, 5.0, 0.1)
    assert energia(final) == pytest.approx(energia(inicial))


@pytest.mark.parametrize("clase, orden", [(Euler, 1), (RungeKutta2, 2), (RungeKutta4, 4)])
def test_orden_de_convergencia(clase, orden):
    # Oscilador armónico: x'' = -x, con solución exacta (cos t, -sin t)
    oscilador = lambda t, e: np.array([e[1], -e[0]])
    exacta = np.array([np.cos(1.0), -np.sin(1.0)])
    errores = [np.linalg.norm(integrar(clase, oscilador, np.array([1.0, 0.0]), 1.0, dt) - exacta)
               for dt in (0.02, 0.01)]
    assert np.log2(errores[0] / errores[1]) == pytest.approx(orden, abs=0.15)


# ---------------------------------------------------------------- Runge-Kutta-Fehlberg 4(5)
from Paquetes.PaqueteEDOs.integradores import RKF45, EulerAdaptativo, HeunAdaptativo  # noqa: E402


def _matriz_A():
    A = np.zeros((6, 6))
    for i, fila in enumerate(RKF45.A):
        A[i, :len(fila)] = fila
    return A


def test_rkf45_tiene_los_coeficientes_de_fehlberg():
    # Tabla de Fehlberg (1969), como aparece en Burden y Faires
    assert RKF45.C == pytest.approx([0, 1/4, 3/8, 12/13, 1, 1/2])
    assert RKF45.B4 == pytest.approx([25/216, 0, 1408/2565, 2197/4104, -1/5, 0])
    assert RKF45.B5 == pytest.approx([16/135, 0, 6656/12825, 28561/56430, -9/50, 2/55])
    assert _matriz_A().sum(axis=1) == pytest.approx(RKF45.C)          # consistencia de cada etapa


def test_rkf45_cumple_las_condiciones_de_orden():
    A, c = _matriz_A(), RKF45.C
    for b, orden in ((RKF45.B4, 4), (RKF45.B5, 5)):
        # Condiciones de orden hasta 4 (comunes a ambos)
        assert b.sum() == pytest.approx(1)
        assert b @ c == pytest.approx(1/2)
        assert b @ c**2 == pytest.approx(1/3)
        assert b @ A @ c == pytest.approx(1/6)
        assert b @ c**3 == pytest.approx(1/4)
        assert (b * c) @ A @ c == pytest.approx(1/8)
        assert b @ A @ c**2 == pytest.approx(1/12)
        assert b @ A @ A @ c == pytest.approx(1/24)
    # La de orden 5 cumple además b·c^4 = 1/5; la de orden 4 no
    assert RKF45.B5 @ c**4 == pytest.approx(1/5)
    assert RKF45.B4 @ c**4 != pytest.approx(1/5)


def test_rk45_de_scipy_no_es_fehlberg():
    # 'RK45' en solve_ivp es Dormand-Prince 5(4): otra tabla de coeficientes
    from scipy.integrate import RK45
    assert list(RK45.C[:6]) == pytest.approx([0, 1/5, 3/10, 4/5, 8/9, 1])
    assert list(RK45.C[:6]) != pytest.approx(list(RKF45.C))


def test_rkf45_orden_de_convergencia():
    # Con tolerancia enorme nunca rechaza un paso: se comporta como un método de paso fijo de orden 5
    oscilador = lambda t, e: np.array([e[1], -e[0]])
    exacta = np.array([np.cos(1.0), -np.sin(1.0)])
    errores = []
    for dt in (0.1, 0.05):
        integrador, estado, t = RKF45(oscilador, rtol=1e6, atol=1e6), np.array([1.0, 0.0]), 0.0
        for _ in range(round(1.0 / dt)):
            estado, usado = integrador.step(t, estado, dt)
            assert usado == dt
            t += usado
        errores.append(np.linalg.norm(estado - exacta))
    assert np.log2(errores[0] / errores[1]) == pytest.approx(5, abs=0.2)


@pytest.mark.parametrize("clase, tolerancia", [(RKF45, 1e-4), (HeunAdaptativo, 1e-2), (EulerAdaptativo, 0.1)])
def test_adaptativos_ajustan_el_paso(clase, tolerancia):
    oscilador = lambda t, e: np.array([e[1], -e[0]])
    integrador, estado, t, dt = clase(oscilador), np.array([1.0, 0.0]), 0.0, 1.0   # paso inicial demasiado grande
    pasos = []
    while t < 10.0:
        estado, usado = integrador.step(t, estado, min(dt, 10.0 - t))
        t += usado
        pasos.append(usado)
        dt = integrador.dt_sugerido
    assert t == pytest.approx(10.0)
    assert estado == pytest.approx([np.cos(10.0), -np.sin(10.0)], abs=tolerancia)
    assert min(pasos) < 1.0                                   # redujo el paso inicial
    assert integrador.dt_sugerido > 0
