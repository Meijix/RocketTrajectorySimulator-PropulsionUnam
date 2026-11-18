"""Pestaña Mapa."""
import webbrowser
from tkinter import messagebox

import customtkinter as ctk
import numpy as np

from Simulador.GUI import backend, mapa
from .tema import Tema, fuente
from .widgets import Tarjeta, boton, colocar_figura, figura, nota, panel, titulo


class PestanaMapa(ctk.CTkFrame):
    """Mapa real con el sitio, la trayectoria simulada, el impacto y la trayectoria GPS del vuelo real."""

    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.df = self.resumen = None
        self.capas = {"simulada": [], "real": []}
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        marco = panel(self)
        marco.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        marco.grid_columnconfigure(0, weight=1)
        marco.grid_rowconfigure(1, weight=1)
        titulo(marco, "Trayectoria sobre el terreno").grid(row=0, column=0, sticky="w", padx=16, pady=(12, 4))
        capas = ctk.CTkFrame(marco, fg_color="transparent")
        capas.grid(row=0, column=0, sticky="e", padx=16, pady=(12, 4))
        self.interruptores = {}
        for clave, texto, color in (("simulada", "Simulada", Tema.AMARILLO), ("real", "Vuelo real (GPS)", Tema.ROJO)):
            s = ctk.CTkSwitch(capas, text=texto, font=fuente(12), text_color=Tema.TEXTO, progress_color=color,
                              command=self._aplicar_capas)
            s.select()
            s.pack(side="left", padx=8)
            self.interruptores[clave] = s
        self.fig = figura(8, 6)
        self.ax = self.fig.add_subplot(111)
        self.lienzo = colocar_figura(self.fig, marco)
        self.lienzo.get_tk_widget().grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        lado = ctk.CTkFrame(self, fg_color="transparent")
        lado.grid(row=0, column=1, sticky="nsew")
        lado.grid_columnconfigure(0, weight=1)
        self.lanzamiento = Tarjeta(lado, "Lanzamiento")
        self.impacto = Tarjeta(lado, "Impacto simulado", destacada=True)
        self.real = Tarjeta(lado, "Vuelo real · último punto GPS")
        for i, tarjeta in enumerate((self.lanzamiento, self.impacto, self.real)):
            tarjeta.valor.configure(font=fuente(15, mono=True))
            tarjeta.detalle.configure(wraplength=290, justify="left")
            tarjeta.grid(row=i, column=0, sticky="ew", pady=(0, 8))
        self.copiar = boton(lado, "Copiar coordenadas de impacto", self.copiar_coordenadas, state="disabled")
        self.copiar.grid(row=3, column=0, sticky="ew", pady=(0, 8))
        self.abrir = boton(lado, "Abrir mapa interactivo", self.abrir_en_navegador, state="disabled", border_color=Tema.TEXTO)
        self.abrir.grid(row=4, column=0, sticky="ew")
        nota(lado, "El fondo del mapa necesita conexión a internet. Sin ella la trayectoria se dibuja sobre un fondo liso.",
             wraplength=290).grid(row=5, column=0, sticky="w", pady=8)
        self.limpiar()

    def limpiar(self):
        self.df = self.resumen = None
        self.ax.clear()
        self.ax.set_facecolor(Tema.PANEL)
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.ax.text(0.5, 0.5, "Ejecute una simulación para ver dónde despega y dónde cae el cohete.",
                     color=Tema.TENUE, ha="center", va="center", fontsize=11, transform=self.ax.transAxes)
        self.lienzo.draw_idle()
        for tarjeta in (self.lanzamiento, self.impacto, self.real):
            tarjeta.fijar("--")
        self.copiar.configure(state="disabled", text="Copiar coordenadas de impacto")
        self.abrir.configure(state="disabled")

    def copiar_coordenadas(self):
        self.clipboard_clear()
        self.clipboard_append(f"{self.resumen['lat_impacto']:.6f}, {self.resumen['lon_impacto']:.6f}")
        self.copiar.configure(text="Coordenadas copiadas")

    def abrir_en_navegador(self):
        try:
            ruta = mapa.escribir_html(backend.datos_mapa_interactivo(self.df, self.resumen))
            webbrowser.open("file://" + ruta)
        except Exception as error:
            messagebox.showerror("Mapa", f"No se pudo abrir el mapa interactivo:\n{error}")

    def _aplicar_capas(self):
        for clave, artistas in self.capas.items():
            for artista in artistas:
                artista.set_visible(bool(self.interruptores[clave].get()))
        self.lienzo.draw_idle()

    def mostrar(self, df, r):
        self.df, self.resumen = df, r
        real = r.get("vuelo_real")
        final = "Impacto simulado" if r["t_impacto"] is not None else "Punto final (sin impacto)"
        self.lanzamiento.fijar(f"{r['lat_lanzamiento']:.5f}°, {r['lon_lanzamiento']:.5f}°",
                               f"{r['altitud_sitio']:.0f} m s. n. m. · azimut {r['azimut_riel']:.0f}°")
        self.impacto.fijar(f"{r['lat_impacto']:.5f}°, {r['lon_impacto']:.5f}°",
                           f"a {r['distancia']:.0f} m del sitio · rumbo {r['rumbo_impacto']:.0f}°"
                           + ("" if r["t_impacto"] is not None else "\nPunto final: no hubo impacto en el tiempo simulado"))
        if real:
            ultimo = real["ultimo"]
            distancia, rumbo = backend.distancia_y_rumbo(r["lat_lanzamiento"], r["lon_lanzamiento"], ultimo["lat"], ultimo["lon"])
            separacion, _ = backend.distancia_y_rumbo(r["lat_impacto"], r["lon_impacto"], ultimo["lat"], ultimo["lon"])
            self.real.fijar(f"{ultimo['lat']:.5f}°, {ultimo['lon']:.5f}°",
                            f"a {distancia:.0f} m del sitio · rumbo {rumbo:.0f}°\n{ultimo['nota']}\n"
                            f"a {separacion:.0f} m del impacto simulado", Tema.ROJO)
        else:
            self.real.fijar("--", "Solo se muestra si el lanzamiento es desde el sitio del vuelo real.")
        self.copiar.configure(state="normal", text="Copiar coordenadas de impacto")
        self.abrir.configure(state="normal")
        try:
            self._dibujar(df, r, real, final)
        except Exception as error:
            messagebox.showerror("Mapa", f"No se pudo dibujar el mapa:\n{error}")

    def _dibujar(self, df, r, real, final):
        ax, fondo = self.ax, r.get("mapa")
        zoom = fondo["zoom"] if fondo else 14
        pixeles = lambda lat, lon: mapa.a_pixeles(lat, lon, zoom)
        marca = dict(markeredgecolor="white", linestyle="none")
        ax.clear()
        if fondo:
            ax.imshow(fondo["imagen"], extent=fondo["extent"], interpolation="bilinear")
        else:
            ax.set_facecolor("#1C1C1C")

        simulada = ax.plot(*pixeles(df["latitud"], df["longitud"]), color="#1F4FD8" if fondo else Tema.AMARILLO, linewidth=2.5, label="Trayectoria simulada")
        simulada += ax.plot(*pixeles(r["lat_apogeo"], r["lon_apogeo"]), marker="o", color="#E6A700", markersize=10, label=f"Apogeo ({r['apogeo']:.0f} m)", **marca)
        simulada += ax.plot(*pixeles(r["lat_impacto"], r["lon_impacto"]), marker="X", color="#1F4FD8" if fondo else Tema.AMARILLO, markersize=13, label=final, **marca)
        reales = []
        if real:
            gps = np.array(real["trayectoria"])
            reales += ax.plot(*pixeles(gps[:, 0], gps[:, 1]), color="#C8102E", linewidth=2.5, linestyle="--", label="Vuelo real (GPS)")
            reales += ax.plot(*pixeles(real["ultimo"]["lat"], real["ultimo"]["lon"]), marker="X", color="#C8102E", markersize=12, label="Último punto GPS", **marca)
        ax.plot(*pixeles(r["lat_lanzamiento"], r["lon_lanzamiento"]), marker="^", color="#1A7F37", markersize=13, label="Lanzamiento", **marca)
        self.capas = {"simulada": simulada, "real": reales}

        if fondo:
            izq, der, abajo, arriba = fondo["limites"]
            ax.set_xlim(izq, der)
            ax.set_ylim(abajo, arriba)
        else:
            ax.margins(0.25)
            ax.invert_yaxis()
            ax.text(0.5, 0.02, "Sin conexión: no se pudo descargar el mapa de fondo", transform=ax.transAxes,
                    ha="center", fontsize=9, color=Tema.TENUE)
        ax.set_aspect("equal")
        ax.set_xticks([])
        ax.set_yticks([])

        # Barra de escala de 1 km
        color_escala = "black" if fondo else Tema.TEXTO
        metros_por_pixel = 156543.03392 * np.cos(np.radians(r["lat_lanzamiento"])) / 2 ** zoom
        (x0, x1), (y0, y1) = ax.get_xlim(), ax.get_ylim()
        bx, by = x0 + 0.04 * (x1 - x0), y0 + 0.05 * (y1 - y0)
        ax.plot([bx, bx + 1000 / metros_por_pixel], [by, by], color=color_escala, linewidth=3, solid_capstyle="butt")
        ax.text(bx, by + 0.015 * (y1 - y0), "1 km", fontsize=9, va="bottom", color=color_escala)
        if fondo:
            ax.text(0.995, 0.005, fondo["atribucion"], transform=ax.transAxes, ha="right", va="bottom", fontsize=7,
                    bbox=dict(facecolor="white", alpha=0.7, edgecolor="none", pad=1.5))
        ax.legend(loc="upper left", bbox_to_anchor=(1.02, 1.0), fontsize=9, borderaxespad=0, facecolor=Tema.PANEL,
                  edgecolor=Tema.BORDE, labelcolor=Tema.TEXTO)
        self.fig.tight_layout(pad=0.5)
        self._aplicar_capas()
