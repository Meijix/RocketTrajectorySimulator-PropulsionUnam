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
        estado0 = np.array([0, 0, 0, 0, 0, 0, np.deg2rad(83), 0], dtype=float)
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


# ---------------------------------------------------------------- física: riel, masa, inercia
def test_en_el_riel_el_cohete_no_se_hunde_ni_se_sale_del_eje():
    vuelo, tiempos, sim = _vuelo_propio("RungeKutta4", 1.0, 0.005, 0.005)
    eje = np.array([np.cos(np.deg2rad(83)), 0.0, np.sin(np.deg2rad(83))])
    posiciones = sim[:, 0:3]
    recorrido = posiciones @ eje
    fuera_del_eje = np.linalg.norm(posiciones - np.outer(recorrido, eje), axis=1)
    assert np.linalg.norm(posiciones[-1]) < 10.0                 # sigue en el riel de 10 m
    assert sim[:, 2].min() >= 0.0                                # nunca baja del suelo
    assert fuera_del_eje.max() < 1e-9                            # solo se desliza a lo largo del eje
    assert np.all(np.diff(recorrido) >= -1e-12)                  # no retrocede
    assert sim[:, 6] == pytest.approx(np.deg2rad(83))            # no gira
    assert recorrido[tiempos <= 0.1].max() == pytest.approx(0.0, abs=1e-9)   # el empuje aún no vence al peso


def test_el_propelente_se_consume_durante_todo_el_quemado(vuelo_libre):
    df, r = vuelo_libre
    masa = lambda t: float(np.interp(t, df["t"], df["masa"]))
    consumido = masa(0) - masa(r["t_MECO"] + 1)
    assert consumido == pytest.approx(15.07, abs=0.05)
    # A la mitad del quemado aún queda propelente (antes se acababa a los 10 s de 21.6 s)
    assert masa(10) - masa(r["t_MECO"] + 1) > 1.0
    assert masa(20) - masa(r["t_MECO"] + 1) > 0.05


def test_masa_proporcional_al_impulso():
    cohete = backend.construir_cohete(backend.PARAMS_XITLE, backend.RUTAS_XITLE)
    assert cohete.masa_segun_impulso                              # tabla de masa de 10 s, empuje de 21.6 s
    trapecio = getattr(np, "trapezoid", None) or np.trapz
    t, F = cohete._t_empuje, cohete._empuje
    for instante in (2.0, 8.0, 15.0):
        cohete.actualizar_masa(instante)
        fraccion = trapecio(np.append(F[t < instante], np.interp(instante, t, F)), np.append(t[t < instante], instante)) / cohete.I_total
        esperado = cohete._masa_oxi[0] + fraccion * (cohete._masa_oxi[-1] - cohete._masa_oxi[0])
        assert cohete.componentes["oxidante"].masa == pytest.approx(esperado, rel=1e-3)


def test_la_inercia_baja_al_consumirse_el_propelente():
    cohete = backend.construir_cohete(backend.PARAMS_XITLE, backend.RUTAS_XITLE)
    cohete.actualizar_masa(0.0)
    inercia_llena, propia_llena = cohete.Ix, cohete.componentes["oxidante"].Ix
    cohete.actualizar_masa(30.0)
    assert cohete.Ix < inercia_llena
    assert cohete.componentes["oxidante"].Ix < 0.1 * propia_llena   # la inercia propia sigue a la masa


def test_centroide_de_las_aletas():
    from Paquetes.PaqueteFisica.componentes import Aletas
    # Aleta rectangular (sin barrido): el centroide está a media cuerda
    rect = Aletas("a", 1.0, np.zeros(3), 0.152, 4, 0.1, 0.2, 0.2, 0.0, 0.0)
    assert rect.CG[2] == pytest.approx(0.1)
    # Aleta triangular con la punta retrasada una cuerda: centroide a 2/3 de la cuerda raíz
    tri = Aletas("a", 1.0, np.zeros(3), 0.152, 4, 0.1, 0.3, 1e-9, 0.3, 0.0)
    assert tri.CG[2] == pytest.approx(0.2, abs=1e-6)


