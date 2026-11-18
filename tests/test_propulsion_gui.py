"""La interfaz nueva (PropulsionGUI) describe los mismos parámetros que entiende el backend."""
import pytest

pytest.importorskip("customtkinter")

from Simulador.GUI import backend  # noqa: E402
from Simulador.GUI.propulsion import componentes, pestana_tablas, tema  # noqa: E402

# Parámetros que no pertenecen a un componente del cohete (pestaña Simulación)
ENTORNO = {"launch_lat", "launch_lon", "launch_alt", "launch_date", "atm_delta_t", "atm_pressure_hpa", "wind_mode",
           "wind_base_speed", "wind_from", "wind_mean_speed", "wind_speed_var", "wind_angle_var", "wind_seed",
           "rail_len", "rail_angle", "rail_azimuth", "sim_max_time", "sim_time_step", "load_gust", "integrator", "recovery"}


def campos_del_cohete():
    return [c.param for comp in componentes.COMPONENTES for c in comp.campos]


def test_cada_campo_es_un_parametro_del_backend():
    assert set(campos_del_cohete()) <= set(backend.PARAMS_XITLE)


def test_ningun_parametro_del_cohete_se_queda_sin_campo():
    assert set(campos_del_cohete()) | ENTORNO == set(backend.PARAMS_XITLE)
    assert len(campos_del_cohete()) == len(set(campos_del_cohete()))


def test_el_primer_campo_de_cada_componente_es_su_masa():
    for comp in componentes.COMPONENTES:
        assert "mass" in comp.campos[0].param, comp.nombre


def test_los_nombres_coinciden_con_el_analisis_de_estabilidad():
    filas = {fila[0] for fila in backend.analizar_estabilidad(backend.PARAMS_XITLE, backend.RUTAS_XITLE)["filas"]}
    nombres = {comp.nombre for comp in componentes.COMPONENTES}
    assert filas <= nombres                      # el motor no aparece en el análisis si su masa es 0
    assert nombres - filas <= {"Motor (masa inerte)"}


@pytest.mark.parametrize("tabla", pestana_tablas.TABLAS)
def test_las_tablas_del_xitle_se_leen(tabla):
    x, y = pestana_tablas.leer_tabla(tabla, backend.RUTAS_XITLE[tabla.clave])
    assert len(x) == len(y) > 10


def test_conversion_de_campos():
    assert tema.a_numero("0.81") == 0.81
    assert tema.a_numero("ogiva") == "ogiva"
    assert tema.a_numero("") == ""
    assert tema.a_texto(4.0) == "4" and tema.a_texto(0.152) == "0.152" and tema.a_texto("DOP853") == "DOP853"


@pytest.mark.parametrize("margen, estado", [(0.5, "inestable"), (1.2, "marginal"), (4.2, "estable")])
def test_estado_del_margen(margen, estado):
    assert tema.estado_margen(margen)[0] == estado


# --- Gráficas interactivas ---------------------------------------------------------------
def _figura_con(serie, vuelo):
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    from matplotlib.figure import Figure
    from Simulador.GUI.propulsion import graficas

    df, resumen = vuelo
    fig = Figure()
    lienzo = FigureCanvasAgg(fig)
    ax = fig.add_subplot(111)
    capa = graficas.CapaMovil(lienzo)
    t, x, y = graficas.dibujar_serie(ax, df, resumen, serie)
    cabeceo = df["theta"].to_numpy() if serie.x != "t" else None
    cursor = graficas.Cursor(capa, ax, serie, t, x, y, cabeceo=cabeceo)
    lienzo.draw()
    return df, resumen, ax, capa, cursor


def test_todas_las_series_existen_en_los_resultados(vuelo_libre):
    from Simulador.GUI.propulsion import graficas

    df, _ = vuelo_libre
    assert len(graficas.PANELES) == 6
    for serie in graficas.SERIES:
        assert serie.x in df.columns and serie.y in df.columns, serie.nombre


def test_el_cursor_sigue_la_curva(vuelo_libre):
    import numpy as np
    from Simulador.GUI.propulsion import graficas

    df, _, _, capa, cursor = _figura_con(graficas.SERIES[0], vuelo_libre)   # altitud
    cursor.mover(12.5)
    capa.actualizar()
    x, y = cursor.punto.get_data()
    assert x[0] == pytest.approx(12.5)
    assert y[0] == pytest.approx(np.interp(12.5, df["t"], df["z"]))
    assert cursor.linea.get_visible()


def test_el_angulo_de_ataque_solo_tiene_cursor_durante_el_ascenso(vuelo_libre):
    from Simulador.GUI.propulsion import graficas

    serie = next(s for s in graficas.SERIES if s.solo_ascenso)
    _, resumen, _, _, cursor = _figura_con(serie, vuelo_libre)
    cursor.mover(resumen["t_apogeo"] + 5)
    assert len(cursor.punto.get_data()[0]) == 0 and not cursor.linea.get_visible()
    cursor.mover(resumen["t_apogeo"] / 2)
    assert len(cursor.punto.get_data()[0]) == 1


def test_el_cohete_de_la_trayectoria_gira_con_el_cabeceo(vuelo_libre):
    import numpy as np
    from matplotlib.backend_bases import MouseEvent
    from Simulador.GUI.propulsion import graficas

    serie = next(s for s in graficas.SERIES if s.x != "t")
    df, resumen, ax, _, cursor = _figura_con(serie, vuelo_libre)
    for instante in (3.0, resumen["t_apogeo"], resumen["t_impacto"] - 2):
        cursor.mover(instante)
        assert cursor.giro == pytest.approx(np.interp(instante, df["t"], df["theta"]))
    # El ratón sobre un punto de la trayectoria devuelve el instante de ese punto
    i = int(len(df) * 0.7)
    px, py = ax.transData.transform((df["x"].iloc[i], df["z"].iloc[i]))
    assert cursor.instante_en(MouseEvent("motion_notify_event", ax.figure.canvas, px, py)) == pytest.approx(df["t"].iloc[i], abs=0.2)
