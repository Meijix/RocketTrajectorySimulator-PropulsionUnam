import numpy as np
import matplotlib.pyplot as plt

from angulos import *
#from Xitle import Xitle
#from simulacion1 import * #datos_simulados,posiciones,velocidades,thetas, omegas
from simulacion2 import *
from dibujarCohete import *

#tiempos, sim, CPs, CGs, masavuelo, viento_vuelo_mags, viento_vuelo_dirs, viento_vuelo_vecs, Tvecs, Dvecs, Nvecs, accels, palancas, accangs, Gammas, Alphas, torcas, Cds, Machs = zip*(datos_simulados)

#Cambiar el vuelo a graficar
#vuelo_graficar=vuelo1
vuelo_graficar=vuelo_paracaidas

import time 
inicio = time.time()
# GRAFICAS
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
#Grafica 0. Trayectoria y orientacion con cohete en diferentes puntos
plt.xlabel('Alcance (m)')
plt.ylabel('Altura (m)')
plt.title('Trayectoria del cohete Xitle en el tiempo')
plt.plot(posiciones[:, 0], posiciones[:, 2], color='purple')
plt.gca().set_aspect("equal")

# Dibujar el cohete cada x segundos
x = 8
x = x * 100

for i in range(0, len(tiempos), x):
  dibujar_cohete(posiciones[i, 0], posiciones[i, 2], np.rad2deg(thetas[i]), 200)  # Ajusta longitud y altura según sea necesario
  #dibujar_cohete(posiciones[i, 0], posiciones[i, 2], thetas[i], 500)

plt.show()

#print(np.rad2deg(thetas))


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
plt.xlim(0,vuelo_graficar.tiempo_apogeo+10)
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
plt.xlim(0,vuelo_graficar.tiempo_apogeo+20)
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
plt.gca().set_aspect("equal")
plt.show()
'''
####################
# GRAFICAS 3D
# Extract the launch and impact points
launch_point = posiciones[0]
impact_point = posiciones[-1]

# Create the figure and 3D axes
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection="3d")

# Plot the trajectory
ax.plot(posiciones[:, 0], posiciones[:, 1], posiciones[:, 2])

# Plot the launch and impact points with different colors
ax.scatter(launch_point[0], launch_point[1], launch_point[2], c='blue', label='Punto de lanzamiento')
ax.scatter(impact_point[0], impact_point[1], impact_point[2], c='red', label='Punto de impacto')

# Create a circle in the xy plane with a diameter of 1000 meters around the impact point
circle_radius = 1000
circle_points = np.linspace(0, 2*np.pi, 100)
circle_x = impact_point[0] + circle_radius * np.cos(circle_points)
circle_y = impact_point[1] + circle_radius * np.sin(circle_points)

# Plot the circle in the xy plane
ax.plot(circle_x, circle_y, 0, color='gray', linestyle='--', label='1000 m radio de seguridad')

# Set labels, title, and limits
ax.set_xlabel("Alcance (m)")
ax.set_ylabel("Desplazamiento (m)")
ax.set_zlabel("Altura (m)")
ax.set_title("Trayectoria del cohete Xitle en el tiempo")
#ax.set_xlim(0, 10000)
#ax.set_ylim(0, 10000)
#ax.set_zlim(0, 10000)

# Add legend and show plot
ax.legend()
plt.show()



##################
fin = time.time()
print(f"Tiempo graficando: {fin-inicio:.1f}s")

#################\
#ANIMACIONES
#ANIMACION 1. Trayectoria
# ...

# Crear figura y axes 3D
# ...

# Crear figura y axes 3D
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection="3d")

# Plotear la trayectoria inicial
ax.plot(posiciones[:, 0], posiciones[:, 1], posiciones[:, 2])

# Crear un objeto cohete que se va a dibujar en cada frame
cohete, = ax.plot([], [], [], 'o-', lw=2)

# Crear un objeto trayectoria que se va a dibujar en cada frame
trayectoria, = ax.plot([], [], [], 'b-', lw=1)

# Crear un objeto quiver para dibujar la orientación del cohete
quiver, = ax.quiver([], [], [], [], [], [], color='r', length=10)

# Función que se llama en cada frame de la animación
def animate(i):
    cohete.set_data(posiciones[:i, 0], posiciones[:i, 1])
    cohete.set_3d_properties(posiciones[:i, 2])
    cohete.set_markersize(10)
    cohete.set_markerfacecolor('b')
    cohete.set_markeredgecolor('b')
    cohete.set_linewidth(2)
    cohete.set_linestyle('-')
    
    trayectoria.set_data(posiciones[:i, 0], posiciones[:i, 1])
    trayectoria.set_3d_properties(posiciones[:i, 2])
    trayectoria.set_linewidth(1)
    trayectoria.set_linestyle('-')
    trayectoria.set_color('b')
    
    # Actualizar la posición y dirección del quiver
    quiver.set_segments([[[posiciones[i, 0], posiciones[i, 1], posiciones[i, 2]], 
                          [posiciones[i, 0] + np.cos(thetas[i]), posiciones[i, 1] + np.sin(thetas[i]), posiciones[i, 2]]]])
    
    return cohete, trayectoria, quiver,

# Crear la animación
ani = animation.FuncAnimation(fig, animate, frames=len(tiempos), blit=True, interval=50)

# Mostrar la animación
plt.show()