def test_la_normal_restaura_con_cualquier_angulo(vuelo_libre):
    # El signo de la fuerza normal depende de sin(alpha): alpha y alpha + 360° dan lo mismo
    from Paquetes.PaqueteFisica.atmosfera import atmosfera
    from Paquetes.PaqueteFisica.viento import Viento
    from Paquetes.PaqueteFisica.vuelo import Vuelo
    with contextlib.redirect_stdout(io.StringIO()):
        cohete = backend.construir_cohete(backend.PARAMS_XITLE, backend.RUTAS_XITLE)
    vuelo = Vuelo(cohete, atmosfera(), Viento(vel_base=0, vel_mean=0, vel_var=0, var_ang=0, semilla=1))
    v_rel, pos = np.array([100.0, 0.0, 0.0]), np.array([0.0, 0.0, 1000.0])
    _, normal = vuelo.calc_aero(pos, v_rel, np.deg2rad(5))
    _, normal_vuelta = vuelo.calc_aero(pos, v_rel, np.deg2rad(5 + 360))
    assert normal[2] > 0 and normal[0] == pytest.approx(0.0, abs=1e-9)     # nariz arriba: sustentación hacia arriba
    assert normal_vuelta == pytest.approx(normal)


# ---------------------------------------------------------------- amortiguamiento del cabeceo
def _vuelo_de_prueba():
    from Paquetes.PaqueteFisica.atmosfera import atmosfera
    from Paquetes.PaqueteFisica.viento import Viento
    from Paquetes.PaqueteFisica.vuelo import Vuelo
    with contextlib.redirect_stdout(io.StringIO()):
        cohete = backend.construir_cohete(backend.PARAMS_XITLE, backend.RUTAS_XITLE)
    return Vuelo(cohete, atmosfera(), Viento(vel_base=0, vel_mean=0, vel_var=0, var_ang=0, semilla=1))


def test_el_amortiguamiento_se_opone_al_giro():
    vuelo = _vuelo_de_prueba()
    vuelo.vehiculo.actualizar_masa(30.0)                       # motor apagado: solo amortiguamiento aerodinámico
    v_rel = np.array([200.0, 0.0, 0.0])
    estado = lambda omega: np.array([0, 0, 1000.0, 200.0, 0, 0, 0.0, omega])
    assert vuelo.torca_amortiguamiento(30.0, estado(0.5), v_rel) < 0
    assert vuelo.torca_amortiguamiento(30.0, estado(-0.5), v_rel) > 0
    assert vuelo.torca_amortiguamiento(30.0, estado(0.0), v_rel) == 0
    # Proporcional a omega y a la velocidad del aire
    assert vuelo.torca_amortiguamiento(30.0, estado(1.0), v_rel) == pytest.approx(2 * vuelo.torca_amortiguamiento(30.0, estado(0.5), v_rel))
    assert vuelo.torca_amortiguamiento(30.0, estado(0.5), 2 * v_rel) == pytest.approx(2 * vuelo.torca_amortiguamiento(30.0, estado(0.5), v_rel))


def test_formula_del_amortiguamiento_aerodinamico():
    vuelo = _vuelo_de_prueba()
    cohete = vuelo.vehiculo
    cohete.actualizar_masa(30.0)
    # Suma de CN_i (x_i - x_CG)^2 hecha a mano con nariz, aletas y boattail
    suma = sum(c.CN * (c.posicion[2] + c.CP[2] - cohete.CG[2]) ** 2
               for c in (cohete.componentes["Nariz"], cohete.componentes["Aletas"], cohete.componentes["Boattail"]))
    assert cohete.coef_amortiguamiento_aero() == pytest.approx(suma)
    assert suma > 0
    _, rho, _, _ = vuelo.atmosfera.calc_propiedades(1000.0)
    esperado = -0.5 * rho * 200.0 * cohete.A * suma * 0.5
    assert vuelo.torca_amortiguamiento(30.0, np.array([0, 0, 1000.0, 200.0, 0, 0, 0.0, 0.5]), np.array([200.0, 0, 0])) == pytest.approx(esperado)


