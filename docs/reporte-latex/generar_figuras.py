"""Genera las figuras del reporte de diseño del Xitle II a partir del simulador.

    python docs/reporte-latex/generar_figuras.py

Las guarda en docs/reporte-latex/figuras/, de donde las toman el reporte en LaTeX y el de
Markdown (docs/reporte-xitle2.md). También copia ahí las imágenes de la interfaz que usa el reporte.
"""
import contextlib
import io
import os
import shutil
import sys
import tempfile

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, "..", ".."))
sys.path.insert(0, RAIZ)

from Paquetes.PaqueteFisica import resistencia  # noqa: E402
from Simulador.GUI import backend  # noqa: E402

FIGURAS = os.path.join(AQUI, "figuras")
AZUL, ROJO, VERDE, NARANJA, GRIS = "#1F4FD8", "#C8102E", "#1A7F37", "#D9730D", "#555555"
plt.rcParams.update({"font.size": 9, "axes.grid": True, "grid.alpha": 0.35, "grid.linestyle": "--",
                     "axes.spines.top": False, "axes.spines.right": False, "savefig.dpi": 160})
PARAMS = dict(backend.PARAMS_XITLE, wind_seed=2024)


def callado(funcion, *args, **kwargs):
    """Llama al simulador sin que imprima sus avisos."""
    with contextlib.redirect_stdout(io.StringIO()):
        return funcion(*args, **kwargs)


def simular(rutas=None, **cambios):
    return callado(backend.ejecutar_simulacion, dict(PARAMS, **cambios), rutas or backend.RUTAS_XITLE)


def guardar(fig, nombre):
    fig.tight_layout()
    fig.savefig(os.path.join(FIGURAS, nombre))
    plt.close(fig)
    print("figura", nombre)


def marcar_eventos(ax, r):
    ax.axvline(r["t_MECO"], color=NARANJA, linestyle="--", linewidth=0.9)
    ax.axvline(r["t_apogeo"], color=VERDE, linestyle="--", linewidth=0.9)


def figura_motor():
    empuje = pd.read_csv(backend.RUTAS_XITLE["thrust"])
    t, f = empuje["time"].to_numpy(), empuje["thrust"].to_numpy()
    acumulado = np.concatenate(([0], np.cumsum(0.5 * (f[1:] + f[:-1]) * np.diff(t))))
    fig, ax = plt.subplots(figsize=(6.5, 3.2))
    ax.plot(t, f, color=ROJO, label="Empuje")
    ax.fill_between(t, f, color=ROJO, alpha=0.12)
    ax.set_xlabel("Tiempo (s)"); ax.set_ylabel("Empuje (N)")
    ax2 = ax.twinx(); ax2.grid(False); ax2.spines["right"].set_visible(True)
    ax2.plot(t, 100 * acumulado / acumulado[-1], color=AZUL, label="Impulso entregado")
    ax2.set_ylabel("Impulso entregado (%)"); ax2.set_ylim(0, 105)
    t90 = np.interp(0.9 * acumulado[-1], acumulado, t)
    ax2.plot(t90, 90, "o", color=AZUL); ax2.annotate(f"90 % a los {t90:.1f} s", (t90, 90), xytext=(t90 + 1.5, 70), color=AZUL)
    ax.legend(*[sum(x, []) for x in zip(ax.get_legend_handles_labels(), ax2.get_legend_handles_labels())], loc="center right")
    guardar(fig, "motor.png")


def figura_estabilidad(df, r):
    fig, ejes = plt.subplots(1, 3, figsize=(9, 2.9))
    ejes[0].plot(df["t"], df["masa"], color=AZUL); ejes[0].set_ylabel("Masa (kg)")
    ejes[1].plot(df["t"], df["CG"], color=AZUL, label="Centro de gravedad")
    ejes[1].plot(df["t"], df["CP"], color=ROJO, label="Centro de presión")
    ejes[1].set_ylabel("Posición desde la punta (m)"); ejes[1].invert_yaxis(); ejes[1].legend(fontsize=7)
    ejes[2].plot(df["t"], df["margen"], color=VERDE); ejes[2].set_ylabel("Margen estático (calibres)")
    ejes[2].axhline(1.5, color=GRIS, linewidth=0.8, linestyle=":"); ejes[2].set_ylim(0, 4.6)
    ejes[2].text(26, 1.6, "mínimo usual, 1.5", fontsize=7, color=GRIS)
    for ax in ejes:
        ax.set_xlim(0, 30); ax.set_xlabel("Tiempo (s)"); ax.axvline(r["t_MECO"], color=NARANJA, linestyle="--", linewidth=0.9)
    guardar(fig, "estabilidad.png")


