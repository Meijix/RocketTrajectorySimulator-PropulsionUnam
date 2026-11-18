"""Cargas estructurales del cohete durante el ascenso: fuerza axial, cortante y momento flector.

El cohete se trata como una viga libre a lo largo de su eje. La coordenada s se mide desde
la punta de la nariz hacia la cola, igual que las posiciones de los componentes. En cada
instante se toman del simulador las fuerzas externas (empuje, aerodinámicas, peso) y se
reparten sobre la viga; las aceleraciones de cuerpo rígido que producen dan las fuerzas de
inercia (principio de d'Alembert), y al cortar la viga en s se obtiene lo que la parte de
atrás le hace a la de adelante:

    compresión(s)  fuerza axial; positiva cuando el tramo está comprimido [N]
    cortante(s)    fuerza transversal en el plano de cabeceo [N]
    momento(s)     momento flector en el plano de cabeceo [N m]

Las tres valen cero en los dos extremos del cohete, porque la viga está libre.

Hipótesis sobre dónde actúa cada fuerza
---------------------------------------
- Empuje: en el extremo trasero del fuselaje (se puede cambiar con `s_empuje`).
- Fuerza aerodinámica axial (casi todo el arrastre): en la punta de la nariz. Es el reparto
  más desfavorable para la compresión de los tramos delanteros.
- Fuerza aerodinámica transversal: repartida entre nariz, aletas y boattail en proporción a
  su coeficiente de fuerza normal, cada una en su centro de presión. La resultante cae en
  el centro de presión del cohete, como en el simulador.
- Amortiguamiento del cabeceo: las mismas fuerzas locales que dan el momento de
  amortiguamiento del simulador (y el chorro del motor en la tobera).
- Masa de cada componente: repartida a lo largo de su longitud, con una densidad lineal
  que respeta su centro de gravedad.

Ráfaga de diseño
----------------
Con el viento del vuelo simulado el ángulo de ataque es pequeño y la flexión, también. Para
dimensionar se suele añadir una ráfaga lateral que llega de golpe: el cohete no alcanza a
girar y vuela un instante con el ángulo de ataque que resulta de sumar la ráfaga a su
velocidad. `envolvente` calcula las cargas dos veces: con el viento simulado y con una
ráfaga perpendicular al eje aplicada en cada instante del ascenso.

Alcance: se calcula solo el ascenso (hasta el apogeo). En el riel solo hay carga axial: las
fuerzas laterales las absorbe el riel. La carga de apertura de los paracaídas se obtiene
aparte, de la simulación del descenso. Solo se consideran las fuerzas en el plano de cabeceo.
"""
import numpy as np

from Paquetes.utils.funciones import calc_gravedad


def _longitud(comp):
    """Longitud de un componente a lo largo del eje (las aletas ocupan su cuerda raíz)."""
    if hasattr(comp, "long"):
        return float(comp.long)
    return float(getattr(comp, "C_r", 0.0))


def longitud_viga(cohete):
    """Extremo trasero de la viga: el componente que llega más atrás (las aletas pueden sobresalir)."""
    return max(float(c.posicion[2]) + _longitud(c) for c in cohete.componentes.values())


def distribucion_de_masa(cohete, bordes):
    """Masa de cada tramo de la viga [kg], con la masa actual de los componentes.

    `bordes` son las posiciones de los cortes (n + 1 valores de 0 a la longitud de la viga).
    Cada componente se reparte sobre su longitud con densidad lineal a + b*u, elegida para
    que su masa y su centro de gravedad sean los del componente. Si eso exigiera densidad
    negativa (centro de gravedad fuera del tercio central), se usa la distribución triangular
    más cercana.
    """
    bordes = np.asarray(bordes, dtype=float)
    dm = np.zeros(len(bordes) - 1)
    for comp in cohete.componentes.values():
        masa = float(comp.masa)
        if masa <= 0:
            continue
        inicio, largo = float(comp.posicion[2]), _longitud(comp)
        if largo < 1e-6:                                   # componente puntual
            i = min(max(np.searchsorted(bordes, inicio, side="right") - 1, 0), len(dm) - 1)
            dm[i] += masa
            continue
        centro = min(max(float(comp.CG[2]), largo / 3), 2 * largo / 3)
        b = 12 * masa * (centro - largo / 2) / largo**3
        a = masa / largo - b * largo / 2
        # Masa acumulada desde el frente del componente: a*u + b*u²/2
        u = np.clip(bordes - inicio, 0.0, largo)
        acumulada = a * u + b * u**2 / 2
        dm += np.diff(acumulada)
    return dm


