# Gráfica de altura vs tiempo de datos experimentales y simulados
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- Rutas de archivos ---
ruta_simulada = r'C:\Users\Natalia\OneDrive\Archivos\Tesis\GitHubCode\SimuladorVueloNat\3DOF-Rocket-PU\Simulador\Resultados\OutputFiles\VueloLibre-DOP853-110\datos.csv'
ruta_simulada2 = r'C:\Users\Natalia\OneDrive\Archivos\Tesis\GitHubCode\SimuladorVueloNat\3DOF-Rocket-PU\Simulador\Resultados\OutputFiles\VueloLibre-DOP853-0\datos.csv'


# --- Cargar datos ---
pd_simulado = pd.read_csv(ruta_simulada)
pd_simulado2 = pd.read_csv(ruta_simulada2)
#pd_simulado1 = pd.read_csv(ruta_simulada1)

# --- Procesar simulaciones ---
t_sim = pd_simulado['t'] + 7
alt_sim = pd_simulado['z']
des_sim = pd_simulado['x']

t_sim2 = pd_simulado2['t'] + 7
alt_sim2 = pd_simulado2['z']
des_sim2 = pd_simulado2['x']

horizontalv_sim = pd_simulado['vx']
verticalv_sim = pd_simulado['vz']
horizontalv_sim2 = pd_simulado2['vx']
verticalv_sim2 = pd_simulado2['vz']


# --- Crear figura ---
plt.figure(figsize=(12, 8))


plt.plot(t_sim, alt_sim, label='Simulación DOP853', color='red', linestyle='--', linewidth=2, alpha=0.9)
plt.plot(t_sim2, alt_sim2, label='Simulación con viento', color='orange', linestyle='--', linewidth=2, alpha=0.9)


plt.plot(t_sim, des_sim, label='Desplazamiento Sim DOP853', color='blue', linestyle='--', linewidth=2, alpha=0.9)
plt.plot(t_sim2, des_sim2, label='Desplazamiento Sim DOP853 con viento', color='purple', linestyle='--', linewidth=2, alpha=0.9)

# --- Marcar apogeos ---
def marcar_apogeo(t, alt, nombre, color):
    idx_max = np.argmax(alt)
    plt.plot(t.iloc[idx_max], alt.iloc[idx_max], 'o', color=color, markersize=8)
    plt.text(t.iloc[idx_max]+7, alt.iloc[idx_max] + 7, f'{nombre}\n{alt.iloc[idx_max]:.1f} m', ha='center', color=color)

def marcar_apogeo1(t, alt, nombre, color):
    idx_max = np.argmax(alt)
    plt.plot(t.iloc[idx_max], alt.iloc[idx_max], 'o', color=color, markersize=8)
    plt.text(t.iloc[idx_max]-7, alt.iloc[idx_max], f'{nombre}\n{alt.iloc[idx_max]:.1f} m', ha='center', color=color)


marcar_apogeo(t_sim, alt_sim, 'Apogeo', 'red')
marcar_apogeo(t_sim2, alt_sim2, 'Apogeo', 'orange')
marcar_apogeo1(t_sim, des_sim, 'Apogeo', 'blue')
marcar_apogeo1(t_sim2, des_sim2, 'Apogeo', 'purple')


# --- Configurar gráfica ---
plt.title('Altitud vs Tiempo - Experimental vs Simulaciones', fontsize=14)
plt.xlabel('Tiempo [s]', fontsize=10)
plt.ylabel('Altitud [m]', fontsize=10)
plt.legend(fontsize=12)
plt.grid(True)
plt.tight_layout()

# --- Mostrar gráfica ---
plt.show()



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


plt.figure(figsize=(12, 8))
# --- Graficar simulaciones ---
plt.plot(t_sim, horizontalv_sim, label='Vel Hor Sim DOP853', color='red', linestyle='--', linewidth=2, alpha=0.9)
plt.plot(t_sim, verticalv_sim, label='Vel Vert Sim DOP853', color='green', linestyle='--', linewidth=2, alpha=0.9)

plt.plot(t_sim2, horizontalv_sim2, label='Vel Hor Sim DOP853 con viento', color='orange', linestyle='--', linewidth=2, alpha=0.9)
plt.plot(t_sim2, verticalv_sim2, label='Vel Vert Sim DOP853 con viento', color='purple', linestyle='--', linewidth=2, alpha=0.9)


marcar_velocidad_maxima(t_sim, verticalv_sim, 'Máx', 'green')
marcar_velocidad_maxima(t_sim, horizontalv_sim, 'Máx', 'red')
marcar_velocidad_maxima(t_sim2, verticalv_sim2, 'Máx', 'purple')
marcar_velocidad_maxima(t_sim2, horizontalv_sim2, 'Máx', 'orange')


# --- Configurar gráfica ---
plt.title('Velocidad vs Tiempo - Experimental vs Simulación', fontsize=14)
plt.xlabel('Tiempo [s]', fontsize=10)
plt.ylabel('Velocidad [m/s]', fontsize=10)
plt.legend(fontsize=12)
plt.grid(True)
plt.tight_layout()
plt.show()
