"""Modelo atmosférico contra la Atmósfera Estándar Internacional (ISA 1976)."""
import pytest

from Paquetes.PaqueteFisica.atmosfera import atmosfera

R_TIERRA = 6371000

# altitud geopotencial (m): (temperatura K, presión Pa, densidad kg/m3)
ISA = {
    0: (288.15, 101325.0, 1.2250),
    5000: (255.65, 54019.9, 0.73612),
    11000: (216.65, 22632.1, 0.36392),
    20000: (216.65, 5474.89, 0.088035),
    32000: (228.65, 868.019, 0.013225),
}


def propiedades(h_geopotencial):
    z = h_geopotencial * R_TIERRA / (R_TIERRA - h_geopotencial)   # altitud geométrica equivalente
    return atmosfera().calc_propiedades(z)


@pytest.mark.parametrize("h", ISA)
def test_isa_hasta_32_km(h):
    T, rho, p, cs = propiedades(h)
    T_ref, p_ref, rho_ref = ISA[h]
    assert T == pytest.approx(T_ref, rel=1e-3)
    assert p == pytest.approx(p_ref, rel=5e-3)
    assert rho == pytest.approx(rho_ref, rel=5e-3)
    assert cs == pytest.approx((1.4 * 287.05287 * T_ref) ** 0.5, rel=1e-3)


def test_la_densidad_decrece_con_la_altura():
    alturas = range(0, 45000, 1000)
    densidades = [atmosfera().calc_propiedades(z)[1] for z in alturas]
    assert all(a > b for a, b in zip(densidades, densidades[1:]))


@pytest.mark.parametrize("h, rho_ref", [(47000, 1.4275e-3), (51000, 8.616e-4), (71000, 6.421e-5)])
def test_isa_sobre_47_km(h, rho_ref):
    # Antes la densidad estaba mal por encima de 47 km (hasta 26 veces mayor a 80 km)
    _, rho, _, _ = propiedades(h)                       # h: altura geopotencial (bases de capa)
    assert rho == pytest.approx(rho_ref, rel=0.01)


@pytest.mark.parametrize("z, rho_ref", [(60000, 3.097e-4), (80000, 1.846e-5)])
def test_isa_en_altura_geometrica(z, rho_ref):
    # Valores de la tabla de la atmósfera estándar de 1976 en altura geométrica
    assert atmosfera().calc_propiedades(z)[1] == pytest.approx(rho_ref, rel=0.01)


def test_por_encima_de_la_ultima_capa_devuelve_cuatro_valores():
    T, rho, p, cs = atmosfera().calc_propiedades(100000)
    assert T == pytest.approx(186.87, abs=0.5) and 0 < rho < 1e-5 and p > 0 and cs > 0


def test_altitud_del_sitio():
    # Con el sitio a 1395 m, la altura 0 del simulador tiene las propiedades de la ISA a 1395 m
    al_nivel_del_mar, en_el_sitio = atmosfera(), atmosfera(altitud_sitio=1395)
    assert en_el_sitio.calc_propiedades(0) == pytest.approx(al_nivel_del_mar.calc_propiedades(1395))
    assert en_el_sitio.calc_propiedades(3000) == pytest.approx(al_nivel_del_mar.calc_propiedades(4395))
    assert en_el_sitio.calc_propiedades(0)[1] < 1.225 * 0.9


def test_dia_del_vuelo_reproduce_los_niveles_de_presion():
    # Spaceport America, 22-jun-2024: alturas de 700, 600, 500 y 400 hPa del reanálisis
    from Simulador.src.dia_de_vuelo import cargar_condiciones, crear_atmosfera
    condiciones = cargar_condiciones()
    dia = crear_atmosfera(condiciones)
    sitio = condiciones["sitio"]["altitud_m"]
    T, rho, p, _ = dia.calc_propiedades(0)
    assert p == pytest.approx(86850) and T == pytest.approx(299.1, abs=0.2)
    assert rho == pytest.approx(p / (287.05287 * T))                      # gas ideal
    for altitud, presion in ((3208, 70000), (4477, 60000), (5938, 50000), (7673, 40000)):
        assert dia.calc_propiedades(altitud - sitio)[2] == pytest.approx(presion, rel=0.01)
    assert dia.calc_propiedades(5938 - sitio)[0] - 273.15 == pytest.approx(-3.3, abs=1.0)   # temperatura en 500 hPa


def test_un_dia_caluroso_tiene_aire_menos_denso():
    assert atmosfera(delta_T=20).calc_propiedades(0)[1] < atmosfera().calc_propiedades(0)[1]
