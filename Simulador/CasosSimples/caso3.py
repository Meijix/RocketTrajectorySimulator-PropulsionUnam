#Caso 3
#Movimiento vertical con gravedad y arrastre cuadratico
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
import os
import sys


# Agregar la ruta del directorio que contiene los paquetes al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from Paquetes.PaqueteEDOs.integradores import Euler, RungeKutta4

# Constantes y configuración
g = 9.81
x0, y0 = 0, 0
#v = 50 # m/s magnitud de la velocidad inicial
#v0x, v0y = v* np.cos(np.pi/4), v * np.sin(np.pi/4)
v0x, v0y = 50, 50
estado0 = [x0, y0, v0x, v0y]

t_max = 30
k = 0.1
m = 1
dt_vals = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5]
metodos_adaptativos = ['RK45', 'BDF', 'LSODA', 'DOP853']
metodos_fijos = [(Euler, "Euler"), (RungeKutta4, "RK4")]


# Funciones base
def sol_analitica(t, estado0):
    x0, y0, vx0, vy0 = estado0

    # Constantes auxiliares
    alpha = k / m
    sqrt_gk = np.sqrt(g * alpha)
    factor_v = np.sqrt(alpha / g)

    # Componentes de la solución
    vx_t = vx0 / (1 + alpha * vx0 * t)
    x_t = (1 / alpha) * np.log(1 + alpha * vx0 * t) + x0

    vy_t = np.sqrt(g / alpha) * np.tan(
        -sqrt_gk * t + np.arctan(vy0 * factor_v)
    )

    y_t = (1 / alpha) * np.log(
        np.sqrt(1 + vy0**2 * alpha / g) *
        np.cos(sqrt_gk * t - np.arctan(vy0 * factor_v))
    )

    y_t += y0  # ajustar si y0 ≠ 0

    return np.array([x_t, y_t, vx_t, vy_t])


def fun_derivada(t, state):
    x, y, vx, vy = state
    v = np.sqrt(vx**2 + vy**2)
    ax = - (k / m) * v * vx
    ay = -g - (k / m) * v * vy
    return np.array([vx, vy, ax, ay])


def evento_apogeo(t, y): return y[1]
evento_apogeo.terminal = True
evento_apogeo.direction = -1

def evento_impacto(t, y):
    return y[1]  # y representa la posición vertical

evento_impacto.terminal = True      # detiene la integración
evento_impacto.direction = -1       # solo detecta cuando y cruza 0 descendiendo

# Almacenar resultados para análisis
# Almacenar resultados para análisis
resultados = []

# 1. Adaptativos automáticos
dt_evolucion = []  # Lista para almacenar la evolución del paso de tiempo

for metodo in metodos_adaptativos:
    sol = solve_ivp(fun_derivada, [0, t_max], estado0, method=metodo, events=evento_impacto)

    for t, x, y, vx, vy in zip(sol.t, sol.y[0], sol.y[1], sol.y[2], sol.y[3]):
        x_a, y_a, vx_a, vy_a = sol_analitica(t, estado0)
        resultados.append([f"{metodo}_auto", np.nan, t, x, y, vx, vy, x_a, y_a, vx_a, vy_a])

    # Guardar pasos de tiempo locales
    dt_locales = np.diff(sol.t)
    t_locales = sol.t[:-1]
    for ti, dti in zip(t_locales, dt_locales):
        dt_evolucion.append([metodo, ti, dti])

df_dtevo = pd.DataFrame(dt_evolucion, columns=["Método", "t", "dt"])


# Evolución temporal del paso de tiempo
plt.figure(figsize=(10, 6))
for metodo in df_dtevo["Método"].unique():
    sub = df_dtevo[df_dtevo["Método"] == metodo]
    plt.plot(sub["t"], sub["dt"], label=metodo, marker='o', markersize=3, linewidth=1.5)

plt.xlabel("Tiempo [s]")
plt.ylabel("Paso de tiempo local (dt) [s]")
plt.title("Evolución temporal del paso de tiempo en métodos adaptativos")
plt.grid(True)
plt.legend(title="Método")
plt.tight_layout()
plt.show()

import seaborn as sns

def resumen_dt_por_metodo(df):
    return df.groupby("Método").agg(
        #dt_inicial=("dt", lambda x: x.iloc[0]),
        dt_final=("dt", lambda x: x.iloc[-1]),
        #dt_min=("dt", "min"),
        dt_max=("dt", "max"),
        dt_promedio=("dt", "mean")
    ).reset_index()

