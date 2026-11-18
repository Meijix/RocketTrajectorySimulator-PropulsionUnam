"""Cargas estructurales: fuerza axial, cortante y momento flector a lo largo del cohete."""
import contextlib
import io

import numpy as np
import pytest

from conftest import volar
from Paquetes.PaqueteFisica import cargas
from Simulador.GUI import backend


# ---------------------------------------------------------------- viga con solución analítica
L, MASA = 4.0, 40.0
BORDES = np.linspace(0, L, 2001)
DM = np.full(2000, MASA / 2000)
U = BORDES / L


def test_viga_empujada_desde_la_cola():
    # Acelerada por un empuje T en la cola: cada sección empuja la masa que tiene delante, compresión = T·u
    r = cargas.cargas_viga(BORDES, DM, [(L, 500.0)], [])
    assert r["compresion"][1:-1] == pytest.approx(500.0 * U[1:-1])
    assert r["a_axial"] == pytest.approx(500.0 / MASA)
    assert np.abs(r["cortante"]).max() == 0 and np.abs(r["momento"]).max() == 0


def test_viga_con_arrastre_en_la_nariz_y_empuje_en_la_cola():
    # Empuje T en la cola y arrastre D en la nariz: compresión = D + (T - D)·u
    r = cargas.cargas_viga(BORDES, DM, [(0.0, -100.0), (L, 500.0)], [])
    assert r["compresion"][1:-1] == pytest.approx(100.0 + 400.0 * U[1:-1])


def test_viga_apoyada_en_su_base():
    # En reposo vertical sobre su base: cada sección carga el peso de lo que tiene encima
    g = 9.81
    r = cargas.cargas_viga(BORDES, DM, [(L, MASA * g)], [], g_axial=-g)
    assert r["a_axial"] == pytest.approx(0.0, abs=1e-12)
    assert r["compresion"][1:-1] == pytest.approx(MASA * g * U[1:-1])


def test_viga_libre_con_fuerza_transversal_en_la_punta():
    # Solución exacta de una viga uniforme libre: |V| = F|1 - 4u + 3u²|, |M| = F·L·u(1 - u)², máximo 4FL/27 en u = 1/3
    F = 100.0
    r = cargas.cargas_viga(BORDES, DM, [], [(0.0, F)])
    assert np.abs(r["cortante"][1:-1]) == pytest.approx(F * np.abs(1 - 4 * U[1:-1] + 3 * U[1:-1] ** 2), abs=0.1)
    assert np.abs(r["momento"]) == pytest.approx(F * L * U * (1 - U) ** 2, abs=0.05)
    assert np.abs(r["momento"]).max() == pytest.approx(4 * F * L / 27, rel=1e-4)
    assert r["acel_angular"] == pytest.approx(F * (L / 2) / (MASA * L**2 / 12), rel=1e-5)


def test_la_gravedad_sola_no_carga_una_viga_en_caida_libre():
    r = cargas.cargas_viga(BORDES, DM, [], [], g_axial=-5.0, g_transversal=-8.0)
    for clave in ("compresion", "cortante", "momento"):
        assert np.abs(r[clave]).max() == pytest.approx(0.0, abs=1e-9)


def test_las_cargas_se_anulan_en_los_extremos():
    r = cargas.cargas_viga(BORDES, DM, [(0.0, -80.0), (3.9, 600.0)], [(0.3, 40.0), (3.7, -25.0), (4.0, 5.0)],
                           g_axial=-9.0, g_transversal=-3.0, omega=0.4)
    for clave in ("compresion", "cortante", "momento"):
        assert r[clave][0] == 0.0
        assert r[clave][-1] == pytest.approx(0.0, abs=1e-8)


# ---------------------------------------------------------------- el cohete
@pytest.fixture(scope="module")
def cohete():
    with contextlib.redirect_stdout(io.StringIO()):
        return backend.construir_cohete(backend.PARAMS_XITLE, backend.RUTAS_XITLE)


@pytest.mark.parametrize("t", [0.0, 6.0, 30.0])
def test_la_distribucion_de_masa_respeta_masa_y_centro_de_gravedad(cohete, t):
    cohete.actualizar_masa(t)
    bordes = np.linspace(0, cargas.longitud_viga(cohete), 801)
    dm = cargas.distribucion_de_masa(cohete, bordes)
    centros = 0.5 * (bordes[1:] + bordes[:-1])
    s_cg = (dm * centros).sum() / dm.sum()
    assert dm.min() >= 0
    assert dm.sum() == pytest.approx(cohete.masa, rel=1e-9)
    assert s_cg == pytest.approx(cohete.CG[2], abs=0.01)
    assert (dm * (centros - s_cg) ** 2).sum() == pytest.approx(cohete.Ix, rel=0.02)


