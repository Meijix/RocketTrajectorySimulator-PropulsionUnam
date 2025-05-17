# Gráfica de altura vs tiempo de datos experimentales y simulados
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- Rutas de archivos ---
ruta_experimental = r'C:\Users\Natalia\OneDrive\Archivos\Tesis\GitHubCode\SimuladorVueloNat\3DOF-Rocket-PU\Archivos\DatosVuelo\DatosExperimentalesLimpios.csv'
#ruta_simulada = r'C:\Users\Natalia\OneDrive\Archivos\Tesis\GitHubCode\SimuladorVueloNat\3DOF-Rocket-PU\Simulador\Resultados\OutputFiles\VueloLibre-DOP853-110\datos.csv'
ruta_simulada = r'C:\Users\Natalia\OneDrive\Archivos\Tesis\GitHubCode\SimuladorVueloNat\3DOF-Rocket-PU\Simulador\Resultados\OutputFiles\VueloLibre-DOP853-0\datos.csv'
ruta_openrocket = r'C:\Users\Natalia\OneDrive\Archivos\Tesis\GitHubCode\SimuladorVueloNat\3DOF-Rocket-PU\Archivos\VueloOpenRocket.csv'
ruta_openrocket = r'C:\Users\Natalia\OneDrive\Archivos\Tesis\GitHubCode\SimuladorVueloNat\3DOF-Rocket-PU\Archivos\OpenRocketViento.csv'

# --- Cargar datos ---
pd_experimental = pd.read_csv(ruta_experimental)
pd_simulado = pd.read_csv(ruta_simulada)
#pd_simulado2 = pd.read_csv(ruta_simulada2)
#pd_simulado1 = pd.read_csv(ruta_simulada1)

# --- Función para convertir TIME-FTW ---
def convertir_time_ftw_column(columna_ftw):
    tiempos_segundos = []
    for time_str in columna_ftw.dropna():
        minutos, segundos = map(float, str(time_str).split(':'))
        total_seconds = minutos * 60 + segundos
        tiempos_segundos.append(total_seconds)
    return pd.Series(tiempos_segundos, index=columna_ftw.dropna().index)


def marcar_velocidad_maxima(t, v, nombre, color, desplazamiento_x=2, desplazamiento_y=2):
    """
    Marca el punto de velocidad máxima en una gráfica de velocidad.

    Parámetros:
    - t: array o Serie de tiempos
    - v: array o Serie de velocidades
    - nombre: texto del nombre para la etiqueta
    - color: color del marcador y texto
    - desplazamiento_x: cuánto desplazar la etiqueta horizontalmente
    - desplazamiento_y: cuánto desplazar la etiqueta verticalmente
    """
    idx_max = np.argmax(np.abs(v))  # Puede ser útil si v puede ser negativa (como velocidad vertical de impacto)
    plt.plot(t.iloc[idx_max], v.iloc[idx_max], 'o', color=color, markersize=8)
    plt.text(
        t.iloc[idx_max] + desplazamiento_x,
        v.iloc[idx_max] + desplazamiento_y,
        f'{nombre}\n{v.iloc[idx_max]:.1f} m/s',
        color=color,
        ha='left',
    )

def marcar_velocidad_maxima1(t, v, nombre, color, desplazamiento_x=2, desplazamiento_y=2):
    """
    Marca el punto de velocidad máxima en una gráfica de velocidad.

    Parámetros:
    - t: array o Serie de tiempos
    - v: array o Serie de velocidades
    - nombre: texto del nombre para la etiqueta
    - color: color del marcador y texto
    - desplazamiento_x: cuánto desplazar la etiqueta horizontalmente
    - desplazamiento_y: cuánto desplazar la etiqueta verticalmente
    """
    idx_max = np.argmax(np.abs(v))  # Puede ser útil si v puede ser negativa (como velocidad vertical de impacto)
    plt.plot(t.iloc[idx_max], v.iloc[idx_max], 'o', color=color, markersize=8)
    plt.text(
        t.iloc[idx_max] + desplazamiento_x,
        v.iloc[idx_max] + desplazamiento_y,
        f'{nombre}\n{v.iloc[idx_max]:.1f} m/s',
        color=color,
        ha='right',
    )

# --- Procesar ASYB ---
t_asyb = pd.to_numeric(pd_experimental['TIME-ASYB']) / 1000
t_asyb = t_asyb - t_asyb.min()
t_asyb = t_asyb + 22  # Corrección temporal manual
alt_asyb = pd.to_numeric(pd_experimental['ALTITUD-ASYB'], errors='coerce')