def figura_fuerzas(df, r):
    fig, ax = plt.subplots(figsize=(6.5, 3.0))
    tramo = df[df["t"] <= r["t_apogeo"]]
    ax.plot(tramo["t"], tramo["empuje"], color=ROJO, label="Empuje")
    ax.plot(tramo["t"], tramo["arrastre"], color=AZUL, label="Arrastre")
    ax.plot(tramo["t"], tramo["masa"] * 9.79, color=GRIS, label="Peso")
    ax.set_yscale("log"); ax.set_ylim(5, 4000); ax.set_xlabel("Tiempo (s)"); ax.set_ylabel("Fuerza (N)")
    marcar_eventos(ax, r); ax.legend()
    guardar(fig, "fuerzas.png")


def escalar_tabla(clave, columna, factor):
    tabla = pd.read_csv(backend.RUTAS_XITLE[clave]); tabla[columna] *= factor
    ruta = os.path.join(tempfile.mkdtemp(), f"{clave}.csv"); tabla.to_csv(ruta, index=False)
    return dict(backend.RUTAS_XITLE, **{clave: ruta})


def figura_sensibilidad(base):
    constante = dict(wind_mode=backend.VIENTOS[1], wind_base_speed=8)
    casos = [("Empuje −5 %", dict(rutas=escalar_tabla("thrust", "thrust", 0.95))),
             ("Empuje +5 %", dict(rutas=escalar_tabla("thrust", "thrust", 1.05))),
             ("Arrastre +10 %", dict(rutas=escalar_tabla("drag", "cd", 1.10))),
             ("Arrastre −10 %", dict(rutas=escalar_tabla("drag", "cd", 0.90))),
             ("Carga útil +2 kg", dict(cu_mass=6.3)), ("Carga útil −2 kg", dict(cu_mass=2.3)),
             ("Riel a 80°", dict(rail_angle=80)), ("Riel a 87°", dict(rail_angle=87)),
             ("Viento 8 m/s cruzado", dict(wind_from=130, **constante)),
             ("Viento 8 m/s de frente", dict(wind_from=220, **constante))]
    nombres, cambios = [], []
    for nombre, opciones in casos:
        _, r = simular(integrator="LSODA", **opciones)
        nombres.append(nombre); cambios.append(r["apogeo"] - base)
        print(f"  {nombre}: apogeo {r['apogeo']:.0f} m ({cambios[-1]:+.0f}), cae a {r['distancia']:.0f} m")
    fig, ax = plt.subplots(figsize=(6.5, 3.4))
    y = np.arange(len(nombres))[::-1]
    ax.barh(y, cambios, color=[VERDE if c > 0 else ROJO for c in cambios])
    ax.set_yticks(y, nombres); ax.axvline(0, color="black", linewidth=0.8)
    ax.set_xlabel("Cambio en el apogeo (m)")
    for yi, c in zip(y, cambios):
        ax.text(c + (15 if c > 0 else -15), yi, f"{c:+.0f}", va="center", ha="left" if c > 0 else "right", fontsize=8)
    ax.set_xlim(min(cambios) - 130, max(cambios) + 130)
    guardar(fig, "sensibilidad.png")


