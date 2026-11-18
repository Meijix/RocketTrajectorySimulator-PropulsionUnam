"""Conversión entre coordenadas del simulador y geográficas, y mapa."""
import numpy as np
import pytest

from Paquetes.utils.geografia import a_geograficas, desplazamiento_este_norte, direccion_viento_simulador, distancia_y_rumbo
from Simulador.GUI import mapa


@pytest.mark.parametrize("azimut, este_norte", [(0, (0, 1000)), (90, (1000, 0)), (180, (0, -1000)), (270, (-1000, 0))])
def test_x_apunta_hacia_el_azimut_del_riel(azimut, este_norte):
    assert desplazamiento_este_norte(1000, 0, azimut) == pytest.approx(este_norte, abs=1e-6)


def test_y_queda_a_la_izquierda():
    # Riel hacia el norte: +y es el oeste
    assert desplazamiento_este_norte(0, 500, 0) == pytest.approx((-500, 0), abs=1e-6)


def test_ida_y_vuelta():
    lat, lon = a_geograficas(3500, -400, 32.94753, -106.91019, 220)
    distancia, rumbo = distancia_y_rumbo(32.94753, -106.91019, lat, lon)
    assert distancia == pytest.approx(np.hypot(3500, 400), rel=1e-3)
    assert rumbo == pytest.approx(220 + np.rad2deg(np.arctan2(400, 3500)), abs=0.1)   # -y: a la derecha


def test_trayectoria_gps_del_vuelo_real():
    # El último punto GPS está a 4553 m del sitio con rumbo 220°
    distancia, rumbo = distancia_y_rumbo(32.94753, -106.91019, 32.91602, -106.94135)
    assert distancia == pytest.approx(4553, abs=15)
    assert rumbo == pytest.approx(220, abs=1)


@pytest.mark.parametrize("desde, azimut, esperado", [
    (220, 220, 180),   # viene de donde apunta el riel: viento de frente
    (40, 220, 0),      # viene de atrás: viento de cola
    (130, 220, 270),   # viene de la izquierda del riel: empuja hacia -y
    (310, 220, 90),    # viene de la derecha: empuja hacia +y
])
def test_direccion_del_viento(desde, azimut, esperado):
    assert direccion_viento_simulador(desde, azimut) == pytest.approx(esperado)


def test_pixeles_web_mercator():
    x, y = mapa.a_pixeles(0.0, 0.0, 0)
    assert (float(x), float(y)) == pytest.approx((128, 128))
    x_norte, y_norte = mapa.a_pixeles(33.0, -107.0, 10)
    x_sur, y_sur = mapa.a_pixeles(32.0, -106.0, 10)
    assert y_norte < y_sur and x_norte < x_sur          # el norte arriba, el este a la derecha


def test_mapa_interactivo(tmp_path, vuelo_libre):
    from Simulador.GUI import backend
    df, r = vuelo_libre
    ruta = mapa.escribir_html(backend.datos_mapa_interactivo(df, r), str(tmp_path / "mapa.html"))
    html = open(ruta, encoding="utf-8").read()
    assert f"{r['lat_impacto']:.5f}"[:7] in html and "leaflet" in html and "Vuelo real" in html
