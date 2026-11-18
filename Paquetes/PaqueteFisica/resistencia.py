"""Comprobación de resistencia a partir de las cargas: pandeo del fuselaje y flameo de las aletas.

Usa las cargas de Paquetes/PaqueteFisica/cargas.py y los materiales de
Archivos/estructura_xitle.json. Para cada comprobación se da un margen de seguridad:

    margen = resistencia / (factor de seguridad * carga) - 1

Un margen positivo significa que la pieza resiste la carga multiplicada por el factor de
seguridad; uno negativo, que no.

Pandeo del fuselaje (tubos de pared delgada)
--------------------------------------------
Cada tramo cilíndrico trabaja a compresión (fuerza axial P) y a flexión (momento M):
    esfuerzo axial      sigma_a = P / A
    esfuerzo de flexión sigma_f = M * R / I
Un cilindro de pared delgada perfecto pandea a
    sigma_clasico = E * t / (R * sqrt(3 * (1 - nu^2)))
pero los tubos reales pandean mucho antes por sus imperfecciones. La monografía NASA SP-8007
("Buckling of Thin-Walled Circular Cylinders") da el factor de reducción empírico
    gamma = 1 - 0.901 * (1 - exp(-phi))     para compresión axial
    gamma = 1 - 0.731 * (1 - exp(-phi))     para flexión
    phi = (1 / 16) * sqrt(R / t)
y la condición combinada   sigma_a / (gamma_a * sigma_clasico) + sigma_f / (gamma_f * sigma_clasico) <= 1.
Además se comprueba que el esfuerzo total no supere la resistencia a compresión del material.

Para la fibra de carbono se usa la fórmula de material isótropo con el módulo E del laminado;
es una aproximación (un laminado es ortótropo) y SP-8007 se obtuvo con cilindros metálicos.

Flameo de las aletas
--------------------
Velocidad de flameo según NACA TN 4197 (Martin, 1958), el criterio habitual en cohetería:

    V_f = a * sqrt( G / ( 1.337 * AR^3 * p * (lambda + 1) / ( (AR + 2) * (t/c)^3 ) ) )

a: velocidad del sonido, p: presión del aire, G: módulo de cortante del material,
AR = envergadura^2 / área de una aleta, lambda = cuerda de punta / cuerda de raíz,
t/c = espesor / cuerda de raíz. El flameo depende de la altura: a y p cambian con ella.

Muchas calculadoras llevan un 2 adicional en el denominador,
1.337 * AR^3 * p * (lambda + 1) / (2 * (AR + 2) * (t/c)^3), que da una velocidad de flameo
raíz de 2 veces mayor. Aquí se usa por defecto la forma sin ese 2, que es la más conservadora
y la que resulta de la ecuación original (39.3 * AR^3 / ((t/c)^3 (AR + 2)) * (lambda + 1)/2 * p/p0,
con 39.3 en psi). `factor_2=True` usa la otra.
"""
import json
import math
import os

import numpy as np

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
RUTA_ESTRUCTURA = os.path.join(RAIZ, 'Archivos', 'estructura_xitle.json')


def cargar_estructura(ruta=RUTA_ESTRUCTURA):
    with open(ruta, 'r', encoding='utf-8') as f:
        return json.load(f)


# ---------------------------------------------------------------- pandeo de cilindros
def esfuerzo_pandeo_clasico(E, nu, radio, espesor):
    """Esfuerzo de pandeo de un cilindro perfecto de pared delgada a compresión axial [Pa]."""
    return E * espesor / (radio * math.sqrt(3.0 * (1.0 - nu**2)))


def factor_reduccion(radio, espesor, flexion=False):
    """Factor de reducción por imperfecciones de NASA SP-8007 (0.731 en flexión, 0.901 en compresión)."""
    phi = math.sqrt(radio / espesor) / 16.0
    return 1.0 - (0.731 if flexion else 0.901) * (1.0 - math.exp(-phi))


