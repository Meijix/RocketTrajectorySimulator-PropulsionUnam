import pandas as pd
import numpy as np


ruta=r'C:\Users\Natalia\OneDrive\PROPULSION-UNAM-DOCS\EVA-20km\El_Gavilan_I_ParafinaRapida_10%_298K_27-Sep-2024.txt'

# Leer el archivo .txt en un DataFrame
df = pd.read_csv(ruta, sep=',')
#print(df)

df['tiempo_recorrido'] = df['time'] - 100
tiempo_rec=df['tiempo_recorrido']
#print("Tiempo despues",tiempo_rec)

# Guardar las primeras dos columnas en un nuevo archivo .txt

df[['tiempo_recorrido', 'Thrust']].to_csv(r'../salidaCurva.txt', sep='\t', index=False)

#Grafica
import matplotlib.pyplot as plt
plt.plot(df['time'], df['Thrust'])
plt.xlabel('Tiempo [s]')
plt.ylabel('Thrust [N]')
plt.title('Thrust vs Tiempo')
plt.show()