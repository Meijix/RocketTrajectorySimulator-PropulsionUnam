# Gráfica de altura vs tiempo de datos experimentales y simulados
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- Rutas de archivos ---
ruta_experimental = r'C:\Users\Natalia\OneDrive\Archivos\Tesis\GitHubCode\SimuladorVueloNat\3DOF-Rocket-PU\Archivos\DatosVuelo\DatosExperimentalesLimpios.csv'
ruta_simulada = r'C:\Users\Natalia\OneDrive\Archivos\Tesis\GitHubCode\SimuladorVueloNat\3DOF-Rocket-PU\Simulador\Resultados\OutputFiles\VueloLibre-DOP853-110\datos.csv'
#ruta_simulada1 = r'C:\Users\Natalia\OneDrive\Archivos\Tesis\GitHubCode\SimuladorVueloNat\3DOF-Rocket-PU\Simulador\Resultados\OutputFiles\VueloLibre-DOP853-100\datos.csv'

# --- Cargar datos ---
pd_experimental = pd.read_csv(ruta_experimental)
pd_simulado = pd.read_csv(ruta_simulada)
#pd_simulado1 = pd.read_csv(ruta_simulada1)

# --- Función para convertir TIME-FTW ---
def convertir_time_ftw_column(columna_ftw):
    tiempos_segundos = []
    for time_str in columna_ftw.dropna():
        minutos, segundos = map(float, str(time_str).split(':'))
        total_seconds = minutos * 60 + segundos
        tiempos_segundos.append(total_seconds)
    return pd.Series(tiempos_segundos, index=columna_ftw.dropna().index)

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

# --- Procesar simulaciones ---
t_sim = pd_simulado['t'] + 7
alt_sim = pd_simulado['z']

#t_sim1 = pd_simulado1['t'] + 7
#alt_sim1 = pd_simulado1['z']

#Imprimir altitud maxima, tiempo de apogeo y tiempo de impacto
print("Altitud Maxima Experimental:",alt_ftw.max(),"m")
print("Altitud Maxima Simulada:",alt_sim.max(),"m")
print("Tiempo de Apogeo Experimental:",t_ftw[alt_ftw.idxmax()],"s")
print("Tiempo de Apogeo Simulado:",t_sim[alt_sim.idxmax()],"s")
print("Tiempo de Impacto Experimental:",t_ftw.iloc[-1],"s")
print("Tiempo de Impacto Simulado:",t_sim.iloc[-1],"s")

#############Velocidades####################
horizontalv=pd_experimental['HORZV']
horizontalv=horizontalv[:len(t_ftw)]/3.6 #Convertir a m/s
verticalv=pd_experimental['VERTV']
verticalv=verticalv[:len(t_ftw)]/3.6 #Convertir a m/s

horizontalv_sim = pd_simulado['vx']
verticalv_sim = pd_simulado['vz']

##Imprimir velocidad horizontal y vertical maxima
print("Velocidad Horizontal Maxima Experimental:",horizontalv.max(),"m/s")
print("Velocidad Vertical Maxima Experimental:",verticalv.max(),"m/s")
print("Velocidad Horizontal Maxima Simulada:",horizontalv_sim.max(),"m/s")
print("Velocidad Vertical Maxima Simulada:",verticalv_sim.max(),"m/s")

############Aceleraciones####################
ax=pd_experimental['ax']
ay=pd_experimental['ay']
az=pd_experimental['az']



# --- Crear figura ---
plt.figure(figsize=(12, 8))

# --- Graficar reconstrucción de tiro parabólico ---
#plt.plot(t_reconstruido, alt_reconstruida, label='Reconstrucción parabólica ASYB (0-22s)', color='purple', linestyle=':')

# --- Graficar experimental ---
#plt.plot(t_asyb, alt_asyb, label='Telemetría ASYB', color='orange', linewidth=2, alpha=0.8)
plt.plot(t_ftw, alt_ftw, label='GPS FTW', color='blue', linewidth=2, alpha=0.8)

# --- Graficar simulaciones ---
plt.plot(t_sim, alt_sim, label='Simulación DOP853-110', color='red', linestyle='--', linewidth=2, alpha=0.9)
#plt.plot(t_sim1, alt_sim1, label='Simulación DOP853-100', color='green', linestyle='--', linewidth=2, alpha=0.9)

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
marcar_apogeo(t_sim, alt_sim, 'Apogeo Sim DOP853-110', 'red')
#marcar_apogeo(t_sim1, alt_sim1, 'Apogeo Sim DOP853-100', 'green')

# --- Configurar gráfica ---
plt.title('Altitud vs Tiempo - Experimental vs Simulación', fontsize=14)
plt.xlabel('Tiempo [s]', fontsize=10)
plt.ylabel('Altitud [m]', fontsize=10)
plt.legend(fontsize=12)
plt.grid(True)
plt.tight_layout()

# --- Mostrar gráfica ---
plt.show()




plt.figure(figsize=(12, 8))
# --- Graficar experimental ---
plt.plot(t_ftw, horizontalv, label='Velocidad Horizontal', color='blue', linewidth=2, alpha=0.8)
plt.plot(t_ftw, verticalv, label='Velocidad Vertical', color='orange', linewidth=2, alpha=0.8)

# --- Graficar simulaciones ---
plt.plot(t_sim, horizontalv_sim, label='Velocidad Horizontal Sim DOP853-110', color='red', linestyle='--', linewidth=2, alpha=0.9)
plt.plot(t_sim, verticalv_sim, label='Velocidad Vertical Sim DOP853-110', color='green', linestyle='--', linewidth=2, alpha=0.9)
# --- Configurar gráfica ---
plt.title('Velocidad vs Tiempo - Experimental vs Simulación', fontsize=14)
plt.xlabel('Tiempo [s]', fontsize=10)
plt.ylabel('Velocidad [m/s]', fontsize=10)
plt.legend(fontsize=12)
plt.grid(True)
plt.tight_layout()
plt.show()

###Errores relativos de altitud y velocidad

erro_altitud = (alt_sim.max() - alt_ftw.max()) / alt_ftw.max() * 100
erro_velmaxvert = (verticalv_sim.max() - verticalv.max()) / verticalv.max() * 100
erro_velocidad = (np.sqrt(horizontalv_sim**2 + verticalv_sim**2) - np.sqrt(horizontalv**2 + verticalv[:len(horizontalv_sim)]**2)) / np.sqrt(horizontalv**2 + verticalv[:len(horizontalv_sim)]**2) * 100

#Errores de tiempo de apogeo y tiempo de impacto
erro_t_apogeo = (t_sim[alt_sim.idxmax()] - t_ftw[alt_ftw.idxmax()]) / t_ftw[alt_ftw.idxmax()] * 100
erro_t_impacto = (t_sim.iloc[-1] - t_ftw.iloc[-1]) / t_ftw.iloc[-1] * 100

print("Error relativo de altitud:", erro_altitud, "%")
print("Error relativo de velocidad vertical maxima:", erro_velmaxvert, "%")
print("Error relativo de velocidad:", erro_velocidad.max(), "%")
print("Error relativo de tiempo de apogeo:", erro_t_apogeo, "%")
print("Error relativo de tiempo de impacto:", erro_t_impacto, "%")