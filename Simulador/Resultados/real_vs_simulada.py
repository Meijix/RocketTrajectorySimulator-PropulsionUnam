# Comparación de la altura vs. tiempo de las simulaciones con los datos experimentales
#Diversas eficiencias de la simulación
#un mismo integrador
import pandas as pd
import matplotlib.pyplot as plt

# Datos experimentales
df_exp = pd.read_csv(r'C:\Users\Natalia\OneDrive\Archivos\Tesis\GithubCode\SimuladorVueloNat\3DOF-Rocket-PU\Archivos\AlturavsTiempo-Xitle2.csv')
# Extraer los datos experimentales
altitude = df_exp['ALTURA [km]']*1000 # Convertir a metros
time = df_exp['tiempo [s]']-10 # Restar el tiempo de ignición
#Apogeo experimental
apogeo_exp = altitude.max()
t_apogeo_exp = time[altitude.idxmax()]
####################################################

TipoVuelo = 'VueloLibre'
integrador='RungeKutta4'
eficiencias = [100, 90, 80, 70, 60]
datos = {}
#Extraer los datos de las simulaciones
#Lee datos de las carpetas {TipoVuelo}-{integrador}-{efi}
for efi in eficiencias:
    #print("Eficiencia:",efi)
    ruta = f'C:/Users/Natalia/OneDrive/Archivos/Tesis/GithubCode/SimuladorVueloNat/3DOF-Rocket-PU/Simulador/Resultados/OutputFiles/{TipoVuelo}-{integrador}-{efi}/datos.csv'
    #Nombre dependiendo de la eficiencia
    df_simu = pd.read_csv(ruta)
    #Extraer los datos
    altitude_simu = df_simu['z']
    time_simu = df_simu['t']
    #Guardar los datos en diccionario cuyo nombre es el porcentaje de eficiencia
    datos[efi] = {'z': altitude_simu, 't': time_simu}

# Create a plot of altitude vs. time
# Plot experimental data
plt.plot(time, altitude, label=" experimental real", color='darkblue')
#Apogeo experimental
plt.axvline(x=t_apogeo_exp, color='indianred', linestyle='--')
plt.scatter(t_apogeo_exp, apogeo_exp, color='r')
#Valor del apogeo experimental
plt.text(t_apogeo_exp, apogeo_exp, f'{apogeo_exp:.2f}', ha='left', va='bottom')
#Simulaciones
for efi in eficiencias:
    plt.plot(datos[efi]['t'], datos[efi]['z'], label=f"simulada {efi}%", linestyle='--')

# Add labels and title
plt.xlabel('Tiempo (s)')
plt.ylabel('Altura (km)')
plt.title('Xitle 2: Altura vs. Tiempo')
plt.legend()

# Show the plot
plt.show()