def figura_recuperacion():
    fig, ejes = plt.subplots(1, 2, figsize=(9, 3.1))
    for modo, nombre, color in zip(backend.RECUPERACION, ("Vuelo libre", "Solo drogue", "Drogue y principal"), (ROJO, NARANJA, AZUL)):
        df, r = simular(recovery=modo, integrator="LSODA")
        ejes[0].plot(df["t"], df["z"], color=color, label=nombre)
        baja = df[df["t"] > r["t_apogeo"]]
        ejes[1].plot(baja["velocidad"], baja["z"], color=color, label=nombre)
    ejes[0].set_xlabel("Tiempo (s)"); ejes[0].set_ylabel("Altura sobre el sitio (m)"); ejes[0].legend()
    ejes[1].set_xlabel("Velocidad durante el descenso (m/s)"); ejes[1].set_ylabel("Altura sobre el sitio (m)"); ejes[1].set_xscale("log")
    ejes[1].set_xticks([10, 20, 50, 100, 200, 300], ["10", "20", "50", "100", "200", "300"]); ejes[1].minorticks_off()
    guardar(fig, "recuperacion.png")


def figura_cargas(env):
    fig, ejes = plt.subplots(3, 1, figsize=(7.5, 6.2), sharex=True)
    rafaga = env.get("con_rafaga")
    for ax, (clave, etiqueta) in zip(ejes, (("compresion_max", "Compresión (N)"), ("cortante_max", "Cortante (N)"), ("momento_max", "Momento flector (N m)"))):
        ax.plot(env["s"], env[clave], color=AZUL, label="Viento del día")
        if rafaga:
            ax.plot(env["s"], rafaga[clave], color=ROJO, linestyle="--", label=f"Ráfaga lateral de {env['rafaga']:g} m/s")
        ax.set_ylabel(etiqueta); ax.set_ylim(bottom=0)
        for _, inicio, _fin in env["secciones"]:
            ax.axvline(inicio, color=GRIS, linewidth=0.5, alpha=0.6)
    ejes[0].legend(loc="upper left", fontsize=8)
    tope = ejes[0].get_ylim()[1]
    for nombre, inicio, _fin in env["secciones"]:
        ejes[0].text(inicio + 0.02, tope * 1.02, nombre, rotation=25, fontsize=7, ha="left", va="bottom", color=GRIS)
    ejes[-1].set_xlabel("Posición desde la punta de la nariz (m)"); ejes[-1].set_xlim(0, float(env["s"][-1]))
    fig.subplots_adjust(top=0.86)
    guardar(fig, "cargas.png")


def figura_esfuerzos(res):
    tramos = res["fuselaje"]
    nombres = [f["tramo"] for f in tramos]
    x = np.arange(len(tramos))
    fig, ejes = plt.subplots(1, 2, figsize=(9, 3.2))
    ejes[0].bar(x, [f["sigma_axial"] / 1e6 for f in tramos], color=AZUL, label="Compresión axial")
    ejes[0].bar(x, [f["sigma_flexion"] / 1e6 for f in tramos], bottom=[f["sigma_axial"] / 1e6 for f in tramos], color=ROJO, label="Flexión (con ráfaga)")
    ejes[0].set_ylabel("Esfuerzo (MPa)"); ejes[0].legend(fontsize=8)
    ejes[1].bar(x, [f["margen_pandeo"] for f in tramos], color=VERDE)
    ejes[1].set_yscale("log"); ejes[1].set_ylabel("Margen de seguridad al pandeo")
    for ax in ejes:
        ax.set_xticks(x, nombres, rotation=30, ha="right", fontsize=8)
    guardar(fig, "esfuerzos.png")


def figura_flameo(df, r, res):
    estructura = resistencia.cargar_estructura()
    atm = backend.crear_atmosfera(PARAMS)
    asc = df[df["t"] <= r["t_apogeo"]]
    n = lambda clave: float(PARAMS[clave])
    espesor = res["flameo"]["espesor"]

    def flameo(G, esp):
        valores = []
        for z in asc["z"]:
            _, _, presion, sonido = atm.calc_propiedades(z)
            valores.append(resistencia.velocidad_flameo(G, esp, n("fin_root_chord"), n("fin_tip_chord"), n("fin_span"), sonido, presion))
        return np.array(valores)

    g090 = estructura["materiales"]["fibra_de_carbono"]["G_Pa"]
    g45 = estructura["materiales"]["fibra_de_carbono_casi_isotropa"]["G_Pa"]
    fig, ax = plt.subplots(figsize=(6.5, 3.4))
    ax.plot(asc["velocidad"], asc["z"] / 1000, color="black", linewidth=1.8, label="Velocidad del cohete")
    curvas = (("0/90, 3 mm (actual)", flameo(g090, espesor), ROJO, "-"), ("0/90, 4.7 mm", flameo(g090, 0.0047), NARANJA, "--"),
              ("con capas a ±45°, 3 mm", flameo(g45, espesor), VERDE, "-"))
    for nombre, v, color, estilo in curvas:
        ax.plot(v, asc["z"] / 1000, color=color, linestyle=estilo, label=f"Flameo, {nombre}")
        print(f"  flameo {nombre}: mínimo cociente {np.min(v / asc['velocidad'].clip(lower=1)):.2f}, a ras de suelo {v[0]:.0f} m/s, a 1.77 km {np.interp(1765, asc['z'], v):.0f} m/s")
    ax.set_xlabel("Velocidad (m/s)"); ax.set_ylabel("Altura sobre el sitio (km)"); ax.set_xlim(0, 700)
    ax.legend(fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.22), ncol=2, frameon=False)
    guardar(fig, "flameo.png")


