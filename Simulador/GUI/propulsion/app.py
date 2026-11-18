"""Ventana principal: parámetros compartidos, pestañas, simulación y configuración."""
import contextlib
import io
import json
import multiprocessing
import os
import time
import tkinter as tk
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from tkinter import filedialog, messagebox

import customtkinter as ctk

from Simulador.GUI import backend
from .componentes import COMPONENTES
from .pestana_analisis import PestanaAnalisis
from .pestana_cargas import PestanaCargas
from .pestana_cohete import PestanaCohete
from .pestana_mapa import PestanaMapa
from .pestana_resultados import PestanaResultados
from .pestana_simulacion import PestanaSimulacion
from .pestana_tablas import TABLAS, PestanaTablas
from .tema import Tema, a_numero, a_texto, elegir_familias, fuente
from .widgets import Selector, boton


class App(ctk.CTk):
    PESTANAS = (("Cohete", PestanaCohete), ("Tablas de Datos", PestanaTablas), ("Simulación", PestanaSimulacion),
                ("Análisis (CG-CP)", PestanaAnalisis), ("Resultados", PestanaResultados), ("Mapa", PestanaMapa),
                ("Cargas", PestanaCargas))
    ESPERA_MS = 300   # pausa tras el último cambio antes de recalcular CG y CP

    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("Dark")
        elegir_familias()
        self.title("Simulador de vuelo · Propulsión UNAM")
        self.geometry("1400x900")
        self.minsize(1240, 720)
        self.configure(fg_color=Tema.FONDO)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Parámetros compartidos por todas las pestañas
        self.vars = {nombre: tk.StringVar(value=a_texto(valor)) for nombre, valor in backend.PARAMS_XITLE.items()}
        self.rutas = {clave: ruta if os.path.isfile(ruta) else None for clave, ruta in backend.RUTAS_XITLE.items()}
        self.hilos = ThreadPoolExecutor(max_workers=1)   # descargas del mapa del sitio
        self.proceso = self.tarea = None                 # simulación en curso
        self.inicio = 0.0
        self._pendiente = None

        self._crear_encabezado()
        self.contenido = ctk.CTkFrame(self, fg_color="transparent")
        self.contenido.grid(row=1, column=0, sticky="nsew", padx=20, pady=(4, 12))
        self.contenido.grid_columnconfigure(0, weight=1)
        self.contenido.grid_rowconfigure(0, weight=1)
        self.pestanas = {nombre: clase(self.contenido, self) for nombre, clase in self.PESTANAS}
        self._crear_barra()

        for variable in self.vars.values():
            variable.trace_add("write", lambda *_: self.al_cambiar())
        self.navegacion.elegir("Cohete")
        self.pestanas["Simulación"].sincronizar()
        self.refrescar()
        self.protocol("WM_DELETE_WINDOW", self.cerrar)

    # ------------------------------------------------------------ Estructura
    def _crear_encabezado(self):
        cabeza = ctk.CTkFrame(self, fg_color="transparent")
        cabeza.grid(row=0, column=0, sticky="ew", padx=20, pady=(12, 4))
        cabeza.grid_columnconfigure(1, weight=1)
        nombre = ctk.CTkFrame(cabeza, fg_color="transparent")
        nombre.grid(row=0, column=0, sticky="w", padx=(0, 20))
        ctk.CTkLabel(nombre, text="Simulador de vuelo", font=fuente(20, negrita=True), text_color=Tema.TEXTO, anchor="w").pack(anchor="w")
        ctk.CTkLabel(nombre, text="Propulsión UNAM", font=fuente(12), text_color=Tema.TENUE, anchor="w").pack(anchor="w")
        self.navegacion = Selector(cabeza, [(n, n) for n, _ in self.PESTANAS], self.mostrar_pestana, ancho=96)
        self.navegacion.grid(row=0, column=1, sticky="w")
        self._dibujar_trama(cabeza).grid(row=0, column=2, sticky="e")

    def _dibujar_trama(self, master):
        """Trama de puntos que se desvanece, como la de las presentaciones del equipo."""
        ancho, alto, paso = 130, 52, 13
        lienzo = tk.Canvas(master, width=ancho, height=alto, bg=Tema.FONDO, highlightthickness=0)
        for columna in range(ancho // paso):
            for fila in range(alto // paso):
                brillo = int(22 + 70 * (columna / (ancho // paso)) * (1 - fila / (alto // paso + 1)))
                x, y = columna * paso + 6, fila * paso + 6
                lienzo.create_oval(x - 2.5, y - 2.5, x + 2.5, y + 2.5, fill=f"#{brillo:02x}{brillo:02x}{brillo:02x}", outline="")
        return lienzo

    def _crear_barra(self):
        barra = ctk.CTkFrame(self, fg_color=Tema.BARRA, corner_radius=0, border_width=0)
        barra.grid(row=2, column=0, sticky="ew")
        barra.grid_columnconfigure(3, weight=1)
        self.boton_simular = boton(barra, "▶  Ejecutar Simulación", self.simular, principal=True, height=44, width=210)
        self.boton_simular.grid(row=0, column=0, padx=(20, 8), pady=12)
        boton(barra, "Guardar Datos", self.guardar_configuracion).grid(row=0, column=1, padx=4)
        boton(barra, "Cargar Datos", self.cargar_configuracion).grid(row=0, column=2, padx=4)
        estado = ctk.CTkFrame(barra, fg_color="transparent")
        estado.grid(row=0, column=3, sticky="ew", padx=20)
        estado.grid_columnconfigure(0, weight=1)
        self.progreso = ctk.CTkProgressBar(estado, height=6, progress_color=Tema.AMARILLO, fg_color=Tema.BORDE)
        self.progreso.set(0)
        self.progreso.grid(row=0, column=0, sticky="ew", pady=(0, 4))
        self.estado = ctk.CTkLabel(estado, text="Listo", font=fuente(12), text_color=Tema.TENUE, anchor="w")
        self.estado.grid(row=1, column=0, sticky="ew")

    def mostrar_pestana(self, nombre):
        for clave, pestana in self.pestanas.items():
            if clave == nombre:
                pestana.grid(row=0, column=0, sticky="nsew")
            else:
                pestana.grid_forget()

    def avisar(self, mensaje, color=Tema.TENUE):
        self.estado.configure(text=mensaje, text_color=color)

    # ------------------------------------------------------------ Parámetros
    def parametros(self):
        """Todos los parámetros como los espera el backend: números donde se puede, texto donde no."""
        return {nombre: a_numero(variable.get()) for nombre, variable in self.vars.items()}

    def numero(self, nombre):
        """Valor numérico de un parámetro. Lanza ValueError si el campo no tiene un número."""
        return float(self.vars[nombre].get())

    def restablecer_cohete(self):
        """Devuelve los campos de los componentes a los valores del Xitle II."""
        for comp in COMPONENTES:
            for c in comp.campos:
                self.vars[c.param].set(a_texto(backend.PARAMS_XITLE[c.param]))

    def al_cambiar(self):
        """Programa un recálculo. Varios cambios seguidos (al teclear) dan un solo recálculo."""
        if self._pendiente is not None:
            self.after_cancel(self._pendiente)
        self._pendiente = self.after(self.ESPERA_MS, self.refrescar)

    def calcular_estabilidad(self):
        """Devuelve (resultado de backend.analizar_estabilidad, None) o (None, mensaje de error)."""
        try:
            with contextlib.redirect_stdout(io.StringIO()):   # el motor imprime avisos al construir el cohete
                return backend.analizar_estabilidad(self.parametros(), self.rutas), None
        except Exception as error:
            return None, str(error)

    def refrescar(self):
        """Recalcula CG, CP y margen y actualiza las pestañas que dependen de los parámetros."""
        self._pendiente = None
        estabilidad, error = self.calcular_estabilidad()
        for nombre in ("Cohete", "Simulación", "Análisis (CG-CP)"):
            self.pestanas[nombre].refrescar(estabilidad)
        if self.tarea is None or self.tarea.done():
            self.avisar(f"Revisa los datos: {error}" if error else "Listo", Tema.ROJO if error else Tema.TENUE)

    # ------------------------------------------------------------ Simulación
    def simular(self):
        if self.tarea is not None and not self.tarea.done():
            return messagebox.showwarning("Simulación en curso", "Espere a que termine la simulación.")
        params = self.parametros()
        faltan = [t.nombre.lower() for t in TABLAS if not os.path.isfile(str(self.rutas.get(t.clave)))]
        if faltan:
            return messagebox.showerror("Faltan datos", "Cargue en 'Tablas de Datos' los archivos de: " + ", ".join(faltan) + ".")
        try:
            backend.validar_parametros(params)
        except ValueError as error:
            return messagebox.showerror("Error de validación", str(error))

        self.boton_simular.configure(state="disabled")
        self.pestanas["Resultados"].limpiar("Simulando el vuelo...")
        self.pestanas["Mapa"].limpiar()
        self.pestanas["Cargas"].limpiar("Simulando el vuelo...")
        self.navegacion.elegir("Resultados")
        self.progreso.configure(mode="indeterminate")
        self.progreso.start()
        # La simulación corre en otro proceso: la ventana sigue respondiendo y el cálculo no comparte
        # memoria con Tk (ejecutar el simulador en un hilo de la interfaz no es seguro).
        self.proceso = ProcessPoolExecutor(max_workers=1, mp_context=multiprocessing.get_context("spawn"))
        self.tarea = self.proceso.submit(backend.ejecutar_simulacion, params, dict(self.rutas), None, True)
        self.inicio = time.time()
        self.after(200, self._esperar_simulacion)

    def _esperar_simulacion(self):
        if not self.tarea.done():
            self.avisar(f"Simulando el vuelo... {time.time() - self.inicio:.0f} s", Tema.TEXTO_2)
            self.after(200, self._esperar_simulacion)
            return
        self.proceso.shutdown(wait=False)
        self.progreso.stop()
        self.progreso.configure(mode="determinate")
        self.boton_simular.configure(state="normal")
        try:
            df, resumen = self.tarea.result()
        except Exception as error:
            self.progreso.set(0)
            self.pestanas["Resultados"].limpiar()
            self.avisar(f"Error: {error}", Tema.ROJO)
            messagebox.showerror("Error de simulación", f"Ocurrió un error en el simulador:\n\n{error}")
            return
        self.progreso.set(1)
        self.pestanas["Resultados"].mostrar(df, resumen)
        self.pestanas["Mapa"].mostrar(df, resumen)
        self.pestanas["Cargas"].mostrar(resumen)
        self.avisar(f"Simulación completada con {backend.etiqueta(resumen['integrador'])}: "
                    f"apogeo {resumen['apogeo']:.0f} m en t = {resumen['t_apogeo']:.1f} s", Tema.TEXTO_2)

    # --------------------------------------------------------- Configuración
    def guardar_configuracion(self):
        """Guarda los parámetros y las rutas de las tablas, en el mismo formato que ModernGUI."""
        ruta = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")], title="Guardar configuración")
        if not ruta:
            return
        try:
            with open(ruta, "w", encoding="utf-8") as archivo:
                json.dump({**self.parametros(), **self.rutas}, archivo, indent=4, ensure_ascii=False)
        except OSError as error:
            return messagebox.showerror("Error al guardar", f"No se pudo guardar el archivo:\n{error}")
        self.avisar(f"Configuración guardada en {os.path.basename(ruta)}")

    def cargar_configuracion(self):
        ruta = filedialog.askopenfilename(filetypes=[("JSON", "*.json")], title="Cargar configuración")
        if not ruta:
            return
        try:
            with open(ruta, "r", encoding="utf-8") as archivo:
                datos = json.load(archivo)
        except (OSError, ValueError) as error:
            return messagebox.showerror("Error al cargar", f"No se pudo leer el archivo:\n{error}")
        self.aplicar_configuracion(datos)
        self.avisar(f"Configuración cargada desde {os.path.basename(ruta)}")

    def aplicar_configuracion(self, datos):
        """Pone en los campos los valores de un diccionario de configuración."""
        for nombre, variable in self.vars.items():
            if nombre in datos:
                variable.set(a_texto(datos[nombre]))
        tablas = self.pestanas["Tablas de Datos"]
        for tabla in TABLAS:
            if datos.get(tabla.clave):
                tablas.cargar(tabla, datos[tabla.clave], avisar=False)
        if tablas.visible:
            tablas.visualizar(tablas.visible)
        self.pestanas["Simulación"].sincronizar()
        self.pestanas["Simulación"].cargar_mapa_sitio()
        self.refrescar()

    def cerrar(self):
        self.hilos.shutdown(wait=False, cancel_futures=True)
        if self.proceso is not None:
            self.proceso.shutdown(wait=False, cancel_futures=True)
        self.destroy()
