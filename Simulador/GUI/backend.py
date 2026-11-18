"""Puente entre la interfaz gráfica (ModernGUI) y el motor de simulación.

No depende de tkinter: recibe el diccionario de parámetros de los formularios y
devuelve objetos del simulador, tablas y DataFrames. Así se puede probar sin abrir
la ventana (ver tests/test_gui_backend.py).

Convención de posiciones: "Posición Z" es la distancia, en metros, desde la punta
de la nariz hasta el extremo frontal del componente (la misma que usa PaqueteFisica).
"""
import math
import os
import sys

import numpy as np
import pandas as pd

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)

from Paquetes.PaqueteEDOs.metodos import CLAVES_VUELO, etiqueta  # noqa: F401 (etiqueta la usa la GUI)
from Paquetes.PaqueteFisica.atmosfera import atmosfera
from Paquetes.PaqueteFisica.cohete import Cohete, Parachute
from Paquetes.PaqueteFisica.componentes import Aletas, Boattail, Cilindro, Cono
from Paquetes.PaqueteFisica.riel import Torrelanzamiento
from Paquetes.PaqueteFisica.viento import Viento
from Paquetes.PaqueteFisica.vuelo import Vuelo
from Paquetes.utils.geografia import a_geograficas, direccion_viento_simulador, distancia_y_rumbo
from Simulador.GUI import mapa
from Simulador.src import dia_de_vuelo

# Todos los métodos del catálogo; DOP853 primero porque es el que se usa por defecto
INTEGRADORES = ["DOP853"] + [clave for clave in CLAVES_VUELO if clave != "DOP853"]
RECUPERACION = ["Vuelo libre (sin paracaídas)", "Paracaídas drogue en el apogeo"]
VIENTOS = ["Perfil del día del vuelo (22-jun-2024)", "Constante (campos de abajo)"]
GEOMETRIAS_NARIZ = {"ogiva": "ogiva", "Cónico": "conica", "Elíptico": "eliptica", "Parabólico": "parabolica"}

# Diámetro de los componentes internos (aviónica, carga útil, paracaídas plegados, motor)
DIAM_INTERNO = 0.14

# Archivos de datos del Xitle II incluidos en el repositorio
RUTAS_XITLE = {
    "thrust": os.path.join(RAIZ, "Archivos", "CurvasEmpuje", "pruebaestaica28mayo2024.csv"),
    "drag": os.path.join(RAIZ, "Archivos", "cdmachXitle.csv"),
    "mass": os.path.join(RAIZ, "Archivos", "CurvasEmpuje", "MegaPunisherFatMasadot.csv"),
}

