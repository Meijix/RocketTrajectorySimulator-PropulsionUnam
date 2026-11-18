"""Simulación de vuelo completa del Xitle II (regresiones de los errores corregidos)."""
import io
import contextlib

import numpy as np
import pytest

from conftest import volar
from Simulador.GUI import backend


def test_la_masa_disminuye_durante_el_quemado(vuelo_libre):
    df, resumen = vuelo_libre
    masa = df["masa"].to_numpy()
    assert masa[0] > masa[-1] + 10                       # se consumen más de 10 kg de propelente
    assert np.all(np.diff(masa) <= 1e-9)                 # nunca aumenta
    tras_quemado = df[df["t"] > resumen["t_MECO"] + 0.5]["masa"]
    assert tras_quemado.max() == pytest.approx(tras_quemado.min())


def test_eventos_del_vuelo(vuelo_libre):
    df, r = vuelo_libre
    assert 0 < r["t_salida_riel"] < r["t_apogeo"] < r["t_impacto"]
    assert r["apogeo"] == pytest.approx(df["z"].max())
    assert df["z"].iloc[-1] == pytest.approx(0.0, abs=1.0)          # la integración termina en el suelo
    assert np.all(np.diff(df["t"]) > 0)
    assert not df.isna().any().any()


def test_apogeo_en_rango_fisico(vuelo_libre):
    # Vuelo real del Xitle II: 6573 m sobre el sitio. El simulador debe quedar en el mismo orden.
    assert 6000 < vuelo_libre[1]["apogeo"] < 8000


def test_el_paracaidas_frena_el_descenso(vuelo_libre, vuelo_paracaidas):
    libre, paracaidas = vuelo_libre[1], vuelo_paracaidas[1]
    assert paracaidas["apogeo"] == pytest.approx(libre["apogeo"], rel=1e-3)   # mismo ascenso
    assert paracaidas["vel_impacto"] < 60
    assert paracaidas["vel_impacto"] < 0.25 * libre["vel_impacto"]
    assert paracaidas["t_impacto"] > 2 * libre["t_impacto"]


@pytest.mark.parametrize("integrador", ["RK45", "BDF"])
def test_los_integradores_coinciden(vuelo_libre, integrador):
    _, otro = volar(integrator=integrador)
    assert otro["apogeo"] == pytest.approx(vuelo_libre[1]["apogeo"], rel=5e-3)
    assert otro["t_impacto"] == pytest.approx(vuelo_libre[1]["t_impacto"], rel=5e-3)


def test_dos_corridas_seguidas_son_identicas(vuelo_libre):
    # Antes la masa quedaba "en seco" tras el primer vuelo y el segundo daba otro apogeo
    _, repetido = volar()
    assert repetido["apogeo"] == pytest.approx(vuelo_libre[1]["apogeo"], rel=1e-9)


def test_tiempo_maximo_menor_que_el_vuelo():
    df, r = volar(sim_max_time=30)
    assert r["t_impacto"] is None and r["vel_impacto"] is None
    assert df["t"].iloc[-1] == pytest.approx(30.0)


def test_integrador_propio_runge_kutta_2():
    # 'RungeKutta2' estaba en la lista de integradores pero no se podía usar
    with contextlib.redirect_stdout(io.StringIO()):
        df, _ = volar(integrator="RungeKutta2", sim_max_time=3, sim_time_step=0.01)
    assert df["z"].iloc[-1] > 50


def test_viento_reproducible_con_semilla():
    from Paquetes.PaqueteFisica.viento import Viento
    a, b = Viento(semilla=7), Viento(semilla=7)
    assert np.allclose(a.vector_en(12.3), b.vector_en(12.3))
    assert np.allclose(a.vector_en(12.3), a.vector_en(12.3))   # mismo t, mismo viento
    a.reiniciar_rafagas()
    assert np.allclose(a.vector_en(12.3), b.vector_en(12.3))


# ---------------------------------------------------------------- paso de los integradores propios
def _vuelo_propio(integrador, t_max, dt, dt_out):
    from Paquetes.PaqueteFisica.atmosfera import atmosfera
    from Paquetes.PaqueteFisica.viento import Viento
    from Paquetes.PaqueteFisica.vuelo import Vuelo
    with contextlib.redirect_stdout(io.StringIO()):
        cohete = backend.construir_cohete(backend.PARAMS_XITLE, backend.RUTAS_XITLE)
        vuelo = Vuelo(cohete, atmosfera(), Viento(semilla=1))
        estado0 = np.array([0, 0, 0, 0, 0, 0, np.deg2rad(87), 0], dtype=float)
        salida = vuelo.simular_vuelo(estado0, t_max, dt, dt_out, integrador)
    return vuelo, np.array(salida[0]), np.array(salida[1])


@pytest.mark.parametrize("dt, dt_out, pasos, puntos", [
    (0.01, 0.01, 300, 301),     # un punto guardado por paso (más el inicial)
    (0.01, 0.05, 300, 61),      # se guarda cada 5 pasos, sin cambiar el paso
    (0.01, 0.001, 3000, 3001),  # salida más fina que el paso: el paso queda limitado a dt_out
])
def test_los_integradores_propios_respetan_dt(dt, dt_out, pasos, puntos):
    vuelo, tiempos, _ = _vuelo_propio("RungeKutta4", 3.0, dt, dt_out)
    assert vuelo.pasos == pasos
    assert len(tiempos) == puntos
    assert np.diff(tiempos) == pytest.approx(dt_out)
    assert tiempos[-1] == pytest.approx(3.0)


