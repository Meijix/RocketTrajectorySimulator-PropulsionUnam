
import pandas as pd
import matplotlib.pyplot as plt

from simulacion1 import *

# Load the data from the CSV file
#Corregir el path file
df = pd.read_csv(r'C:\Users\Natalia\OneDrive\Tesis\GithubCode\3DOF-Rocket-PU\Archivos\AlturavsTiempo-Xitle2.csv')

# Extract the altitude and time columns
altitude = df['ALTURA [km]']
time = df['tiempo [s]']

# Create a plot of altitude vs. time
plt.plot(time-7, altitude, label="real")
plt.plot(tiempos[1:], posiciones[:, 2]/1000, label="simulada")
plt.xlabel('Tiempo (s)')
plt.ylabel('Altura (km)')
plt.title('Xitle 2: Altura vs. Tiempo')
plt.legend()

# Show the plot
plt.show()