df_resumen_dt = resumen_dt_por_metodo(df_dtevo)

# Gráfica de resumen de estadísticas de dt
plt.figure(figsize=(12, 6))
df_melt = df_resumen_dt.melt(id_vars="Método", var_name="Estadística", value_name="dt")

ax = sns.barplot(data=df_melt, x="Método", y="dt", hue="Estadística")
for container in ax.containers:
    ax.bar_label(container, fmt="%.4f", padding=3)

plt.title("Estadísticas del paso de tiempo en métodos adaptativos")
plt.ylabel("Paso de tiempo (dt)")
plt.xlabel("Método")
plt.grid(True, axis='y')
plt.tight_layout()
plt.show()


####################################
#################################
# 2. Adaptativos con max_step
for metodo in metodos_adaptativos:
    for dt in dt_vals:
        nombre_metodo = f"{metodo}_dt={dt:.3f}"
        sol = solve_ivp(fun_derivada, [0, t_max], [x0, y0, v0x, v0y], method=metodo, max_step=dt, events=evento_impacto)
        for t, x, y, vx, vy in zip(sol.t, sol.y[0], sol.y[1], sol.y[2], sol.y[3]):
            estado_a = sol_analitica(t, estado0)
            x_a, y_a, vx_a, vy_a = estado_a
            resultados.append([nombre_metodo, dt, t, x, y, vx, vy, x_a, y_a, vx_a, vy_a])

# 3. Euler y RK4
for clase, nombre in metodos_fijos:
    for dt in dt_vals:
        nombre_metodo = f"{nombre}_dt={dt:.3f}"
        integ = clase(fun_derivada)
        estado = np.array([x0, y0, v0x, v0y])
        t = 0
        while t < t_max:
            nuevo_estado, _ = integ.step(t, estado, dt)
            t += dt
            if nuevo_estado[1] < 0:
                break
            estado = nuevo_estado
            x, y, vx, vy = estado
            estado_a = sol_analitica(t, estado0)
            x_a, y_a, vx_a, vy_a = estado_a
            resultados.append([nombre_metodo, dt, t, x, y, vx, vy, x_a, y_a, vx_a, vy_a])

# Convertir a estructura numpy
df = pd.DataFrame(resultados, columns=["Método", "dt", "t", "x_num","y_num", "vx_num","vy_num", "x_analitica", "y_analitica","vx_analitica", "vy_analitica"])

# ================== GRÁFICAS =====================

apogeo_data = []
for metodo in df["Método"].unique():
    sub = df[df["Método"] == metodo]
    if not sub.empty and sub["dt"].notna().any():
        y_max = sub["y_num"].max()
        t_ap = sub[sub["y_num"] == y_max]["t"].iloc[0]
        apogeo_data.append([metodo, sub["dt"].iloc[0], y_max, t_ap])

df_apogeo = pd.DataFrame(apogeo_data, columns=["Método", "dt", "z_apogeo", "t_apogeo"])

# 1. Trayectoria para dt=0.5 con marcadores y apogeo analítico
plt.figure()
for metodo in df["Método"].unique():
    if "_dt=0.5" in metodo:
        sub = df[df["Método"] == metodo]
        plt.plot(sub["t"], sub["y_num"], label=metodo.split("_")[0], marker='o', markersize=4, linestyle='-')

plt.plot(sub["t"], sub["y_analitica"], label="Analítica", color="gray", linewidth=1, linestyle='--')
#plt.plot(t_ap, z_ap, marker='*', color='red', markersize=14, label="Apogeo analítico (punto)")
#plt.axhline(v0y**2 / (2 * g), color='gray', linestyle=':', linewidth=2, label="Apogeo analítico")
plt.title("Trayectoria para dt = 0.5")
plt.xlabel("t [s]"); plt.ylabel("y(t) [m]")
plt.legend(); plt.grid(); plt.tight_layout()
plt.show()

# 2. Velocidad vertical para dt=0.5 con marcadores
plt.figure()
for metodo in df["Método"].unique():
    if "_dt=0.5" in metodo:
        sub = df[df["Método"] == metodo]
        plt.plot(sub["t"], sub["vy_num"], label=metodo.split("_")[0], marker='x', markersize=4, linestyle='-')

