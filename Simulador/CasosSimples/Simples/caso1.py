#Caso 1
#Movimiento vertical con gravedad y masa cte
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
import os
import sys


# Agregar la ruta del directorio que contiene los paquetes al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from Paquetes.PaqueteEDOs.integradores import Euler, RungeKutta4

# Constantes y configuración
g = 9.81
z0, v0 = 0, 50
t_max = 20
dt_vals = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5]
metodos_adaptativos = ['RK45', 'BDF', 'LSODA', 'DOP853']
metodos_fijos = [(Euler, "Euler"), (RungeKutta4, "RK4")]

# Funciones base
def f_gravedad(t, y): return np.array([y[1], -g])
def sol_analitica(t): return np.array([z0 + v0*t - 0.5*g*t**2, v0 - g*t])

def evento_impacto(t, y):
    """
    Evento que detecta el impacto del objeto con el suelo.
    Se activa cuando la posición z(t) cruza 0 descendiendo.
    """
    return y[0]  # z(t)
evento_impacto.terminal = True  # Detiene la integración
evento_impacto.direction = -1   # Solo detecta cruces descendentes (de arriba hacia abajo)

# Almacenar resultados para análisis
resultados = []

# 1. Adaptativos automáticos (con registro de evolución de dt)
dt_evolucion = []  # Lista para almacenar la evolución del paso de tiempo

for metodo in metodos_adaptativos:
    sol = solve_ivp(f_gravedad, [0, t_max], [z0, v0], method=metodo, events=evento_impacto)
    
    # Guardar resultados principales
    for t, z, v in zip(sol.t, sol.y[0], sol.y[1]):
        z_a, v_a = sol_analitica(t)
        resultados.append([metodo + "_auto", np.nan, t, z, v, z_a, v_a])
    
    # Calcular y guardar pasos de tiempo locales
    dt_locales = np.diff(sol.t)
    t_locales = sol.t[:-1]
    for ti, dti in zip(t_locales, dt_locales):
        dt_evolucion.append([metodo, ti, dti])

# Convertir evolución de pasos a DataFrame
df_dtevo = pd.DataFrame(dt_evolucion, columns=["Método", "t", "dt"])


# Gráfica: Evolución temporal del paso de tiempo para métodos automáticos
plt.figure(figsize=(10, 6))
for metodo in df_dtevo["Método"].unique():
    sub = df_dtevo[df_dtevo["Método"] == metodo]
    plt.plot(sub["t"], sub["dt"], label=metodo, marker='o', markersize=4, linestyle='-')
plt.axhline(y=0.5, color='gray', linestyle='--', linewidth=1, label="dt=0.5 (fijo)")
plt.axhline(y=0.2, color='gray', linestyle='--', linewidth=1, label="dt=0.2 (fijo)")
plt.axhline(y=0.1, color='gray', linestyle='--', linewidth=1, label="dt=0.1 (fijo)")   

plt.xlabel("Tiempo [s]")
plt.ylabel("Paso de tiempo local (dt) [s]")
plt.title("Evolución temporal del paso de tiempo en métodos automáticos")
plt.grid(True)
plt.legend(title="Método adaptativo")
plt.tight_layout()
plt.show()


import seaborn as sns

# Cargar el DataFrame df_dtevo simulado (puede sustituirse con lectura de CSV si fuera externo)
# Simulación para prueba - este bloque se reemplaza al ejecutar en el entorno real con df_dtevo ya definido
# Aquí simulamos el contenido de df_dtevo para continuar con la visualización
# Reemplazar esta parte por: df_dtevo = pd.read_csv("archivo.csv") si se necesita cargar externamente

# Aquí va el cálculo estadístico para dt por método
def resumen_dt_por_metodo(df):
    resumen = df.groupby("Método").agg(
        #dt_inicial=("dt", lambda x: x.iloc[0]),
        dt_final=("dt", lambda x: x.iloc[-1]),
        #dt_min=("dt", "min"),
        dt_max=("dt", "max"),
        dt_promedio=("dt", "mean")
    ).reset_index()
    return resumen

