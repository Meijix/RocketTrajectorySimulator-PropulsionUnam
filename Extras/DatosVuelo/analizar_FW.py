
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

#df = pd.read_csv(r'C:\Users\Natalia\OneDrive\Tesis\GithubCode\3DOF-Rocket-PU\Archivos\Copia de FthrWtTRAKR_06-22-2024_12_37_13.csv')
df = pd.read_csv(r'C:\Users\Natalia\OneDrive\Tesis\GithubCode\3DOF-Rocket-PU\Archivos\DatosVuelo\FTW.csv')

ifirst = 934
t_apogeo = 43
FT_TO_M = 0.3048

tiempo_np = pd.to_datetime(df["TIME"], format="%H:%M:%S.%f").to_numpy()
tiempo = np.array([(tiempo_np[i]-tiempo_np[ifirst])/np.timedelta64(1,'s') for i in range(len(tiempo_np))])

tiempo = tiempo[ifirst:]
vertv = df.iloc[ifirst:]["VERTV"]*FT_TO_M


# plt.plot(tiempo[1:]-tiempo[:-1])
# plt.show()

plt.figure()
plt.plot(tiempo, vertv)
plt.title("Velocidad vertical")
plt.xlabel('Tiempo [s]')
plt.ylabel('m/s')
plt.axvline(t_apogeo, ls="--")

plt.figure()
vertacc = np.gradient(vertv)
plt.plot(vertacc)
plt.title("Aceleración vertical")
plt.ylabel('m/s^2')
plt.axvline(t_apogeo, ls="--")
plt.axhline(-9.8, ls="-", color="gray")

plt.show()

