"""Pestaña Resultados."""
from tkinter import filedialog, messagebox

import customtkinter as ctk
import numpy as np
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk

from Simulador.GUI import backend
from .tema import Tema, fuente
from .widgets import Tarjeta, boton, colocar_figura, estilo_ejes, figura, panel


class PestanaResultados(ctk.CTkFrame):
    """Cifras del vuelo y seis gráficas con un cursor de tiempo común."""

    SERIES = (("z", "Altitud", "z (m)", Tema.AMARILLO), ("velocidad", "Velocidad", "|v| (m/s)", Tema.AZUL),
              ("aceleracion", "Aceleración", "|a| (m/s²)", Tema.ROJO), ("mach", "Número de Mach", "Mach", Tema.VERDE))
    TARJETAS = (("apogeo", "Apogeo"), ("vel_max", "Velocidad máxima"), ("riel", "Salida del riel"),
                ("impacto", "Impacto"), ("distancia", "Cayó a"), ("margen", "Margen estático mínimo"))

    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.df = None
        self.cursores = []
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        fila = ctk.CTkFrame(self, fg_color="transparent")
        fila.grid(row=0, column=0, sticky="ew")
        self.tarjetas = {}
        for i, (clave, nombre) in enumerate(self.TARJETAS):
            fila.grid_columnconfigure(i, weight=1, uniform="kpi")
            self.tarjetas[clave] = Tarjeta(fila, nombre, destacada=clave == "apogeo")
            self.tarjetas[clave].grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 8, 0))

        control = panel(self)
        control.grid(row=1, column=0, sticky="ew", pady=8)
        control.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(control, text="Recorre el vuelo", font=fuente(12), text_color=Tema.TEXTO_2).grid(row=0, column=0, padx=(16, 8), pady=10)
        self.tiempo = ctk.CTkSlider(control, from_=0, to=1, progress_color=Tema.AMARILLO, button_color=Tema.AMARILLO,
                                    button_hover_color=Tema.AMARILLO_CLARO, fg_color=Tema.BORDE, command=self._mover_cursor,
                                    state="disabled")
        self.tiempo.grid(row=0, column=1, sticky="ew")
        self.lectura = ctk.CTkLabel(control, text="", font=fuente(12, mono=True), text_color=Tema.TEXTO, width=330, anchor="w")
        self.lectura.grid(row=0, column=2, padx=12)
        self.exportar = boton(control, "Exportar CSV", self.exportar_csv, state="disabled", border_color=Tema.TEXTO)
        self.exportar.grid(row=0, column=3, padx=(0, 12), pady=8)

        self.marco = panel(self)
        self.marco.grid(row=2, column=0, sticky="nsew")
        self.marco.grid_columnconfigure(0, weight=1)
        self.marco.grid_rowconfigure(0, weight=1)
        self.fig = figura(9, 5)
        self.lienzo = colocar_figura(self.fig, self.marco)
        self.lienzo.get_tk_widget().grid(row=0, column=0, sticky="nsew", padx=10, pady=(10, 0))
        barra = NavigationToolbar2Tk(self.lienzo, self.marco, pack_toolbar=False)   # zoom, desplazamiento y guardar imagen
        barra.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 6))
        self.limpiar()

    def limpiar(self, mensaje="Los resultados de la simulación se mostrarán aquí."):
        self.df = None
        self.cursores = []
        self.fig.clear()
        self.fig.text(0.5, 0.5, mensaje, color=Tema.TENUE, ha="center", va="center", fontsize=12)
        self.lienzo.draw_idle()
        self.tiempo.configure(state="disabled")
        self.exportar.configure(state="disabled")
        self.lectura.configure(text="")
        for tarjeta in self.tarjetas.values():
            tarjeta.fijar("--")

    def exportar_csv(self):
        ruta = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")], title="Exportar resultados")
        if not ruta:
            return
        try:
            self.df.to_csv(ruta, index=False)
        except OSError as error:
            messagebox.showerror("Error al exportar", f"No se pudo guardar el archivo:\n{error}")

    def mostrar(self, df, r):
        self.df, self.resumen = df, r
        texto = lambda valor, formato: "--" if valor is None else format(valor, formato)
        t = self.tarjetas
        t["apogeo"].fijar(f"{r['apogeo']:.0f} m", f"t = {r['t_apogeo']:.1f} s")
        t["vel_max"].fijar(f"{r['vel_max']:.1f} m/s", f"Mach {r['mach_max']:.2f}")
        t["riel"].fijar(f"{texto(r['vel_salida_riel'], '.1f')} m/s", f"t = {texto(r['t_salida_riel'], '.2f')} s")
        if r["t_impacto"] is None:
            t["impacto"].fijar("Sin impacto", f"antes de t = {r['t_final']:.0f} s")
        else:
            detalle = f"t = {r['t_impacto']:.1f} s"
            if r.get("t_principal") is not None:
                detalle += f" · principal a {r['altura_principal']:.0f} m"
            t["impacto"].fijar(f"{r['vel_impacto']:.1f} m/s", detalle)
        t["distancia"].fijar(f"{r['distancia']:.0f} m", f"rumbo {r['rumbo_impacto']:.0f}° · {r['lat_impacto']:.5f}°, {r['lon_impacto']:.5f}°")
        t["margen"].fijar(f"{r['margen_min']:.2f} cal", backend.etiqueta(r["integrador"]))

        self._graficar(df, r)
        self.exportar.configure(state="normal")
        self.tiempo.configure(state="normal", from_=0, to=float(df["t"].iloc[-1]))
        self.tiempo.set(r["t_apogeo"])
        self._mover_cursor(r["t_apogeo"])

    def _graficar(self, df, r):
        self.fig.clear()
        self.cursores = []
        eventos = [(r["t_MECO"], Tema.NARANJA, "fin de quemado"), (r["t_apogeo"], Tema.VERDE, "apogeo")]
        if r.get("t_principal") is not None:
            eventos.append((r["t_principal"], "#C28BFF", "paracaídas principal"))

        def cursor(ax, columna_x, columna_y, color):
            punto, = ax.plot([], [], marker="o", color="white", markeredgecolor=color, markeredgewidth=2, markersize=7, zorder=5)
            self.cursores.append((punto, columna_x, columna_y))

        for posicion, (columna, nombre, eje_y, color) in enumerate(self.SERIES, start=1):
            ax = self.fig.add_subplot(2, 3, posicion)
            ax.plot(df["t"], df[columna], color=color, linewidth=1.4)
            for instante, tono, _ in eventos:
                if instante <= df["t"].iloc[-1]:
                    ax.axvline(instante, color=tono, linestyle="--", linewidth=0.9)
            estilo_ejes(ax, nombre, "Tiempo (s)", eje_y)
            cursor(ax, "t", columna, color)

        # Ángulo de ataque: solo entre la salida del riel y el apogeo (después no es representativo)
        tramo = df[(df["t"] >= (r["t_salida_riel"] or 0.0)) & (df["t"] <= r["t_apogeo"])]
        ax = self.fig.add_subplot(2, 3, 5)
        ax.plot(tramo["t"], tramo["alpha"], color=Tema.NARANJA, linewidth=1.4)
        estilo_ejes(ax, "Ángulo de ataque (riel a apogeo)", "Tiempo (s)", "α (°)")
        cursor(ax, "t", "alpha", Tema.NARANJA)
        self.tramo_alpha = (float(tramo["t"].iloc[0]), float(tramo["t"].iloc[-1])) if len(tramo) else (0.0, 0.0)

        ax = self.fig.add_subplot(2, 3, 6)
        ax.plot(df["x"], df["z"], color=Tema.TEXTO, linewidth=1.4)
        estilo_ejes(ax, "Trayectoria (plano de vuelo)", "x (m)", "z (m)")
        cursor(ax, "x", "z", Tema.TEXTO)

        leyenda = "Líneas punteadas: " + ", ".join(f"{nombre} ({instante:.1f} s)" for instante, _, nombre in eventos)
        self.fig.text(0.5, 0.008, leyenda, ha="center", fontsize=8, color=Tema.TENUE)
        self.fig.tight_layout(pad=1.4, rect=(0, 0.02, 1, 1))

    def _mover_cursor(self, instante):
        """Coloca el punto de cada gráfica en el instante elegido y actualiza la lectura."""
        if self.df is None:
            return
        df, t = self.df, float(instante)
        leer = lambda columna: float(np.interp(t, df["t"], df[columna]))
        for punto, columna_x, columna_y in self.cursores:
            if columna_y == "alpha" and not self.tramo_alpha[0] <= t <= self.tramo_alpha[1]:
                punto.set_data([], [])   # el ángulo de ataque solo se grafica hasta el apogeo
            else:
                punto.set_data([leer(columna_x)], [leer(columna_y)])
        self.lienzo.draw_idle()
        self.lectura.configure(text=f"t = {t:5.1f} s   z = {leer('z'):6.0f} m   v = {leer('velocidad'):5.1f} m/s   Mach {leer('mach'):.2f}")
