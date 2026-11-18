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
