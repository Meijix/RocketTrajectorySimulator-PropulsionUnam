"""Constructores de los controles de la interfaz, todos con el mismo estilo."""
import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from .tema import Tema, a_numero, fuente


def panel(master, **opciones):
    return ctk.CTkFrame(master, fg_color=Tema.PANEL, border_color=Tema.BORDE, border_width=1,
                        corner_radius=16, **opciones)


def titulo(master, texto, tam=16):
    return ctk.CTkLabel(master, text=texto, font=fuente(tam, negrita=True), text_color=Tema.TEXTO, anchor="w")


def nota(master, texto, **opciones):
    return ctk.CTkLabel(master, text=texto, font=fuente(11), text_color=Tema.TENUE, anchor="w",
                        justify="left", **opciones)


def boton(master, texto, comando, principal=False, **opciones):
    """Botón en forma de píldora: amarillo si es la acción principal, de contorno si no."""
    estilo = dict(corner_radius=20, height=40)
    if principal:
        estilo.update(fg_color=Tema.AMARILLO, hover_color=Tema.AMARILLO_CLARO, text_color="#0A0A0A",
                      font=fuente(14, negrita=True))
    else:
        estilo.update(fg_color="transparent", hover_color=Tema.BORDE, text_color=Tema.TEXTO,
                      border_width=1, border_color=Tema.BORDE_CAMPO, font=fuente(13))
    estilo.update(opciones)
    return ctk.CTkButton(master, text=texto, command=comando, **estilo)


def entrada(master, variable, **opciones):
    return ctk.CTkEntry(master, textvariable=variable, fg_color=Tema.FONDO, border_color=Tema.BORDE_CAMPO,
                        text_color=Tema.TEXTO, corner_radius=18, height=36, font=fuente(13, mono=True), **opciones)


def campo(master, etiqueta, variable, unidad="", opciones=None):
    """Etiqueta arriba y, debajo, una casilla (o un menú si se dan opciones) con su unidad."""
    marco = ctk.CTkFrame(master, fg_color="transparent")
    marco.grid_columnconfigure(0, weight=1)
    ctk.CTkLabel(marco, text=etiqueta, font=fuente(12), text_color=Tema.TEXTO_2, anchor="w").grid(
        row=0, column=0, columnspan=2, sticky="w")
    if opciones:
        control = ctk.CTkOptionMenu(marco, variable=variable, values=list(opciones), fg_color=Tema.FONDO,
                                    button_color=Tema.BORDE_CAMPO, button_hover_color=Tema.TENUE,
                                    text_color=Tema.TEXTO, dropdown_fg_color=Tema.PANEL, corner_radius=18,
                                    height=36, font=fuente(13))
    else:
        control = entrada(marco, variable)
    control.grid(row=1, column=0, sticky="ew")
    if unidad:
        ctk.CTkLabel(marco, text=unidad, font=fuente(12), text_color=Tema.TENUE, width=24).grid(row=1, column=1, padx=(6, 0))
    marco.control = control
    return marco


def deslizador(master, variable, desde, hasta, pasos, formato="{:.0f}"):
    """Control deslizante ligado a una variable de texto (la misma que usa la casilla)."""
    control = ctk.CTkSlider(master, from_=desde, to=hasta, number_of_steps=pasos, width=120, progress_color=Tema.AMARILLO,
                            button_color=Tema.AMARILLO, button_hover_color=Tema.AMARILLO_CLARO, fg_color=Tema.BORDE,
                            command=lambda valor: variable.set(formato.format(valor)))

    def seguir_variable(*_):
        valor = a_numero(variable.get())
        if isinstance(valor, float) and control.winfo_exists():
            control.set(min(max(valor, desde), hasta))

    # La variable vive más que el control (los campos del cohete se reconstruyen al cambiar de pieza)
    rastro = variable.trace_add("write", seguir_variable)
    control.bind("<Destroy>", lambda _: variable.trace_remove("write", rastro))
    seguir_variable()
    return control


