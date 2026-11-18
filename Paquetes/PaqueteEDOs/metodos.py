"""Catálogo de los métodos de integración y una forma única de usarlos.

Todas las comparaciones (casos simples, vuelo completo, pruebas) toman de aquí la lista
de métodos y sus nombres, para que un mismo nombre signifique siempre el mismo método.

    from Paquetes.PaqueteEDOs.metodos import METODOS, FIJOS, ADAPTATIVOS, resolver

    sol = resolver("RKF45", f, (0, 20), y0)             # adaptativo, paso libre
    sol = resolver("RK45", f, (0, 20), y0, dt=0.1)      # adaptativo con paso máximo 0.1
    sol = resolver("RK4", f, (0, 20), y0, dt=0.1)       # paso fijo 0.1
    sol.t, sol.y, sol.pasos, sol.nfev, sol.tiempo
"""
from dataclasses import dataclass
from time import perf_counter

import numpy as np
from scipy.integrate import solve_ivp

from Paquetes.PaqueteEDOs.integradores import Euler, RungeKutta2, RungeKutta4, RKF45


@dataclass(frozen=True)
class Metodo:
    corto: str        # nombre corto para leyendas y tablas
    clave: str        # nombre con el que se elige en el simulador de vuelo
    nombre: str       # nombre del método en la literatura
    orden: str        # orden de la solución que se propaga (y del estimador de error, si lo hay)
    paso: str         # "fijo" o "adaptativo"
    origen: str       # "propio" (Paquetes/PaqueteEDOs/integradores.py) o "SciPy"
    tipo: str         # "explícito", "implícito" o "automático"
    clase: object = None   # clase del integrador propio


METODOS = {m.corto: m for m in [
    Metodo("Euler", "Euler", "Euler explícito", "1", "fijo", "propio", "explícito", Euler),
    Metodo("RK2", "RungeKutta2", "Heun (Runge-Kutta de orden 2)", "2", "fijo", "propio", "explícito", RungeKutta2),
    Metodo("RK4", "RungeKutta4", "Runge-Kutta clásico de orden 4", "4", "fijo", "propio", "explícito", RungeKutta4),
    Metodo("RKF45", "RKF45", "Runge-Kutta-Fehlberg 4(5)", "5(4)", "adaptativo", "propio", "explícito", RKF45),
    Metodo("RK23", "RK23", "Bogacki-Shampine 3(2)", "3(2)", "adaptativo", "SciPy", "explícito"),
    Metodo("RK45", "RK45", "Dormand-Prince 5(4)", "5(4)", "adaptativo", "SciPy", "explícito"),
    Metodo("DOP853", "DOP853", "Dormand-Prince 8(5,3)", "8(5,3)", "adaptativo", "SciPy", "explícito"),
    Metodo("BDF", "BDF", "BDF de orden variable (1 a 5)", "1-5", "adaptativo", "SciPy", "implícito"),
    Metodo("LSODA", "LSODA", "LSODA (Adams / BDF con cambio automático)", "variable", "adaptativo", "SciPy", "automático"),
]}

FIJOS = [m.corto for m in METODOS.values() if m.paso == "fijo"]
ADAPTATIVOS = [m.corto for m in METODOS.values() if m.paso == "adaptativo"]
# Nombres con los que el simulador de vuelo elige integrador, en el mismo orden
CLAVES_VUELO = [m.clave for m in METODOS.values()]


def metodo(nombre):
    """Busca un método por su nombre corto ("RK4") o por su clave de vuelo ("RungeKutta4")."""
    if nombre in METODOS:
        return METODOS[nombre]
    for m in METODOS.values():
        if m.clave == nombre:
            return m
    raise KeyError(f"Método desconocido: {nombre!r}. Disponibles: {', '.join(METODOS)}")


def etiqueta(nombre):
    """Texto para leyendas: 'RK45 · Dormand-Prince 5(4)'."""
    m = metodo(nombre)
    return f"{m.corto} · {m.nombre}"


@dataclass
class Solucion:
    metodo: str
    t: np.ndarray          # tiempos, forma (n,)
    y: np.ndarray          # estados, forma (dim, n), como solve_ivp
    pasos: int             # pasos aceptados
    nfev: int              # evaluaciones de la función de derivadas
    tiempo: float          # tiempo de cómputo de la integración (s), el menor de las repeticiones
    rechazados: int = 0    # pasos repetidos por exceder la tolerancia (solo RKF45)
    termino_por_evento: bool = False


def _cruza(evento, valor_antes, valor_despues):
    direccion = getattr(evento, "direction", 0)
    if direccion < 0:
        return valor_antes > 0 >= valor_despues
    if direccion > 0:
        return valor_antes < 0 <= valor_despues
    return valor_antes * valor_despues <= 0 and valor_antes != valor_despues


