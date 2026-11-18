"""Pestaña Resultados."""
import time
from tkinter import filedialog, messagebox

import customtkinter as ctk
import numpy as np
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk

from Simulador.GUI import backend
from .graficas import PANELES, CapaMovil, Cursor, dibujar_serie, eventos_del_vuelo
from .tema import Tema, fuente
from .ventana_grafica import VentanaGrafica
from .widgets import Tarjeta, boton, colocar_figura, figura, panel


class PestanaResultados(ctk.CTkFrame):
    """Cifras del vuelo y seis gráficas con un cursor de tiempo común.

    El cursor se mueve de tres formas: con el control deslizante, pasando el ratón sobre una
    gráfica o con el botón de reproducir. Un doble clic sobre una gráfica la abre en grande.
    """

    TARJETAS = (("apogeo", "Apogeo"), ("vel_max", "Velocidad máxima"), ("riel", "Salida del riel"),
                ("impacto", "Impacto"), ("distancia", "Cayó a"), ("margen", "Margen estático mínimo"))
    VELOCIDADES = {"1×": 1.0, "5×": 5.0, "20×": 20.0}   # segundos de vuelo por segundo de reloj
    CUADRO_MS = 33                                       # pausa entre cuadros al reproducir

    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.df = self.resumen = None
        self.cursores = []
        self.instante = 0.0
        self.reproduciendo = False
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
        control.grid_columnconfigure(2, weight=1)
        self.boton_reproducir = boton(control, "▶  Reproducir", self.alternar_reproduccion, state="disabled", width=130)
        self.boton_reproducir.grid(row=0, column=0, padx=(12, 6), pady=8)
        self.velocidad = ctk.CTkOptionMenu(control, values=list(self.VELOCIDADES), width=70, height=36, corner_radius=18,
                                           fg_color=Tema.FONDO, button_color=Tema.BORDE_CAMPO, button_hover_color=Tema.TENUE,
                                           text_color=Tema.TEXTO, dropdown_fg_color=Tema.PANEL, font=fuente(13))
        self.velocidad.set("5×")
        self.velocidad.grid(row=0, column=1, padx=(0, 10))
        self.tiempo = ctk.CTkSlider(control, from_=0, to=1, progress_color=Tema.AMARILLO, button_color=Tema.AMARILLO,
                                    button_hover_color=Tema.AMARILLO_CLARO, fg_color=Tema.BORDE, command=self.ir_a,
                                    state="disabled")
        self.tiempo.grid(row=0, column=2, sticky="ew")
        self.lectura = ctk.CTkLabel(control, text="", font=fuente(12, mono=True), text_color=Tema.TEXTO, width=430, anchor="w")
        self.lectura.grid(row=0, column=3, padx=12)
        self.exportar = boton(control, "Exportar CSV", self.exportar_csv, state="disabled", border_color=Tema.TEXTO)
        self.exportar.grid(row=0, column=4, padx=(0, 12), pady=8)

        self.marco = panel(self)
        self.marco.grid(row=2, column=0, sticky="nsew")
        self.marco.grid_columnconfigure(0, weight=1)
        self.marco.grid_rowconfigure(0, weight=1)
        self.fig = figura(9, 5)
        self.lienzo = colocar_figura(self.fig, self.marco)
        self.lienzo.get_tk_widget().grid(row=0, column=0, sticky="nsew", padx=10, pady=(10, 0))
        self.barra = NavigationToolbar2Tk(self.lienzo, self.marco, pack_toolbar=False)   # zoom, desplazamiento y guardar imagen
        self.barra.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 6))
        self.capa = CapaMovil(self.lienzo)
        self.lienzo.mpl_connect("motion_notify_event", self._al_mover_raton)
        self.lienzo.mpl_connect("button_press_event", self._al_hacer_clic)
        self.limpiar()

    def limpiar(self, mensaje="Los resultados de la simulación se mostrarán aquí."):
        self.detener()
        self.df = self.resumen = None
        self.cursores = []
        self.capa.vaciar()
        self.fig.clear()
        self.fig.text(0.5, 0.5, mensaje, color=Tema.TENUE, ha="center", va="center", fontsize=12)
        self.lienzo.draw_idle()
        for control in (self.tiempo, self.exportar, self.boton_reproducir):
            control.configure(state="disabled")
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

        self.detener()
        self.t_final = float(df["t"].iloc[-1])
        self._graficar(df, r)
        for control in (self.exportar, self.boton_reproducir):
            control.configure(state="normal")
        self.tiempo.configure(state="normal", from_=0, to=self.t_final)
        self.ir_a(r["t_apogeo"])

    def _graficar(self, df, r):
        self.fig.clear()
        self.capa.vaciar()
        self.cursores = []
        cabeceo = df["theta"].to_numpy(dtype=float)
        for posicion, serie in enumerate(PANELES, start=1):
            ax = self.fig.add_subplot(2, 3, posicion)
            t, x, y = dibujar_serie(ax, df, r, serie)
            # En la trayectoria el cursor es un cohete pequeño que gira con el ángulo de cabeceo
            self.cursores.append(Cursor(self.capa, ax, serie, t, x, y, cabeceo=cabeceo if serie.x != "t" else None))
        self.lecturas = [c for c in self.cursores if c.serie.y in ("z", "velocidad", "mach") and c.serie.x == "t"]
        self.cabeceo = (df["t"].to_numpy(dtype=float), cabeceo)

        leyenda = "Líneas punteadas: " + ", ".join(f"{nombre} ({instante:.1f} s)" for instante, _, nombre in eventos_del_vuelo(r))
        self.fig.text(0.5, 0.008, leyenda + ".  Pasa el cursor sobre una gráfica para leerla; doble clic para ampliarla.",
                      ha="center", fontsize=8, color=Tema.TENUE)
        self.fig.tight_layout(pad=1.4, rect=(0, 0.02, 1, 1))
        self.lienzo.draw_idle()

    # ------------------------------------------------------------- Cursor de tiempo
    def ir_a(self, instante):
        """Lleva el cursor de todas las gráficas, el control deslizante y la lectura a un instante."""
        if self.df is None:
            return
        self.instante = t = float(min(max(float(instante), 0.0), self.t_final))
        self.tiempo.set(t)
        for cursor in self.cursores:
            cursor.mover(t)
        self.capa.actualizar()
        valores = "   ".join(c.serie.formato.format(c.valor(t)) for c in self.lecturas)
        self.lectura.configure(text=f"t = {t:5.1f} s   {valores}   θ = {np.interp(t, *self.cabeceo):.0f}°")

    def _sin_herramienta(self):
        """True si no está activo el zoom ni el desplazamiento de la barra de matplotlib."""
        return getattr(self.barra.mode, "name", "NONE") == "NONE"

    def _cursor_de(self, evento):
        return next((c for c in self.cursores if c.ax is evento.inaxes), None)

    def _al_mover_raton(self, evento):
        cursor = self._cursor_de(evento)
        if cursor is None or self.reproduciendo or not self._sin_herramienta():
            return
        instante = cursor.instante_en(evento)
        if instante is not None:
            self.ir_a(instante)

    def _al_hacer_clic(self, evento):
        cursor = self._cursor_de(evento)
        if cursor is not None and evento.dblclick and self._sin_herramienta():
            VentanaGrafica(self, self.df, self.resumen, cursor.serie)

    # ----------------------------------------------------------------- Reproducción
    def alternar_reproduccion(self):
        if self.reproduciendo:
            return self.detener()
        if self.df is None:
            return
        if self.instante >= self.t_final - 1e-6:
            self.ir_a(0.0)   # ya estaba al final: vuelve a empezar
        self.reproduciendo = True
        self.boton_reproducir.configure(text="❚❚  Pausar")
        self._ultimo_cuadro = time.perf_counter()
        self.after(self.CUADRO_MS, self._avanzar)

    def detener(self):
        self.reproduciendo = False
        self.boton_reproducir.configure(text="▶  Reproducir")

    def _avanzar(self):
        """Avanza el vuelo según el tiempo real transcurrido, para que la rapidez no dependa del equipo."""
        if not self.reproduciendo or self.df is None:
            return
        ahora = time.perf_counter()
        paso = (ahora - self._ultimo_cuadro) * self.VELOCIDADES[self.velocidad.get()]
        self._ultimo_cuadro = ahora
        self.ir_a(self.instante + paso)
        if self.instante >= self.t_final - 1e-6:
            return self.detener()
        self.after(self.CUADRO_MS, self._avanzar)