def cargas_viga(bordes, dm, axiales, transversales, g_axial=0.0, g_transversal=0.0, omega=0.0):
    """Fuerza axial, cortante y momento flector de una viga libre con cargas puntuales.

    bordes          posiciones de los cortes, de la punta (0) a la cola [m]
    dm              masa de cada tramo entre cortes [kg]
    axiales         lista de (s, F): fuerzas a lo largo del eje, positivas hacia la nariz [N]
    transversales   lista de (s, F): fuerzas perpendiculares al eje, en el plano de cabeceo [N]
    g_axial, g_transversal   componentes de la gravedad en esos dos ejes [m/s²]
    omega           velocidad angular de cabeceo [rad/s]

    El sentido transversal positivo es el que hace crecer el ángulo de cabeceo cuando la
    fuerza se aplica por delante del centro de gravedad. Devuelve un diccionario con las
    cargas en cada corte y las aceleraciones de cuerpo rígido usadas.
    """
    bordes = np.asarray(bordes, dtype=float)
    dm = np.asarray(dm, dtype=float)
    centros = 0.5 * (bordes[:-1] + bordes[1:])
    masa = dm.sum()
    s_cg = (dm * centros).sum() / masa
    brazo = s_cg - centros                                 # distancia al CG, positiva hacia la nariz
    inercia = (dm * brazo**2).sum()

    # Aceleraciones de cuerpo rígido que producen las fuerzas aplicadas
    f_axial = sum(f for _, f in axiales)
    f_transversal = sum(f for _, f in transversales)
    momento_cg = sum(f * (s_cg - s) for s, f in transversales)
    a_axial_cg = f_axial / masa + g_axial
    a_transversal_cg = f_transversal / masa + g_transversal
    acel_angular = momento_cg / inercia

    # Carga neta de cada tramo: peso menos masa por aceleración (fuerza de inercia)
    w_axial = dm * (g_axial - (a_axial_cg - omega**2 * brazo))
    w_transversal = dm * (g_transversal - (a_transversal_cg + acel_angular * brazo))

    n = len(bordes)
    # Suma de las cargas de la parte delantera de cada corte
    delante_axial = np.concatenate(([0.0], np.cumsum(w_axial)))
    delante_transversal = np.concatenate(([0.0], np.cumsum(w_transversal)))
    # Momento de esas cargas respecto al corte: cada una con brazo (s_corte - s_carga)
    momento_delante = np.concatenate(([0.0], np.cumsum(w_transversal * centros)))
    delante_momento = delante_transversal * bordes - momento_delante

    ultimo = np.arange(n) == n - 1
    for s, f in axiales:
        delante_axial += f * ((bordes > s) | ultimo)
    for s, f in transversales:
        incluye = (bordes > s) | ultimo
        delante_transversal += f * incluye
        delante_momento += f * (bordes - s) * incluye

    # La parte trasera ejerce sobre la delantera lo opuesto a la carga neta de la delantera
    return {
        "s": bordes,
        "compresion": -delante_axial,
        "cortante": -delante_transversal,
        "momento": -delante_momento,
        "masa": masa, "s_cg": s_cg, "inercia": inercia,
        "a_axial": a_axial_cg, "a_transversal": a_transversal_cg, "acel_angular": acel_angular,
    }


