# Cargas estructurales del Xitle II durante el ascenso
#
# Simula el vuelo libre con las condiciones de condiciones_init.py y calcula la fuerza axial,
# el cortante y el momento flector a lo largo del cohete (ver Paquetes/PaqueteFisica/cargas.py).
# Guarda la tabla y la figura en Simulador/Resultados/OutputFiles/CargasEstructurales/.
# Ejecutar desde la raíz:
#     python -m Simulador.Resultados.cargas_estructurales
import contextlib
import io
import os
import sys

import matplotlib.pyplot as plt

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(RAIZ)

import numpy as np
import pandas as pd

from Paquetes.PaqueteFisica import cargas, resistencia
from Paquetes.PaqueteFisica.vuelo import Vuelo
from Simulador.src import condiciones_init as c_init
from Simulador.src.XitleFile import Xitle
from Simulador.Visualizacion.graficas_cargas import graficar_envolvente, tabla_envolvente, texto_maximos

RAFAGA = 9.0   # [m/s] ráfaga lateral de diseño; 0 para no calcularla
CARPETA = os.path.join(RAIZ, 'Simulador', 'Resultados', 'OutputFiles', 'CargasEstructurales')

Xitle.quitar_paracaidas()
vuelo = Vuelo(Xitle, c_init.atmosfera_actual, c_init.viento_actual)
print("Simulando el vuelo...")
with contextlib.redirect_stdout(io.StringIO()):
    salida = vuelo.simular_vuelo(c_init.estado.copy(), c_init.t_max, c_init.dt, c_init.dt_out, c_init.integrador_actual)
tiempos, sim = salida[0], salida[1]

print("Calculando las cargas...")
env = cargas.envolvente(vuelo, tiempos, sim, rafaga=RAFAGA)

print(f"\nCargas máximas durante el ascenso (hasta t = {env['t_fin']:.1f} s)")
for linea in texto_maximos(env):
    print("  " + linea)
print("\nInstantes más exigentes (viento simulado):")
for nombre, caso in env["casos"].items():
    print(f"  {nombre}: t = {caso['t']:.2f} s, presión dinámica {caso['presion_dinamica']:.0f} Pa, Mach {caso['mach']:.2f}, "
          f"ángulo de ataque {caso['alpha']:.2f}°, compresión máx {caso['compresion'].max():.0f} N, "
          f"momento máx {abs(caso['momento']).max():.1f} N m")

# Comprobación de resistencia: pandeo del fuselaje y flameo de las aletas
# (materiales, espesores y factor de seguridad en Archivos/estructura_xitle.json)
tiempos, sim = np.array(tiempos), np.array(sim)
ascenso = tiempos <= vuelo.tiempo_apogeo
v_aire = np.linalg.norm(sim[:, 3:6] - np.array(salida[7]), axis=1)
comprobacion = resistencia.verificar(vuelo, env, sim[ascenso, 2], v_aire[ascenso])
print("\nComprobación de resistencia")
for linea in resistencia.texto_resumen(comprobacion):
    print("  " + linea)
tabla_fuselaje = pd.DataFrame([{
    "Tramo": f["tramo"], "Material": f["material"], "Espesor [mm]": f["espesor"] * 1e3, "R/t": f["R_t"],
    "Compresión [N]": f["compresion"], "Momento [N m]": f["momento"],
    "Esfuerzo axial [MPa]": f["sigma_axial"] / 1e6, "Esfuerzo de flexión [MPa]": f["sigma_flexion"] / 1e6,
    "Pandeo clásico [MPa]": f["sigma_pandeo_clasico"] / 1e6, "Factor axial": f["gamma_axial"], "Factor flexión": f["gamma_flexion"],
    "Carga axial de pandeo [kN]": f["carga_pandeo_axial"] / 1e3,
    "Margen de pandeo": f["margen_pandeo"], "Margen de resistencia": f["margen_resistencia"],
} for f in comprobacion["fuselaje"]])
print(tabla_fuselaje.to_string(index=False, float_format=lambda v: f"{v:.3g}"))

os.makedirs(CARPETA, exist_ok=True)
tabla_fuselaje.to_csv(os.path.join(CARPETA, 'pandeo_fuselaje.csv'), index=False)
pd.DataFrame([comprobacion["flameo"]]).to_csv(os.path.join(CARPETA, 'flameo_aletas.csv'), index=False)
ruta_tabla = os.path.join(CARPETA, 'envolvente_cargas.csv')
tabla_envolvente(env).to_csv(ruta_tabla, index=False)
fig = plt.figure(figsize=(9, 9))
graficar_envolvente(fig, env)
ruta_figura = os.path.join(CARPETA, 'envolvente_cargas.png')
fig.savefig(ruta_figura, dpi=150)
print(f"\nTabla guardada en: {ruta_tabla}")
print(f"Figura guardada en: {ruta_figura}")
plt.show()