def _propio(m, f, t0, t1, y0, dt, evento, rtol, atol):
    """Integra con un método propio. Devuelve (t, y, pasos, rechazados, termino_por_evento)."""
    adaptativo = m.paso == "adaptativo"
    integrador = m.clase(f, rtol=rtol, atol=atol) if adaptativo else m.clase(f)
    paso_max = dt if dt is not None else np.inf
    h = dt if dt is not None else (t1 - t0) / 100.0      # paso inicial de los adaptativos libres
    eps = 1e-12 * max(1.0, abs(t1))

    t, y = t0, np.array(y0, dtype=float)
    ts, ys = [t], [y.copy()]
    g_antes = evento(t, y) if evento else None
    por_evento = False

    while t < t1 - eps:
        h = min(h, paso_max, t1 - t)
        y_nuevo, usado = integrador.step(t, y, h)
        t_nuevo = t + usado

        if evento is not None:
            g_despues = evento(t_nuevo, y_nuevo)
            if _cruza(evento, g_antes, g_despues):
                por_evento = True
                if adaptativo:
                    # Localizar el cruce sobre un interpolante cúbico de Hermite del paso
                    # (solo cuesta dos evaluaciones de f, como la salida densa de solve_ivp)
                    f_a, f_b = f(t, y), f(t_nuevo, y_nuevo)

                    def interpolar(s):
                        h00, h10 = 2*s**3 - 3*s**2 + 1, s**3 - 2*s**2 + s
                        h01, h11 = -2*s**3 + 3*s**2, s**3 - s**2
                        return h00*y + h10*usado*f_a + h01*y_nuevo + h11*usado*f_b

                    a, b = 0.0, 1.0
                    for _ in range(60):
                        c = 0.5 * (a + b)
                        if _cruza(evento, g_antes, evento(t + c*usado, interpolar(c))):
                            b = c
                        else:
                            a = c
                    ts.append(t + b*usado)
                    ys.append(interpolar(b))
                # Paso fijo: se descarta el paso que cruza (el último punto queda antes del evento)
                break
            g_antes = g_despues

        t, y = t_nuevo, y_nuevo
        ts.append(t)
        ys.append(y.copy())
        if adaptativo:
            h = integrador.dt_sugerido

    rechazados = getattr(integrador, "rechazados", 0)
    return np.array(ts), np.array(ys).T, len(ts) - 1, rechazados, por_evento


def resolver(nombre, f, t_span, y0, dt=None, events=None, rtol=1e-3, atol=1e-6, repeticiones=3):
    """Integra y' = f(t, y) con cualquiera de los métodos del catálogo.

    dt        Métodos de paso fijo: el paso (obligatorio).
              Métodos adaptativos: paso máximo; None deja el paso libre.
    events    Función g(t, y) con atributo `direction` (como en solve_ivp); la integración
              termina cuando g cruza cero. Los adaptativos devuelven el punto del cruce;
              los de paso fijo terminan en el último paso anterior al cruce.
    rtol, atol  Tolerancias de los métodos adaptativos (por defecto, las de solve_ivp).
    repeticiones  La integración se repite y se reporta el menor tiempo de cómputo.

    Devuelve una Solucion; `t` y `y` incluyen el punto inicial.
    """
    m = metodo(nombre)
    if m.paso == "fijo" and dt is None:
        raise ValueError(f"{m.corto} es de paso fijo: hay que indicar dt.")
    t0, t1 = float(t_span[0]), float(t_span[1])
    y0 = np.array(y0, dtype=float)

    mejor = None
    for _ in range(max(1, repeticiones)):
        llamadas = [0]

        def f_contada(t, y):
            llamadas[0] += 1
            return np.asarray(f(t, y), dtype=float)

        inicio = perf_counter()
        if m.origen == "SciPy":
            sol = solve_ivp(f_contada, (t0, t1), y0, method=m.clave, events=events,
                            max_step=dt if dt is not None else np.inf, rtol=rtol, atol=atol)
            if sol.status == -1:
                raise RuntimeError(f"solve_ivp ({m.corto}) falló: {sol.message}")
            duracion = perf_counter() - inicio
            actual = Solucion(m.corto, sol.t, sol.y, len(sol.t) - 1, llamadas[0], duracion,
                              termino_por_evento=sol.status == 1)
        else:
            t, y, pasos, rechazados, por_evento = _propio(m, f_contada, t0, t1, y0, dt, events, rtol, atol)
            duracion = perf_counter() - inicio
            actual = Solucion(m.corto, t, y, pasos, llamadas[0], duracion, rechazados, por_evento)
        if mejor is None or actual.tiempo < mejor.tiempo:
            mejor = actual
    return mejor


def tabla_metodos():
    """Tabla (lista de diccionarios) con la descripción de todos los métodos."""
    return [{"Método": m.corto, "Nombre": m.nombre, "Orden": m.orden, "Paso": m.paso,
             "Tipo": m.tipo, "Implementación": m.origen} for m in METODOS.values()]


def tabla_comparacion(df_err, corridas, col_posicion, col_velocidad):
    """Tabla de resultados de una comparación: una fila por método y modo de paso.

    df_err    DataFrame con la columna "Método" ("RK45_auto", "RK4_dt=0.1", ...) y los errores.
    corridas  diccionario {nombre: Solucion} con las integraciones correspondientes.
    """
    import pandas as pd
    filas = []
    for _, fila in df_err.iterrows():
        nombre = fila["Método"]
        base, modo = nombre.split("_", 1)
        m, sol = metodo(base), corridas[nombre]
        libre = modo == "auto"
        filas.append({
            "Método": m.corto,
            "Nombre": m.nombre,
            "Implementación": m.origen,
            "Modo": "paso libre" if libre else ("paso fijo" if m.paso == "fijo" else "paso máximo"),
            "dt": np.nan if libre else float(modo.split("=")[1]),
            "Pasos": sol.pasos,
            "Evaluaciones de f": sol.nfev,
            "Tiempo [ms]": sol.tiempo * 1e3,
            "Error L2 posición": fila[col_posicion],
            "Error L2 velocidad": fila[col_velocidad],
        })
    orden = {corto: i for i, corto in enumerate(METODOS)}
    tabla = pd.DataFrame(filas)
    tabla["_orden"] = tabla["Método"].map(orden)
    return tabla.sort_values(["_orden", "dt"], na_position="first").drop(columns="_orden").reset_index(drop=True)
