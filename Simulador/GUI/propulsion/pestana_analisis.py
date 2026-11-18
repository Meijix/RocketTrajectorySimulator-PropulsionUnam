"""Pestaña Análisis (CG-CP)."""
import tkinter as tk
from tkinter import messagebox, ttk

import customtkinter as ctk

from .tema import Tema, estado_margen, fuente_tk
from .widgets import Selector, Tarjeta, boton, nota, panel, titulo


class PestanaAnalisis(ctk.CTkFrame):
    """Tabla de masa, CG y CP por componente, y margen estático al despegue y sin propelente."""

    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.estabilidad = None
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        marco = panel(self)
        marco.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        marco.grid_columnconfigure(0, weight=1)
        marco.grid_rowconfigure(1, weight=1)
        titulo(marco, "Componentes").grid(row=0, column=0, sticky="w", padx=16, pady=(12, 4))
        nota(marco, "Posiciones medidas desde la punta de la nariz.").grid(row=0, column=0, sticky="e", padx=16, pady=(12, 4))
        estilo = ttk.Style(self)
        estilo.theme_use("default")
        estilo.configure("Oscuro.Treeview", background=Tema.PANEL, fieldbackground=Tema.PANEL, foreground=Tema.TEXTO,
                         rowheight=30, borderwidth=0, font=fuente_tk(12, mono=True))
        estilo.configure("Oscuro.Treeview.Heading", background="#1E1E1E", foreground=Tema.TENUE, borderwidth=0,
                         font=fuente_tk(12))
        estilo.map("Oscuro.Treeview", background=[("selected", "#3A3712")], foreground=[("selected", Tema.AMARILLO)])
        columnas = (("componente", "Componente", 220, "w"), ("masa", "Masa (kg)", 110, "e"),
                    ("cg", "Centro de gravedad (m)", 170, "e"), ("cp", "Centro de presión (m)", 170, "e"))
        self.tabla = ttk.Treeview(marco, columns=[c[0] for c in columnas], show="headings", style="Oscuro.Treeview")
        for clave, texto, ancho, ancla in columnas:
            self.tabla.heading(clave, text=texto)
            self.tabla.column(clave, width=ancho, anchor=ancla)
        self.tabla.tag_configure("total", foreground=Tema.AMARILLO)
        self.tabla.grid(row=1, column=0, sticky="nsew", padx=16, pady=(0, 16))

        lado = ctk.CTkFrame(self, fg_color="transparent")
        lado.grid(row=0, column=1, sticky="nsew")
        lado.grid_columnconfigure((0, 1), weight=1, uniform="lado")
        boton(lado, "Calcular CG y CP", self.calcular, border_color=Tema.TEXTO).grid(row=0, column=0, columnspan=2, sticky="ew")
        self.estado = Selector(lado, (("despegue", "Al despegue"), ("seco", "Sin propelente")), lambda _: self._mostrar(), alto=36)
        self.estado.grid(row=1, column=0, columnspan=2, sticky="ew", pady=8)
        self.estado.grid_columnconfigure((0, 1), weight=1)
        self.tarjetas = {}
        for i, (clave, nombre) in enumerate((("masa", "Masa total"), ("longitud", "Longitud"), ("cg", "CG"), ("cp", "CP"))):
            self.tarjetas[clave] = Tarjeta(lado, nombre)
            self.tarjetas[clave].grid(row=2 + i // 2, column=i % 2, sticky="nsew", padx=(0, 4) if i % 2 == 0 else (4, 0), pady=4)
        self.margen = Tarjeta(lado, "Margen estático")
        self.margen.grid(row=4, column=0, columnspan=2, sticky="ew", pady=4)
        self.barra = tk.Canvas(self.margen, height=44, bg=Tema.PANEL, highlightthickness=0)
        self.barra.pack(fill="x", padx=14, pady=(0, 10))
        self.barra.bind("<Configure>", lambda _: self._dibujar_barra())
        nota(lado, "Margen estático = (CP − CG) / diámetro. Menos de 1 calibre es inestable; "
                   "de 1.5 en adelante, estable.", wraplength=300).grid(row=5, column=0, columnspan=2, sticky="w", pady=4)
        self.estado.elegir("despegue", avisar=False)

    def calcular(self):
        """Recalcula ahora mismo y, si no se puede, explica por qué."""
        estabilidad, error = self.app.calcular_estabilidad()
        if error:
            messagebox.showerror("Error de estabilidad", f"No se pudo calcular la estabilidad:\n\n{error}")
        self.app.refrescar()

    def refrescar(self, estabilidad):
        self.estabilidad = estabilidad
        self.tabla.delete(*self.tabla.get_children())
        if estabilidad:
            for nombre, masa, cg, cp in estabilidad["filas"]:
                self.tabla.insert("", "end", values=(nombre, f"{masa:.3f}", f"{cg:.3f}", "N/A" if cp is None else f"{cp:.3f}"))
            e = estabilidad
            self.tabla.insert("", "end", tags=("total",), values=("TOTAL (despegue)", f"{e['masa']:.3f}", f"{e['cg']:.3f}", f"{e['cp']:.3f}"))
            self.tabla.insert("", "end", tags=("total",), values=("TOTAL (sin propelente)", f"{e['masa_seca']:.3f}", f"{e['cg_seco']:.3f}", f"{e['cp']:.3f}"))
        self._mostrar()

    def _valores(self):
        """Masa, CG y margen del estado elegido (al despegue o sin propelente)."""
        e = self.estabilidad
        if self.estado.valor == "seco":
            return e["masa_seca"], e["cg_seco"], e["margen_seco"]
        return e["masa"], e["cg"], e["margen"]

    def _mostrar(self):
        if not self.estabilidad:
            for tarjeta in (*self.tarjetas.values(), self.margen):
                tarjeta.fijar("--")
            return self._dibujar_barra()
        masa, cg, margen = self._valores()
        estado, color = estado_margen(margen)
        self.tarjetas["masa"].fijar(f"{masa:.3f} kg")
        self.tarjetas["longitud"].fijar(f"{self.estabilidad['longitud']:.3f} m")
        self.tarjetas["cg"].fijar(f"{cg:.3f} m", color=Tema.AZUL)
        self.tarjetas["cp"].fijar(f"{self.estabilidad['cp']:.3f} m", color=Tema.ROJO)
        self.margen.fijar(f"{margen:.2f} cal", estado, color)
        self._dibujar_barra()

    def _dibujar_barra(self):
        """Barra de 0 a 8 calibres con las zonas inestable, marginal y estable y una marca en el valor."""
        c, ancho, tope = self.barra, self.barra.winfo_width(), 8.0
        c.delete("all")
        if ancho < 20:
            return
        for inicio, fin, color in ((0, 1, "#8A2A20"), (1, 1.5, "#8A7F1A"), (1.5, tope, "#1E6B28")):
            c.create_rectangle(ancho * inicio / tope, 8, ancho * fin / tope, 20, fill=color, outline="")
        for valor, texto, ancla in ((0, "0", "w"), (1.5, "1.5", "center"), (tope, "8", "e")):
            c.create_text(ancho * valor / tope, 34, text=texto, fill=Tema.TENUE, anchor=ancla, font=fuente_tk(10, mono=True))
        if self.estabilidad:
            x = ancho * min(max(self._valores()[2], 0), tope) / tope
            c.create_rectangle(x - 2, 2, x + 2, 26, fill=Tema.TEXTO, outline="")