# Simulación de df_dtevo si no está presente
# Este bloque debe omitirse en tu entorno real si ya tienes df_dtevo generado
# df_dtevo = pd.DataFrame({
#     "Método": ["RK45"]*5 + ["BDF"]*5,
#     "t": [0, 0.2, 0.4, 0.6, 0.8]*2,
#     "dt": [0.2, 0.2, 0.2, 0.2, 0.2, 0.1, 0.05, 0.03, 0.02, 0.01]
# })

# Asumimos que df_dtevo ya está disponible en el entorno (generado desde el script original)
# Calculamos el resumen
df_resumen_dt = resumen_dt_por_metodo(df_dtevo)

# Gráfica de resumen por método
plt.figure(figsize=(12, 6))
df_melt = df_resumen_dt.melt(id_vars="Método", var_name="Estadística", value_name="dt")

ax= sns.barplot(data=df_melt, x="Método", y="dt", hue="Estadística")

# Agregar etiquetas numéricas en cada barra
for container in ax.containers:
    ax.bar_label(container, fmt="%.4f", padding=3)

plt.title("Estadísticas de paso de tiempo por método adaptativo automático")
plt.ylabel("Paso de tiempo (dt)")
plt.xlabel("Método")
plt.grid(True)
plt.tight_layout()
plt.show()
####################################################
######################################################

# 2. Adaptativos con max_step
for metodo in metodos_adaptativos:
    for dt in dt_vals:
        sol = solve_ivp(f_gravedad, [0, t_max], [z0, v0], method=metodo, max_step=dt, events=evento_impacto)
        for t, z, v in zip(sol.t, sol.y[0], sol.y[1]):
            z_a, v_a = sol_analitica(t)
            resultados.append([f"{metodo}_dt={dt}", dt, t, z, v, z_a, v_a])

# 3. Euler y RK4
for clase, nombre in metodos_fijos:
    for dt in dt_vals:
        integ = clase(f_gravedad)
        estado = np.array([z0, v0])
        t = 0
        while t < t_max:
            nuevo_estado, _ = integ.step(t, estado, dt)
            t += dt
            if nuevo_estado[0] < 0: break
            estado = nuevo_estado
            z, v = estado
            z_a, v_a = sol_analitica(t)
            resultados.append([f"{nombre}_dt={dt}", dt, t, z, v, z_a, v_a])

# Convertir a estructura numpy
df = pd.DataFrame(resultados, columns=["Método", "dt", "t", "z_num", "v_num", "z_analítica", "v_analítica"])

# ================== GRÁFICAS =====================
# Coordenadas del apogeo analítico
t_ap = v0 / g
z_ap = v0**2 / (2 * g)


apogeo_data = []
for metodo in df["Método"].unique():
    sub = df[df["Método"] == metodo]
    if not sub.empty and sub["dt"].notna().any():
        z_max = sub["z_num"].max()
        t_ap = sub[sub["z_num"] == z_max]["t"].iloc[0]
        apogeo_data.append([metodo, sub["dt"].iloc[0], z_max, t_ap])

df_apogeo = pd.DataFrame(apogeo_data, columns=["Método", "dt", "z_apogeo", "t_apogeo"])
# 1. Trayectoria para dt=0.5 con marcadores y apogeo analítico
plt.figure()
for metodo in df["Método"].unique():
    if "_dt=0.5" in metodo:
        sub = df[df["Método"] == metodo]
        plt.plot(sub["t"], sub["z_num"], label=metodo.split("_")[0], marker='o', markersize=4, linestyle='-')

plt.plot(sub["t"], sub["z_analítica"], label="Analítica", color="gray", linewidth=1, linestyle='--')
plt.plot(t_ap, z_ap, marker='*', color='red', markersize=14, label="Apogeo analítico (punto)")
plt.axhline(v0**2 / (2 * g), color='gray', linestyle=':', linewidth=2, label="Apogeo analítico")
plt.title("Trayectoria para dt = 0.5")
plt.xlabel("t [s]"); plt.ylabel("z(t) [m]")
plt.legend(); plt.grid(); plt.tight_layout()
plt.show()


