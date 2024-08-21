import numpy as np
import matplotlib.pyplot as plt

from angulos import *
#from Xitle import Xitle
from simulacion1 import * #datos_simulados,posiciones,velocidades,thetas, omegas
#from simulacion2 import *
from dibujarCohete import *

#tiempos, sim, CPs, CGs, masavuelo, viento_vuelo_mags, viento_vuelo_dirs, viento_vuelo_vecs, Tvecs, Dvecs, Nvecs, accels, palancas, accangs, Gammas, Alphas, torcas, Cds, Machs = zip*(datos_simulados)

vuelo_graficar=vuelo1
#vuelo_graficar=vuelo_paracaidas

# GRAFICAS

# Graficar trayectoria y orientacion con cohete en diferentes puntos
plt.xlabel('Alcance (m)')
plt.ylabel('Altura (m)')
plt.title('Trayectoria del cohete Xitle en el tiempo')
plt.plot(posiciones[:, 0], posiciones[:, 2], color='purple')


# Dibujar el cohete cada 10 segundos
for i in range(0, len(tiempos), 800):
  dibujar_cohete(posiciones[i, 0], posiciones[i, 2], np.rad2deg(thetas[i]), 800)  # Ajusta longitud y altura según sea necesario
  #dibujar_cohete(posiciones[i, 0], posiciones[i, 2], thetas[i], 500)

plt.gca().set_aspect("equal")
plt.show()

print(np.rad2deg(thetas))
###########################

#Graficar el vector viento 
# Get the x and z components of the wind vector
vx = viento_actual.vector[0]
vz = viento_actual.vector[2]

fig, ax = plt.subplots()
ax.arrow(0, 0, vx, vz, head_width=0.5, head_length=0.5, color='r', zorder=10)
ax.set_xlim([-15, 15])
ax.set_ylim([-15, 15])
ax.set_xlabel('x (m)')
ax.set_ylabel('z (m)')
ax.set_title('Vector de viento')
plt.show()
###########################

# GRAFICA 1. Posiciones
plt.figure(figsize=(10, 6))
plt.title("Posición en el tiempo")
plt.xlabel("Tiempo (s)")
plt.ylabel("Posición (m)")
plt.plot(tiempos[:], posiciones[:, 0], label="X")
plt.plot(tiempos[:], posiciones[:, 1], label="Y")
plt.plot(tiempos[:], posiciones[:, 2], label="Z")
vuelo_graficar.muestra_tiempos()
plt.legend()
plt.grid(True)

# GRAFICA 2. Velocidades
plt.figure(figsize=(10, 6))
plt.title("Velocidad en el tiempo")
plt.xlabel("Tiempo (s)")
plt.ylabel("Velocidad (m/s)")
plt.plot(tiempos[:], velocidades[:, 0], label="Vx")
plt.plot(tiempos[:], velocidades[:, 1], label="Vy")
plt.plot(tiempos[:], velocidades[:, 2], label="Vz")
# plt.plot(tiempos[1:], np.linalg.norm(velocidades[:, :]), label="Total", color="black")
vuelo_graficar.muestra_tiempos()
plt.legend()
plt.grid(True)
# Mostrar las gráficas
plt.show()

# GRAFICA 3. Angulos contra el tiempo
plt.figure(figsize=(10, 6))
plt.title("Comportamiento angular en el tiempo")
plt.xlabel("Tiempo (s)")
plt.ylabel("Ángulo (grados)")
plt.plot(tiempos[:], nice_angle(thetas), label="Theta")
plt.plot(tiempos[:], nice_angle(omegas), label="Omega",alpha=0.5)
vuelo_graficar.muestra_tiempos()
plt.axhline(riel.angulo, ls="--", color="lightgray")
plt.axhline(-90, ls="--", color="lightgray")
plt.legend()
plt.grid(True)
# plt.xlim(150,300); plt.ylim(-20, 20)
plt.show()


Tmags = np.array([np.linalg.norm(Tvec) for Tvec in Tvecs])
Dmags = np.array([np.linalg.norm(Dvec) for Dvec in Dvecs])
Nmags = np.array([np.linalg.norm(Nvec) for Nvec in Nvecs])

#GRAFICA 4. Fuerzas (magnitudes)
plt.title("Fuerzas en el tiempo")
plt.plot(tiempos[1:], Tmags, label= "Empuje")
plt.plot(tiempos[1:], Nmags,label="Normal")
plt.plot(tiempos[1:], Dmags, label= "Arrastre")
vuelo_graficar.muestra_tiempos()

plt.xlim(0,vuelo_graficar.tiempo_apogeo+10)
plt.legend()
plt.show()

# GRAFICA 5. Componentes de las fuerzas

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
plt.axvline(vuelo_graficar.tiempo_salida_riel, color="orange", ls="--")
plt.axvline(Xitle.t_MECO, color="darkred", ls="--")
plt.axvline(vuelo_graficar.tiempo_apogeo, color="navy", ls="--")
plt.xlim(0,Xitle.t_MECO+1)
plt.legend()

