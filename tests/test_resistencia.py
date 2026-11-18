"""Comprobación de resistencia: pandeo del fuselaje y flameo de las aletas."""
import math

import numpy as np
import pytest

from Paquetes.PaqueteFisica import resistencia

ACERO = {"E_Pa": 200e9, "nu": 0.3, "resistencia_compresion_Pa": 250e6}


def test_pandeo_clasico():
    # Para nu = 0.3: sigma = 0.605 E t / R
    assert resistencia.esfuerzo_pandeo_clasico(200e9, 0.3, 0.5, 0.001) == pytest.approx(0.605 * 200e9 * 0.001 / 0.5, rel=1e-3)


@pytest.mark.parametrize("r_t, axial, flexion", [(50, 0.679, 0.740), (100, 0.582, 0.661), (400, 0.357, 0.478)])
def test_factores_de_reduccion(r_t, axial, flexion):
    # NASA SP-8007: gamma = 1 - 0.901 (1 - e^-phi), phi = sqrt(R/t)/16; en flexión, 0.731
    assert resistencia.factor_reduccion(r_t, 1.0) == pytest.approx(axial, abs=0.002)
    assert resistencia.factor_reduccion(r_t, 1.0, flexion=True) == pytest.approx(flexion, abs=0.002)
    assert resistencia.factor_reduccion(r_t, 1.0, flexion=True) > resistencia.factor_reduccion(r_t, 1.0)


def test_tubo_a_compresion_pura():
    r_ext, r_int = 0.1, 0.099
    area = math.pi * (r_ext**2 - r_int**2)
    v = resistencia.verificar_tubo(1000.0, 0.0, r_ext, r_int, ACERO, 1.5)
    assert v["sigma_axial"] == pytest.approx(1000.0 / area) and v["sigma_flexion"] == 0
    # Con la carga de pandeo dividida entre el factor de seguridad, el margen es exactamente cero
    limite = resistencia.verificar_tubo(v["carga_pandeo_axial"] / 1.5, 0.0, r_ext, r_int, ACERO, 1.5)
    assert limite["margen_pandeo"] == pytest.approx(0.0, abs=1e-9)
    assert resistencia.verificar_tubo(v["carga_pandeo_axial"], 0.0, r_ext, r_int, ACERO, 1.5)["margen_pandeo"] < 0


def test_tubo_a_flexion_pura():
    r_ext, r_int = 0.1, 0.099
    inercia = math.pi * (r_ext**4 - r_int**4) / 4
    v = resistencia.verificar_tubo(0.0, 500.0, r_ext, r_int, ACERO, 1.5)
    assert v["sigma_flexion"] == pytest.approx(500.0 * r_ext / inercia)
    # La flexión admite más esfuerzo que la compresión antes de pandear
    comprimido = resistencia.verificar_tubo(v["sigma_flexion"] * math.pi * (r_ext**2 - r_int**2), 0.0, r_ext, r_int, ACERO, 1.5)
    assert v["margen_pandeo"] > comprimido["margen_pandeo"]


def test_el_margen_de_resistencia_usa_el_esfuerzo_total():
    v = resistencia.verificar_tubo(2000.0, 300.0, 0.1, 0.099, ACERO, 2.0)
    assert v["margen_resistencia"] == pytest.approx(250e6 / (2.0 * v["sigma_total"]) - 1)


# ---------------------------------------------------------------- flameo
def test_velocidad_de_flameo_formula():
    # Aleta del Xitle: raíz 0.3, punta 0.1, envergadura 0.11, 3 mm, G = 5 GPa, a nivel del mar
    area = 0.5 * (0.3 + 0.1) * 0.11
    ar, conicidad = 0.11**2 / area, 0.1 / 0.3
    denominador = 1.337 * ar**3 * 101325 * (conicidad + 1) / ((ar + 2) * (0.003 / 0.3) ** 3)
    esperado = 340.3 * math.sqrt(5e9 / denominador)
    assert resistencia.velocidad_flameo(5e9, 0.003, 0.3, 0.1, 0.11, 340.3, 101325) == pytest.approx(esperado)
    con_2 = resistencia.velocidad_flameo(5e9, 0.003, 0.3, 0.1, 0.11, 340.3, 101325, factor_2=True)
    assert con_2 == pytest.approx(esperado * math.sqrt(2))