plt.figure()
for metodo in df["Método"].unique():
    if "_dt=0.5" in metodo:
        sub = df[df["Método"] == metodo]
        plt.plot(sub["t"], sub["v_num"], label=metodo.split("_")[0], marker='x', markersize=4, linestyle='-')

plt.plot(sub["t"], sub["v_analítica"], label="Analítica", color="gray", linewidth=1, linestyle='--')
plt.axhline(0, color='gray', linestyle=':', linewidth=1)
plt.title("Velocidad para dt = 0.5")
plt.xlabel("t [s]")
plt.ylabel("v(t) [m/s]")
plt.legend()
plt.grid()
plt.tight_layout()
plt.show()


# Preparar errores por método
errores = []
for metodo in df["Método"].unique():
    sub = df[df["Método"] == metodo]
    pasos = len(sub)
    e_z = np.sqrt(np.mean((sub["z_num"] - sub["z_analítica"])**2))
    e_v = np.sqrt(np.mean((sub["v_num"] - sub["v_analítica"])**2))
    errores.append([metodo, pasos, e_z, e_v, 1/(e_z*pasos), 1/(e_v*pasos)])
df_err = pd.DataFrame(errores, columns=["Método", "Pasos", "L2_z", "L2_v", "Eff_z", "Eff_v"])

# 3. Error L2 en posición vs dt (líneas por método con marcadores; cruz para métodos auto)
plt.figure()
base_metodos = {}
for metodo in df_err["Método"]:
    base = metodo.split("_")[0]
    base_metodos.setdefault(base, []).append(metodo)

colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown', 'teal', 'magenta']
color_idx = 0

for base, metodos in base_metodos.items():
    dts = []
    errores = []
    for metodo in metodos:
        fila = df_err[df_err["Método"] == metodo]
        if fila.empty: continue
        dt = df[df["Método"] == metodo]["dt"].dropna().values[0] if "_dt=" in metodo else 0.55
        err = fila["L2_z"].values[0]
        if "_auto" in metodo:
            color = colors[color_idx % len(colors)]
            plt.scatter(dt, err, marker='x', s=100, color=color, label=base + " (auto)")
            color_idx += 1
        else:
            dts.append(dt)
            errores.append(err)
    if dts:
        plt.plot(dts, errores, label=base, marker='o', linestyle='-')

plt.xscale("log"); plt.yscale("log")
plt.xlabel("dt"); plt.ylabel("Error L2 posición")
plt.title("Convergencia: Error L2 en posición vs dt")
plt.grid(True); 
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
        error = fila["L2_z"].values[0]
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

plt.axhline(v0**2 / (2 * g), color='black', linestyle='--', label="z apogeo analítico")
plt.xlabel("Paso de tiempo (dt)")
plt.ylabel("Altura de apogeo [m]")
plt.ylim(127.2, 127.45)
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

plt.axhline(v0 / g, color='black', linestyle='--', label="t apogeo analítico")
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
    e_l2 = np.sqrt(np.mean((sub["z_num"] - sub["z_analítica"])**2))
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
    plt.text(tiempo*1.007, error*1.006, label_txt, fontsize=8, ha='left', va='bottom', color=color)

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
max_eff_z = df_err["Eff_z"].max()
max_eff_v = df_err["Eff_v"].max()

plt.figure(figsize=(10, 6))
handles = {}

for i, row in df_err.iterrows():
    metodo = row["Método"]
    base = row["base"]
    color = color_map[base]
    eff_z = row["Eff_z"]
    eff_v = row["Eff_v"]
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
    plt.text(eff_z * 1.05, eff_v * 1.05, label_txt, fontsize=8, ha='left', va='bottom', color=color)

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