def vuelo_medido():
    """Tiempo desde el despegue, altura y velocidad vertical del rastreador GPS."""
    gps = pd.read_csv(os.path.join(RAIZ, "Archivos", "DatosVuelo", "FTW.csv")); gps.columns = [c.strip() for c in gps.columns]
    partes = gps["TIME"].astype(str).str.split(":", expand=True).astype(float)
    segundos = (partes[0] * 60 + partes[1]).to_numpy()
    segundos = segundos + 3600 * np.cumsum(np.concatenate(([0], np.diff(segundos) < -1800)))   # el reloj da minutos y segundos
    altura = gps["Alt AGL (ft)"] * 0.3048
    en_tierra = altura[: altura.idxmax()] < 15
    inicio = en_tierra[en_tierra].index[-1]
    return segundos[inicio:] - segundos[inicio], altura[inicio:].to_numpy(), (gps["VERTV"] * 0.3048)[inicio:].to_numpy()


def figura_vuelo_real(df):
    t, z, vz = vuelo_medido()
    fig, ejes = plt.subplots(1, 3, figsize=(9.5, 3.1))
    ejes[0].plot(df["t"], df["z"], color=AZUL, label="Simulado"); ejes[0].plot(t, z, "o", color=ROJO, markersize=2.5, label="GPS")
    ejes[0].set_ylabel("Altura sobre el sitio (m)"); ejes[0].legend()
    ejes[1].plot(df["t"], df["vz"], color=AZUL); ejes[1].plot(t, vz, "o", color=ROJO, markersize=2.5)
    ejes[1].set_ylabel("Velocidad vertical (m/s)")
    ejes[2].plot(t, np.interp(t, df["t"], df["z"]) - z, color=GRIS)
    ejes[2].set_ylabel("Altura simulada menos medida (m)"); ejes[2].axvspan(5, 15, color=NARANJA, alpha=0.15)
    ejes[2].text(16, 60, "la diferencia nace\nentre los 5 y los 15 s", fontsize=7, color=NARANJA)
    for ax in ejes:
        ax.set_xlabel("Tiempo desde el despegue (s)"); ax.set_xlim(0, 84)
    guardar(fig, "vuelo-real.png")


def copiar_imagenes():
    for nombre in ("esquema-cohete.png", "resultados-vuelo.png", "mapa-vuelo.png", "propulsion-pestana-cohete.png",
                   "propulsion-pestana-resultados.png", "propulsion-pestana-cargas.png"):
        shutil.copy(os.path.join(RAIZ, "docs", "images", nombre), os.path.join(FIGURAS, nombre))


if __name__ == "__main__":
    os.makedirs(FIGURAS, exist_ok=True)
    df, r = simular()
    print(f"caso base: apogeo {r['apogeo']:.0f} m")
    figura_motor()
    figura_estabilidad(df, r)
    figura_fuerzas(df, r)
    figura_sensibilidad(simular(integrator="LSODA")[1]["apogeo"])
    figura_recuperacion()
    figura_cargas(r["cargas"])
    figura_esfuerzos(r["resistencia"])
    figura_flameo(df, r, r["resistencia"])
    figura_vuelo_real(df)
    copiar_imagenes()
