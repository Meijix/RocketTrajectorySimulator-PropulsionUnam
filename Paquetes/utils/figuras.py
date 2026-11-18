"""Guardar automáticamente las figuras de un script cada vez que se muestran."""
import os
import re
import unicodedata

import matplotlib.pyplot as plt


def _nombre_archivo(texto):
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-zA-Z0-9]+", "-", texto).strip("-").lower()[:60] or "figura"


def guardar_figuras_al_mostrar(carpeta, dpi=150):
    """Hace que plt.show() guarde antes cada figura abierta en `carpeta` (01-titulo.png, 02-...).

    Las figuras se numeran en el orden en que el script las muestra, y después se cierran.
    """
    os.makedirs(carpeta, exist_ok=True)
    mostrar_original = plt.show
    contador = [0]

    def mostrar(*args, **kwargs):
        for numero in plt.get_fignums():
            figura = plt.figure(numero)
            titulo = figura.get_suptitle() if hasattr(figura, "get_suptitle") else ""
            if not titulo and figura.axes:
                titulo = figura.axes[0].get_title()
            contador[0] += 1
            figura.savefig(os.path.join(carpeta, f"{contador[0]:02d}-{_nombre_archivo(titulo)}.png"),
                           dpi=dpi, bbox_inches="tight")
        mostrar_original(*args, **kwargs)
        plt.close("all")

    plt.show = mostrar
