"""Campos del formulario de cada componente del cohete.

Los nombres de los parámetros son los de backend.PARAMS_XITLE, y el nombre de cada
componente es el que devuelve backend.analizar_estabilidad.
"""
from dataclasses import dataclass

from Simulador.GUI import backend
from .tema import Tema


@dataclass(frozen=True)
class Campo:
    param: str            # nombre del parámetro en backend.PARAMS_XITLE
    etiqueta: str
    unidad: str = ""
    opciones: tuple = ()  # si no está vacío, el campo es un menú


@dataclass(frozen=True)
class Componente:
    clave: str
    nombre: str           # el mismo nombre que devuelve backend.analizar_estabilidad
    grupo: str
    campos: tuple
    aviso: str = ""


GRUPOS = {"Externos": Tema.VERDE, "Internos": Tema.AZUL, "Propelentes": Tema.ROJO}
AVISO_POSICION = "La posición se mide desde la punta de la nariz hasta el frente de la pieza."


def _tubo(pref, nombre):
    return Componente(pref, nombre, "Externos", (
        Campo(f"{pref}_mass", "Masa", "kg"), Campo(f"{pref}_len", "Longitud", "m"),
        Campo(f"{pref}_pos_z", "Posición Z", "m"), Campo(f"{pref}_diam_ext", "Diámetro exterior", "m"),
        Campo(f"{pref}_diam_int", "Diámetro interior", "m"),
        Campo(f"{pref}_material", "Material", opciones=tuple(backend.MATERIALES))))


def _interno(pref, nombre, masa, etiqueta_masa="Masa", extra=(), aviso=""):
    return Componente(pref, nombre, "Internos", (
        Campo(masa, etiqueta_masa, "kg"), Campo(f"{pref}_pos_z", "Posición Z", "m"),
        Campo(f"{pref}_len", "Longitud", "m")) + tuple(extra), aviso)


COMPONENTES = (
    Componente("nose", "Nariz", "Externos", (
        Campo("nose_mass", "Masa", "kg"), Campo("nose_len", "Longitud", "m"), Campo("nose_pos_z", "Posición Z", "m"),
        Campo("nose_diam", "Diámetro", "m"),
        Campo("nose_shape", "Geometría", opciones=tuple(backend.GEOMETRIAS_NARIZ)))),
    _tubo("coples", "Coples"),
    _tubo("tubo_recup", "Tubo recuperación"),
    _tubo("transfer", "Transferidor"),
    _tubo("tanque_vacio", "Tanque vacío"),
    _tubo("valvulas", "Válvulas"),
    _tubo("cc", "Cámara de combustión"),
    Componente("bt", "Boattail", "Externos", (
        Campo("bt_mass", "Masa", "kg"), Campo("bt_len", "Longitud", "m"), Campo("bt_pos_z", "Posición Z", "m"),
        Campo("bt_diam_front", "Diámetro frontal", "m"), Campo("bt_diam_rear", "Diámetro trasero", "m"),
        Campo("bt_espesor", "Espesor", "m"))),
    Componente("fin", "Aletas", "Externos", (
        Campo("fin_mass", "Masa total", "kg"), Campo("fin_num", "Número"), Campo("fin_pos_z", "Posición Z", "m"),
        Campo("fin_span", "Envergadura", "m"), Campo("fin_root_chord", "Cuerda de raíz", "m"),
        Campo("fin_tip_chord", "Cuerda de punta", "m"), Campo("fin_xr", "Retraso de la punta", "m"),
        Campo("fin_sweep", "Ángulo de barrido", "°"), Campo("fin_thickness", "Espesor", "m"),
        Campo("fin_material", "Material", opciones=tuple(backend.MATERIALES))),
        "El material y el espesor se usan para comprobar el flameo."),
    _interno("avionics", "Aviónica", "avionics_mass"),
    _interno("cu", "Carga útil", "cu_mass"),
    _interno("motor", "Motor (masa inerte)", "motor_mass_inert", "Masa inerte",
             aviso="Con masa 0 la pieza no se incluye en el cohete."),
    _interno("drogue", "Drogue", "drogue_mass", extra=(
        Campo("drogue_chute_diam", "Diámetro del paracaídas", "m"), Campo("drogue_cd", "Coeficiente de arrastre"),
        Campo("drogue_fill", "Constante de llenado")),
        aviso="Se abre en el apogeo."),
    _interno("main", "Main", "main_mass", extra=(
        Campo("main_chute_diam", "Diámetro del paracaídas", "m"), Campo("main_cd", "Coeficiente de arrastre"),
        Campo("main_deploy_alt", "Altura de despliegue", "m"), Campo("main_fill", "Constante de llenado")),
        aviso="Se abre en el descenso, a la altura indicada sobre el sitio."),
    Componente("oxidante", "Oxidante", "Propelentes", (
        Campo("oxidante_mass", "Masa inicial", "kg"), Campo("oxidante_pos_z", "Posición Z", "m"),
        Campo("oxidante_len", "Longitud", "m"), Campo("oxidante_diam", "Diámetro", "m")),
        "Durante el vuelo la masa sale de la tabla del motor."),
    Componente("grano", "Grano", "Propelentes", (
        Campo("grano_mass", "Masa inicial", "kg"), Campo("grano_pos_z", "Posición Z", "m"),
        Campo("grano_length", "Longitud", "m"), Campo("grano_outer_diam", "Diámetro exterior", "m"),
        Campo("grano_inner_diam", "Diámetro interior", "m")),
        "Durante el vuelo la masa sale de la tabla del motor."),
)
TUBOS = ("coples", "tubo_recup", "transfer", "tanque_vacio", "valvulas", "cc")
