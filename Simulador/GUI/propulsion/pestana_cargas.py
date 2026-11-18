"""Pestaña Cargas: cargas estructurales del ascenso, pandeo del fuselaje y flameo de las aletas."""
from tkinter import filedialog, messagebox

import customtkinter as ctk

from Simulador.Visualizacion.graficas_cargas import tabla_envolvente
from .tema import Tema
from .widgets import Tarjeta, boton, colocar_figura, estilo_ejes, figura, nota, panel


class PestanaCargas(ctk.CTkFrame):
    """Compresión, cortante y momento flector a lo largo del cohete, y la comprobación de resistencia
    con los materiales elegidos en la pestaña Cohete."""

    TARJETAS = (("compresion", "Compresión máxima"), ("momento", "Momento flector máximo"),
                ("pandeo", "Pandeo del fuselaje"), ("flameo", "Flameo de las aletas"), ("apertura", "Apertura del paracaídas"))
    PANELES = (("compresion_max", "Compresión (N)"), ("cortante_max", "Cortante (N)"), ("momento_max", "Momento (N m)"))

    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.envolvente = None
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        fila = ctk.CTkFrame(self, fg_color="transparent")
        fila.grid(row=0, column=0, sticky="ew")
        self.tarjetas = {}
        for i, (clave, nombre) in enumerate(self.TARJETAS):
            fila.grid_columnconfigure(i, weight=1, uniform="cargas")
            self.tarjetas[clave] = Tarjeta(fila, nombre, destacada=clave == "flameo")
            self.tarjetas[clave].grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 8, 0))

        control = panel(self)
        control.grid(row=1, column=0, sticky="ew", pady=8)
        control.grid_columnconfigure(0, weight=1)
        self.explicacion = nota(control, "", wraplength=1050)
        self.explicacion.grid(row=0, column=0, sticky="w", padx=16, pady=10)
        self.exportar = boton(control, "Exportar CSV", self.exportar_csv, state="disabled", border_color=Tema.TEXTO)
        self.exportar.grid(row=0, column=1, padx=12, pady=8)

        self.marco = panel(self)
        self.marco.grid(row=2, column=0, sticky="nsew")
        self.marco.grid_columnconfigure(0, weight=1)
        self.marco.grid_rowconfigure(0, weight=1)
        self.fig = figura(9, 5)
        self.lienzo = colocar_figura(self.fig, self.marco)
        self.lienzo.get_tk_widget().grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.limpiar()

    def limpiar(self, mensaje="Ejecute una simulación para ver las cargas a lo largo del cohete."):
        self.envolvente = None
        self.fig.clear()
        self.fig.text(0.5, 0.5, mensaje, color=Tema.TENUE, ha="center", va="center", fontsize=12)
        self.lienzo.draw_idle()
        self.exportar.configure(state="disabled")
        self.explicacion.configure(text="Cargas del ascenso (hasta el apogeo). El material de cada tramo y el espesor de las "
                                        "aletas se eligen en la pestaña Cohete.")
        for tarjeta in self.tarjetas.values():
            tarjeta.fijar("--")

    def exportar_csv(self):
        ruta = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")], title="Exportar cargas")
        if not ruta:
            return
        try:
            tabla_envolvente(self.envolvente).to_csv(ruta, index=False)
        except OSError as error:
            messagebox.showerror("Error al exportar", f"No se pudo guardar el archivo:\n{error}")

    def mostrar(self, r):
        env = r.get("cargas")
        if not env:
            return self.limpiar("No se calcularon las cargas.")
        self.envolvente = env
        t = self.tarjetas
        maximos = env["maximos"]
        t["compresion"].fijar(f"{maximos['compresion']['valor']:.0f} N",
                              f"a {maximos['compresion']['s']:.2f} m de la punta, t = {maximos['compresion']['t']:.1f} s")
        rafaga = env.get("con_rafaga")
        momento = (rafaga or env)["maximos"]["momento"]
        t["momento"].fijar(f"{momento['valor']:.0f} N m", (f"con ráfaga de {env['rafaga']:g} m/s, " if rafaga else "") +
                           f"a {momento['s']:.2f} m, t = {momento['t']:.1f} s")

        resistencia = r.get("resistencia")
        if resistencia and resistencia["fuselaje"]:
            peor = min(resistencia["fuselaje"], key=lambda f: f["margen_pandeo"])
            cumple = peor["margen_pandeo"] >= 0
            t["pandeo"].fijar(f"margen {peor['margen_pandeo']:+.1f}", f"{peor['tramo']}, pared de {peor['espesor'] * 1000:.1f} mm",
                              Tema.VERDE if cumple else Tema.ROJO)
        else:
            t["pandeo"].fijar("--")
        flameo = resistencia["flameo"] if resistencia else None
        if flameo:
            cumple = flameo["margen"] >= 0
            t["flameo"].fijar(f"{flameo['velocidad_flameo']:.0f} m/s",
                              f"cohete a {flameo['velocidad_cohete']:.0f} m/s · mínimo {flameo['espesor_minimo'] * 1000:.1f} mm",
                              Tema.VERDE if cumple else Tema.ROJO)
        else:
            t["flameo"].fijar("--")
        if r.get("fuerza_apertura_principal") is not None:
            t["apertura"].fijar(f"{r['fuerza_apertura_principal']:.0f} N", f"principal, {r['g_apertura_principal']:.1f} g")
        elif r.get("fuerza_apertura_drogue") is not None:
            t["apertura"].fijar(f"{r['fuerza_apertura_drogue']:.0f} N", f"drogue, {r['g_apertura_drogue']:.1f} g")
        else:
            t["apertura"].fijar("--", "vuelo sin paracaídas")

        texto = "Margen = resistencia / (factor de seguridad × carga) − 1; positivo = cumple."
        if resistencia:
            texto = f"Factor de seguridad {resistencia['factor_seguridad']:g}. " + texto
        if flameo:
            estado = "cumplen" if flameo["margen"] >= 0 else "NO cumplen"
            texto += (f"  Aletas de {flameo['material']}, {flameo['espesor'] * 1000:.1f} mm: flameo a {flameo['velocidad_flameo']:.0f} m/s, "
                      f"{flameo['cociente']:.2f} veces la velocidad del cohete ({estado}).")
        self.explicacion.configure(text=texto)

        self.fig.clear()
        ejes = self.fig.subplots(3, 1, sharex=True)
        for ax, (clave, etiqueta) in zip(ejes, self.PANELES):
            ax.plot(env["s"], env[clave], color=Tema.AMARILLO, linewidth=1.6, label="Viento simulado")
            if rafaga:
                ax.plot(env["s"], rafaga[clave], color=Tema.ROJO, linewidth=1.6, linestyle="--",
                        label=f"Con ráfaga lateral de {env['rafaga']:g} m/s")
            estilo_ejes(ax, "", "", etiqueta)
            ax.set_ylim(bottom=0)
            for _, inicio, _fin in env["secciones"]:
                ax.axvline(inicio, color=Tema.BORDE_CAMPO, linewidth=0.6)
        leyenda = ejes[0].legend(fontsize=8, loc="upper left", facecolor=Tema.PANEL, edgecolor=Tema.BORDE_CAMPO)
        for texto_leyenda in leyenda.get_texts():
            texto_leyenda.set_color(Tema.TEXTO)
        arriba = ejes[0].get_ylim()[1]
        for nombre, inicio, _fin in env["secciones"]:
            ejes[0].text(inicio + 0.02, arriba * 1.03, nombre, rotation=20, fontsize=7, ha="left", va="bottom", color=Tema.TENUE)
        ejes[-1].set_xlabel("Posición a lo largo del cohete, desde la punta de la nariz (m)", color=Tema.TENUE, fontsize=8)
        ejes[-1].set_xlim(0, float(env["s"][-1]))
        self.fig.tight_layout(rect=(0, 0, 1, 0.93))
        self.lienzo.draw_idle()
        self.exportar.configure(state="normal")