def test_amortiguamiento_por_el_chorro_solo_con_el_motor_encendido():
    vuelo = _vuelo_de_prueba()
    cohete = vuelo.vehiculo
    en_reposo = np.zeros(3)                                    # sin aire relativo: solo queda el chorro
    estado = np.array([0, 0, 1000.0, 0, 0, 0, 0.0, 0.5])
    cohete.actualizar_masa(5.0)
    brazo = cohete.longtotal - cohete.CG[2]
    assert vuelo.torca_amortiguamiento(5.0, estado, en_reposo) == pytest.approx(-cohete.flujo_masico(5.0) * brazo ** 2 * 0.5)
    assert cohete.flujo_masico(5.0) > 0.5
    cohete.actualizar_masa(30.0)
    assert vuelo.torca_amortiguamiento(30.0, estado, en_reposo) == 0
    # El flujo másico integrado es la masa de propelente consumida
    tiempos = np.linspace(0, cohete.t_MECO, 20001)
    trapecio = getattr(np, "trapezoid", None) or np.trapz
    assert trapecio([cohete.flujo_masico(t) for t in tiempos], tiempos) == pytest.approx(15.07, abs=0.02)


def test_el_amortiguamiento_atenua_las_oscilaciones():
    amplitudes = {}
    for activo in (False, True):
        vuelo = _vuelo_de_prueba()
        vuelo.amortiguamiento = activo
        with contextlib.redirect_stdout(io.StringIO()):
            salida = vuelo.simular_vuelo(np.array([0, 0, 0, 0, 0, 0, np.deg2rad(83), 0], dtype=float), 12.0, 0.01, 0.01, "RK45")
        t, omega = np.array(salida[0]), np.array(salida[1])[:, 7]
        tramo = (t > 6) & (t < 12)
        amplitudes[activo] = omega[tramo].max() - omega[tramo].min()
    assert amplitudes[True] < 0.7 * amplitudes[False]


# ---------------------------------------------------------------- recuperación en dos etapas
@pytest.fixture(scope="module")
def vuelo_dos_etapas():
    return volar(recovery=backend.RECUPERACION[2])


def test_dos_etapas_abre_el_principal_a_su_altura(vuelo_dos_etapas):
    df, r = vuelo_dos_etapas
    assert r["t_apogeo"] < r["t_principal"] < r["t_impacto"]
    assert r["altura_principal"] == pytest.approx(450.0, abs=0.5)
    # Antes de abrirse baja con el drogue; después, mucho más despacio
    assert 25 < r["vel_antes_principal"] < 45
    assert r["vel_impacto"] < 0.5 * r["vel_antes_principal"]
    assert r["vel_impacto"] < 15


def test_dos_etapas_frente_a_solo_drogue(vuelo_paracaidas, vuelo_dos_etapas):
    solo_drogue, dos_etapas = vuelo_paracaidas[1], vuelo_dos_etapas[1]
    assert solo_drogue["t_principal"] is None
    assert dos_etapas["apogeo"] == pytest.approx(solo_drogue["apogeo"], rel=1e-3)
    assert dos_etapas["vel_impacto"] < 0.5 * solo_drogue["vel_impacto"]       # aterriza más despacio
    assert dos_etapas["t_impacto"] > solo_drogue["t_impacto"]                 # y tarda más
    # Hasta que se abre el principal las dos trayectorias son la misma
    t = dos_etapas["t_principal"] - 1.0
    z = lambda vuelo: float(np.interp(t, vuelo[0]["t"], vuelo[0]["z"]))
    assert z(vuelo_dos_etapas) == pytest.approx(z(vuelo_paracaidas), abs=1.0)