# Valores por defecto de los formularios: el Xitle II tal como está en Simulador/src/XitleFile.py
PARAMS_XITLE = {
    # --- Componentes externos ---
    "nose_len": 0.81, "nose_mass": 0.8, "nose_pos_z": 0.0, "nose_diam": 0.152, "nose_shape": "ogiva",
    "coples_len": 0.176, "coples_mass": 1.5, "coples_pos_z": 0.81, "coples_diam_ext": 0.152, "coples_diam_int": 0.149,
    "tubo_recup_len": 0.92, "tubo_recup_mass": 2.3, "tubo_recup_pos_z": 0.986, "tubo_recup_diam_ext": 0.152, "tubo_recup_diam_int": 0.149,
    "transfer_len": 0.25, "transfer_mass": 1.0, "transfer_pos_z": 1.906, "transfer_diam_ext": 0.152, "transfer_diam_int": 0.149,
    "tanque_vacio_len": 1.25, "tanque_vacio_mass": 8.7, "tanque_vacio_pos_z": 2.156, "tanque_vacio_diam_ext": 0.152, "tanque_vacio_diam_int": 0.149,
    "valvulas_len": 0.167, "valvulas_mass": 2.4, "valvulas_pos_z": 3.406, "valvulas_diam_ext": 0.152, "valvulas_diam_int": 0.149,
    "cc_len": 0.573, "cc_mass": 4.3, "cc_pos_z": 3.573, "cc_diam_ext": 0.152, "cc_diam_int": 0.102,
    "bt_len": 0.12, "bt_mass": 0.251, "bt_pos_z": 4.146, "bt_diam_front": 0.152, "bt_diam_rear": 0.132, "bt_espesor": 0.003,
    "fin_num": 4, "fin_mass": 1.1, "fin_pos_z": 4.146, "fin_span": 0.11, "fin_root_chord": 0.3, "fin_tip_chord": 0.1,
    "fin_xr": 0.2, "fin_sweep": 25,
    # --- Componentes internos ---
    "avionics_mass": 1.8, "avionics_pos_z": 0.20, "avionics_len": 0.21,
    "cu_mass": 4.3, "cu_pos_z": 0.50, "cu_len": 0.3,
    "motor_mass_inert": 0.0, "motor_pos_z": 3.573, "motor_len": 0.5,
    "drogue_mass": 0.6, "drogue_pos_z": 1.0, "drogue_len": 0.17, "drogue_chute_diam": 0.944, "drogue_cd": 0.8,
    "main_mass": 1.7, "main_pos_z": 1.4, "main_len": 0.30,
    # --- Propelentes ---
    "oxidante_mass": 12.0, "oxidante_pos_z": 2.156, "oxidante_len": 1.33, "oxidante_diam": 0.1461,
    "grano_mass": 4.0, "grano_pos_z": 3.573, "grano_length": 0.505, "grano_outer_diam": 0.158, "grano_inner_diam": 0.334,
    # --- Entorno y simulación ---
    # Sitio y día del vuelo real del Xitle II (Archivos/DatosVuelo/condiciones_2024-06-22.json)
    "launch_lat": 32.94753, "launch_lon": -106.91019, "launch_alt": 1395, "launch_date": "2024-06-22",
    "atm_delta_t": 20, "atm_pressure_hpa": 868.5,
    "wind_mode": VIENTOS[0],
    "wind_base_speed": 2, "wind_from": 195, "wind_mean_speed": 1, "wind_speed_var": 1, "wind_angle_var": 15, "wind_seed": "",
    "rail_len": 10, "rail_angle": 84, "rail_azimuth": 220,
    "sim_max_time": 400, "sim_time_step": 0.01, "integrator": "DOP853", "recovery": RECUPERACION[0],
}

# (clave del diccionario de componentes, prefijo de los campos, nombre visible)
_TUBOS_EXTERNOS = [
    ("coples", "coples", "Coples"),
    ("Tubo recuperación", "tubo_recup", "Tubo recuperación"),
    ("Transferidor de carga", "transfer", "Transferidor"),
    ("tanquevacio", "tanque_vacio", "Tanque vacío"),
    ("valvulas", "valvulas", "Válvulas"),
    ("Cámara Combustión", "cc", "Cámara de combustión"),
]
_INTERNOS = [
    ("Aviónica", "avionics", "avionics_mass", "Aviónica"),
    ("Carga Útil", "cu", "cu_mass", "Carga útil"),
    ("drogue", "drogue", "drogue_mass", "Drogue"),
    ("main", "main", "main_mass", "Main"),
    ("motor", "motor", "motor_mass_inert", "Motor (masa inerte)"),
]


def _num(params, clave):
    """Lee un parámetro numérico; si falta usa el valor por defecto del Xitle."""
    valor = params.get(clave, PARAMS_XITLE.get(clave))
    try:
        return float(valor)
    except (TypeError, ValueError):
        raise ValueError(f"El campo '{clave}' debe ser un número (valor recibido: {valor!r}).")


def _semilla(params):
    """Semilla de las ráfagas: entero para repetir el mismo viento; vacío = viento distinto en cada corrida."""
    valor = str(params.get("wind_seed", "")).strip()
    if valor == "":
        return None
    try:
        return int(float(valor))
    except ValueError:
        raise ValueError("La semilla del viento debe ser un número entero (o dejarse vacía).")


def _presion_sitio(params):
    """Presión en el sitio en Pa; None (campo vacío) usa la de la atmósfera estándar a esa altitud."""
    valor = str(params.get("atm_pressure_hpa", "")).strip()
    if valor == "":
        return None
    try:
        hpa = float(valor)
    except ValueError:
        raise ValueError("La presión en el sitio debe ser un número en hPa (o dejarse vacía).")
    if not 300 <= hpa <= 1100:
        raise ValueError("La presión en el sitio debe estar entre 300 y 1100 hPa.")
    return hpa * 100.0