def test_la_viga_llega_hasta_el_final_del_cohete(cohete):
    # En el Xitle II las aletas terminan donde empieza el boattail, así que la viga acaba en el boattail
    assert cohete.componentes["Aletas"].bottom[2] == pytest.approx(4.146)
    assert cargas.longitud_viga(cohete) == pytest.approx(cohete.longtotal) == pytest.approx(4.266)


def test_la_viga_se_alarga_si_las_aletas_sobresalen(cohete):
    aletas = cohete.componentes["Aletas"]
    original = aletas.posicion.copy()
    try:
        aletas.posicion = original + [0.0, 0.0, 0.3]      # raíz 0.3 m más atrás: sobresale del boattail
        assert cargas.longitud_viga(cohete) > cohete.longtotal
    finally:
        aletas.posicion = original


# ---------------------------------------------------------------- el vuelo
@pytest.fixture(scope="module")
def envolvente(vuelo_libre):
    return vuelo_libre[1]["cargas"]


def test_compresion_maxima_cerca_del_empuje_maximo(envolvente, cohete):
    m = envolvente["maximos"]["compresion"]
    empuje_max = cohete._empuje.max()
    assert 0.9 * empuje_max < m["valor"] < empuje_max           # algo menos: la cola también se acelera
    assert m["s"] == pytest.approx(cohete.longtotal, abs=0.05)  # justo delante de donde entra el empuje
    assert m["t"] == pytest.approx(cohete._t_empuje[cohete._empuje.argmax()], abs=0.2)


def test_la_compresion_crece_hacia_la_cola_en_el_empuje_maximo(envolvente, cohete):
    caso = envolvente["casos"]["Máxima compresión"]
    dentro = envolvente["s"] < cohete.longtotal - 0.01
    assert np.all(np.diff(caso["compresion"][dentro]) >= -1e-6)


def test_cierre_en_todos_los_casos(envolvente):
    for grupo in (envolvente, envolvente["con_rafaga"]):
        for caso in grupo["casos"].values():
            for clave in ("compresion", "cortante", "momento"):
                assert caso[clave][-1] == pytest.approx(0.0, abs=1e-6)


def test_la_rafaga_aumenta_la_flexion_y_no_la_compresion(envolvente):
    nominal, rafaga = envolvente["maximos"], envolvente["con_rafaga"]["maximos"]
    assert rafaga["momento"]["valor"] > 3 * nominal["momento"]["valor"]
    assert rafaga["cortante"]["valor"] > 3 * nominal["cortante"]["valor"]
    assert rafaga["compresion"]["valor"] == pytest.approx(nominal["compresion"]["valor"], rel=0.01)
    # La flexión máxima con ráfaga ocurre cerca de la máxima presión dinámica
    assert rafaga["momento"]["t"] == pytest.approx(envolvente["casos"]["Máxima presión dinámica"]["t"], abs=1.5)


def test_en_el_riel_solo_hay_carga_axial(envolvente):
    # Hasta la salida del riel el momento es cero: el máximo de cada sección ocurre después
    assert envolvente["t_momento"][envolvente["momento_max"] > 0].min() >= envolvente["casos"]["Salida del riel"]["t"] - 1e-9


def test_antes_de_despegar_la_base_sostiene_el_peso(cohete):
    from Paquetes.PaqueteFisica.atmosfera import atmosfera
    from Paquetes.PaqueteFisica.viento import Viento
    from Paquetes.PaqueteFisica.vuelo import Vuelo
    vuelo = Vuelo(cohete, atmosfera(), Viento(vel_base=0, vel_mean=0, vel_var=0, var_ang=0, semilla=1))
    theta = np.deg2rad(83)
    c = cargas.cargas_en_instante(vuelo, 0.0, np.array([0, 0, 0, 0, 0, 0, theta, 0.0]))
    assert c["en_riel"] and c["a_axial"] == pytest.approx(0.0, abs=1e-9)
    # Justo delante de la base, la compresión es el peso (su componente a lo largo del riel) menos el empuje inicial
    i = np.searchsorted(c["s"], cohete.longtotal) - 1
    peso_axial = c["masa"] * 9.80665 * np.sin(theta)
    assert c["compresion"][i] == pytest.approx(peso_axial, rel=0.02)
    assert np.abs(c["momento"]).max() == 0


def test_sin_rafaga_no_se_calcula_el_caso():
    _, r = volar(load_gust=0, sim_max_time=12)
    assert r["cargas"]["con_rafaga"] is None


def test_tabla_y_texto_de_la_envolvente(envolvente):
    from Simulador.Visualizacion.graficas_cargas import tabla_envolvente, texto_maximos
    tabla = tabla_envolvente(envolvente)
    assert len(tabla) == len(envolvente["s"]) and "Momento flector máx con ráfaga [N m]" in tabla.columns
    assert any("ráfaga" in linea for linea in texto_maximos(envolvente))
