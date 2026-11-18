"""Gráficas y tabla de las cargas estructurales (envolvente de Paquetes/PaqueteFisica/cargas.py)."""
import numpy as np
import pandas as pd

AZUL, ROJO, GRIS = "#1F4FD8", "#C8102E", "#666666"


def tabla_envolvente(env):
    """Envolvente por sección como DataFrame: cargas máximas con el viento simulado y con ráfaga."""
    tabla = pd.DataFrame({
        "s [m]": env["s"],
        "Compresión máx [N]": env["compresion_max"],
        "Tracción máx [N]": env["traccion_max"],
        "Cortante máx [N]": env["cortante_max"],
        "Momento flector máx [N m]": env["momento_max"],
        "t compresión máx [s]": env["t_compresion"],
        "t momento máx [s]": env["t_momento"],
    })
    rafaga = env.get("con_rafaga")
    if rafaga:
        tabla["Compresión máx con ráfaga [N]"] = rafaga["compresion_max"]
        tabla["Cortante máx con ráfaga [N]"] = rafaga["cortante_max"]
        tabla["Momento flector máx con ráfaga [N m]"] = rafaga["momento_max"]
        tabla["t momento máx con ráfaga [s]"] = rafaga["t_momento"]
    return tabla


def texto_maximos(env):
    """Líneas de texto con el mayor valor de cada carga, dónde y cuándo ocurre."""
    def linea(nombre, m, unidad):
        return f"{nombre}: {m['valor']:.0f} {unidad} en s = {m['s']:.2f} m (t = {m['t']:.1f} s)"
    m = env["maximos"]
    lineas = [linea("Compresión máxima", m["compresion"], "N"),
              linea("Cortante máximo", m["cortante"], "N"),
              linea("Momento flector máximo", m["momento"], "N m")]
    if env.get("con_rafaga"):
        r = env["con_rafaga"]["maximos"]
        caso = env["con_rafaga"]["casos"]["Máximo momento flector"]
        lineas.append(f"Con ráfaga lateral de {env['rafaga']:g} m/s: cortante {r['cortante']['valor']:.0f} N, "
                      f"momento flector {r['momento']['valor']:.0f} N m en s = {r['momento']['s']:.2f} m "
                      f"(t = {r['momento']['t']:.1f} s, Mach {caso['mach']:.2f}, ángulo de ataque {abs(caso['alpha']):.1f}°)")
    return lineas


def graficar_envolvente(fig, env):
    """Dibuja en `fig` la envolvente de compresión, cortante y momento flector a lo largo del cohete."""
    s = env["s"]
    rafaga = env.get("con_rafaga")
    paneles = [
        ("Compresión máxima (N)", "compresion_max"),
        ("Cortante máximo (N)", "cortante_max"),
        ("Momento flector máximo (N m)", "momento_max"),
    ]
    ejes = fig.subplots(3, 1, sharex=True)
    for ax, (etiqueta, clave) in zip(ejes, paneles):
        ax.plot(s, env[clave], color=AZUL, linewidth=1.8, label="Viento simulado")
        if rafaga:
            ax.plot(s, rafaga[clave], color=ROJO, linewidth=1.8, linestyle="--",
                    label=f"Con ráfaga lateral de {env['rafaga']:g} m/s")
        ax.set_ylabel(etiqueta, fontsize=9)
        ax.grid(True, linestyle="--", alpha=0.5)
        ax.tick_params(labelsize=8)
        ax.set_ylim(bottom=0)
        # Límites de los tramos del fuselaje
        for _, inicio, _fin in env["secciones"]:
            ax.axvline(inicio, color=GRIS, linewidth=0.6, alpha=0.6)
    ejes[0].legend(fontsize=8, loc="upper left")
    # Nombres de los tramos del fuselaje sobre la primera gráfica (las líneas verticales son sus límites)
    arriba = ejes[0].get_ylim()[1]
    for nombre, inicio, fin in env["secciones"]:
        ejes[0].text(inicio + 0.02, arriba * 1.03, nombre, rotation=35, fontsize=7, ha="left", va="bottom", color=GRIS)
    ejes[-1].set_xlabel("Posición a lo largo del cohete, desde la punta de la nariz (m)", fontsize=9)
    ejes[-1].set_xlim(0, float(np.max(s)))
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    return ejes