plt.plot(sub["t"], sub["vy_analitica"], label="Analítica vy", color="gray", linewidth=1, linestyle='--')
plt.title("Velocidad vertical para dt = 0.5")
plt.xlabel("t [s]")
plt.ylabel("v_y(t) [m/s]")
plt.legend()
plt.grid()
plt.tight_layout()
plt.show()

# 3. Velocidad horizontal para dt=0.5 con marcadores
plt.figure()
for metodo in df["Método"].unique():
    if "_dt=0.5" in metodo:
        sub = df[df["Método"] == metodo]
        plt.plot(sub["t"], sub["vx_num"], label=metodo.split("_")[0], marker='x', markersize=4, linestyle='-')

plt.plot(sub["t"], sub["vx_analitica"], label="Analítica vx", color="gray", linewidth=1, linestyle='--')
plt.title("Velocidad horizontal para dt = 0.5")
plt.xlabel("t [s]")
plt.ylabel("v_x(t) [m/s]")
plt.legend()
plt.grid()
plt.tight_layout()
plt.show()

# 4. Posición horizontal para dt=0.5 con marcadores
plt.figure()
for metodo in df["Método"].unique():
    if "_dt=0.5" in metodo:
        sub = df[df["Método"] == metodo]
        plt.plot(sub["t"], sub["x_num"], label=metodo.split("_")[0], marker='o', markersize=4, linestyle='-')

plt.plot(sub["t"], sub["x_analitica"], label="Analítica x", color="gray", linewidth=1, linestyle='--')
plt.title("Posición horizontal para dt = 0.5")
plt.xlabel("t [s]")
plt.ylabel("x(t) [m]")
plt.legend()
plt.grid()
plt.tight_layout()
plt.show()


# Preparar errores por método
errores = []
for metodo in df["Método"].unique():
    sub = df[df["Método"] == metodo]
    pasos = len(sub)
    e_x = np.sqrt(np.mean((sub["x_num"] - sub["x_analitica"])**2))
    e_y = np.sqrt(np.mean((sub["y_num"] - sub["y_analitica"])**2))

    e_vx = np.sqrt(np.mean((sub["vx_num"] - sub["vx_analitica"])**2))
    e_vy = np.sqrt(np.mean((sub["vy_num"] - sub["vy_analitica"])**2))

    # Error total en posición y velocidad
    dist_pos = np.sqrt((sub["x_num"] - sub["x_analitica"])**2 + (sub["y_num"] - sub["y_analitica"])**2)
    dist_vel = np.sqrt((sub["vx_num"] - sub["vx_analitica"])**2 + (sub["vy_num"] - sub["vy_analitica"])**2)

    # Norma L2 (media cuadrática)
    e_pos = np.sqrt(np.mean(dist_pos**2))
    e_vel = np.sqrt(np.mean(dist_vel**2))

    # Número de pasos
    N = len(sub)

    # Eficiencia
    Eff_pos = 1 / (e_pos * N)
    Eff_vel = 1 / (e_vel * N)

    #corregir las eficiencias
    errores.append([metodo, pasos, e_x, e_y, e_vx, e_vy, e_pos, e_vel, dist_pos, dist_vel, Eff_pos, Eff_vel]) #

df_err = pd.DataFrame(errores, columns=["Método", "Pasos", "error_x", "error_y", "error_vx", "error_vy", "L2_pos", "L2_vel", "dist_pos", "dist_vel", "Eff_pos", "Eff_vel"])

# 3. L2 en posición vs dt (líneas por método con marcadores; cruz para métodos auto)
plt.figure()
base_metodos = {}
colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown', 'teal', 'magenta']
color_idx = 0

# Agrupar métodos por base (Euler, RK4, etc.)
for metodo in df_err["Método"]:
    base = metodo.split("_")[0]
    base_metodos.setdefault(base, []).append(metodo)

# Graficar por base
for base, metodos in base_metodos.items():
    dts = []
    errores = []
    for metodo in metodos:
        fila = df_err[df_err["Método"] == metodo]
        if fila.empty:
            continue

        # Obtener dt de df original
        sub_df = df[df["Método"] == metodo]
        if sub_df.empty:
            continue
        dt = sub_df["dt"].dropna().iloc[0] if "_dt=" in metodo else 0.55
        err = fila["L2_pos"].iloc[0]

        if "_auto" in metodo:
            color = colors[color_idx % len(colors)]
            plt.scatter(dt, err, marker='x', s=100, color=color, label=base + " (auto)")
            color_idx += 1
        else:
            dts.append(dt)
            errores.append(err)

    if dts:
        plt.plot(dts, errores, label=base, marker='o', linestyle='-')