def verificar_tubo(compresion, momento, radio_ext, radio_int, material, factor_seguridad):
    """Esfuerzos y márgenes de un tramo cilíndrico con fuerza axial `compresion` [N] y `momento` [N m]."""
    espesor = radio_ext - radio_int
    radio = 0.5 * (radio_ext + radio_int)                       # radio medio
    area = math.pi * (radio_ext**2 - radio_int**2)
    inercia = math.pi * (radio_ext**4 - radio_int**4) / 4.0
    sigma_axial = compresion / area
    sigma_flexion = momento * radio_ext / inercia
    sigma_total = sigma_axial + sigma_flexion

    clasico = esfuerzo_pandeo_clasico(material["E_Pa"], material["nu"], radio, espesor)
    gamma_axial, gamma_flexion = factor_reduccion(radio, espesor), factor_reduccion(radio, espesor, flexion=True)
    # Fracción de la capacidad de pandeo que se usa (interacción lineal de SP-8007)
    uso_pandeo = sigma_axial / (gamma_axial * clasico) + sigma_flexion / (gamma_flexion * clasico)
    uso_resistencia = sigma_total / material["resistencia_compresion_Pa"]

    def margen(uso):
        return math.inf if uso <= 0 else 1.0 / (factor_seguridad * uso) - 1.0

    return {
        "espesor": espesor, "radio": radio, "R_t": radio / espesor,
        "sigma_axial": sigma_axial, "sigma_flexion": sigma_flexion, "sigma_total": sigma_total,
        "sigma_pandeo_clasico": clasico, "gamma_axial": gamma_axial, "gamma_flexion": gamma_flexion,
        "sigma_pandeo_axial": gamma_axial * clasico,
        "carga_pandeo_axial": gamma_axial * clasico * area,     # fuerza axial que lo pandea, sin flexión [N]
        "margen_pandeo": margen(uso_pandeo),
        "margen_resistencia": margen(uso_resistencia),
    }


def verificar_fuselaje(cohete, envolvente, estructura):
    """Pandeo y resistencia de cada tramo cilíndrico del fuselaje con las cargas de la envolvente.

    En cada tramo se toman la mayor compresión y el mayor momento flector de todo el ascenso
    (con ráfaga, si se calculó). No ocurren en el mismo instante, así que combinarlos es
    conservador. La nariz y el boattail no son cilindros y no se comprueban.
    """
    fs = estructura["factor_seguridad"]
    fuselaje = estructura["fuselaje"]
    s = envolvente["s"]
    rafaga = envolvente.get("con_rafaga")
    compresion = np.maximum(envolvente["compresion_max"], rafaga["compresion_max"]) if rafaga else envolvente["compresion_max"]
    momento = np.maximum(envolvente["momento_max"], rafaga["momento_max"]) if rafaga else envolvente["momento_max"]

    filas = []
    for comp in cohete.componentes_externos.values():
        if not (hasattr(comp, "rad_ext") and hasattr(comp, "rad_int")) or comp.rad_int <= 0 or comp.rad_int >= comp.rad_ext:
            continue                                            # nariz, boattail o pieza maciza
        inicio, fin = float(comp.posicion[2]), float(comp.posicion[2] + comp.long)
        dentro = (s >= inicio - 1e-9) & (s <= fin + 1e-9)
        clave = fuselaje.get("material_por_tramo", {}).get(comp.nombre, fuselaje["material_por_defecto"])
        material = estructura["materiales"][clave]
        fila = verificar_tubo(float(compresion[dentro].max()), float(momento[dentro].max()),
                              float(comp.rad_ext), float(comp.rad_int), material, fs)
        fila.update({"tramo": comp.nombre, "material": material["nombre"], "s_inicio": inicio, "s_fin": fin,
                     "compresion": float(compresion[dentro].max()), "momento": float(momento[dentro].max())})
        filas.append(fila)
    return filas


# ---------------------------------------------------------------- flameo de aletas
def velocidad_flameo(G, espesor, cuerda_raiz, cuerda_punta, envergadura, velocidad_sonido, presion, factor_2=False):
    """Velocidad de flameo de una aleta trapezoidal según NACA TN 4197 [m/s]."""
    area = 0.5 * (cuerda_raiz + cuerda_punta) * envergadura
    alargamiento = envergadura**2 / area
    conicidad = cuerda_punta / cuerda_raiz
    denominador = 1.337 * alargamiento**3 * presion * (conicidad + 1.0) / ((alargamiento + 2.0) * (espesor / cuerda_raiz) ** 3)
    if factor_2:
        denominador /= 2.0
    return velocidad_sonido * np.sqrt(G / denominador)