def cargas_en_instante(vuelo, t, estado, bordes=None, n_tramos=400, s_empuje=None, rafaga=0.0):
    """Cargas a lo largo del cohete en el instante t, con el estado [x, y, z, vx, vy, vz, theta, omega].

    `rafaga` [m/s] añade al viento una ráfaga perpendicular al eje del cohete, en el plano de
    cabeceo, sin cambiar su actitud (ráfaga que llega de golpe). En el riel no tiene efecto.
    """
    cohete = vuelo.vehiculo
    estado = np.asarray(estado, dtype=float)
    pos, vel, theta, omega = estado[0:3], estado[3:6], estado[6], estado[7]
    z = pos[2]

    cohete.actualizar_masa(t)
    # En el ascenso no hay paracaídas abiertos
    cohete.parachute_active1 = False
    cohete.main_active = False
    vuelo.t_actual = t

    if bordes is None:
        bordes = np.linspace(0.0, longitud_viga(cohete), n_tramos + 1)
    if s_empuje is None:
        s_empuje = float(cohete.longtotal)
    dm = distribucion_de_masa(cohete, bordes)

    eje = np.array((np.cos(theta), 0.0, np.sin(theta)))          # hacia la nariz
    normal = np.array((-np.sin(theta), 0.0, np.cos(theta)))      # transversal, en el plano de cabeceo
    gravedad = calc_gravedad(z + vuelo.atmosfera.altitud_sitio)
    g_axial, g_transversal = -gravedad * np.sin(theta), -gravedad * np.cos(theta)

    viento = vuelo.viento.vector_en(t, z) + rafaga * normal
    v_rel = vel - viento
    rapidez = np.linalg.norm(v_rel)
    if z <= vuelo.atmosfera.h_max:
        _, rho, _, cs = vuelo.atmosfera.calc_propiedades(z)
    else:
        rho, cs = 0.0, 1.0
    arrastre, fuerza_normal = vuelo.calc_aero(pos, v_rel, theta)
    aero = arrastre + fuerza_normal
    empuje = float(cohete.calc_empuje_magn(t))

    axiales = [(0.0, float(aero @ eje)), (s_empuje, empuje)]
    transversales = []
    en_riel = vuelo.en_riel(pos)

    if en_riel:
        # El riel absorbe las fuerzas laterales; la base sostiene al cohete si el empuje no vence al peso
        g_transversal, omega = 0.0, 0.0
        masa = dm.sum()
        a_eje = sum(f for _, f in axiales) / masa + g_axial
        if a_eje < 0 and pos @ eje <= 0 and vel @ eje <= 0:
            axiales.append((s_empuje, -a_eje * masa))     # reacción de la base, en el extremo del fuselaje
    else:
        con_normal = [c for c in cohete.componentes.values() if c.CN]
        cn_total = sum(c.CN for c in con_normal)
        transversal_total = float(aero @ normal)
        amortiguamiento = 0.5 * rho * rapidez * cohete.A if vuelo.amortiguamiento else 0.0
        s_cg = float(cohete.CG[2])
        for c in con_normal:
            s_c = float(c.posicion[2] + c.CP[2])
            fuerza = transversal_total * c.CN / cn_total
            fuerza -= amortiguamiento * c.CN * (s_cg - s_c) * omega        # amortiguamiento aerodinámico
            transversales.append((s_c, fuerza))
        if vuelo.amortiguamiento:
            transversales.append((s_empuje, -cohete.flujo_masico(t) * (s_cg - s_empuje) * omega))   # chorro

    cargas = cargas_viga(bordes, dm, axiales, transversales, g_axial, g_transversal, omega)
    alpha = vuelo.calc_alpha(v_rel, theta) if rapidez > 0 else 0.0
    cargas.update({
        "t": t, "en_riel": en_riel, "empuje": empuje,
        "presion_dinamica": 0.5 * rho * rapidez**2,
        "mach": rapidez / cs,
        "alpha": float(np.degrees(np.arctan2(np.sin(alpha), np.cos(alpha)))),
        "rafaga": rafaga,
    })
    return cargas


def secciones(cohete):
    """Tramos externos del fuselaje como (nombre, s inicial, s final), para rotular las gráficas."""
    return [(c.nombre, float(c.posicion[2]), float(c.posicion[2]) + _longitud(c))
            for c in cohete.componentes_externos.values()]


CLAVES_CASO = ("t", "compresion", "cortante", "momento", "presion_dinamica", "mach", "alpha", "empuje",
               "a_axial", "a_transversal", "acel_angular", "masa", "rafaga")


def _caso(cargas):
    return {clave: (cargas[clave] if isinstance(cargas[clave], np.ndarray) else float(cargas[clave]))
            for clave in CLAVES_CASO}