# Estética
plt.xscale("log")
plt.yscale("log")
plt.xlabel("Paso de tiempo (dt)")
plt.ylabel("Error total en posición (distancia)")
plt.title("Convergencia:L2 en posición vs dt")
plt.grid(True)
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)
plt.tight_layout()
plt.show()


# 5. Eficiencia numérica: Error L2 en posición vs número de pasos (color por método base, estrella para auto, línea identidad)
plt.figure(figsize=(10, 6))
base_metodos = {}
colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple', 'tab:brown', 'tab:pink', 'tab:gray']
color_map = {}

for metodo in df_err["Método"]:
    base = metodo.split("_")[0]
    base_metodos.setdefault(base, []).append(metodo)

for i, (base, metodos) in enumerate(base_metodos.items()):
    color = colors[i % len(colors)]
    color_map[base] = color
    for metodo in metodos:
        fila = df_err[df_err["Método"] == metodo]
        if fila.empty: continue
        pasos = fila["Pasos"].values[0]
        error = fila["L2_pos"].values[0]
        marker = '*' if '_auto' in metodo else 'o'
        plt.scatter(pasos, error, color=color, label=base if metodo == metodos[0] else "", s=100 if marker == '*' else 60, marker=marker)

plt.xscale("log"); plt.yscale("log")
plt.xlabel("Número de pasos")
plt.ylabel("Error L2 en posición")
plt.title("Eficiencia numérica: Error vs número de pasos")
plt.grid(True)
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)
plt.tight_layout()
plt.show()

# Gráfica 12: Apogeo y tiempo de apogeo vs dt
# Extraer base y asignar color
df_apogeo["base"] = df_apogeo["Método"].apply(lambda x: x.split("_")[0])
bases = sorted(df_apogeo["base"].unique())
colores = plt.cm.tab10(np.linspace(0, 1, len(bases)))
color_map = dict(zip(bases, colores))

# 1️⃣ Gráfica de altura de apogeo vs dt
plt.figure(figsize=(10, 5))
for base in bases:
    sub_base = df_apogeo[df_apogeo["base"] == base].copy()
    sub_base["dt_plot"] = sub_base["dt"]
    sub_base.loc[sub_base["dt_plot"].isna(), "dt_plot"] = 1e-3
    sub_base = sub_base.sort_values("dt_plot")

    # Línea + estrella si es automático
    plt.plot(sub_base["dt_plot"], sub_base["z_apogeo"], color=color_map[base], marker='o', label=base)
    auto_point = sub_base[sub_base["dt"].isna()]
    if not auto_point.empty:
        plt.scatter(auto_point["dt_plot"], auto_point["z_apogeo"], marker='*', s=150, color=color_map[base], label=base + " (auto)")

#plt.axhline(v0y**2 / (2 * g), color='black', linestyle='--', label="z apogeo analítico")
plt.xlabel("Paso de tiempo (dt)")
plt.ylabel("Altura de apogeo [m]")
plt.title("Altura de apogeo vs paso de tiempo")
plt.grid(True)
plt.legend(loc='best')
plt.tight_layout()
plt.show()


# 2️⃣ Gráfica de tiempo al apogeo vs dt
plt.figure(figsize=(10, 5))
for base in bases:
    sub_base = df_apogeo[df_apogeo["base"] == base].copy()
    sub_base["dt_plot"] = sub_base["dt"]
    sub_base.loc[sub_base["dt_plot"].isna(), "dt_plot"] = 1e-3
    sub_base = sub_base.sort_values("dt_plot")

    plt.plot(sub_base["dt_plot"], sub_base["t_apogeo"], color=color_map[base], marker='o', label=base)
    auto_point = sub_base[sub_base["dt"].isna()]
    if not auto_point.empty:
        plt.scatter(auto_point["dt_plot"], auto_point["t_apogeo"], marker='*', s=150, color=color_map[base], label=base + " (auto)")

