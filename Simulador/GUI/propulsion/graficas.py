"""Piezas de las gráficas interactivas del vuelo: qué se grafica, el cursor y cómo moverlo rápido.

    Serie        una curva del vuelo (qué columnas, qué ejes, qué color)
    CapaMovil    redibuja solo los cursores, sin volver a pintar las curvas
    Cursor       la marca que señala un instante sobre una serie
"""
from dataclasses import dataclass

import numpy as np
from matplotlib.markers import MarkerStyle
from matplotlib.path import Path
from matplotlib.transforms import Affine2D

from .tema import Tema
from .widgets import estilo_ejes


@dataclass(frozen=True)
class Serie:
    nombre: str
    x: str                       # columna del eje horizontal ("t" en casi todas)
    y: str
    eje_x: str
    eje_y: str
    color: str
    formato: str = "{:.1f}"      # cómo se escribe el valor en la lectura
    solo_ascenso: bool = False   # graficar solo entre la salida del riel y el apogeo


TIEMPO = "Tiempo (s)"
SERIES = (
    Serie("Altitud", "t", "z", TIEMPO, "z (m)", Tema.AMARILLO, "{:.0f} m"),
    Serie("Velocidad", "t", "velocidad", TIEMPO, "|v| (m/s)", Tema.AZUL, "{:.1f} m/s"),
    Serie("Aceleración", "t", "aceleracion", TIEMPO, "|a| (m/s²)", Tema.ROJO, "{:.1f} m/s²"),
    Serie("Número de Mach", "t", "mach", TIEMPO, "Mach", Tema.VERDE, "Mach {:.2f}"),
    Serie("Ángulo de ataque (riel a apogeo)", "t", "alpha", TIEMPO, "α (°)", Tema.NARANJA, "{:.2f}°", solo_ascenso=True),
    Serie("Trayectoria (plano de vuelo)", "x", "z", "x (m)", "z (m)", Tema.TEXTO, "z = {:.0f} m"),
    Serie("Ángulo de cabeceo", "t", "theta", TIEMPO, "θ (°)", Tema.NARANJA, "{:.1f}°"),
    Serie("Masa", "t", "masa", TIEMPO, "Masa (kg)", Tema.AZUL, "{:.2f} kg"),
    Serie("Empuje", "t", "empuje", TIEMPO, "Empuje (N)", Tema.ROJO, "{:.0f} N"),
    Serie("Arrastre", "t", "arrastre", TIEMPO, "Arrastre (N)", Tema.ROJO, "{:.0f} N"),
    Serie("Fuerza normal", "t", "normal", TIEMPO, "Normal (N)", Tema.VERDE, "{:.1f} N"),
    Serie("Margen estático", "t", "margen", TIEMPO, "Margen (calibres)", Tema.VERDE, "{:.2f} cal"),
    Serie("Coeficiente de arrastre", "t", "cd", TIEMPO, "Cd", Tema.AMARILLO, "Cd {:.3f}"),
    Serie("Viento", "t", "viento", TIEMPO, "Viento (m/s)", Tema.AZUL, "{:.1f} m/s"),
)
PANELES = SERIES[:6]   # las seis que se ven en la pestaña Resultados


def eventos_del_vuelo(resumen):
    """Instantes que se marcan con una línea punteada: (tiempo, color, nombre)."""
    eventos = [(resumen["t_MECO"], Tema.NARANJA, "fin de quemado"), (resumen["t_apogeo"], Tema.VERDE, "apogeo")]
    if resumen.get("t_principal") is not None:
        eventos.append((resumen["t_principal"], "#C28BFF", "paracaídas principal"))
    return eventos


def dibujar_serie(ax, df, resumen, serie):
    """Grafica una serie en los ejes dados. Devuelve los arreglos (t, x, y) de lo graficado."""
    tramo = df
    if serie.solo_ascenso:
        tramo = df[(df["t"] >= (resumen["t_salida_riel"] or 0.0)) & (df["t"] <= resumen["t_apogeo"])]
    t, x, y = (tramo[columna].to_numpy(dtype=float) for columna in ("t", serie.x, serie.y))
    ax.clear()
    ax.plot(x, y, color=serie.color, linewidth=1.4)
    if serie.x == "t":
        for instante, color, _ in eventos_del_vuelo(resumen):
            if instante <= df["t"].iloc[-1]:
                ax.axvline(instante, color=color, linestyle="--", linewidth=0.9)
    estilo_ejes(ax, serie.nombre, serie.eje_x, serie.eje_y)
    return t, x, y


