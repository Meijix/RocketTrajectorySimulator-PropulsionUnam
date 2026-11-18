"""Ventana con una sola gráfica del vuelo en grande, con zoom y lectura al pasar el cursor."""
import tkinter as tk

import customtkinter as ctk
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk

from .graficas import SERIES, CapaMovil, Cursor, dibujar_serie
from .tema import Tema, fuente
from .widgets import campo, colocar_figura, figura, nota, panel


class VentanaGrafica(ctk.CTkToplevel):
    """Se abre con doble clic sobre una gráfica de Resultados. Un menú cambia la variable."""

    def __init__(self, master, df, resumen, serie):
        super().__init__(master)
        self.df, self.resumen = df, resumen
        self.series = {s.nombre: s for s in SERIES if s.y in df.columns and s.x in df.columns}
        self.cursor = None
        self.title("Gráfica del vuelo")
        self.geometry("1000x640")
        self.configure(fg_color=Tema.FONDO)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        arriba = ctk.CTkFrame(self, fg_color="transparent")
        arriba.grid(row=0, column=0, sticky="ew", padx=16, pady=(12, 4))
        arriba.grid_columnconfigure(1, weight=1)
        self.variable = tk.StringVar(value=serie.nombre)
        self.variable.trace_add("write", lambda *_: self._graficar())
        menu = campo(arriba, "Variable", self.variable, opciones=tuple(self.series))
        menu.control.configure(width=300)
        menu.grid(row=0, column=0, sticky="w")
        self.lectura = ctk.CTkLabel(arriba, text="", font=fuente(14, mono=True), text_color=Tema.TEXTO, anchor="e")
        self.lectura.grid(row=0, column=1, sticky="e", padx=8)

        marco = panel(self)
        marco.grid(row=1, column=0, sticky="nsew", padx=16, pady=(4, 8))
        marco.grid_columnconfigure(0, weight=1)
        marco.grid_rowconfigure(0, weight=1)
        self.fig = figura(9, 5)
        self.ax = self.fig.add_subplot(111)
        self.lienzo = colocar_figura(self.fig, marco)
        self.lienzo.get_tk_widget().grid(row=0, column=0, sticky="nsew", padx=10, pady=(10, 0))
        self.barra = NavigationToolbar2Tk(self.lienzo, marco, pack_toolbar=False)
        self.barra.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 6))
        nota(self, "Pasa el cursor sobre la curva para leer el valor. La barra sirve para acercar, desplazar y "
                   "guardar la imagen.").grid(row=2, column=0, sticky="w", padx=18, pady=(0, 10))

        self.capa = CapaMovil(self.lienzo)
        self.lienzo.mpl_connect("motion_notify_event", self._al_mover)
        self._graficar()

    def _graficar(self):
        serie = self.series.get(self.variable.get())
        if serie is None:
            return
        self.capa.vaciar()
        t, x, y = dibujar_serie(self.ax, self.df, self.resumen, serie)
        self.cursor = Cursor(self.capa, self.ax, serie, t, x, y)
        self.fig.tight_layout(pad=1.4)
        self.lectura.configure(text="")
        self.lienzo.draw_idle()

    def _al_mover(self, evento):
        if evento.inaxes is not self.ax or self.cursor is None:
            return
        instante = self.cursor.instante_en(evento)
        if instante is None:
            return
        self.cursor.mover(instante)
        self.capa.actualizar()
        self.lectura.configure(text=f"t = {instante:.2f} s    " + self.cursor.serie.formato.format(self.cursor.valor(instante)))