# --- Reconstruir primeros 22 segundos como tiro parabólico ---
# Parámetros del tiro
g = 9.81  # gravedad
t_reconstruido = np.linspace(0, 22, 100)  # 100 puntos de 0 a 22 segundos

# Estimar velocidad inicial para alcanzar el primer dato de alt_asyb
altura_objetivo = alt_asyb.iloc[0]

# Modelo parabólico
#alt_reconstruida = np.linspace(0, altura_objetivo, len(t_reconstruido))
altura_objetivo = alt_asyb.iloc[0]  # Altura donde empiezan tus datos experimentales

# Exponente suavizado (2.2 o 2.5 funciona bien según la forma que muestras)
n = 2.2

# Coeficiente a
a = altura_objetivo / (22**n)

# Modelo de reconstrucción
alt_reconstruida = a * t_reconstruido**n

# --- Procesar FTW ---
t_ftw_raw = pd_experimental['TIME-FTW']
t_ftw = convertir_time_ftw_column(t_ftw_raw)
t_ftw = t_ftw - t_ftw.min()

alt_ftw = pd.to_numeric(pd_experimental['ALTITUD-FTW'], errors='coerce')
alt_ftw = alt_ftw[:len(t_ftw)]


###desplazamiento (horizontal range en el eje x)
#esta en ft 
desp_ftw = pd_experimental['Rango (m)']
desp_ftw = pd.to_numeric(desp_ftw, errors='coerce')
#quitar el valor inicial
desp_ftw = desp_ftw - desp_ftw.iloc[0]
desp_ftw = desp_ftw[:len(t_ftw)]

# --- Procesar simulaciones ---
t_sim = pd_simulado['t'] + 7
alt_sim = pd_simulado['z']
desp_sim= pd_simulado['x']



#############Velocidades####################
horizontalv=pd_experimental['HORZV']
horizontalv=horizontalv[:len(t_ftw)]/3.6 #Convertir a m/s
verticalv=pd_experimental['VERTV']
verticalv=verticalv[:len(t_ftw)]/3.6 #Convertir a m/s

horizontalv_sim = pd_simulado['vx']
verticalv_sim = pd_simulado['vz']

################OPENROCKET
pd_openrocket = pd.read_csv(ruta_openrocket)
t_or = pd_openrocket['Time (s)']+7  # Ajustar el tiempo
alt_or = pd_openrocket['Altitude (m)']
desp_or = pd_openrocket['Lateral distance (m)']
vz_or = pd_openrocket['Vertical velocity (m/s)']
vx_or = pd_openrocket['Lateral velocity (m/s)']  # Esta es la horizontal


# --- Crear figura ---
plt.figure(figsize=(12, 8))

# --- Graficar reconstrucción de tiro parabólico ---
#plt.plot(t_reconstruido, alt_reconstruida, label='Reconstrucción parabólica ASYB (0-22s)', color='purple', linestyle=':')

# --- Graficar experimental ---
#plt.plot(t_asyb, alt_asyb, label='Telemetría ASYB', color='orange', linewidth=2, alpha=0.8)
plt.plot(t_ftw, alt_ftw, label='GPS FTW', color='blue', linewidth=2, alpha=0.8)
# --- Graficar simulaciones ---
plt.plot(t_sim, alt_sim, label='Simulación DOP853', color='red', linestyle='--', linewidth=2, alpha=0.9)
plt.plot(t_or, alt_or, label='Simulación OpenRocket', color='green', linestyle='-.', linewidth=2, alpha=0.9)

# --- Marcar apogeos ---
def marcar_apogeo(t, alt, nombre, color):
    idx_max = np.argmax(alt)
    plt.plot(t.iloc[idx_max], alt.iloc[idx_max], 'o', color=color, markersize=8)
    plt.text(t.iloc[idx_max]+7, alt.iloc[idx_max] + 7, f'{nombre}\n{alt.iloc[idx_max]:.1f} m', ha='center', color=color)

def marcar_apogeo1(t, alt, nombre, color):
    idx_max = np.argmax(alt)
    plt.plot(t.iloc[idx_max], alt.iloc[idx_max], 'o', color=color, markersize=8)
    plt.text(t.iloc[idx_max]-7, alt.iloc[idx_max], f'{nombre}\n{alt.iloc[idx_max]:.1f} m', ha='center', color=color)