def crear_atmosfera(params):
    """Atmósfera ISA ajustada a la altitud del sitio, la desviación de temperatura y la presión medida."""
    return atmosfera(altitud_sitio=_num(params, "launch_alt"), delta_T=_num(params, "atm_delta_t"),
                     presion_sitio=_presion_sitio(params))


def crear_viento(params):
    """Viento según el modo elegido: el perfil del día del vuelo real o un viento constante con ráfagas."""
    azimut = _num(params, "rail_azimuth")
    if params.get("wind_mode", VIENTOS[0]) == VIENTOS[0]:
        return dia_de_vuelo.crear_viento(dia_de_vuelo.cargar_condiciones(), azimut, semilla=_semilla(params))
    return Viento(vel_base=_num(params, "wind_base_speed"), vel_mean=_num(params, "wind_mean_speed"),
                  vel_var=_num(params, "wind_speed_var"), var_ang=_num(params, "wind_angle_var"),
                  ang_base=direccion_viento_simulador(_num(params, "wind_from"), azimut), semilla=_semilla(params))


def vuelo_real():
    """Trayectoria GPS del vuelo real del Xitle II: lista de [lat, lon] desde el despegue y último punto."""
    try:
        gps = pd.read_csv(os.path.join(RAIZ, "Archivos", "DatosVuelo", "FTW.csv"))
        gps.columns = [c.strip() for c in gps.columns]
        altura = gps["Alt AGL (ft)"] * 0.3048
        en_tierra = altura[: altura.idxmax()] < 15
        inicio = en_tierra[en_tierra].index[-1]
        tramo = gps.loc[inicio:]
        return {
            "trayectoria": tramo[["TRACKER Lat", "TRACKER Lon"]].values.tolist(),
            "sitio": (float(tramo["TRACKER Lat"].iloc[0]), float(tramo["TRACKER Lon"].iloc[0])),
            "ultimo": {"lat": float(tramo["TRACKER Lat"].iloc[-1]), "lon": float(tramo["TRACKER Lon"].iloc[-1]),
                       "nota": f"a {altura.iloc[-1]:.0f} m de altura, aún bajando"},
            "apogeo": float(altura.max()),
        }
    except Exception as error:
        print(f"No se pudo leer la trayectoria GPS del vuelo real: {error}")
        return None


def _pos(z):
    return np.array([0.0, 0.0, z])


def validar_parametros(params):
    """Lanza ValueError con un mensaje claro si algún parámetro no tiene sentido físico."""
    positivos = ["nose_len", "nose_diam", "bt_len", "bt_diam_front", "bt_diam_rear", "fin_span",
                 "fin_root_chord", "fin_tip_chord", "rail_len", "sim_max_time", "sim_time_step"]
    positivos += [f"{pref}_len" for _, pref, _ in _TUBOS_EXTERNOS]
    for clave in positivos:
        if _num(params, clave) <= 0:
            raise ValueError(f"El campo '{clave}' debe ser mayor que 0.")
    for clave in params:
        if clave.endswith("_mass") or clave == "motor_mass_inert":
            if _num(params, clave) < 0:
                raise ValueError(f"La masa '{clave}' no puede ser negativa.")
    if _num(params, "fin_num") < 3:
        raise ValueError("El número de aletas debe ser al menos 3.")
    angulo = _num(params, "rail_angle")
    if not 0 < angulo <= 90:
        raise ValueError("El ángulo de elevación del riel debe estar entre 0° y 90°.")
    if not -90 <= _num(params, "launch_lat") <= 90 or not -180 <= _num(params, "launch_lon") <= 180:
        raise ValueError("La latitud debe estar entre -90° y 90° y la longitud entre -180° y 180°.")
    if _num(params, "launch_alt") < -500 or _num(params, "launch_alt") > 6000:
        raise ValueError("La altitud del sitio debe estar entre -500 m y 6000 m sobre el nivel del mar.")
    _presion_sitio(params)
    _semilla(params)
    if params.get("integrator", "DOP853") not in INTEGRADORES:
        raise ValueError(f"Integrador desconocido: {params.get('integrator')!r}.")


