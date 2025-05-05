import matplotlib.pyplot as plt
import pandas as pd

# Load the three uploaded files
file1_path = r"C:\Users\Natalia\OneDrive\Tesis\GithubCode\3DOF-Rocket-PU\Archivos\DatosVuelo\ASYB.csv"
file2_path = r"C:\Users\Natalia\OneDrive\Tesis\GithubCode\3DOF-Rocket-PU\Archivos\DatosVuelo\FTW.csv"
file3_path = r"C:\Users\Natalia\OneDrive\Archivos\Tesis\GithubCode\SimuladorVueloNat\3DOF-Rocket-PU\Simulador\Resultados\OutputFiles\VueloLibre-DOP853-100\datos.csv"
# Load CSV files
print("Ruta1:", file1_path)
print("Ruta2:", file2_path)
print("Ruta3:", file3_path)
print("Cargando archivos CSV...")

df_telemetry = pd.read_csv(file1_path)
df_gps = pd.read_csv(file2_path)
df_vuelo = pd.read_csv(file3_path)

# Display basic info to understand the structure of the data
df_telemetry_info = df_telemetry.info()
df_telemetry_head = df_telemetry.head()

df_gps_info = df_gps.info()
df_gps_head = df_gps.head()
print("Telemetry Data Info:")
print(df_telemetry_info)
print(df_telemetry_head)

print("\nGPS Data Info:")
print(df_gps_info)
print(df_gps_head)


# Convert time to seconds (assuming it's in milliseconds in df_telemetry)
df_telemetry['time_s'] = (df_telemetry['time'] - df_telemetry['time'].min()) / 1000


# Plot altitude vs time
plt.figure(figsize=(10, 5))
plt.plot(df_telemetry['time_s'], df_telemetry['altitude'], label='Altitud (m)')
plt.xlabel("Tiempo (s)")
plt.ylabel("Altitud (m)")
plt.title("Altitud del cohete durante el vuelo")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()


import numpy as np

# Crear una reconstrucción artificial desde 0 m hasta la altitud del primer dato válido (~4350 m)
# Suponiendo un ascenso constante en los primeros segundos
initial_altitude = 0  # altitud inicial (asumida)
first_recorded_time = df_telemetry['time_s'].min()
first_recorded_altitude = df_telemetry['altitude'].iloc[0]

# Asumimos que tomó ~5 segundos en llegar desde el suelo hasta el primer dato registrado
reconstructed_time = np.linspace(-5, 0, 50)
reconstructed_altitude = np.linspace(initial_altitude, first_recorded_altitude, 50)

# Concatenar los datos reconstruidos con los datos reales de los primeros 20 s
reconstructed_df = pd.DataFrame({
    'time_s': reconstructed_time,
    'altitude': reconstructed_altitude
})

full_initial_df = pd.concat([reconstructed_df, initial_flight_df], ignore_index=True)

# Graficar la reconstrucción completa
plt.figure(figsize=(10, 5))
plt.plot(full_initial_df['time_s'], full_initial_df['altitude'], label='Altitud reconstruida', color='tab:blue')
plt.axvline(x=0, linestyle='--', color='gray', label='Inicio de datos reales')
plt.xlabel("Tiempo (s)")
plt.ylabel("Altitud (m)")
plt.title("Reconstrucción del Perfil de Altitud – Inicio del Vuelo")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()