#marcar_apogeo(t_asyb, alt_asyb, 'Apogeo ASYB', 'orange')
marcar_apogeo1(t_ftw, alt_ftw, 'Apogeo FTW', 'blue')
marcar_apogeo(t_sim, alt_sim, 'Apogeo Sim DOP853', 'red')
#marcar_apogeo(t_sim1, alt_sim1, 'Apogeo Sim DOP853-100', 'green')
marcar_apogeo(t_or, alt_or, 'Apogeo OpenRocket', 'green')

# --- Configurar gráfica ---
plt.title('Altura vs Tiempo - Experimental vs Simulaciones', fontsize=14)
plt.xlabel('Tiempo [s]', fontsize=10)
plt.ylabel('Altitud [m]', fontsize=10)
plt.legend(fontsize=12)
plt.grid(True)
plt.tight_layout()

# --- Mostrar gráfica ---
plt.show()




plt.figure(figsize=(12, 8))
# --- Graficar experimental ---
plt.plot(t_ftw, horizontalv, label='Vel Hor Exp', color='blue', linewidth=2, alpha=0.8)
plt.plot(t_ftw, verticalv, label='Vel Vert Exp', color='orange', linewidth=2, alpha=0.8)

# --- Graficar simulaciones ---
plt.plot(t_sim, horizontalv_sim, label='Vel Hor Sim DOP853', color='red', linestyle='--', linewidth=2, alpha=0.9)
plt.plot(t_sim, verticalv_sim, label='Vel Vert Sim DOP853', color='green', linestyle='--', linewidth=2, alpha=0.9)


plt.plot(t_or, vx_or, label='Vel Hor OR', color='purple', linestyle=':', linewidth=2)
plt.plot(t_or, vz_or, label='Vel Vert OR', color='deeppink', linestyle=':', linewidth=2)
marcar_velocidad_maxima(t_ftw, verticalv, 'Máx', 'orange')
marcar_velocidad_maxima(t_sim, verticalv_sim, 'Máx', 'green')
marcar_velocidad_maxima1(t_or, vz_or, 'Máx', 'deeppink')
marcar_velocidad_maxima1(t_ftw, horizontalv, 'Máx', 'blue')
marcar_velocidad_maxima1(t_sim, horizontalv_sim, 'Máx', 'red')
marcar_velocidad_maxima1(t_or, vx_or, 'Máx', 'purple')

# --- Configurar gráfica ---
plt.title('Velocidad vs Tiempo - Experimental vs Simulaciones', fontsize=14)
plt.xlabel('Tiempo [s]', fontsize=10)
plt.ylabel('Velocidad [m/s]', fontsize=10)
plt.legend(fontsize=12)
plt.grid(True)
plt.tight_layout()
plt.show()


###graficar el desplazamiento horizontal
plt.figure(figsize=(10,6))
plt.plot(t_ftw, desp_ftw, label='FTW', color='blue', linewidth=2, alpha=0.8)
plt.plot(t_sim, desp_sim, label='Sim DOP853', color='red', linestyle='--', linewidth=2, alpha=0.9)
plt.plot(t_or, desp_or, label='OpenRocket', color='green', linestyle='-.', linewidth=2, alpha=0.9)
#marker en los maximos
marcar_apogeo1(t_ftw, desp_ftw, 'Máx FTW', 'blue')
marcar_apogeo(t_sim, desp_sim, 'Máx Sim', 'red')
marcar_apogeo(t_or, desp_or, 'Máx OR', 'green')

plt.title('Desplazamiento Horizontal')
plt.xlabel('Tiempo (s)')
plt.ylabel('Desplazamiento (m)')
plt.legend()
plt.grid()
plt.show()


###Errores relativos de altitud y velocidad con OPENROCKET
erro_alt_or = (alt_or.max() - alt_ftw.max()) / alt_ftw.max() * 100
erro_desp_or = (desp_or.max() - desp_ftw.max()) / desp_ftw.max() * 100
erro_t_apogeo_or = (t_or[alt_or.idxmax()] - t_ftw[alt_ftw.idxmax()]) / t_ftw[alt_ftw.idxmax()] * 100
erro_t_impacto_or = (t_or.iloc[-1] - t_ftw.iloc[-1]) / t_ftw.iloc[-1] * 100
erro_vz_or = (vz_or.max() - verticalv.max()) / verticalv.max() * 100
error_vx_or = (vx_or.max() - horizontalv.max()) / horizontalv.max() * 100