def _verificar_rutas(rutas):
    nombres = {"thrust": "empuje", "drag": "arrastre (Cd vs Mach)", "mass": "masa del motor"}
    for clave, nombre in nombres.items():
        ruta = rutas.get(clave)
        if not ruta or not os.path.isfile(ruta):
            raise ValueError(f"Falta el archivo de {nombre}. Cárguelo en la pestaña 'Tablas de Datos'.")


def construir_cohete(params, rutas, riel=None, nombre="Cohete GUI"):
    """Crea el objeto Cohete del simulador a partir de los campos del formulario."""
    validar_parametros(params)
    _verificar_rutas(rutas)
    n = lambda clave: _num(params, clave)
    if riel is None:
        riel = Torrelanzamiento(n("rail_len"), n("rail_angle"))

    geometria = GEOMETRIAS_NARIZ.get(params.get("nose_shape", "ogiva"), params.get("nose_shape", "ogiva"))
    nariz = Cono("Nariz", n("nose_mass"), _pos(n("nose_pos_z")), n("nose_len"), n("nose_diam"), geometria)

    componentes = {"Nariz": nariz}
    externos = {"Nariz": nariz}
    for clave, pref, visible in _TUBOS_EXTERNOS:
        tubo = Cilindro(visible, n(f"{pref}_mass"), _pos(n(f"{pref}_pos_z")), n(f"{pref}_len"),
                        n(f"{pref}_diam_ext"), n(f"{pref}_diam_int"))
        componentes[clave] = tubo
        externos[clave] = tubo

    for clave, pref, campo_masa, visible in _INTERNOS:
        masa = n(campo_masa)
        if masa <= 0:
            continue   # componente opcional sin masa: no se incluye
        componentes[clave] = Cilindro(visible, masa, _pos(n(f"{pref}_pos_z")), n(f"{pref}_len"), DIAM_INTERNO, 0)

    componentes["oxidante"] = Cilindro("Oxidante", n("oxidante_mass"), _pos(n("oxidante_pos_z")),
                                       n("oxidante_len"), n("oxidante_diam"), 0)
    componentes["grano"] = Cilindro("Grano", n("grano_mass"), _pos(n("grano_pos_z")), n("grano_length"),
                                    n("grano_outer_diam"), n("grano_inner_diam"))
    componentes["Aletas"] = Aletas("Aletas", n("fin_mass"), _pos(n("fin_pos_z")), n("cc_diam_ext"),
                                   int(n("fin_num")), n("fin_span"), n("fin_root_chord"), n("fin_tip_chord"),
                                   n("fin_xr"), math.radians(n("fin_sweep")))
    boattail = Boattail("Boattail", n("bt_mass"), _pos(n("bt_pos_z")), n("bt_len"),
                        n("bt_diam_front"), n("bt_diam_rear"), n("bt_espesor"))
    componentes["Boattail"] = boattail
    externos["Boattail"] = boattail

    cohete = Cohete(nombre, "hibrido", componentes, externos, rutas["drag"], rutas["thrust"], rutas["mass"], riel)
    cohete.d_ext = n("nose_diam")
    return cohete


def analizar_estabilidad(params, rutas):
    """CG, CP y margen estático (en calibres) al despegue y al final del quemado."""
    cohete = construir_cohete(params, rutas)
    diametro = cohete.d_ext

    def margen():
        return (cohete.CP[2] - cohete.CG[2]) / diametro

    cohete.actualizar_masa(0.0)   # masas de propelente de la tabla del motor en t = 0
    filas = []
    for comp in cohete.componentes.values():
        cp = comp.posicion[2] + comp.CP[2] if comp.CN else None
        filas.append((comp.nombre, comp.masa, comp.posicion[2] + comp.CG[2], cp))
    resultado = {
        "filas": filas,
        "masa": cohete.masa, "cg": cohete.CG[2], "cp": cohete.CP[2], "margen": margen(),
        "longitud": cohete.longtotal, "diametro": diametro,
    }
    cohete.actualizar_masa(cohete.t_MECO + 1.0)
    resultado.update(masa_seca=cohete.masa, cg_seco=cohete.CG[2], margen_seco=margen())
    return resultado


