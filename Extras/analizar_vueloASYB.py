#Analisis de datos de vuelo de la ASYB
#SPAC 2024-Xitle2

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.signal import savgol_filter

df = pd.read_csv(r'C:\Users\Natalia\OneDrive\Tesis\GithubCode\3DOF-Rocket-PU\Archivos\Copia de vueloSpaceport.csv')

#pasos de tiempo en milisegundos entre cada recepcion de datos
diffs = df["time"].to_numpy()[1:]-df["time"].to_numpy()[:-1]
plt.plot(diffs)
plt.title("Variacion del paso en datos recolectados")
plt.show()

#datos obtenidos
tiempo = df["time"]/1e3
altitud = df["altitude"]
altitud_suave = savgol_filter(altitud, 25, 13)

#Equiespaciamiento de datos
def calc_dato(t):
  if t > tiempo.max():
    return 0
  else:
    # Realizar interpolación
    return np.interp(t, tiempo, altitud)

#cant=tiempo.max()/0.2
#cant=int(cant)
#print(cant)
#tiempo_equiesp=np.linspace(0,3740,cant)
time_equiesp=np.linspace(3676,3739,2000)
altura_interp = [calc_dato(t) for t in time_equiesp]

plt.plot(tiempo, altitud, label="Cruda")
#plt.plot(tiempo, altitud_suave, label="Suavizada")
plt.plot(time_equiesp,altura_interp, label= "Interpolacion")
plt.legend()
plt.show()

# plt.plot(tiempo, ax, label="ax")
# plt.plot(tiempo, ay, label="ay")
# plt.plot(tiempo, az, label="az")
# plt.plot(tiempo, atot, label="tot")
# plt.legend()



vert_vel = np.gradient(altitud, 0.2)
# vert_vel2 = np.gradient(altitud_suave, 0.2)
vert_vel3 = np.gradient(altura_interp, 0.2)
plt.figure()

plt.plot(tiempo-3676, vert_vel, label="De datos")
#plt.plot(tiempo, savgol_filter(vert_vel, 25, 1))
plt.plot(time_equiesp-3676, vert_vel3, label="De equiespaciamiento")
plt.title("Velocidad vertical numerica")
plt.legend()
plt.show()



vert_acc = np.gradient(savgol_filter(vert_vel, 25, 5))
#plt.figure()
#plt.title("Aceleración vertical")
#plt.plot(tiempo, vert_acc)

#plt.show()



#aceleraciones obtenidas
ax = df["ax"]
ay = df["ay"] #acc vertical de datos
az = df["az"]
atot = np.sqrt(ax**2+ay**2+az**2)

plt.figure()
plt.title("Aceleraciones")
plt.plot(ax, label="ax")
plt.plot(ay, label="ay")
plt.plot(az, label="az")
plt.plot(atot,label="a total")
plt.legend()
plt.show()


#Coomparacion: Aceleracion vertical
acc_vel = np.gradient(vert_vel, 0.2)
# vert_vel2 = np.gradient(altitud_suave, 0.2)
acc_vel3 = np.gradient(vert_vel3, 0.2)


plt.figure()

plt.plot(tiempo-3676, acc_vel, label="Numerica de datos")
#plt.plot(tiempo, savgol_filter(vert_vel, 25, 1))
plt.plot(time_equiesp-3676, acc_vel3, label="Num de equiespaciamiento")
plt.plot(tiempo-3676,ay,label="Datos directos")
plt.title("Aceleracion vertical numerica")
plt.legend()
plt.show()
