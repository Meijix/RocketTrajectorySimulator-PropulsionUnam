import numpy as np
from numpy import *
import pandas as pd
import matplotlib.pyplot as plt
from scipy import *
import scipy.integrate as integrate

motorThrustTable = pd.read_csv(r'C:\Users\Natalia\OneDrive\Tesis\GithubCode\3DOF-Rocket-PU\Archivos\pruebaestaica28mayo2024.csv')
t_MECO = motorThrustTable['time'].max() #tiempo en que se acaba el empuje

motorMassTable = pd.read_csv(r'C:\Users\Natalia\OneDrive\Tesis\GithubCode\3DOF-Rocket-PU\Archivos\MegaPunisherFatMasadot.csv')
motorMassTable['time'] = motorMassTable['Time (s)']
motorMassTable['oxi'] = motorMassTable['Oxidizer Mass (kg)']
motorMassTable['grano'] = motorMassTable['Fuel Mass (kg)']

m_prop=motorMassTable['oxi'].max()+motorMassTable['grano'].max()
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

print("Masa inicial del propelente", m_prop)
print("Impulso total: ",I_total)
print("Impulso especifico: ", I)
print("Empuje promedio", T_avg)