class CapaMovil:
    """Artistas que cambian muchas veces por segundo (los cursores).

    Cada vez que la figura se dibuja completa se guarda su imagen; después, mover un cursor
    solo repone esa imagen y pinta los cursores encima. Así seguir al ratón o reproducir el
    vuelo no obliga a volver a trazar las curvas.
    """

    def __init__(self, lienzo):
        self.lienzo = lienzo
        self.artistas = []
        self.fondo = None
        lienzo.mpl_connect("draw_event", self._al_dibujar)

    def agregar(self, artista):
        artista.set_animated(True)
        self.artistas.append(artista)
        return artista

    def vaciar(self):
        self.artistas = []
        self.fondo = None

    def _pintar(self):
        for artista in self.artistas:
            artista.axes.draw_artist(artista)

    def _al_dibujar(self, _evento):
        self.fondo = self.lienzo.copy_from_bbox(self.lienzo.figure.bbox)
        self._pintar()

    def actualizar(self):
        if self.fondo is None:
            return self.lienzo.draw_idle()   # aún no hay imagen guardada: dibujo completo
        self.lienzo.restore_region(self.fondo)
        self._pintar()
        self.lienzo.blit(self.lienzo.figure.bbox)


# Silueta de un cohete que apunta hacia +x; se gira con el ángulo de cabeceo
_SILUETA = Path([(1.0, 0.0), (0.5, 0.17), (-0.6, 0.17), (-1.0, 0.5), (-0.85, 0.0), (-1.0, -0.5), (-0.6, -0.17),
                 (0.5, -0.17), (1.0, 0.0)], closed=True)


class Cursor:
    """Marca que señala un instante del vuelo sobre una serie ya graficada.

    En las gráficas contra el tiempo es un punto con una línea vertical. Si se pide `cohete`,
    es la silueta de un cohete girada según el ángulo de cabeceo.
    """

    def __init__(self, capa, ax, serie, t, x, y, cabeceo=None):
        self.ax, self.serie = ax, serie
        self.t, self.x, self.y = t, x, y
        self.cabeceo = cabeceo                     # ángulo de cabeceo en grados, o None para un punto
        self.giro = None                           # ángulo con el que está dibujado el cohete
        self.linea = None
        if serie.x == "t":
            self.linea = capa.agregar(ax.axvline(0, color=Tema.TEXTO, linewidth=0.8, alpha=0.6, visible=False))
        tam, borde = (24, 1.2) if cabeceo is not None else (7, 2)
        self.punto, = ax.plot([], [], marker="o", linestyle="none", color="white", markeredgecolor=serie.color,
                              markeredgewidth=borde, markersize=tam, zorder=5)
        capa.agregar(self.punto)

    def contiene(self, instante):
        return len(self.t) > 0 and self.t[0] <= instante <= self.t[-1]

    def valor(self, instante):
        return float(np.interp(instante, self.t, self.y))

    def mover(self, instante):
        visible = self.contiene(instante)
        if self.linea is not None:
            self.linea.set_visible(visible)
            self.linea.set_xdata([instante, instante])
        if not visible:
            return self.punto.set_data([], [])
        self.punto.set_data([np.interp(instante, self.t, self.x)], [self.valor(instante)])
        if self.cabeceo is not None:
            self.giro = float(np.interp(instante, self.t, self.cabeceo))
            self.punto.set_marker(MarkerStyle(_SILUETA, transform=Affine2D().rotate_deg(self.giro)))

    def instante_en(self, evento):
        """Instante del vuelo que corresponde a la posición del ratón sobre esta gráfica."""
        if len(self.t) == 0 or evento.xdata is None:
            return None
        if self.serie.x == "t":
            return float(min(max(evento.xdata, self.t[0]), self.t[-1]))
        # Trayectoria: el punto de la curva más cercano al ratón, medido en fracción de los ejes
        (x0, x1), (y0, y1) = self.ax.get_xlim(), self.ax.get_ylim()
        distancia = ((self.x - evento.xdata) / (x1 - x0)) ** 2 + ((self.y - evento.ydata) / (y1 - y0)) ** 2
        return float(self.t[int(np.argmin(distancia))])
