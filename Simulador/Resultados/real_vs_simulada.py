
import pandas as pd
import matplotlib.pyplot as plt
import sys
import os

# Agregar la ruta del directorio que contiene los paquetes al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from Simulador.src.VueloLibre import *

# Load the data from the CSV file
#Corregir el path file
df = pd.read_csv(r'C:\Users\Natalia\OneDrive\Archivos\Tesis\GithubCode\SimuladorVueloNat\3DOF-Rocket-PU\Archivos\AlturavsTiempo-Xitle2.csv')

# Extract the altitude and time columns
altitude = df['ALTURA [km]']
time = df['tiempo [s]']

# Create a plot of altitude vs. time
plt.plot(time-7, altitude, label="real")
plt.plot(tiempos[:], posiciones[:, 2]/1000, label="simulada")
plt.xlabel('Tiempo (s)')
plt.ylabel('Altura (km)')
plt.title('Xitle 2: Altura vs. Tiempo')
plt.legend()

# Show the plot
plt.show()