def verificar_flameo(aletas, alturas, velocidades, atmosfera, estructura):
    """Compara la velocidad del cohete con la de flameo a lo largo del ascenso.

    alturas [m sobre el sitio] y velocidades respecto al aire [m/s] son la trayectoria del
    ascenso. Devuelve el punto más cercano al flameo y el espesor mínimo de aleta para
    cumplir el factor de seguridad (la velocidad de flameo crece con el espesor elevado a 3/2).
    """
    datos = estructura["aletas"]
    material = estructura["materiales"][datos["material"]]
    fs = estructura["factor_seguridad"]
    espesor = datos["espesor_m"]
    alturas, velocidades = np.asarray(alturas, dtype=float), np.asarray(velocidades, dtype=float)

    propiedades = np.array([atmosfera.calc_propiedades(z) for z in alturas])      # T, rho, p, a
    presion, sonido = propiedades[:, 2], propiedades[:, 3]
    geometria = (espesor, aletas.C_r, aletas.C_t, aletas.span)
    v_flameo = velocidad_flameo(material["G_Pa"], *geometria, sonido, presion)
    v_flameo_2 = velocidad_flameo(material["G_Pa"], *geometria, sonido, presion, factor_2=True)

    con_velocidad = velocidades > 1.0
    cociente = np.where(con_velocidad, v_flameo / np.maximum(velocidades, 1e-9), np.inf)
    i = int(np.argmin(cociente))
    area = 0.5 * (aletas.C_r + aletas.C_t) * aletas.span
    return {
        "material": material["nombre"], "G": material["G_Pa"], "espesor": espesor,
        "alargamiento": aletas.span**2 / area, "conicidad": aletas.C_t / aletas.C_r,
        "velocidad_flameo": float(v_flameo[i]),                 # en el punto más crítico
        "velocidad_flameo_con_factor_2": float(v_flameo_2[i]),
        "velocidad_cohete": float(velocidades[i]),
        "altura": float(alturas[i]),
        "cociente": float(cociente[i]),                         # velocidad de flameo / velocidad del cohete
        "margen": float(cociente[i] / fs - 1.0),
        "espesor_minimo": float(espesor * (fs / cociente[i]) ** (2.0 / 3.0)),
        "velocidad_maxima": float(velocidades.max()),
    }


def verificar(vuelo, envolvente, alturas, velocidades, estructura=None):
    """Comprobación completa: fuselaje (pandeo y resistencia) y aletas (flameo)."""
    estructura = estructura or cargar_estructura()
    cohete = vuelo.vehiculo
    resultado = {
        "factor_seguridad": estructura["factor_seguridad"],
        "fuselaje": verificar_fuselaje(cohete, envolvente, estructura),
        "flameo": None,
    }
    aletas = cohete.componentes.get("Aletas")
    if aletas is not None:
        resultado["flameo"] = verificar_flameo(aletas, alturas, velocidades, vuelo.atmosfera, estructura)
    return resultado


def texto_resumen(resultado):
    """Líneas de texto con lo esencial de la comprobación."""
    fs = resultado["factor_seguridad"]
    lineas = [f"Factor de seguridad: {fs:g}. Margen = resistencia / (factor × carga) − 1; positivo = cumple."]
    fuselaje = resultado["fuselaje"]
    if fuselaje:
        peor = min(fuselaje, key=lambda f: min(f["margen_pandeo"], f["margen_resistencia"]))
        lineas.append(f"Fuselaje: el tramo más cargado es {peor['tramo']} ({peor['material']}, pared de {peor['espesor']*1000:.1f} mm): "
                      f"margen de pandeo {peor['margen_pandeo']:+.1f}, margen de resistencia {peor['margen_resistencia']:+.1f}.")
    f = resultado["flameo"]
    if f:
        estado = "cumple" if f["margen"] >= 0 else "NO cumple"
        lineas.append(f"Aletas ({f['espesor']*1000:.1f} mm, G = {f['G']/1e9:.0f} GPa): flameo a {f['velocidad_flameo']:.0f} m/s frente a "
                      f"{f['velocidad_cohete']:.0f} m/s del cohete a {f['altura']:.0f} m (cociente {f['cociente']:.2f}, margen {f['margen']:+.2f}: {estado}). "
                      f"Espesor mínimo: {f['espesor_minimo']*1000:.1f} mm.")
    return lineas
