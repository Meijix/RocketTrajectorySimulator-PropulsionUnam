"""Colores, fuentes y conversiones de texto que usa toda la interfaz."""
from tkinter import font as tkfont

import customtkinter as ctk


class Tema:
    FONDO = "#060606"
    PANEL = "#141414"
    BARRA = "#0D0D0D"
    BORDE = "#2A2A2A"
    BORDE_CAMPO = "#4A4A4A"
    TEXTO = "#FFFFFF"
    TEXTO_2 = "#D0D0D0"
    TENUE = "#B5B5B5"
    AMARILLO = "#F5E63B"
    AMARILLO_CLARO = "#FFF27A"
    SELECCION = "#2A2812"
    VERDE = "#3DDC4A"
    AZUL = "#5B8CFF"
    ROJO = "#FF6A5A"
    NARANJA = "#FF8A3A"


# Familias de letra, en orden de preferencia; se elige la primera instalada
_PREFERIDAS = {"texto": ("Lexend", "Avenir Next", "Helvetica Neue", "Segoe UI"),
               "mono": ("JetBrains Mono", "Menlo", "Consolas", "DejaVu Sans Mono")}
_familias = {"texto": None, "mono": None}


def elegir_familias():
    """Busca las familias de letra disponibles. Necesita que ya exista la ventana."""
    instaladas = set(tkfont.families())
    for uso, candidatas in _PREFERIDAS.items():
        _familias[uso] = next((f for f in candidatas if f in instaladas), None)


def fuente(tam=13, negrita=False, mono=False):
    return ctk.CTkFont(family=_familias["mono" if mono else "texto"], size=tam,
                       weight="bold" if negrita else "normal")


def fuente_tk(tam, mono=False):
    """Fuente para los lienzos de tkinter y las tablas, que no usan CTkFont."""
    return (_familias["mono" if mono else "texto"] or "Helvetica", tam)


def a_texto(valor):
    """Texto de un valor para ponerlo en una casilla (4.0 se muestra como 4)."""
    if isinstance(valor, float) and valor.is_integer():
        return str(int(valor))
    return str(valor)


def a_numero(texto):
    """Convierte el texto de un campo a número; si no lo es, devuelve el texto tal cual."""
    try:
        return float(texto)
    except (TypeError, ValueError):
        return texto


def estado_margen(margen):
    """Texto y color del margen estático (en calibres)."""
    if margen < 1:
        return "inestable", Tema.ROJO
    if margen < 1.5:
        return "marginal", Tema.AMARILLO
    return "estable", Tema.VERDE