def test_velocidad_terminal_con_el_principal(vuelo_dos_etapas):
    # Al llegar al suelo el peso se equilibra con el arrastre de los dos paracaídas y del cohete
    df, r = vuelo_dos_etapas
    p = backend.PARAMS_XITLE
    cd_area = p["drogue_cd"] * np.pi * p["drogue_chute_diam"] ** 2 / 4 + p["main_cd"] * np.pi * p["main_chute_diam"] ** 2 / 4
    masa, rho = float(df["masa"].iloc[-1]), 1.012                     # densidad en el sitio ese día
    terminal = np.sqrt(2 * masa * 9.79 / (rho * cd_area))
    assert r["vel_impacto"] == pytest.approx(terminal, rel=0.08)


@pytest.mark.parametrize("integrador", ["RK45", "RungeKutta4"])
def test_dos_etapas_con_otros_integradores(vuelo_dos_etapas, integrador):
    with contextlib.redirect_stdout(io.StringIO()):
        _, otro = volar(recovery=backend.RECUPERACION[2], integrator=integrador)
    assert otro["t_principal"] == pytest.approx(vuelo_dos_etapas[1]["t_principal"], abs=0.1)
    assert otro["vel_impacto"] == pytest.approx(vuelo_dos_etapas[1]["vel_impacto"], rel=0.02)


def test_principal_sobre_el_apogeo_se_abre_en_el_apogeo():
    _, r = volar(recovery=backend.RECUPERACION[2], main_deploy_alt=9000)
    assert r["t_principal"] == pytest.approx(r["t_apogeo"])
    # Bajar 7 km con el principal tarda más de 400 s: con el tiempo máximo de 1000 s sí llega al suelo
    assert 400 < r["t_impacto"] < 1000
    assert r["vel_impacto"] < 15


def test_tiempo_maximo_por_defecto():
    from Simulador.src import condiciones_init
    assert backend.PARAMS_XITLE["sim_max_time"] == 1000 and condiciones_init.t_max == 1000


def test_vuelo_libre_no_abre_paracaidas(vuelo_libre):
    assert vuelo_libre[1]["t_principal"] is None and not vuelo_libre[1]["paracaidas"]


def test_validacion_del_paracaidas_principal():
    with pytest.raises(ValueError, match="principal"):
        backend.validar_parametros(dict(backend.PARAMS_XITLE, recovery=backend.RECUPERACION[2], main_deploy_alt=0))


# ---------------------------------------------------------------- vaciado del tanque de oxidante
def test_la_columna_de_oxidante_se_acorta_hacia_el_fondo():
    cohete = backend.construir_cohete(backend.PARAMS_XITLE, backend.RUTAS_XITLE)
    oxidante = cohete.componentes["oxidante"]
    p = backend.PARAMS_XITLE
    fondo = p["oxidante_pos_z"] + p["oxidante_len"]

    cohete.actualizar_masa(0.0)                                   # tanque lleno
    masa_llena = oxidante.masa
    assert oxidante.long == pytest.approx(p["oxidante_len"])
    assert oxidante.posicion[2] == pytest.approx(p["oxidante_pos_z"])
    cg_lleno, inercia_llena = oxidante.posicion[2] + oxidante.CG[2], oxidante.Ix

    cohete.actualizar_masa(5.0)                                   # a medio vaciar
    fraccion = oxidante.masa / masa_llena
    assert 0.3 < fraccion < 0.8
    assert oxidante.long == pytest.approx(p["oxidante_len"] * fraccion)          # longitud proporcional a la masa
    assert oxidante.posicion[2] + oxidante.long == pytest.approx(fondo)          # el fondo no se mueve
    assert oxidante.posicion[2] + oxidante.CG[2] == pytest.approx(fondo - oxidante.long / 2)
    assert oxidante.posicion[2] + oxidante.CG[2] > cg_lleno                      # el centro baja hacia la cola
    # Inercia propia de un cilindro macizo con la masa y la longitud actuales
    radio = p["oxidante_diam"] / 2
    assert oxidante.Ix == pytest.approx(oxidante.masa * (3 * radio**2 + oxidante.long**2) / 12)
    assert oxidante.Ix < inercia_llena * fraccion                 # baja más rápido que la masa