plt.subplot(1, 3, 2)
plt.title("Arrastre [N]")
#plt.ylabel("Newtons")
plt.plot(tiempos[1:], Dxs, label="X")
plt.plot(tiempos[1:], Dys, label="Y")
plt.plot(tiempos[1:], Dzs, label="Z")
vuelo_graficar.muestra_tiempos()
plt.xlim(0,vuelo_graficar.tiempo_apogeo+1)
plt.legend()

plt.subplot(1, 3, 3)
plt.title("Normal [N]")
#plt.ylabel("Newtons")
plt.plot(tiempos[1:], Nxs, label="X")
plt.plot(tiempos[1:], Nys, label="Y")
plt.plot(tiempos[1:], Nzs, label="Z")
vuelo_graficar.muestra_tiempos()
#plt.xlim(0,vuelo1.tiempo_apogeo+1)
#plt.ylim(-6,2.2)
plt.legend()
plt.show()

CGs = np.array(CGs)
CPs = np.array(CPs)

#GRAFICA 6. Estabilidad
plt.figure(figsize=(18,4))
#si se definen asi los calibres???
stab = (CPs-CGs)/diam_ext
plt.subplot(1, 2, 1)
plt.plot(tiempos[1:], CGs[:,2],label="CG")
plt.plot(tiempos[1:], CPs[:,2],label="CP")
plt.title("Posición axial del CG y del CP")
plt.xlabel("Tiempo (s)")
plt.ylabel("Posición axial (m)")
vuelo_graficar.muestra_tiempos()
plt.legend()

plt.subplot(1, 2, 2)
plt.plot(tiempos[1:], stab[:,2], color="C2",label="estabilidad")
plt.title("Estabilidad (calibres)")
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

# GRAFICA 7. Theta, Velocidad y aceleración angular (derivada de theta)
plt.figure(figsize=(16,5))

plt.subplot(1, 4, 1)
plt.plot(tiempos[:], nice_angle(thetas))
#plt.xlim(0,vuelo1.tiempo_apogeo+10)
vuelo_graficar.muestra_tiempos()
plt.title("Ángulo de inclinación (Pitch)")#pitch (theta)

plt.subplot(1, 4, 2)
plt.plot(tiempos[:], nice_angle(omegas))
plt.axhline(0, ls="--", color="lightgray")
#plt.xlim(0,vuelo1.tiempo_apogeo+10)
vuelo_graficar.muestra_tiempos()
plt.title("Velocidad angular(omega)")

plt.subplot(1, 4, 3)
plt.plot(tiempos[1:], nice_angle(accangs))
#plt.xlim(0,vuelo1.tiempo_apogeo+10)
vuelo_graficar.muestra_tiempos()
plt.title("Aceleración angular")

plt.subplot(1, 4, 4)
palancas = np.array(palancas)
plt.plot(tiempos[1:], palancas[:,0],label= "comp x")
plt.plot(tiempos[1:], palancas[:,1],label="comp y")
plt.plot(tiempos[1:], palancas[:,2], label = "comp z")
plt.title("Componentes del brazo de momento")
#plt.xlim(0,vuelo1.tiempo_apogeo+10)
vuelo_graficar.muestra_tiempos()
plt.legend()
plt.show()

#GRAFICA 8. Angulos
plt.figure(figsize=(14,4))
plt.title("Ángulos en el tiempo")
plt.xlabel("Tiempo (s)")
plt.ylabel("Ángulo (grados º)")
plt.plot(tiempos[:], [normalize_angle(x) for x in np.rad2deg(thetas)], label = 'Ángulo de inclinación (theta)')#pitch
plt.plot(tiempos[1:], [normalize_angle(x) for x in np.rad2deg(Gammas)], label = 'Ángulo de vuelo (gamma)')#FPA
plt.plot(tiempos[1:], [normalize_angle(x) for x in np.rad2deg(Alphas)],label = 'Ángulo de ataque (alpha)')
plt.axvline(vuelo_graficar.tiempo_apogeo, color="0.5")
plt.axhline(0, ls="--", color="gray")
plt.axhline(riel.angulo, ls="--", color="lightgray")
plt.axhline(-90, ls="--", color="lightgray")
# plt.xlim(0,vuelo1.tiempo_apogeo+20)
vuelo_graficar.muestra_tiempos()
plt.legend()
plt.xlim(0,100)
#plt.ylim(75,80.5)
plt.show()

#GRAFICA 9. Variacion de masa
plt.xlabel('Tiempo (s)')
plt.ylabel('Masa (kg)')
plt.title('Masa del cohete Xitle en el tiempo')
plt.xlim(0,vuelo_graficar.tiempo_apogeo+5)
vuelo_graficar.muestra_tiempos()
plt.plot(tiempos, masavuelo)
plt.show()

'''
# GRAFICA 10. Trayectoria
plt.xlabel('Alcance (m)')
plt.ylabel('Altura (m)')
plt.title('Trayectoria del cohete Xitle en el tiempo')
plt.plot(posiciones[:, 0], posiciones[:, 2])
# plt.ylim(0, 10000)
#plt.gca().set_aspect("equal")
plt.show()
'''
