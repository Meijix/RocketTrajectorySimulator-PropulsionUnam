import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.signal import savgol_filter

df = pd.read_csv(r'C:\Users\Natalia\OneDrive\Tesis\GithubCode\3DOF-Rocket-PU\Archivos\Copia de vueloSpaceport.csv')

diffs = df["time"].to_numpy()[1:]-df["time"].to_numpy()[:-1]
plt.plot(diffs)
plt.show()

tiempo = df["time"]/1e3
altitud = df["altitude"]
altitud_suave = savgol_filter(altitud, 25, 13)
ax = df["ax"]
ay = df["ay"]
az = df["az"]
atot = np.sqrt(ax**2+ay**2+az**2)

# plt.plot(tiempo, altitud, label="Cruda")
# plt.plot(tiempo, altitud_suave, label="Suavizada")
# plt.legend()
plt.show()

# plt.plot(tiempo, ax, label="ax")
# plt.plot(tiempo, ay, label="ay")
# plt.plot(tiempo, az, label="az")
# plt.plot(tiempo, atot, label="tot")
# plt.legend()



vert_vel = np.gradient(altitud, 0.2)
# vert_vel2 = np.gradient(altitud_suave, 0.2)
plt.figure()

plt.plot(tiempo, vert_vel)
plt.plot(tiempo, savgol_filter(vert_vel, 25, 1))
# plt.plot(tiempo, vert_vel2)



vert_acc = np.gradient(savgol_filter(vert_vel, 25, 5))
plt.figure()
plt.title("Aceleración vertical")
plt.plot(tiempo, vert_acc)

plt.show()