def test_el_vaciado_del_tanque_no_cambia_la_masa_total():
    cohete = backend.construir_cohete(backend.PARAMS_XITLE, backend.RUTAS_XITLE)
    cohete.actualizar_masa(8.0)
    assert cohete.masa == pytest.approx(sum(c.masa for c in cohete.componentes.values()))
    cg = sum(c.masa * (c.posicion[2] + c.CG[2]) for c in cohete.componentes.values()) / cohete.masa
    assert cohete.CG[2] == pytest.approx(cg)


def test_el_cohete_sigue_siendo_estable_durante_el_quemado(vuelo_libre):
    df, r = vuelo_libre
    assert df["margen"].min() > 1.0


# ---------------------------------------------------------------- grano de combustible
def test_el_canal_del_grano_se_ensancha_al_quemarse():
    cohete = backend.construir_cohete(backend.PARAMS_XITLE, backend.RUTAS_XITLE)
    grano = cohete.componentes["grano"]
    p = backend.PARAMS_XITLE
    r_ext, r_int0 = p["grano_outer_diam"] / 2, p["grano_inner_diam"] / 2
    assert p["grano_inner_diam"] == 0.0334 and cohete.grano_con_regresion

    cohete.actualizar_masa(0.0)
    masa_inicial = grano.masa
    assert grano.diam_int == pytest.approx(p["grano_inner_diam"])
    diametros = []
    for t in (2.0, 5.0, 10.0, 30.0):
        cohete.actualizar_masa(t)
        # La masa es proporcional al área de la sección: r_ext² - r_int²
        assert (r_ext**2 - grano.rad_int**2) / (r_ext**2 - r_int0**2) == pytest.approx(grano.masa / masa_inicial)
        # Inercia propia de un cilindro hueco con el canal actual
        assert grano.Ix == pytest.approx(grano.masa * (3 * (grano.rad_int**2 + r_ext**2) + p["grano_length"]**2) / 12)
        diametros.append(grano.diam_int)
    assert diametros == sorted(diametros)                         # el canal solo crece
    assert p["grano_inner_diam"] < diametros[-1] < p["grano_outer_diam"]
    assert grano.diam_ext == p["grano_outer_diam"] and grano.long == p["grano_length"]   # exterior y longitud fijos


def test_grano_con_diametros_imposibles():
    with pytest.raises(ValueError, match="Grano"):
        backend.validar_parametros(dict(backend.PARAMS_XITLE, grano_inner_diam=0.334))
    with pytest.raises(ValueError, match="Coples"):
        backend.validar_parametros(dict(backend.PARAMS_XITLE, coples_diam_int=0.2))


# ---------------------------------------------------------------- inflado de los paracaídas
def test_tiempo_de_llenado():
    from Paquetes.PaqueteFisica.cohete import Parachute
    paracaidas = Parachute(2.0, 1.8)                              # por defecto: circular plano macizo
    diametro = np.sqrt(4 * 1.8 / np.pi)
    assert paracaidas.diametro == pytest.approx(diametro)
    assert (paracaidas.k_llenado, paracaidas.exponente, paracaidas.exponente_velocidad) == (8.0, 6.0, 0.9)
    # t = 8 D / v^0.9 con D en pies y v en pies por segundo
    pie = 0.3048
    assert paracaidas.tiempo_llenado(34.0) == pytest.approx(8 * (diametro / pie) / (34.0 / pie) ** 0.9)
    assert paracaidas.tiempo_llenado(34.0) == pytest.approx(0.571, abs=0.005)
    assert paracaidas.tiempo_llenado(68.0) < paracaidas.tiempo_llenado(34.0)       # más rápido, se llena antes
    assert paracaidas.tiempo_llenado(0.0) == Parachute.T_LLENADO_MAX
    assert Parachute(2.0, 1.8, k_llenado=0).tiempo_llenado(34.0) == 0.0
    # Con exponente de velocidad 1 la fórmula no depende de las unidades: t = k D / v
    assert Parachute(2.0, 1.8, exponente_velocidad=1.0).tiempo_llenado(34.0) == pytest.approx(8 * diametro / 34.0)