def ejecutar_simulacion(params, rutas, estado_cb=None, con_mapa=False):
    """Corre el vuelo completo. Devuelve (DataFrame con la trayectoria, dict de resumen).

    con_mapa=True descarga además el fondo de OpenStreetMap de la zona del vuelo (necesita
    internet) y lo deja en resumen["mapa"] para dibujarlo en la interfaz.
    """
    avisar = estado_cb or (lambda mensaje: None)
    n = lambda clave: _num(params, clave)

    avisar("Construyendo el cohete...")
    riel = Torrelanzamiento(n("rail_len"), n("rail_angle"))
    cohete = construir_cohete(params, rutas, riel)

    con_paracaidas = params.get("recovery", RECUPERACION[0]) == RECUPERACION[1]
    if con_paracaidas:
        area = math.pi * n("drogue_chute_diam") ** 2 / 4
        cohete.agregar_paracaidas(Parachute(n("drogue_cd"), area))

    viento = crear_viento(params)
    vuelo = Vuelo(cohete, crear_atmosfera(params), viento)

    integrador = params.get("integrator", "DOP853")
    dt = n("sim_time_step")
    estado0 = np.array([0, 0, 0, 0, 0, 0, np.deg2rad(riel.angulo), 0], dtype=float)

    avisar(f"Integrando el vuelo con {integrador}...")
    (tiempos, sim, CPs, CGs, masas, v_mags, v_dirs, v_vecs, Tvecs, Dvecs, Nvecs, accels,
     palancas, accangs, Gammas, Alphas, torcas, Cds, Machs) = vuelo.simular_vuelo(
        estado0, n("sim_max_time"), dt, dt, integrador)

    avisar("Procesando resultados...")
    sim = np.array(sim)
    if len(sim) == 0:
        raise RuntimeError("La simulación no produjo ningún punto.")
    v_vecs = np.array(v_vecs)
    df = pd.DataFrame({
        "t": tiempos,
        "x": sim[:, 0], "y": sim[:, 1], "z": sim[:, 2],
        "vx": sim[:, 3], "vy": sim[:, 4], "vz": sim[:, 5],
        "theta": np.rad2deg(sim[:, 6]), "omega": sim[:, 7],
        "velocidad": np.linalg.norm(sim[:, 3:6], axis=1),
        "aceleracion": np.linalg.norm(np.array(accels), axis=1),
        "acel_angular": accangs,
        "masa": masas, "CG": CGs, "CP": CPs,
        "margen": (np.array(CPs) - np.array(CGs)) / cohete.d_ext,
        "mach": Machs, "cd": Cds,
        "alpha": np.rad2deg(np.arctan2(np.sin(Alphas), np.cos(Alphas))),
        "gamma": np.rad2deg(Gammas),
        "empuje": np.linalg.norm(np.array(Tvecs), axis=1),
        "arrastre": np.linalg.norm(np.array(Dvecs), axis=1),
        "normal": np.linalg.norm(np.array(Nvecs), axis=1),
        "viento": v_mags, "viento_x": v_vecs[:, 0], "viento_y": v_vecs[:, 1], "viento_z": v_vecs[:, 2],
    })

    # Coordenadas geográficas de la trayectoria
    lat0, lon0, azimut = n("launch_lat"), n("launch_lon"), n("rail_azimuth")
    geo = np.array([a_geograficas(x, y, lat0, lon0, azimut) for x, y in zip(df["x"], df["y"])])
    df["latitud"], df["longitud"] = geo[:, 0], geo[:, 1]

    i_ap = int(df["z"].idxmax())
    fuera_riel = df[df["t"] >= vuelo.tiempo_salida_riel] if vuelo.tiempo_salida_riel is not None else None
    resumen = {
        "integrador": integrador,
        "paracaidas": con_paracaidas,
        "masa_despegue": float(df["masa"].iloc[0]),
        "t_MECO": float(cohete.t_MECO),
        "impulso_total": float(cohete.I_total),
        "t_salida_riel": None if vuelo.tiempo_salida_riel is None else float(vuelo.tiempo_salida_riel),
        "vel_salida_riel": float(fuera_riel["velocidad"].iloc[0]) if fuera_riel is not None and len(fuera_riel) else None,
        "apogeo": float(df["z"].iloc[i_ap]),
        "t_apogeo": float(df["t"].iloc[i_ap]),
        "vel_max": float(df["velocidad"].max()),
        "mach_max": float(df["mach"].max()),
        "acel_max": float(df["aceleracion"].max()),
        "t_impacto": None if vuelo.tiempo_impacto is None else float(vuelo.tiempo_impacto),
        "vel_impacto": float(df["velocidad"].iloc[-1]) if vuelo.tiempo_impacto is not None else None,
        "distancia": float(math.hypot(df["x"].iloc[-1], df["y"].iloc[-1])),
        "rumbo_impacto": distancia_y_rumbo(lat0, lon0, float(df["latitud"].iloc[-1]), float(df["longitud"].iloc[-1]))[1],
        "lat_lanzamiento": lat0, "lon_lanzamiento": lon0, "altitud_sitio": n("launch_alt"), "azimut_riel": azimut,
        "lat_apogeo": float(df["latitud"].iloc[i_ap]), "lon_apogeo": float(df["longitud"].iloc[i_ap]),
        "distancia_apogeo": float(math.hypot(df["x"].iloc[i_ap], df["y"].iloc[i_ap])),
        # Punto final de la simulación: el impacto, o el último punto si se acabó el tiempo antes
        "lat_impacto": float(df["latitud"].iloc[-1]), "lon_impacto": float(df["longitud"].iloc[-1]),
        "viento_modo": params.get("wind_mode", VIENTOS[0]),
        "margen_min": float(df["margen"].min()),
        "t_final": float(df["t"].iloc[-1]),
    }
    # Vuelo real, si el lanzamiento simulado es desde el mismo sitio (a menos de 1 km)
    real = vuelo_real()
    if real and distancia_y_rumbo(lat0, lon0, *real["sitio"])[0] < 1000:
        resumen["vuelo_real"] = real
    else:
        resumen["vuelo_real"] = None

    resumen["mapa"] = None
    if con_mapa:
        avisar("Descargando el mapa de la zona...")
        lats, lons = list(df["latitud"]), list(df["longitud"])
        if resumen["vuelo_real"]:
            lats += [p[0] for p in real["trayectoria"]]
            lons += [p[1] for p in real["trayectoria"]]
        resumen["mapa"] = mapa.descargar_mosaico(lats, lons)

    avisar("Simulación completada.")
    return df, resumen


