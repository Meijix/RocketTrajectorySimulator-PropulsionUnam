"""Pestaña Tablas de Datos."""
import os
from dataclasses import dataclass
from tkinter import filedialog, messagebox

import customtkinter as ctk
import pandas as pd

from .tema import Tema, fuente
from .widgets import boton, colocar_figura, estilo_ejes, figura, nota, panel, titulo


@dataclass(frozen=True)
class Tabla:
    clave: str
    nombre: str
    columnas: tuple       # columnas que necesita el simulador; la primera es el eje x
    grafica: str
    eje_x: str
    eje_y: str
    color: str


TABLAS = (
    Tabla("thrust", "Empuje", ("time", "thrust"), "Curva de empuje", "Tiempo (s)", "Empuje (N)", Tema.ROJO),
    Tabla("drag", "Arrastre", ("mach", "cd"), "Cd contra número de Mach", "Mach", "Cd", Tema.VERDE),
    Tabla("mass", "Masa del motor", ("Time (s)", "Oxidizer Mass (kg)", "Fuel Mass (kg)"),
          "Masa de propelente (oxidante + grano)", "Tiempo (s)", "Masa (kg)", Tema.AZUL),
)


def leer_tabla(tabla, ruta):
    """Lee un CSV y comprueba sus columnas. Devuelve (x, y); en la masa, y es oxidante más grano."""
    datos = pd.read_csv(ruta)
    datos.columns = [str(c).strip() for c in datos.columns]
    faltan = [c for c in tabla.columnas if c not in datos.columns]
    if faltan:
        raise ValueError(f"El archivo debe tener las columnas {list(tabla.columnas)}; faltan {faltan}.")
    x = pd.to_numeric(datos[tabla.columnas[0]], errors="coerce")
    y = sum(pd.to_numeric(datos[c], errors="coerce") for c in tabla.columnas[1:])
    limpio = pd.DataFrame({"x": x, "y": y}).dropna()
    return limpio["x"].to_numpy(), limpio["y"].to_numpy()


class PestanaTablas(ctk.CTkFrame):
    """Importa y grafica las tablas de empuje, arrastre y masa del motor."""

    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.datos = {}
        self.visible = None
        self.grid_rowconfigure(1, weight=1)
        self.archivos, self.estados, self.marcos = {}, {}, {}
        for i, tabla in enumerate(TABLAS):
            self.grid_columnconfigure(i, weight=1, uniform="tabla")
            marco = panel(self)
            marco.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 8, 0))
            marco.grid_columnconfigure((0, 1), weight=1)
            titulo(marco, tabla.nombre).grid(row=0, column=0, sticky="w", padx=16, pady=(12, 0))
            self.estados[tabla.clave] = ctk.CTkLabel(marco, text="", font=fuente(11), corner_radius=10)
            self.estados[tabla.clave].grid(row=0, column=1, sticky="e", padx=16, pady=(12, 0))
            self.archivos[tabla.clave] = ctk.CTkLabel(marco, text="", font=fuente(12, mono=True), text_color=Tema.TEXTO_2, anchor="w")
            self.archivos[tabla.clave].grid(row=1, column=0, columnspan=2, sticky="ew", padx=16)
            nota(marco, "Columnas: " + ", ".join(tabla.columnas)).grid(row=2, column=0, columnspan=2, sticky="w", padx=16)
            boton(marco, "Importar CSV", lambda t=tabla: self.importar(t)).grid(row=3, column=0, sticky="ew", padx=(16, 4), pady=12)
            boton(marco, "Visualizar", lambda t=tabla: self.visualizar(t)).grid(row=3, column=1, sticky="ew", padx=(4, 16), pady=12)
            self.marcos[tabla.clave] = marco

        grafica = panel(self)
        grafica.grid(row=1, column=0, columnspan=3, sticky="nsew", pady=(8, 0))
        grafica.grid_columnconfigure(0, weight=1)
        grafica.grid_rowconfigure(0, weight=1)
        self.fig = figura(8, 4)
        self.ax = self.fig.add_subplot(111)
        self.lienzo = colocar_figura(self.fig, grafica)
        self.lienzo.get_tk_widget().grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.aviso = nota(grafica, "")
        self.aviso.grid(row=1, column=0, sticky="w", padx=16, pady=(0, 10))

        for tabla in TABLAS:
            self.cargar(tabla, self.app.rutas.get(tabla.clave), avisar=False)
        if TABLAS[0].clave in self.datos:
            self.visualizar(TABLAS[0])

    def importar(self, tabla):
        ruta = filedialog.askopenfilename(title=f"Importar {tabla.nombre}", filetypes=[("CSV", "*.csv"), ("Todos", "*.*")])
        if ruta and self.cargar(tabla, ruta):
            self.visualizar(tabla)
            self.app.al_cambiar()

    def cargar(self, tabla, ruta, avisar=True):
        """Lee el archivo y lo deja como la tabla en uso. Devuelve True si se pudo."""
        try:
            if not ruta or not os.path.isfile(ruta):
                raise ValueError("No se encontró el archivo.")
            self.datos[tabla.clave] = leer_tabla(tabla, ruta)
        except Exception as error:
            if avisar:
                messagebox.showerror("Error al cargar CSV", f"No se pudo leer el archivo.\n{error}")
            if tabla.clave not in self.datos:
                self.estados[tabla.clave].configure(text="  Sin cargar  ", fg_color="#4A1A15", text_color="#FFB3AA")
            return False
        self.app.rutas[tabla.clave] = ruta
        self.archivos[tabla.clave].configure(text=os.path.basename(ruta))
        self.estados[tabla.clave].configure(text="  Cargado  ", fg_color="#123A17", text_color="#8BEF94")
        return True

    def visualizar(self, tabla):
        if tabla.clave not in self.datos:
            messagebox.showwarning("Sin datos", f"Cargue un archivo de {tabla.nombre.lower()}.")
            return
        self.visible = tabla
        for clave, marco in self.marcos.items():
            marco.configure(border_color=Tema.AMARILLO if clave == tabla.clave else Tema.BORDE)
        x, y = self.datos[tabla.clave]
        self.ax.clear()
        self.ax.plot(x, y, color=tabla.color, linewidth=1.8)
        self.ax.fill_between(x, y, color=tabla.color, alpha=0.14)
        estilo_ejes(self.ax, tabla.grafica, tabla.eje_x, tabla.eje_y)
        self.fig.tight_layout()
        self.lienzo.draw_idle()
        self.aviso.configure(text=self._resumen(tabla, x, y))

    def _resumen(self, tabla, x, y):
        texto = f"{len(x)} filas · {tabla.eje_x.split(' (')[0].lower()} de {x.min():g} a {x.max():g} · máximo {y.max():.4g}"
        if tabla.clave == "mass" and "thrust" in self.datos:
            fin_empuje = self.datos["thrust"][0].max()
            if abs(x.max() - fin_empuje) > 0.05 * fin_empuje:
                texto += (f"\nEsta tabla dura {x.max():g} s y el empuje {fin_empuje:g} s: el simulador conserva las masas "
                          "inicial y final y consume el propelente en proporción al impulso.")
        return texto
