"""Pestaña Cohete."""
import customtkinter as ctk

from .componentes import AVISO_POSICION, COMPONENTES, GRUPOS
from .esquema import dibujar_cohete
from .tema import Tema, a_numero, estado_margen, fuente
from .widgets import Tarjeta, boton, campo, colocar_figura, deslizador, figura, nota, panel, titulo


class PestanaCohete(ctk.CTkFrame):
    """Lista de componentes, esquema del cohete que se puede tocar y campos de la pieza elegida."""

    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.seleccion = "tanque_vacio"
        self.estabilidad = None
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._crear_lista()
        self._crear_esquema()
        self.inspector = ctk.CTkScrollableFrame(self, fg_color=Tema.PANEL, border_color=Tema.BORDE, border_width=1,
                                                corner_radius=16, width=280)
        self.inspector.grid(row=0, column=2, sticky="nsew", padx=(8, 0))
        self.inspector.grid_columnconfigure(0, weight=1)
        self.seleccionar(self.seleccion)

    def _crear_lista(self):
        lista = ctk.CTkScrollableFrame(self, fg_color=Tema.PANEL, border_color=Tema.BORDE, border_width=1,
                                       corner_radius=16, width=250)
        lista.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        lista.grid_columnconfigure(0, weight=1)
        titulo(lista, "Componentes").grid(row=0, column=0, sticky="w", padx=8, pady=(6, 2))
        self.botones = {}
        fila = 1
        for grupo, color in GRUPOS.items():
            ctk.CTkLabel(lista, text=f"●  {grupo.upper()}", font=fuente(11), text_color=color, anchor="w").grid(
                row=fila, column=0, sticky="w", padx=10, pady=(10, 2))
            fila += 1
            for comp in (c for c in COMPONENTES if c.grupo == grupo):
                b = ctk.CTkButton(lista, text=comp.nombre, anchor="w", corner_radius=18, height=36, border_width=1,
                                  font=fuente(13), text_color=Tema.TEXTO, hover_color=Tema.BORDE,
                                  command=lambda c=comp.clave: self.seleccionar(c))
                b.grid(row=fila, column=0, sticky="ew", padx=4, pady=2)
                self.botones[comp.clave] = b
                fila += 1

    def _crear_esquema(self):
        centro = ctk.CTkFrame(self, fg_color="transparent")
        centro.grid(row=0, column=1, sticky="nsew")
        centro.grid_columnconfigure(0, weight=1)
        centro.grid_rowconfigure(0, weight=1)

        marco = panel(centro)
        marco.grid(row=0, column=0, sticky="nsew")
        marco.grid_columnconfigure(0, weight=1)
        marco.grid_rowconfigure(1, weight=1)
        titulo(marco, "Esquema").grid(row=0, column=0, sticky="w", padx=16, pady=(12, 0))
        nota(marco, "Toca una pieza para editarla. El CG y el margen cambian al escribir.").grid(
            row=0, column=0, sticky="e", padx=16, pady=(12, 0))
        self.fig = figura(7, 3)
        self.ax = self.fig.add_subplot(111)
        self.fig.subplots_adjust(left=0.03, right=0.98, top=0.95, bottom=0.2)
        self.lienzo = colocar_figura(self.fig, marco)
        self.lienzo.get_tk_widget().grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.lienzo.mpl_connect("button_press_event", self._al_tocar)

        tarjetas = ctk.CTkFrame(centro, fg_color="transparent")
        tarjetas.grid(row=1, column=0, sticky="ew", pady=(8, 0))
        self.tarjetas = {}
        for i, (clave, nombre) in enumerate((("masa", "Masa al despegue"), ("cg", "Centro de gravedad"),
                                             ("cp", "Centro de presión"), ("margen", "Margen estático"))):
            tarjetas.grid_columnconfigure(i, weight=1, uniform="tarjeta")
            self.tarjetas[clave] = Tarjeta(tarjetas, nombre)
            self.tarjetas[clave].grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 8, 0))

    def _al_tocar(self, evento):
        """Elige la pieza que está bajo el clic; si hay varias, la que se dibuja encima."""
        if evento.inaxes is not self.ax:
            return
        tocadas = [p for p in self.ax.patches if p.get_gid() and p.contains(evento)[0]]
        if tocadas:
            self.seleccionar(max(tocadas, key=lambda p: p.get_zorder()).get_gid())

    def seleccionar(self, clave):
        self.seleccion = clave
        for nombre, b in self.botones.items():
            elegido = nombre == clave
            b.configure(fg_color=Tema.SELECCION if elegido else "transparent",
                        border_color=Tema.AMARILLO if elegido else Tema.PANEL)
        self._llenar_inspector(next(c for c in COMPONENTES if c.clave == clave))
        self._dibujar()

    def _llenar_inspector(self, comp):
        for hijo in self.inspector.winfo_children():
            hijo.destroy()
        ctk.CTkLabel(self.inspector, text=comp.grupo.upper(), font=fuente(11), text_color=GRUPOS[comp.grupo],
                     anchor="w").grid(row=0, column=0, sticky="w", padx=8, pady=(6, 0))
        titulo(self.inspector, comp.nombre, 19).grid(row=1, column=0, sticky="w", padx=8, pady=(0, 6))
        fila = 2
        for c in comp.campos:
            variable = self.app.vars[c.param]
            campo(self.inspector, c.etiqueta, variable, c.unidad, c.opciones).grid(row=fila, column=0, sticky="ew", padx=8, pady=4)
            fila += 1
            if c.param == comp.campos[0].param:   # la masa también se puede mover con un deslizador
                deslizador(self.inspector, variable, 0, 20, 200, "{:.1f}").grid(row=fila, column=0, sticky="ew", padx=8)
                fila += 1
        nota(self.inspector, comp.aviso or AVISO_POSICION, wraplength=250).grid(row=fila, column=0, sticky="w", padx=8, pady=8)
        boton(self.inspector, "Restablecer valores del Xitle II", self.app.restablecer_cohete).grid(
            row=fila + 1, column=0, sticky="ew", padx=8, pady=(4, 8))

    def _dibujar(self):
        try:
            dibujar_cohete(self.ax, self.app.numero, self.seleccion, self.estabilidad)
        except (TypeError, ValueError):
            return   # hay un campo a medio escribir: se conserva el dibujo anterior
        self.lienzo.draw_idle()

    def refrescar(self, estabilidad):
        """Actualiza el esquema, las tarjetas y las masas de la lista con el último cálculo."""
        self.estabilidad = estabilidad
        self._dibujar()
        masas = {nombre: masa for nombre, masa, _, _ in estabilidad["filas"]} if estabilidad else {}
        for comp in COMPONENTES:
            masa = masas.get(comp.nombre, a_numero(self.app.vars[comp.campos[0].param].get()))
            texto = f"{masa:.2f} kg" if isinstance(masa, float) else "--"
            self.botones[comp.clave].configure(text=f"{comp.nombre}   ·   {texto}")
        if not estabilidad:
            for tarjeta in self.tarjetas.values():
                tarjeta.fijar("--")
            return
        e = estabilidad
        estado, color = estado_margen(e["margen"])
        self.tarjetas["masa"].fijar(f"{e['masa']:.1f} kg", f"{e['masa_seca']:.1f} kg sin propelente")
        self.tarjetas["cg"].fijar(f"{e['cg']:.2f} m", f"{e['cg_seco']:.2f} m sin propelente", Tema.AZUL)
        self.tarjetas["cp"].fijar(f"{e['cp']:.2f} m", f"longitud {e['longitud']:.3f} m", Tema.ROJO)
        self.tarjetas["margen"].fijar(f"{e['margen']:.2f} cal", estado, color)
