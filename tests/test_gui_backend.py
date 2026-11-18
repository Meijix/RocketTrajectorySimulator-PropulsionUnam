"""El backend de la GUI construye el mismo cohete que Simulador/src/XitleFile.py."""
import pytest

from Simulador.GUI import backend


def test_valores_por_defecto_reproducen_el_xitle():
    from Simulador.src.XitleFile import Xitle
    cohete = backend.construir_cohete(backend.PARAMS_XITLE, backend.RUTAS_XITLE)
    assert cohete.masa == pytest.approx(Xitle.masa)
    assert cohete.CG[2] == pytest.approx(Xitle.CG[2])
    assert cohete.CP[2] == pytest.approx(Xitle.CP[2])
    assert cohete.Ix == pytest.approx(Xitle.Ix)
    assert cohete.longtotal == pytest.approx(Xitle.longtotal)


def test_estabilidad_del_xitle():
    est = backend.analizar_estabilidad(backend.PARAMS_XITLE, backend.RUTAS_XITLE)
    assert est["cp"] > est["cg"]                       # CP detrás del CG: estable
    assert est["margen"] > 1
    assert est["margen_seco"] > est["margen"]          # al vaciarse, el CG se mueve hacia la nariz
    assert len(est["filas"]) == len([f for f in est["filas"] if f[1] >= 0])


@pytest.mark.parametrize("cambio, texto", [
    ({"rail_angle": 120}, "riel"),
    ({"nose_len": "abc"}, "nose_len"),
    ({"fin_num": 2}, "aletas"),
    ({"coples_mass": -1}, "negativa"),
    ({"integrator": "Magia"}, "Integrador"),
])
def test_validacion_de_parametros(cambio, texto):
    with pytest.raises(ValueError, match=texto):
        backend.construir_cohete(dict(backend.PARAMS_XITLE, **cambio), backend.RUTAS_XITLE)


def test_falta_un_archivo_de_datos():
    rutas = dict(backend.RUTAS_XITLE, thrust="No cargado")
    with pytest.raises(ValueError, match="empuje"):
        backend.construir_cohete(backend.PARAMS_XITLE, rutas)
