"""Pestaña Simulación."""
import contextlib
import os
import tkinter as tk

import customtkinter as ctk
import numpy as np

from Simulador.GUI import backend, mapa
from .pestana_tablas import TABLAS
from .tema import Tema, a_numero, estado_margen, fuente, fuente_tk
from .widgets import Selector, boton, campo, colocar_figura, deslizador, figura, nota, panel, titulo


class PestanaSimulacion(ctk.CTkScrollableFrame):
    """Sitio, atmósfera, viento, riel y parámetros de la integración.

    Es la pestaña con más campos, así que se puede desplazar si la ventana es baja.
    """

    MODOS_VIENTO = (("perfil", "Perfil del día"), ("constante", "Constante"))
    RECUPERACIONES = ("Vuelo libre", "Drogue en el apogeo", "Dos etapas: drogue y principal")

    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        niveles = backend.dia_de_vuelo.cargar_condiciones()["viento"]["niveles"]
        self.viento_superficie = float(niveles[0]["direccion_desde_grados"])
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure((0, 1, 2), weight=1, uniform="sim")
        self._crear_sitio()
        self._crear_viento_y_riel()
        self._crear_integracion()
        self.after(600, self.cargar_mapa_sitio)

    # ----------------------------------------------------------------- Sitio
    def _crear_sitio(self):
        v = self.app.vars
        marco = panel(self)
        marco.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        marco.grid_columnconfigure((0, 1), weight=1)
        titulo(marco, "Sitio de lanzamiento").grid(row=0, column=0, columnspan=2, sticky="w", padx=16, pady=(12, 4))

        self.fig_mapa = figura(3.2, 2)
        self.ax_mapa = self.fig_mapa.add_axes([0, 0, 1, 1])
        self.lienzo_mapa = colocar_figura(self.fig_mapa, marco)
        self.lienzo_mapa.get_tk_widget().configure(height=190)
        self.lienzo_mapa.get_tk_widget().grid(row=1, column=0, columnspan=2, sticky="ew", padx=16, pady=4)
        self._mensaje_mapa("Cargando el mapa del sitio...")

        campos = (("launch_lat", "Latitud (°)"), ("launch_lon", "Longitud (°)"), ("launch_alt", "Altitud (m s. n. m.)"),
                  ("launch_date", "Fecha (AAAA-MM-DD)"), ("atm_pressure_hpa", "Presión en el sitio (hPa)"),
                  ("atm_delta_t", "ΔT respecto a ISA (°C)"))
        for i, (param, etiqueta) in enumerate(campos):
            campo(marco, etiqueta, v[param]).grid(row=2 + i // 2, column=i % 2, sticky="ew", padx=(16 if i % 2 == 0 else 6, 6 if i % 2 == 0 else 16), pady=4)
        deslizador(marco, v["atm_delta_t"], -30, 30, 60).grid(row=5, column=0, columnspan=2, sticky="ew", padx=16)
        self.temperatura = nota(marco, "", wraplength=280)
        self.temperatura.grid(row=6, column=0, columnspan=2, sticky="w", padx=16)
        boton(marco, "Actualizar mapa del sitio", self.cargar_mapa_sitio).grid(row=7, column=0, columnspan=2, sticky="ew", padx=16, pady=12)

    def _mensaje_mapa(self, texto):
        self.ax_mapa.clear()
        self.ax_mapa.set_facecolor("#1C1C1C")
        self.ax_mapa.set_xticks([])
        self.ax_mapa.set_yticks([])
        self.ax_mapa.text(0.5, 0.5, texto, color=Tema.TENUE, fontsize=9, ha="center", va="center",
                          transform=self.ax_mapa.transAxes)
        self.lienzo_mapa.draw_idle()

    def cargar_mapa_sitio(self):
        """Descarga en otro hilo el mapa de los alrededores del sitio y lo dibuja al terminar."""
        lat, lon = a_numero(self.app.vars["launch_lat"].get()), a_numero(self.app.vars["launch_lon"].get())
        if not (isinstance(lat, float) and isinstance(lon, float)):
            return self._mensaje_mapa("Latitud o longitud no válidas")
        self._mensaje_mapa("Cargando el mapa del sitio...")
        alto, ancho = 0.02, 0.05   # grados: unos 2 km al norte y al sur, y más a los lados porque el recuadro es apaisado
        tarea = self.app.hilos.submit(mapa.descargar_mosaico, [lat - alto, lat + alto], [lon - ancho, lon + ancho], 0.0)
        self._esperar_mapa(tarea, lat, lon)

    def _esperar_mapa(self, tarea, lat, lon):
        if not tarea.done():
            self.after(200, self._esperar_mapa, tarea, lat, lon)
            return
        fondo = tarea.result()
        if not fondo:
            return self._mensaje_mapa(f"Sin conexión: no se pudo descargar el mapa\n{lat:.5f}°, {lon:.5f}°")
        self.ax_mapa.clear()
        self.ax_mapa.imshow(fondo["imagen"], extent=fondo["extent"], interpolation="bilinear")
        x, y = mapa.a_pixeles(lat, lon, fondo["zoom"])
        self.ax_mapa.plot(x, y, marker="^", color=Tema.VERDE, markersize=11, markeredgecolor="white")
        izq, der, abajo, arriba = fondo["limites"]
        self.ax_mapa.set_xlim(izq, der)
        self.ax_mapa.set_ylim(abajo, arriba)
        self.ax_mapa.set_xticks([])
        self.ax_mapa.set_yticks([])
        self.ax_mapa.text(0.99, 0.01, fondo["atribucion"], transform=self.ax_mapa.transAxes, ha="right", va="bottom",
                          fontsize=6, bbox=dict(facecolor="white", alpha=0.7, edgecolor="none", pad=1))
        self.lienzo_mapa.draw_idle()

    # --------------------------------------------------------- Viento y riel
    def _crear_viento_y_riel(self):
        v = self.app.vars
        marco = panel(self)
        marco.grid(row=0, column=1, sticky="nsew", padx=4)
        marco.grid_columnconfigure((0, 1), weight=1)
        titulo(marco, "Viento y riel").grid(row=0, column=0, columnspan=2, sticky="w", padx=16, pady=(12, 4))

        self.brujula = tk.Canvas(marco, width=170, height=170, bg=Tema.PANEL, highlightthickness=0)
        self.brujula.grid(row=1, column=0, padx=(16, 4), pady=4)
        lado = ctk.CTkFrame(marco, fg_color="transparent")
        lado.grid(row=1, column=1, sticky="nsew", padx=(4, 16))
        self.texto_riel = ctk.CTkLabel(lado, text="", font=fuente(13), text_color=Tema.AMARILLO, anchor="w")
        self.texto_riel.pack(fill="x", pady=(14, 0))
        self.texto_viento = ctk.CTkLabel(lado, text="", font=fuente(13), text_color=Tema.AZUL, anchor="w")
        self.texto_viento.pack(fill="x")
        self.texto_relativo = nota(lado, "", wraplength=170)
        self.texto_relativo.pack(fill="x", pady=(4, 0))
        self.riel = tk.Canvas(lado, width=110, height=74, bg=Tema.PANEL, highlightthickness=0)
        self.riel.pack(anchor="w", pady=(6, 0))

        campo(marco, "Azimut del riel (°)", v["rail_azimuth"]).grid(row=2, column=0, sticky="ew", padx=(16, 6), pady=4)
        campo(marco, "Elevación (°)", v["rail_angle"]).grid(row=2, column=1, sticky="ew", padx=(6, 16), pady=4)
        deslizador(marco, v["rail_azimuth"], 0, 359, 359).grid(row=3, column=0, sticky="ew", padx=(16, 6))
        deslizador(marco, v["rail_angle"], 60, 90, 30).grid(row=3, column=1, sticky="ew", padx=(6, 16))
        campo(marco, "Longitud del riel (m)", v["rail_len"]).grid(row=4, column=0, sticky="ew", padx=(16, 6), pady=4)

        self.modo_viento = Selector(marco, self.MODOS_VIENTO, self._al_elegir_viento, alto=36)
        self.modo_viento.grid(row=5, column=0, columnspan=2, sticky="ew", padx=13, pady=(10, 4))
        self.modo_viento.grid_columnconfigure((0, 1), weight=1)

        self.campos_constante = []
        campos = (("wind_base_speed", "Velocidad base (m/s)", True), ("wind_from", "Viene de (°)", True),
                  ("wind_mean_speed", "Ráfaga media (m/s)", False), ("wind_speed_var", "Variación ráfaga (m/s)", False),
                  ("wind_angle_var", "Variación ángulo (°)", False), ("wind_seed", "Semilla (opcional)", False))
        for i, (param, etiqueta, solo_constante) in enumerate(campos):
            c = campo(marco, etiqueta, v[param])
            c.grid(row=6 + i // 2, column=i % 2, sticky="ew", padx=(16 if i % 2 == 0 else 6, 6 if i % 2 == 0 else 16), pady=4)
            if solo_constante:
                self.campos_constante.append(c.control)
        self.nota_viento = nota(marco, "", wraplength=300)
        self.nota_viento.grid(row=9, column=0, columnspan=2, sticky="w", padx=16, pady=(4, 12))

        modo = "perfil" if v["wind_mode"].get() == backend.VIENTOS[0] else "constante"
        self.modo_viento.elegir(modo, avisar=False)
        self._aplicar_modo_viento(modo)

    def _al_elegir_viento(self, modo):
        self.app.vars["wind_mode"].set(backend.VIENTOS[0 if modo == "perfil" else 1])
        self._aplicar_modo_viento(modo)

    def _aplicar_modo_viento(self, modo):
        constante = modo == "constante"
        for control in self.campos_constante:
            control.configure(state="normal" if constante else "disabled",
                              text_color=Tema.TEXTO if constante else Tema.BORDE_CAMPO)
        modelo = ("Viento constante: la dirección es de dónde viene (0° = norte, 90° = este)." if constante else
                  "Perfil del día: viento por niveles de altura del 22-jun-2024. La velocidad base y la dirección "
                  "solo aplican al modelo constante.")
        self.nota_viento.configure(text=modelo + "\nAzimut: rumbo hacia el que se inclina el riel, desde el norte. "
                                                 "Semilla vacía: ráfagas distintas en cada corrida.")

    def _viento_desde(self):
        """Dirección de la que viene el viento que se dibuja: la del campo o la del nivel de superficie del perfil."""
        if self.app.vars["wind_mode"].get() == backend.VIENTOS[0]:
            return self.viento_superficie
        return self.app.numero("wind_from")

    def _dibujar_brujula(self):
        c, centro, radio = self.brujula, 85, 76
        c.delete("all")
        c.create_oval(centro - radio, centro - radio, centro + radio, centro + radio, outline=Tema.BORDE_CAMPO, width=2, fill=Tema.FONDO)
        for letra, dx, dy in (("N", 0, -1), ("S", 0, 1), ("E", 1, 0), ("O", -1, 0)):
            c.create_text(centro + dx * (radio - 12), centro + dy * (radio - 12), text=letra, fill=Tema.TEXTO_2, font=fuente_tk(11))

        def flecha(rumbo, largo, color, ancho, desde_atras=False):
            a = np.radians(rumbo)
            dx, dy = np.sin(a), -np.cos(a)
            inicio = (centro - dx * largo, centro - dy * largo) if desde_atras else (centro, centro)
            c.create_line(*inicio, centro + dx * largo, centro + dy * largo, fill=color, width=ancho, arrow=tk.LAST, arrowshape=(14, 16, 6))

        azimut, desde = self.app.numero("rail_azimuth"), self._viento_desde()
        hacia = (desde + 180) % 360
        flecha(hacia, 44, Tema.AZUL, 3, desde_atras=True)
        flecha(azimut, 56, Tema.AMARILLO, 5)
        c.create_oval(centro - 5, centro - 5, centro + 5, centro + 5, fill=Tema.TEXTO, outline="")

        relativo = (hacia - azimut) % 360
        tipo = "de cola" if relativo < 45 or relativo > 315 else "de frente" if 135 < relativo < 225 else "cruzado"
        self.texto_riel.configure(text=f"━  Riel hacia {azimut:.0f}°")
        self.texto_viento.configure(text=f"━  Viento desde {desde:.0f}°")
        self.texto_relativo.configure(text=f"Viento {tipo} respecto al riel.")

        elevacion = np.radians(self.app.numero("rail_angle"))
        self.riel.delete("all")
        self.riel.create_line(4, 68, 106, 68, fill=Tema.TENUE, width=2)
        self.riel.create_line(14, 68, 14 + 62 * np.cos(elevacion), 68 - 62 * np.sin(elevacion), fill=Tema.AMARILLO, width=5, capstyle=tk.ROUND)

    # ----------------------------------------------------------- Integración
    def _crear_integracion(self):
        v = self.app.vars
        marco = panel(self)
        marco.grid(row=0, column=2, sticky="nsew", padx=(8, 0))
        marco.grid_columnconfigure((0, 1), weight=1)
        titulo(marco, "Simulación").grid(row=0, column=0, columnspan=2, sticky="w", padx=16, pady=(12, 4))
        campo(marco, "Tiempo máximo (s)", v["sim_max_time"]).grid(row=1, column=0, sticky="ew", padx=(16, 6), pady=4)
        campo(marco, "Paso de tiempo (s)", v["sim_time_step"]).grid(row=1, column=1, sticky="ew", padx=(6, 16), pady=4)

        # El menú muestra "DOP853 · Dormand-Prince 8(5,3)"; el parámetro guarda solo la clave
        self.etiquetas = {clave: backend.etiqueta(clave) for clave in backend.INTEGRADORES}
        self.integrador = tk.StringVar(value=self.etiquetas.get(v["integrator"].get(), ""))
        self.integrador.trace_add("write", lambda *_: v["integrator"].set(
            next((clave for clave, texto in self.etiquetas.items() if texto == self.integrador.get()), v["integrator"].get())))
        campo(marco, "Método de integración", self.integrador, opciones=tuple(self.etiquetas.values())).grid(
            row=2, column=0, columnspan=2, sticky="ew", padx=16, pady=4)
        nota(marco, "En los métodos adaptativos el paso de tiempo es el máximo.").grid(row=3, column=0, columnspan=2, sticky="w", padx=16)

        ctk.CTkLabel(marco, text="Recuperación", font=fuente(12), text_color=Tema.TEXTO_2, anchor="w").grid(
            row=4, column=0, columnspan=2, sticky="w", padx=16, pady=(10, 0))
        opciones = list(zip(backend.RECUPERACION, self.RECUPERACIONES))
        self.recuperacion = Selector(marco, opciones, v["recovery"].set, vertical=True, alto=38)
        self.recuperacion.grid(row=5, column=0, columnspan=2, sticky="ew", padx=16)

        campo(marco, "Ráfaga de diseño para las cargas (m/s)", v["load_gust"]).grid(
            row=6, column=0, columnspan=2, sticky="ew", padx=16, pady=(10, 0))

        lista = ctk.CTkFrame(marco, fg_color=Tema.FONDO, corner_radius=14)
        lista.grid(row=7, column=0, columnspan=2, sticky="ew", padx=16, pady=12)
        self.encabezado_lista = ctk.CTkLabel(lista, text="", font=fuente(13, negrita=True), anchor="w")
        self.encabezado_lista.pack(fill="x", padx=14, pady=(10, 2))
        self.puntos = [ctk.CTkLabel(lista, text="", font=fuente(12), anchor="w", justify="left", wraplength=250) for _ in range(3)]
        for etiqueta in self.puntos:
            etiqueta.pack(fill="x", padx=14, pady=1)
        ctk.CTkLabel(lista, text="", height=4).pack()

    def sincronizar(self):
        """Pone los selectores de acuerdo con los parámetros (por ejemplo, al cargar una configuración)."""
        v = self.app.vars
        modo = "perfil" if v["wind_mode"].get() == backend.VIENTOS[0] else "constante"
        self.modo_viento.elegir(modo, avisar=False)
        self._aplicar_modo_viento(modo)
        if v["recovery"].get() in backend.RECUPERACION:
            self.recuperacion.elegir(v["recovery"].get(), avisar=False)
        self.integrador.set(self.etiquetas.get(v["integrator"].get(), self.integrador.get()))

    def refrescar(self, estabilidad):
        with contextlib.suppress(TypeError, ValueError):
            self._dibujar_brujula()
            base = 15 - 0.0065 * self.app.numero("launch_alt") + self.app.numero("atm_delta_t")
            self.temperatura.configure(text=f"Temperatura estándar más ΔT en el sitio: {base:.1f} °C. "
                                            "ΔT = 0 y presión vacía dan la atmósfera estándar a esa altitud.")
        if self.recuperacion.valor != self.app.vars["recovery"].get():
            self.sincronizar()

        comprobaciones = []
        if estabilidad:
            estado, _ = estado_margen(estabilidad["margen"])
            comprobaciones.append((estado == "estable", f"Cohete {estado}, margen {estabilidad['margen']:.2f} calibres"))
        else:
            comprobaciones.append((False, "No se pudo calcular la estabilidad del cohete"))
        faltan = [t.nombre.lower() for t in TABLAS if not os.path.isfile(str(self.app.rutas.get(t.clave)))]
        comprobaciones.append((not faltan, "Faltan tablas: " + ", ".join(faltan) if faltan else "Empuje, arrastre y masa cargados"))
        try:
            backend.validar_parametros(self.app.parametros())
            comprobaciones.append((True, "Sitio, viento, riel y simulación válidos"))
        except ValueError as error:
            comprobaciones.append((False, str(error)))
        for etiqueta, (bien, texto) in zip(self.puntos, comprobaciones):
            etiqueta.configure(text=f"●  {texto}", text_color=Tema.VERDE if bien else Tema.ROJO)
        listo = all(bien for bien, _ in comprobaciones[1:])
        self.encabezado_lista.configure(text="Listo para simular" if listo else "Revisa antes de simular",
                                        text_color=Tema.TEXTO if listo else Tema.ROJO)
