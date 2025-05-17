import numpy as np
from numpy import *
import pandas as pd
import matplotlib.pyplot as plt
from scipy import *
import sys
import os


# Agregar la ruta del directorio que contiene los paquetes al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from Paquetes.utils.funciones import obtener_path_archivo


motorThrustTable = obtener_path_archivo('Archivos', 'CurvasEmpuje', 'pruebaestaica28mayo2024.csv')
motorMassTable = obtener_path_archivo('Archivos', 'CurvasEmpuje', 'MegaPunisherFatMasadot.csv')
# Leer los archivos CSV en dataframes
thrust_data = pd.read_csv(motorThrustTable)
mass_data = pd.read_csv(motorMassTable)

# Mostrar las primeras filas de las tablas para confirmar la carga
print("Thrust Data:")
print(thrust_data.head())
print("\nMass Data:")
print(mass_data.head())

# Graficar las tablas
plt.figure(figsize=(10, 6))

# Graficar la curva de empuje
plt.subplot(2, 1, 1)
plt.plot(thrust_data['Time'], thrust_data['Thrust'], label='Thrust')
plt.title('Curva de Empuje')
plt.xlabel('Tiempo [s]')
plt.ylabel('Empuje [N]')
plt.grid(True)
plt.legend()

# Graficar la masa del motor
plt.subplot(2, 1, 2)
plt.plot(mass_data['Time'], mass_data['Mass'], label='Mass', color='orange')
plt.title('Curva de Masa del Motor')
plt.xlabel('Tiempo [s]')
plt.ylabel('Masa [kg]')
plt.grid(True)
plt.legend()

# Mostrar las gráficas
plt.tight_layout()
plt.show()




############################################


motorMassTable['time'] = motorMassTable['Time (s)']
motorMassTable['oxi'] = motorMassTable['Oxidizer Mass (kg)']
motorMassTable['grano'] = motorMassTable['Fuel Mass (kg)']

m_oxidante=motorMassTable['oxi'].max()
m_grano=motorMassTable['grano'].max()
#m_prop=motorMassTable['oxi'].max()+motorMassTable['grano'].max()
m_prop=m_grano+m_oxidante
# Calcular el área de la curva empuje vs tiempo utilizando la regla del trapecio
#Vamos a probar otro tipo de integracion para mejorarlo?
I_total = np.trapz(y=motorThrustTable['thrust'], x=motorThrustTable['time'])
I=I_total/(m_prop*9.81)
T_avg=I_total/t_MECO

def calc_empuje(t):
  if t > t_MECO:
    return 0
  else:
    # Realizar interpolación
    return np.interp(t, motorThrustTable['time'], motorThrustTable['thrust'])
  
  # Define the time values for the exact and interpolated thrust curves
time_exact = motorThrustTable['time']
time_interp = np.linspace(0, t_MECO, 1000)

# Calculate the exact and interpolated thrust values
thrust_exact = motorThrustTable['thrust']
thrust_interp = [calc_empuje(t) for t in time_interp]

# Plot the exact and interpolated thrust curves
plt.plot(time_exact, thrust_exact, label='Exact Thrust', marker="*")
plt.plot(time_interp, thrust_interp, label='Interpolated Thrust')

# Add a legend and axis labels
plt.legend()
plt.xlabel('Time (s)')
plt.ylabel('Thrust (N)')
#plt.xlim(15,20)
plt.figsize=(25,8)
# Show the plot
plt.show()

##Impresion en terminal de datos importates del motor
print("Masa inicial del propelente", m_prop)
print("Impulso total: ",I_total)
print("Impulso especifico: ", I)
print("Empuje promedio", T_avg)