def test_area_de_arrastre_durante_el_llenado():
    from Paquetes.PaqueteFisica.cohete import Parachute
    paracaidas, completo = Parachute(2.0, 1.8), 2.0 * 1.8
    assert paracaidas.area_arrastre(-0.1, 0.4) == 0.0
    assert paracaidas.area_arrastre(0.0, 0.4) == 0.0
    assert paracaidas.area_arrastre(0.2, 0.4) == pytest.approx(completo / 64)     # a la mitad del llenado, (1/2)^6
    assert paracaidas.area_arrastre(0.4, 0.4) == pytest.approx(completo)
    assert paracaidas.area_arrastre(5.0, 0.4) == pytest.approx(completo)
    assert paracaidas.area_arrastre(0.0, 0.0) == pytest.approx(completo)          # apertura instantánea
    areas = [paracaidas.area_arrastre(t, 0.4) for t in np.linspace(0, 0.5, 30)]
    assert areas == sorted(areas)
    assert Parachute(2.0, 1.8, exponente=2).area_arrastre(0.2, 0.4) == pytest.approx(completo / 4)


@pytest.fixture(scope="module")
def dos_etapas_instantaneo():
    return volar(recovery=backend.RECUPERACION[2], drogue_fill=0, main_fill=0)


def test_el_inflado_reduce_la_carga_de_apertura(vuelo_dos_etapas, dos_etapas_instantaneo):
    con_inflado, instantaneo = vuelo_dos_etapas[1], dos_etapas_instantaneo[1]
    assert instantaneo["llenado_principal"] == 0.0
    # Tiempo de llenado del principal: 8·D/v^0.9 (en pies) con la velocidad a la que bajaba con el drogue
    pie = 0.3048
    assert con_inflado["llenado_principal"] == pytest.approx(8 * (1.514 / pie) / (con_inflado["vel_antes_principal"] / pie) ** 0.9, rel=0.03)
    assert 0.4 < con_inflado["llenado_principal"] < 0.8
    assert con_inflado["fuerza_apertura_principal"] < 0.9 * instantaneo["fuerza_apertura_principal"]
    assert con_inflado["g_apertura_principal"] > 1.0              # aun así frena más que la gravedad


def test_carga_de_apertura_instantanea(dos_etapas_instantaneo):
    # Sin inflado, la fuerza máxima es la presión dinámica al abrirse por el Cd·A completo
    df, r = dos_etapas_instantaneo
    p = backend.PARAMS_XITLE
    cd_area = p["drogue_cd"] * np.pi * p["drogue_chute_diam"] ** 2 / 4 + p["main_cd"] * np.pi * p["main_chute_diam"] ** 2 / 4
    rho = 1.012 * (1 - 450 / 9000)                                # densidad a 450 m sobre el sitio, aproximada
    assert r["fuerza_apertura_principal"] == pytest.approx(0.5 * rho * r["vel_antes_principal"] ** 2 * cd_area, rel=0.06)


def test_el_inflado_casi_no_cambia_la_trayectoria(vuelo_dos_etapas, dos_etapas_instantaneo):
    con_inflado, instantaneo = vuelo_dos_etapas[1], dos_etapas_instantaneo[1]
    assert con_inflado["apogeo"] == pytest.approx(instantaneo["apogeo"], rel=1e-6)
    assert con_inflado["t_impacto"] == pytest.approx(instantaneo["t_impacto"], abs=1.0)
    assert con_inflado["vel_impacto"] == pytest.approx(instantaneo["vel_impacto"], rel=0.02)
    assert con_inflado["distancia"] == pytest.approx(instantaneo["distancia"], abs=20)


def test_la_fuerza_del_paracaidas_es_cero_antes_de_abrirse(vuelo_dos_etapas):
    df, r = vuelo_dos_etapas
    assert df[df["t"] < r["t_apogeo"] - 0.1]["fuerza_paracaidas"].max() == 0.0
    assert df[df["t"] > r["t_apogeo"] + 5]["fuerza_paracaidas"].min() > 0.0