class Selector(ctk.CTkFrame):
    """Grupo de botones del que solo uno está elegido (pestañas, modos, recuperación)."""

    def __init__(self, master, opciones, al_elegir, vertical=False, alto=40, ancho=140):
        """`ancho` es el ancho mínimo de cada botón; si el texto no cabe, el botón crece."""
        super().__init__(master, fg_color="transparent")
        self.al_elegir = al_elegir
        self.valor = None
        self.botones = {}
        for i, (valor, texto) in enumerate(opciones):
            b = ctk.CTkButton(self, text=texto, corner_radius=alto // 2, height=alto, width=ancho, border_width=1,
                              font=fuente(13), command=lambda v=valor: self.elegir(v))
            if vertical:
                b.grid(row=i, column=0, sticky="ew", pady=3)
                self.grid_columnconfigure(0, weight=1)
            else:
                b.grid(row=0, column=i, sticky="ew", padx=3)
            self.botones[valor] = b

    def elegir(self, valor, avisar=True):
        self.valor = valor
        for clave, b in self.botones.items():
            if clave == valor:
                b.configure(fg_color=Tema.AMARILLO, hover_color=Tema.AMARILLO_CLARO, text_color="#0A0A0A",
                            border_color=Tema.AMARILLO)
            else:
                b.configure(fg_color="#1A1A1A", hover_color=Tema.BORDE, text_color=Tema.TEXTO,
                            border_color="#3A3A3A")
        if avisar:
            self.al_elegir(valor)


class Tarjeta(ctk.CTkFrame):
    """Cifra destacada con su nombre y una línea de detalle."""

    def __init__(self, master, nombre, destacada=False):
        super().__init__(master, fg_color=Tema.PANEL, border_width=1, corner_radius=16,
                         border_color=Tema.AMARILLO if destacada else Tema.BORDE)
        self.color = Tema.AMARILLO if destacada else Tema.TEXTO
        ctk.CTkLabel(self, text=nombre, font=fuente(12), text_color=Tema.TENUE, anchor="w").pack(
            fill="x", padx=14, pady=(10, 0))
        self.valor = ctk.CTkLabel(self, text="--", font=fuente(22, negrita=True), text_color=self.color, anchor="w")
        self.valor.pack(fill="x", padx=14)
        self.detalle = ctk.CTkLabel(self, text="", font=fuente(11), text_color=Tema.TEXTO_2, anchor="w")
        self.detalle.pack(fill="x", padx=14, pady=(0, 10))

    def fijar(self, valor, detalle="", color=None):
        self.valor.configure(text=valor, text_color=color or self.color)
        self.detalle.configure(text=detalle)


def figura(ancho, alto):
    return Figure(figsize=(ancho, alto), dpi=100, facecolor=Tema.PANEL)


def estilo_ejes(ax, titulo_ejes="", xlabel="", ylabel=""):
    """Aplica el tema oscuro a unos ejes de matplotlib."""
    ax.set_facecolor(Tema.PANEL)
    ax.set_title(titulo_ejes, color=Tema.TEXTO, fontsize=10)
    ax.set_xlabel(xlabel, color=Tema.TENUE, fontsize=8)
    ax.set_ylabel(ylabel, color=Tema.TENUE, fontsize=8)
    ax.tick_params(colors=Tema.TENUE, labelsize=8)
    ax.grid(True, color=Tema.BORDE, linewidth=0.6)
    for lado in ax.spines.values():
        lado.set_color(Tema.BORDE_CAMPO)


def colocar_figura(fig, master):
    """Pone la figura en un widget que se adapta al espacio que le dé la rejilla."""
    lienzo = FigureCanvasTkAgg(fig, master=master)
    # Tamaño pedido pequeño: así la figura se encoge en pantallas chicas en vez de salirse de la ventana
    lienzo.get_tk_widget().configure(bg=Tema.PANEL, highlightthickness=0, width=240, height=120)
    return lienzo