#Errores relativos de altitud y velocidad con SIMULADOR
erro_altitud = (alt_sim.max() - alt_ftw.max()) / alt_ftw.max() * 100
erro_desp = (desp_sim.max() - desp_ftw.max()) / desp_ftw.max() * 100
erro_t_apogeo = (t_sim[alt_sim.idxmax()] - t_ftw[alt_ftw.idxmax()]) / t_ftw[alt_ftw.idxmax()] * 100
erro_t_impacto = (t_sim.iloc[-1] - t_ftw.iloc[-1]) / t_ftw.iloc[-1] * 100
erro_velmaxvert = (verticalv_sim.max() - verticalv.max()) / verticalv.max() * 100
erro_velmaxhor = (horizontalv_sim.max() - horizontalv.max()) / horizontalv.max() * 100


# --- Altitudes máximas ---
print("Altitud Máxima Experimental:", f"{alt_ftw.max():.2f}", "m")
print("Altitud Máxima Simulada:", f"{alt_sim.max():.2f}", "m")
print("Altitud Máxima OpenRocket:", f"{alt_or.max():.2f}", "m")

# --- Desplazamientos máximos ---
print("\nDesplazamiento Experimental:", f"{desp_ftw.max():.2f}", "m")
print("Desplazamiento Sim DOP853:", f"{desp_sim.max():.2f}", "m")
print("Desplazamiento OpenRocket:", f"{desp_or.max():.2f}", "m")

# --- Tiempos de apogeo ---
print("\nTiempo de Apogeo Experimental:", f"{t_ftw[alt_ftw.idxmax()]:.2f}", "s")
print("Tiempo de Apogeo Simulado:", f"{t_sim[alt_sim.idxmax()]:.2f}", "s")
print("Tiempo de Apogeo OpenRocket:", f"{t_or[alt_or.idxmax()]:.2f}", "s")

# --- Tiempos de impacto ---
print("\nTiempo de Impacto Experimental:", f"{t_ftw.iloc[-1]:.2f}", "s")
print("Tiempo de Impacto Simulado:", f"{t_sim.iloc[-1]:.2f}", "s")
print("Tiempo de Impacto OpenRocket:", f"{t_or.iloc[-1]:.2f}", "s")

# --- Velocidades máximas ---
print("\nVelocidad Vertical Máxima Experimental:", f"{verticalv.max():.2f}", "m/s")
print("Velocidad Vertical Máxima Simulada:", f"{verticalv_sim.max():.2f}", "m/s")
print("Velocidad Vertical Máxima OpenRocket:", f"{vz_or.max():.2f}", "m/s")

print("\nVelocidad Horizontal Máxima Experimental:", f"{horizontalv.max():.2f}", "m/s")
print("Velocidad Horizontal Máxima Simulada:", f"{horizontalv_sim.max():.2f}", "m/s")
print("Velocidad Horizontal Máxima OpenRocket:", f"{vx_or.max():.2f}", "m/s")

# --- Velocidad vertical de impacto ---
print("\nVelocidad Vertical de Impacto Experimental:", f"{verticalv.iloc[-1]:.2f}", "m/s")
print("Velocidad Vertical de Impacto Simulada:", f"{verticalv_sim.iloc[-1]:.2f}", "m/s")
print("Velocidad Vertical de Impacto OpenRocket:", f"{vz_or.iloc[-1]:.2f}", "m/s")

# --- Errores relativos OPENROCKET ---
print("\nErrores relativos OpenRocket:")
print("Altitud:", f"{erro_alt_or:.2f}", "%")
print("Desplazamiento:", f"{erro_desp_or:.2f}", "%")
print("Tiempo de Apogeo:", f"{erro_t_apogeo_or:.2f}", "%")
print("Tiempo de Impacto:", f"{erro_t_impacto_or:.2f}", "%")
print("Velocidad Vertical Máx:", f"{erro_vz_or:.2f}", "%")
print("Velocidad Horizontal Máx:", f"{error_vx_or:.2f}", "%")

# --- Errores relativos SIMULADOR ---
print("\nErrores relativos Simulador:")
print("Altitud:", f"{erro_altitud:.2f}", "%")
print("Desplazamiento:", f"{erro_desp:.2f}", "%")
print("Tiempo de Apogeo:", f"{erro_t_apogeo:.2f}", "%")
print("Tiempo de Impacto:", f"{erro_t_impacto:.2f}", "%")
print("Velocidad Vertical Máx:", f"{erro_velmaxvert:.2f}", "%")
print("Velocidad Horizontal Máx:", f"{erro_velmaxhor:.2f}", "%")