def test_tendencias_del_flameo():
    base = resistencia.velocidad_flameo(5e9, 0.003, 0.3, 0.1, 0.11, 340.0, 90000.0)
    f = lambda **cambios: resistencia.velocidad_flameo(**{**dict(G=5e9, espesor=0.003, cuerda_raiz=0.3, cuerda_punta=0.1,
                                                                  envergadura=0.11, velocidad_sonido=340.0, presion=90000.0), **cambios})
    assert f(espesor=0.006) == pytest.approx(base * 2**1.5)      # crece con el espesor elevado a 3/2
    assert f(G=20e9) == pytest.approx(base * 2)                  # y con la raíz del módulo de cortante
    assert f(presion=45000.0) == pytest.approx(base * math.sqrt(2))   # el aire menos denso lo retrasa
    assert f(envergadura=0.2) < base                             # una aleta más larga flamea antes


def test_comprobacion_del_xitle(vuelo_libre):
    df, r = vuelo_libre
    res = r["resistencia"]
    assert res["factor_seguridad"] == 1.5
    tramos = {f["tramo"]: f for f in res["fuselaje"]}
    assert set(tramos) == {"Coples", "Tubo recuperación", "Transferidor", "Tanque vacío", "Válvulas", "Cámara de combustión"}
    assert "Aluminio" in tramos["Coples"]["material"] and "carbono" in tramos["Tanque vacío"]["material"]
    assert tramos["Tanque vacío"]["espesor"] == pytest.approx(0.0015)
    # Las cargas de vuelo quedan muy lejos de pandear el fuselaje
    assert min(f["margen_pandeo"] for f in res["fuselaje"]) > 10
    assert all(f["compresion"] > 0 and f["momento"] > 0 for f in res["fuselaje"])

    flameo = res["flameo"]
    assert flameo["velocidad_cohete"] == pytest.approx(r["vel_max"], rel=0.05)     # lo más crítico, cerca de la velocidad máxima
    assert flameo["cociente"] == pytest.approx(flameo["velocidad_flameo"] / flameo["velocidad_cohete"])
    assert flameo["margen"] == pytest.approx(flameo["cociente"] / 1.5 - 1)
    # Con el espesor mínimo, el cociente es justo el factor de seguridad
    assert (flameo["espesor_minimo"] / flameo["espesor"]) ** 1.5 * flameo["cociente"] == pytest.approx(1.5)
    assert any("Aletas" in linea for linea in resistencia.texto_resumen(res))


# ---------------------------------------------------------------- materiales elegidos en la interfaz
def test_materiales_por_defecto_del_xitle():
    from Simulador.GUI import backend
    p = backend.PARAMS_XITLE
    assert p["coples_material"] == "Aluminio 6061-T6"
    assert all(p[f"{pref}_material"] == "Fibra de carbono 0/90" for pref in ("tubo_recup", "transfer", "tanque_vacio", "valvulas", "cc"))
    assert p["fin_material"] == "Fibra de carbono 0/90" and p["fin_thickness"] == 0.003      # aletas: tejido 0/90 de 3 mm
    estructura = backend.estructura_desde_parametros(p)
    assert estructura["fuselaje"]["material_por_tramo"]["Coples"] == "aluminio_6061_T6"
    assert estructura["aletas"] == {**estructura["aletas"], "material": "fibra_de_carbono", "espesor_m": 0.003}
    assert set(backend.MATERIALES.values()) == set(estructura["materiales"])


def test_cambiar_el_material_cambia_la_comprobacion(vuelo_libre):
    from conftest import volar
    base = vuelo_libre[1]["resistencia"]
    _, otro = volar(fin_material="Fibra de carbono casi isótropa (0/90 y ±45)", fin_thickness=0.004, tanque_vacio_material="Aluminio 6061-T6")
    r = otro["resistencia"]
    # Flameo: crece con la raíz de G y con el espesor elevado a 3/2
    esperado = base["flameo"]["velocidad_flameo"] * (18e9 / 5e9) ** 0.5 * (4 / 3) ** 1.5
    assert r["flameo"]["velocidad_flameo"] == pytest.approx(esperado, rel=0.01)
    assert r["flameo"]["margen"] > 0 > base["flameo"]["margen"]
    tanque = {f["tramo"]: f for f in r["fuselaje"]}["Tanque vacío"]
    assert "Aluminio" in tanque["material"]
    # Las cargas no dependen del material
    assert otro["cargas"]["maximos"]["compresion"]["valor"] == pytest.approx(vuelo_libre[1]["cargas"]["maximos"]["compresion"]["valor"], rel=1e-6)


def test_material_desconocido():
    from Simulador.GUI import backend
    with pytest.raises(ValueError, match="Material desconocido"):
        backend.validar_parametros(dict(backend.PARAMS_XITLE, fin_material="Madera balsa"))
    with pytest.raises(ValueError, match="espesor"):
        backend.validar_parametros(dict(backend.PARAMS_XITLE, fin_thickness=0))