def _recorrer(vuelo, instantes, estados, bordes, s_empuje, rafaga):
    """Máximos por sección y casos más exigentes recorriendo el ascenso con la ráfaga dada."""
    n = len(bordes)
    maximos = {clave: np.zeros(n) for clave in ("compresion_max", "traccion_max", "cortante_max", "momento_max")}
    cuando = {clave: np.zeros(n) for clave in ("t_compresion", "t_traccion", "t_cortante", "t_momento")}
    mejores = {}            # caso -> (valor, cargas)

    def candidato(nombre, valor, cargas):
        if nombre not in mejores or valor > mejores[nombre][0]:
            mejores[nombre] = (valor, cargas)

    salida_riel = None
    for t, estado in zip(instantes, estados):
        c = cargas_en_instante(vuelo, t, estado, bordes=bordes, s_empuje=s_empuje, rafaga=rafaga)
        for clave, t_clave, valores in (
                ("compresion_max", "t_compresion", c["compresion"]),
                ("traccion_max", "t_traccion", -c["compresion"]),
                ("cortante_max", "t_cortante", np.abs(c["cortante"])),
                ("momento_max", "t_momento", np.abs(c["momento"]))):
            mayor = valores > maximos[clave]
            maximos[clave][mayor] = valores[mayor]
            cuando[t_clave][mayor] = t
        candidato("Máxima presión dinámica", c["presion_dinamica"], c)
        candidato("Máxima compresión", c["compresion"].max(), c)
        candidato("Máximo momento flector", np.abs(c["momento"]).max(), c)
        if salida_riel is None and not c["en_riel"]:
            salida_riel = c
    if salida_riel is not None:
        mejores["Salida del riel"] = (0.0, salida_riel)

    def resumen(clave, t_clave):
        i = int(np.argmax(maximos[clave]))
        return {"valor": float(maximos[clave][i]), "s": float(bordes[i]), "t": float(cuando[t_clave][i])}

    resultado = dict(maximos)
    resultado.update(cuando)
    resultado["casos"] = {nombre: _caso(cargas) for nombre, (_, cargas) in mejores.items()}
    resultado["maximos"] = {
        "compresion": resumen("compresion_max", "t_compresion"),
        "traccion": resumen("traccion_max", "t_traccion"),
        "cortante": resumen("cortante_max", "t_cortante"),
        "momento": resumen("momento_max", "t_momento"),
    }
    return resultado


def envolvente(vuelo, tiempos, sim, paso=0.05, n_tramos=400, s_empuje=None, rafaga=9.0):
    """Cargas máximas en cada sección durante el ascenso y los instantes más exigentes.

    Recorre la trayectoria ya simulada (tiempos, estados) cada `paso` segundos hasta el
    apogeo. Devuelve un diccionario con:
        s                      posiciones de los cortes
        compresion_max         mayor compresión en cada corte
        traccion_max           mayor tracción en cada corte (como valor positivo)
        cortante_max           mayor cortante en valor absoluto
        momento_max            mayor momento flector en valor absoluto
        t_*                    instante en que cada corte alcanzó su máximo
        maximos                el mayor valor de cada carga, dónde y cuándo
        casos                  cargas completas en los instantes más exigentes
        secciones              tramos del fuselaje
        con_rafaga             lo mismo (máximos, instantes, casos) añadiendo en todo el ascenso
                               una ráfaga lateral de `rafaga` m/s; None si rafaga es 0
    """
    cohete = vuelo.vehiculo
    tiempos = np.asarray(tiempos, dtype=float)
    sim = np.asarray(sim, dtype=float)
    t_fin = vuelo.tiempo_apogeo if vuelo.tiempo_apogeo is not None else tiempos[-1]

    cohete.actualizar_masa(0.0)
    bordes = np.linspace(0.0, longitud_viga(cohete), n_tramos + 1)
    instantes = np.arange(0.0, t_fin + 1e-9, paso)
    estados = np.column_stack([np.interp(instantes, tiempos, sim[:, k]) for k in range(sim.shape[1])])

    resultado = {"s": bordes, "secciones": secciones(cohete), "t_fin": float(t_fin), "paso": paso, "rafaga": float(rafaga)}
    resultado.update(_recorrer(vuelo, instantes, estados, bordes, s_empuje, 0.0))
    resultado["con_rafaga"] = _recorrer(vuelo, instantes, estados, bordes, s_empuje, rafaga) if rafaga else None
    return resultado