#plt.axhline(v0y / g, color='black', linestyle='--', label="t apogeo analítico")
plt.xlabel("Paso de tiempo (dt)")
plt.ylabel("Tiempo de apogeo [s]")
plt.title("Tiempo de apogeo vs paso de tiempo")
plt.grid(True)
plt.legend(loc='best')
plt.tight_layout()
plt.show()




# Gráfica 13: Error L2 vs tiempo de cómputo (simulado)
from time import perf_counter
tiempos = []
for metodo in df["Método"].unique():
    sub = df[df["Método"] == metodo]
    t0 = perf_counter()
    e_l2 = np.sqrt(np.mean((sub["x_num"] - sub["x_analitica"])**2 + (sub["y_num"] - sub["y_analitica"])**2))
    t1 = perf_counter()
    tiempos.append([metodo, t1 - t0, e_l2])
df_tiempos = pd.DataFrame(tiempos, columns=["Método", "tiempo", "error_L2"])

# 13. Error L2 vs tiempo computacional (color por método base, estrella para auto, etiquetas dt=..., leyenda por método)
df_tiempos["base"] = df_tiempos["Método"].apply(lambda x: x.split("_")[0])
bases = sorted(df_tiempos["base"].unique())
colores = plt.cm.tab10(np.linspace(0, 1, len(bases)))
color_map = dict(zip(bases, colores))

# Obtener los valores de dt conocidos
dt_dict = df.set_index("Método")["dt"].dropna().to_dict()

plt.figure(figsize=(10, 6))
handles = {}

for i, row in df_tiempos.iterrows():
    metodo = row["Método"]
    base = row["base"]
    color = color_map[base]
    tiempo = row["tiempo"]
    error = row["error_L2"]
    dt = dt_dict.get(metodo, None)
    
    # Selección del marcador
    marker = '*' if dt is None else 'o'
    size = 150 if marker == '*' else 80

    # Dibujar punto
    point = plt.scatter(tiempo, error, color=color, marker=marker, s=size)

    # Guardar un solo punto por método base para la leyenda
    if base not in handles:
        handles[base] = point

    # Etiqueta textual
    label_txt = f"dt={dt:.3f}" if dt is not None else "dt=auto"
    plt.text(tiempo*1.003, error*1.003, label_txt, fontsize=8, ha='left', va='bottom', color=color)

# Ejes y estética
plt.xscale("log")
plt.yscale("log")
plt.xlabel("Tiempo de cómputo (simulado) [s]")
plt.ylabel("Error L2 en posición")
plt.title("Error L2 vs tiempo computacional")
plt.grid(True)