def test_rkf45_en_el_vuelo_completo(vuelo_libre):
    df, r = volar(integrator="RKF45")
    assert r["apogeo"] == pytest.approx(vuelo_libre[1]["apogeo"], rel=5e-3)
    assert r["t_impacto"] == pytest.approx(vuelo_libre[1]["t_impacto"], rel=5e-3)
    assert df["z"].iloc[-1] == pytest.approx(0.0, abs=1e-6)       # el impacto se interpola al suelo


# ---------------------------------------------------------------- viento
def test_el_viento_medio_es_horizontal_y_en_la_direccion_base():
    from Paquetes.PaqueteFisica.viento import Viento
    viento = Viento(vel_base=5, vel_mean=3, vel_var=2, ang_base=230, var_ang=10, semilla=3)
    muestras = np.array([viento.vector_en(t).copy() for t in np.arange(0, 4000, 1.0)])
    vx, vy, vz = muestras.mean(axis=0)
    assert abs(vz) < 0.1                                                    # sin viento vertical neto
    assert np.rad2deg(np.arctan2(vy, vx)) % 360 == pytest.approx(230, abs=1.5)
    assert np.hypot(vx, vy) == pytest.approx(5 + 3, rel=0.05)               # base + ráfaga media
    direcciones = np.rad2deg(np.arctan2(muestras[:, 1], muestras[:, 0])) % 360
    assert 5 < direcciones.std() < 15                                       # la dirección varía ~var_ang


@pytest.mark.parametrize("angulo, esperado", [(0, (4, 0, 0)), (90, (0, 4, 0)), (180, (-4, 0, 0))])
def test_convencion_de_direccion_del_viento(angulo, esperado):
    from Paquetes.PaqueteFisica.viento import Viento
    viento = Viento(vel_base=4, vel_mean=0, vel_var=0, ang_base=angulo, var_ang=0, semilla=1)
    assert viento.vector_en(7.5) == pytest.approx(esperado, abs=1e-9)


# ---------------------------------------------------------------- sitio de lanzamiento y mapa
def test_coordenadas_de_impacto(vuelo_libre):
    from Paquetes.utils.geografia import distancia_y_rumbo
    df, r = vuelo_libre
    assert (r["lat_lanzamiento"], r["lon_lanzamiento"]) == pytest.approx((32.94753, -106.91019))
    assert (df["latitud"].iloc[0], df["longitud"].iloc[0]) == pytest.approx((32.94753, -106.91019))
    distancia, rumbo = distancia_y_rumbo(r["lat_lanzamiento"], r["lon_lanzamiento"], r["lat_impacto"], r["lon_impacto"])
    assert distancia == pytest.approx(r["distancia"], rel=1e-3)
    assert rumbo == pytest.approx(r["rumbo_impacto"])
    assert rumbo == pytest.approx(220, abs=5)                  # cae hacia donde apunta el riel (viento flojo)


def test_el_impacto_simulado_queda_cerca_del_real(vuelo_libre):
    from Paquetes.utils.geografia import distancia_y_rumbo
    _, r = vuelo_libre
    real = r["vuelo_real"]["ultimo"]                           # último punto GPS, a 399 m de altura
    separacion, _ = distancia_y_rumbo(r["lat_impacto"], r["lon_impacto"], real["lat"], real["lon"])
    assert separacion < 600


def test_otro_sitio_no_muestra_el_vuelo_real():
    _, r = volar(launch_lat=19.5, launch_lon=-98.8, launch_alt=2250, sim_max_time=5)
    assert r["vuelo_real"] is None
    assert r["lat_lanzamiento"] == 19.5


def test_la_altitud_del_sitio_sube_el_apogeo(vuelo_libre):
    _, nivel_del_mar = volar(launch_alt=0, atm_delta_t=0, atm_pressure_hpa="")
    assert nivel_del_mar["apogeo"] < vuelo_libre[1]["apogeo"] - 200     # aire más denso, más arrastre


def test_viento_constante_con_direccion_meteorologica():
    # Riel hacia el este (azimut 90°) y viento que viene del este: es viento de frente (-x)
    with contextlib.redirect_stdout(io.StringIO()):
        viento = backend.crear_viento(dict(backend.PARAMS_XITLE, wind_mode=backend.VIENTOS[1], rail_azimuth=90, wind_from=90,
                                           wind_base_speed=6, wind_mean_speed=0, wind_speed_var=0, wind_angle_var=0, wind_seed=1))
    assert viento.vector_en(3.0, 1000.0) == pytest.approx([-6, 0, 0], abs=1e-9)


def test_perfil_de_viento_con_la_altura():
    from Simulador.src.dia_de_vuelo import cargar_condiciones, crear_viento
    condiciones = cargar_condiciones()
    condiciones["viento"].update(rafaga_media_ms=0, rafaga_desviacion_ms=0, variacion_direccion_grados=0)
    viento = crear_viento(condiciones, azimut_riel=220, semilla=1)
    # A 6278 m sobre el sitio (400 hPa): 7.4 m/s que vienen de 210°, casi de frente para un riel a 220°
    arriba = viento.vector_en(40.0, 7673 - 1395).copy()
    assert np.linalg.norm(arriba) == pytest.approx(7.4, rel=1e-6)
    assert arriba[0] == pytest.approx(-7.4 * np.cos(np.deg2rad(10)), rel=1e-6)
    assert np.linalg.norm(viento.vector_en(1.0, 0.0)) == pytest.approx(1.5, rel=1e-6)      # en superficie
    assert viento.vector_en(1.0, 0.0)[2] == 0.0
