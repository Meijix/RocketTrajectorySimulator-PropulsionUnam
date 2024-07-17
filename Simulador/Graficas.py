import numpy as np
import matplotlib.pyplot as plt

from angulos import *

from simulacion1 import *

# Posiciones
plt.figure(figsize=(10, 6))
plt.title("Posición en el tiempo")
plt.xlabel("Tiempo (s)")
plt.ylabel("Posición (m)")
plt.plot(tiempos[1:], posiciones[:, 0], label="X")
plt.plot(tiempos[1:], posiciones[:, 1], label="Y")
plt.plot(tiempos[1:], posiciones[:, 2], label="Z")
vuelo1.muestra_tiempos()
plt.legend()
plt.grid(True)

# Velocidades
plt.figure(figsize=(10, 6))
plt.title("Velocidad en el tiempo")
plt.xlabel("Tiempo (s)")
plt.ylabel("Velocidad (m/s)")
plt.plot(tiempos[1:], velocidades[:, 0], label="Vx")
plt.plot(tiempos[1:], velocidades[:, 1], label="Vy")
plt.plot(tiempos[1:], velocidades[:, 2], label="Vz")
# plt.plot(tiempos[1:], np.linalg.norm(velocidades[:, :]), label="Total", color="black")
vuelo1.muestra_tiempos()
plt.legend()
plt.grid(True)

# Mostrar las gráficas
#plt.show()

# Graficar angulos contra el tiempo
plt.figure(figsize=(10, 6))
plt.title("Comportamiento angular en el tiempo")
plt.xlabel("Tiempo (s)")
plt.ylabel("Ángulo (grados)")
plt.plot(tiempos[1:], nice_angle(thetas), label="Theta")
plt.plot(tiempos[1:], nice_angle(omegas), label="Omega",alpha=0.5)
vuelo1.muestra_tiempos()
plt.axhline(riel.angulo, ls="--", color="lightgray")
plt.axhline(-90, ls="--", color="lightgray")
plt.legend()
plt.grid(True)
# plt.xlim(150,300); plt.ylim(-20, 20)
plt.show()


Tmags = np.array([np.linalg.norm(Tvec) for Tvec in Tvecs])
Dmags = np.array([np.linalg.norm(Dvec) for Dvec in Dvecs])
Nmags = np.array([np.linalg.norm(Nvec) for Nvec in Nvecs])


plt.title("Fuerzas en el tiempo")
plt.plot(tiempos[1:], Tmags, label= "Empuje")
plt.plot(tiempos[1:], Nmags,label="Normal")
plt.plot(tiempos[1:], Dmags, label= "Arrastre")
vuelo1.muestra_tiempos()

plt.xlim(0,vuelo1.tiempo_apogeo+10)
plt.legend()

# Graficar componentes de las fuerzas

Txs, Tys, Tzs = zip(*Tvecs)
Dxs, Dys, Dzs = zip(*Dvecs)
Nxs, Nys, Nzs = zip(*Nvecs)

plt.figure(figsize=(18,4))

plt.subplot(1, 3, 1)
plt.title("Empuje [N]")
plt.ylabel("Newtons")
plt.plot(tiempos[1:], Txs, label="X")
plt.plot(tiempos[1:], Tys, label="Y")
plt.plot(tiempos[1:], Tzs, label="Z")
plt.axvline(vuelo1.tiempo_salida_riel, color="orange", ls="--")
plt.axvline(Xitle.t_MECO, color="darkred", ls="--")
plt.axvline(vuelo1.tiempo_apogeo, color="navy", ls="--")
plt.xlim(0,Xitle.t_MECO+1)
plt.legend()

plt.subplot(1, 3, 2)
plt.title("Arrastre [N]")
#plt.ylabel("Newtons")
plt.plot(tiempos[1:], Dxs, label="X")
plt.plot(tiempos[1:], Dys, label="Y")
plt.plot(tiempos[1:], Dzs, label="Z")
vuelo1.muestra_tiempos()
plt.xlim(0,vuelo1.tiempo_apogeo+1)
plt.legend()

plt.subplot(1, 3, 3)
plt.title("Normal [N]")
#plt.ylabel("Newtons")
plt.plot(tiempos[1:], Nxs, label="X")
plt.plot(tiempos[1:], Nys, label="Y")
plt.plot(tiempos[1:], Nzs, label="Z")
vuelo1.muestra_tiempos()
#plt.xlim(0,vuelo1.tiempo_apogeo+1)
#plt.ylim(-6,2.2)
plt.legend()
plt.show()

CGs = np.array(CGs)
CPs = np.array(CPs)


plt.figure(figsize=(18,4))
#si se definen asi los calibres???
stab = (CPs-CGs)/diam_ext
plt.plot(tiempos[1:], CGs[:,2],label="CG")
plt.plot(tiempos[1:], CPs[:,2],label="CP")
plt.title("Posición axial del CG y del CP")
plt.xlabel("Tiempo (s)")
plt.ylabel("Posición axial (m)")
vuelo1.muestra_tiempos()
plt.legend()

ax2 = plt.twinx()
plt.plot(tiempos[1:], stab[:,2], color="C2",label="estabilidad")
plt.ylabel("Estabilidad (calibres)")
#plt.xlim(0,vuelo1.tiempo_apogeo+10)
plt.legend()
plt.show()

# Componentes del brazo de palanca
#palancas = np.array(palancas)
#plt.plot(tiempos[1:], palancas[:,0], label="x")
#plt.plot(tiempos[1:], palancas[:,1], label="y")
#plt.plot(tiempos[1:], palancas[:,2], label="z")
# plt.plot(tiempo[1:], list(np.linalg.norm(p) for p in palancas))
#plt.xlim(0,vuelo1.tiempo_apogeo+10)
#plt.legend()
#plt.title("Componentes del brazo de palanca")
#plt.xlabel("Tiempo (s)")
#vuelo1.muestra_tiempos()
#plt.show()