# Leyenda por método base
plt.legend(handles.values(), handles.keys(), title="Método", bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()



# Gráfica 14: Comparación total de eficiencia (posición vs velocidad)
# 14. Comparación de eficiencia relativa con color, estrella, etiquetas dt y borde para puntos más eficientes
df_err["base"] = df_err["Método"].apply(lambda x: x.split("_")[0])
bases = sorted(df_err["base"].unique())
colores = plt.cm.tab10(np.linspace(0, 1, len(bases)))
color_map = dict(zip(bases, colores))

# Obtener los valores de dt conocidos
dt_dict = df.set_index("Método")["dt"].dropna().to_dict()

# Identificar máximos
max_eff_z = df_err["Eff_pos"].max()
max_eff_v = df_err["Eff_vel"].max()

plt.figure(figsize=(10, 6))
handles = {}

for i, row in df_err.iterrows():
    metodo = row["Método"]
    base = row["base"]
    color = color_map[base]
    eff_z = row["Eff_pos"]
    eff_v = row["Eff_vel"]
    dt = dt_dict.get(metodo, None)

    marker = '*' if dt is None else 'o'
    size = 150 if marker == '*' else 80

    # Dibujar punto principal
    point = plt.scatter(eff_z, eff_v, color=color, marker=marker, s=size, edgecolors='none')

    # Agregar a leyenda
    if base not in handles:
        handles[base] = point

    # Etiqueta con desplazamiento
    label_txt = f"dt={dt:.3f}" if dt is not None else "dt=auto"
    plt.text(eff_z * 1.05, eff_v * 1.1, label_txt, fontsize=8, ha='left', va='bottom', color=color)

    # Marcar los puntos de eficiencia máxima
    if eff_z == max_eff_z or eff_v == max_eff_v:
        plt.scatter(eff_z, eff_v, facecolors='none', edgecolors='black', s=size + 60, linewidths=1.5)

# Ejes y estética
plt.xlabel("Eficiencia relativa en posición")
plt.ylabel("Eficiencia relativa en velocidad")
plt.title("Comparación de eficiencia relativa por método y paso de tiempo")
plt.grid(True)

# Leyenda por método base
plt.legend(handles.values(), handles.keys(), title="Método", bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()


# Gráfica extra: trayectoria en el plano
plt.figure()
for metodo in df["Método"].unique():
    if "_dt=0.5" in metodo:
        sub = df[df["Método"] == metodo]
        plt.plot(sub["x_num"], sub["y_num"], label=metodo.split("_")[0], marker='o', markersize=4, linestyle='-')
plt.plot(sub["x_analitica"], sub["y_analitica"], linestyle='--', color='gray', label='Analítica')
plt.xlabel("x(t) [m]"); plt.ylabel("y(t) [m]"); plt.title("Trayectoria en el plano")
plt.grid(); plt.legend(); plt.tight_layout(); plt.show()

# === EVOLUCIÓN DEL ERROR TOTAL EN POSICIÓN PARA TODOS LOS MÉTODOS ===
# === SUBPLOTS DE EVOLUCIÓN DE ERROR POR MÉTODO BASE ===import matplotlib.pyplot as plt
# Calcular error absoluto total en posición y limpiar duplicados
df["error_pos"] = np.sqrt((df["x_num"] - df["x_analitica"])**2 + (df["y_num"] - df["y_analitica"])**2)
#df["error_pos"] = np.sqrt((df["vx_num"] - df["vx_analitica"])**2 + (df["vy_num"] - df["vy_analitica"])**2)
df = df.drop_duplicates(subset=["Método", "t"])

# Identificar métodos base (excluyendo RK4_auto)
bases = sorted(set(m.split("_")[0] for m in df["Método"].unique() if not (m.startswith("RK4") and "_auto" in m)))

# Colores únicos por dt
dt_colores = {
    0.01: 'tab:blue',
    0.02: 'tab:orange',
    0.05: 'tab:green',
    0.1: 'tab:red',
    0.2: 'tab:purple',
    0.5: 'tab:brown'
}

# Crear figura 2x3 (3 arriba, 3 abajo)
fig, axs = plt.subplots(2, 3, figsize=(18, 10), sharex=True)
axs = axs.flatten()

legend_handles = {}

# Graficar por método base
for i, base in enumerate(bases[:6]):  # Solo los primeros 6 métodos base
    ax = axs[i]
    
    # Obtener todos los métodos de esta base (excepto RK4_auto)
    metodos_base = [m for m in df["Método"].unique() if m.startswith(base) and not (base == "RK4" and "_auto" in m)]
    
    usados = set()
    for metodo in metodos_base:
        sub = df[df["Método"] == metodo].copy().sort_values("t")
        if sub.empty:
            continue
        dt_val = sub["dt"].dropna().iloc[0] if sub["dt"].notna().any() else None
        if dt_val in usados or dt_val not in dt_colores:
            continue
        usados.add(dt_val)
        if len(usados) >= 6:
            break

        color = dt_colores[dt_val]
        label = f"dt={dt_val:.2f}"
        line, = ax.plot(sub["t"], sub["error_pos"], label=label, color=color, marker='o', markersize=3, linewidth=1)

        # Solo un handle por dt
        if label not in legend_handles:
            legend_handles[label] = line

    ax.set_yscale("log")
    ax.set_title(f"Método: {base}")
    ax.set_ylabel("Error absoluto en posición")
    ax.grid(True, which="both", linestyle="--", linewidth=0.5)

# Eliminar subplot extra si hay
for j in range(len(bases), len(axs)):
    fig.delaxes(axs[j])

# Etiquetas comunes
for ax in axs:
    ax.set_xlabel("t [s]")

# Leyenda general abajo
fig.legend(legend_handles.values(), legend_handles.keys(),
           title="Configuración dt", fontsize=10, loc='lower center',
           bbox_to_anchor=(0.5, -0.02), ncol=6)

fig.suptitle("Evolución del error absoluto en posición por método", fontsize=16)
plt.tight_layout(rect=[0, 0.04, 1, 0.95])
plt.show()
