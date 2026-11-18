"""Dibujo del cohete con matplotlib."""
import matplotlib.patches as patches
import numpy as np

from .componentes import TUBOS
from .tema import Tema
from .widgets import estilo_ejes


def dibujar_cohete(ax, valor, seleccion, estabilidad):
    """Dibuja el cohete acostado, con la nariz a la izquierda. Devuelve la longitud total.

    valor(nombre) da el número de un parámetro. Cada pieza es un parche con `gid` igual a la
    clave del componente, para saber cuál se tocó.
    """
    ax.clear()
    oscuro, claro = "#2E2E2E", "#F2F2F2"

    def parche(clave, puntos, base, orden=2, borde="#8A8A8A", **estilo):
        relleno = Tema.AMARILLO if clave == seleccion else base
        ax.add_patch(patches.Polygon(puntos, closed=True, facecolor=relleno, edgecolor=borde, linewidth=0.8,
                                     zorder=orden, gid=clave, **estilo))

    def rectangulo(z, largo, radio):
        return [(z, radio), (z + largo, radio), (z + largo, -radio), (z, -radio)]

    # Nariz: perfil curvo de la punta a la base
    z0, largo, radio = valor("nose_pos_z"), valor("nose_len"), valor("nose_diam") / 2
    s = np.linspace(0, 1, 14)
    perfil = radio * (1 - (1 - s) ** 2)
    arriba = list(zip(z0 + s * largo, perfil))
    parche("nose", arriba + [(z, -r) for z, r in reversed(arriba)], oscuro)
    total = z0 + largo

    # Tubos del fuselaje: el frente oscuro, la cola clara y el transferidor punteado, como el cohete real
    tonos = {"coples": "#3A3A3A", "tubo_recup": oscuro, "transfer": oscuro, "tanque_vacio": claro,
             "valvulas": "#D8D8D8", "cc": claro}
    for pref in TUBOS:
        z, largo = valor(f"{pref}_pos_z"), valor(f"{pref}_len")
        trama = dict(hatch="ooo", borde=claro) if pref == "transfer" and seleccion != pref else {}
        parche(pref, rectangulo(z, largo, valor(f"{pref}_diam_ext") / 2), tonos[pref], **trama)
        total = max(total, z + largo)

    z, largo = valor("bt_pos_z"), valor("bt_len")
    r1, r2 = valor("bt_diam_front") / 2, valor("bt_diam_rear") / 2
    parche("bt", [(z, r1), (z + largo, r2), (z + largo, -r2), (z, -r1)], "#D8D8D8")
    total = max(total, z + largo)

    if valor("fin_num") > 0:
        z, raiz, punta = valor("fin_pos_z"), valor("fin_root_chord"), valor("fin_tip_chord")
        ancho, retraso, r = valor("fin_span"), valor("fin_xr"), valor("cc_diam_ext") / 2
        aleta = [(z, r), (z + raiz, r), (z + retraso + punta, r + ancho), (z + retraso, r + ancho)]
        parche("fin", aleta, claro)
        parche("fin", [(x, -y) for x, y in aleta], claro)
        total = max(total, z + max(raiz, retraso + punta))

    # Piezas internas y propelentes: una banda al centro, para que el tubo siga siendo visible
    internas = [("avionics", "avionics_len", "#1D2B55", Tema.AZUL), ("cu", "cu_len", "#1D2B55", Tema.AZUL),
                ("drogue", "drogue_len", "#1D2B55", Tema.AZUL), ("main", "main_len", "#1D2B55", Tema.AZUL),
                ("oxidante", "oxidante_len", "#55201B", Tema.ROJO), ("grano", "grano_length", "#55201B", Tema.ROJO)]
    if valor("motor_mass_inert") > 0:
        internas.append(("motor", "motor_len", "#1D2B55", Tema.AZUL))
    for clave, largo, relleno, borde in internas:
        parche(clave, rectangulo(valor(f"{clave}_pos_z"), valor(largo), 0.028), relleno, orden=3, borde=borde)

    if estabilidad:
        for nombre, posicion, color, alto in (("CG", estabilidad["cg"], Tema.AZUL, 0.27), ("CP", estabilidad["cp"], Tema.ROJO, 0.21)):
            ax.axvline(posicion, color=color, linestyle="--", linewidth=1.4, zorder=4)
            ax.text(posicion, alto, f"{nombre} {posicion:.2f} m", color="#060606", fontsize=8, ha="center", va="center",
                    zorder=5, bbox=dict(boxstyle="round,pad=0.3", facecolor=color, edgecolor="none"))

    ax.set_xlim(-0.1, total + 0.25)
    ax.set_ylim(-0.3, 0.32)
    ax.set_yticks([])
    estilo_ejes(ax, xlabel="Distancia desde la punta de la nariz (m)")
    ax.grid(False)
    return total