def datos_mapa_interactivo(df, resumen):
    """Datos que necesita mapa.escribir_html para el mapa interactivo del navegador."""
    r = resumen
    paso = max(1, len(df) // 400)
    trayectoria = df[["latitud", "longitud"]].iloc[::paso].values.tolist() + [[r["lat_impacto"], r["lon_impacto"]]]
    filas = [
        ["Lanzamiento", f"{r['lat_lanzamiento']:.5f}, {r['lon_lanzamiento']:.5f}"],
        ["Apogeo", f"{r['apogeo']:.0f} m sobre el sitio"],
        ["Impacto" if r["t_impacto"] is not None else "Punto final", f"{r['lat_impacto']:.5f}, {r['lon_impacto']:.5f}"],
        ["Distancia", f"{r['distancia']:.0f} m, rumbo {r['rumbo_impacto']:.0f}°"],
    ]
    datos = {
        "lanzamiento": {"lat": r["lat_lanzamiento"], "lon": r["lon_lanzamiento"], "nota": f"{r['altitud_sitio']:.0f} m s. n. m."},
        "apogeo": {"lat": r["lat_apogeo"], "lon": r["lon_apogeo"], "nota": f"{r['apogeo']:.0f} m sobre el sitio"},
        "impacto": {"lat": r["lat_impacto"], "lon": r["lon_impacto"],
                    "nota": f"a {r['distancia']:.0f} m del sitio, rumbo {r['rumbo_impacto']:.0f}°"},
        "trayectoria": trayectoria,
        "resumen": filas,
        "real": None,
    }
    if r.get("vuelo_real"):
        real = r["vuelo_real"]
        datos["real"] = {"trayectoria": real["trayectoria"], "ultimo": real["ultimo"]}
        d, rumbo = distancia_y_rumbo(r["lat_lanzamiento"], r["lon_lanzamiento"], real["ultimo"]["lat"], real["ultimo"]["lon"])
        filas.append(["Vuelo real", f"último GPS a {d:.0f} m, rumbo {rumbo:.0f}°"])
    return datos
