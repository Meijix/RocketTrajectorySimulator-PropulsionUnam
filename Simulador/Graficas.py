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

# Graficar velocidad y aceleración angular (derivada de theta)

plt.figure(figsize=(16,5))

plt.subplot(1, 4, 1)
plt.plot(tiempos[1:], nice_angle(thetas))
#plt.xlim(0,vuelo1.tiempo_apogeo+10)
vuelo1.muestra_tiempos()
plt.title("Ángulo de inclinación (Pitch)")#pitch (theta)

plt.subplot(1, 4, 2)
plt.plot(tiempos[1:], nice_angle(omegas))
plt.axhline(0, ls="--", color="lightgray")
#plt.xlim(0,vuelo1.tiempo_apogeo+10)
vuelo1.muestra_tiempos()
plt.title("Velocidad angular(omega)")

plt.subplot(1, 4, 3)
plt.plot(tiempos[1:], nice_angle(accangs))
#plt.xlim(0,vuelo1.tiempo_apogeo+10)
vuelo1.muestra_tiempos()
plt.title("Aceleración angular")

plt.subplot(1, 4, 4)
palancas = np.array(palancas)
plt.plot(tiempos[1:], palancas[:,0],label= "comp x")
plt.plot(tiempos[1:], palancas[:,1],label="comp y")
plt.plot(tiempos[1:], palancas[:,2], label = "comp z")
plt.title("Componentes del brazo de momento")
#plt.xlim(0,vuelo1.tiempo_apogeo+10)
vuelo1.muestra_tiempos()
plt.legend()

plt.show()


plt.figure(figsize=(14,4))
plt.title("Ángulos en el tiempo")
plt.xlabel("Tiempo (s)")
plt.ylabel("Ángulo (grados º)")
plt.plot(tiempos[1:], [normalize_angle(x) for x in np.rad2deg(thetas)], label = 'Ángulo de inclinación (theta)')#pitch
plt.plot(tiempos[1:], [normalize_angle(x) for x in np.rad2deg(Gammas)], label = 'Ángulo de vuelo (gamma)')#FPA
plt.plot(tiempos[1:], [normalize_angle(x) for x in np.rad2deg(Alphas)],label = 'Ángulo de ataque (alpha)')
plt.axvline(vuelo1.tiempo_apogeo, color="0.5")
plt.axhline(0, ls="--", color="gray")
plt.axhline(riel.angulo, ls="--", color="lightgray")
plt.axhline(-90, ls="--", color="lightgray")
# plt.xlim(0,vuelo1.tiempo_apogeo+20)
vuelo1.muestra_tiempos()
plt.legend()
plt.xlim(0,100)
#plt.ylim(75,80.5)


plt.xlabel('Tiempo (s)')
plt.ylabel('Masa (kg)')
plt.title('Masa del cohete Xitle en el tiempo')
plt.xlim(0,vuelo1.tiempo_apogeo+5)
vuelo1.muestra_tiempos()
plt.plot(tiempos, masavuelo)


# Graficar trayectoria
plt.xlabel('Alcance (m)')
plt.ylabel('Altura (m)')
plt.title('Trayectoria del cohete Xitle en el tiempo')
plt.plot(posiciones[:, 0], posiciones[:, 2])
# plt.ylim(0, 10000)
plt.gca().set_aspect("equal")



# Extract the positions of the trajectory
posiciones = np.array([state[0:3] for state in sim])

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


###GRAFICA 3D
posiciones = np.array([state[0:3] for state in sim])

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
ax.set_title("Trayectoria y orientaciones del cohete Xitle en el tiempo")

# Add legend and show plot
ax.legend()

# Add an arrow indicating the launch angle
# Create a rotation matrix
theta_rad = np.deg2rad(riel.angulo)
#rotation_matrixY = np.array([[np.cos(theta_rad),0, np.sin(theta_rad)],
#                               [0,1,0],
#                            [-np.sin(theta_rad), 0, np.cos(theta_rad)]])

rotation_matrix = np.array([[np.cos(theta_rad), -np.sin(theta_rad), 0],
                            [np.sin(theta_rad), np.cos(theta_rad), 0],
                            [0, 0, 1]])


launch_vector = rotation_matrix @ np.array([800, 0, 0])
ax.quiver(launch_point[0], launch_point[1], launch_point[2], launch_vector[0], launch_vector[1], launch_vector[2], color='green', arrow_length_ratio=0.1)

# Add projections of the trajectory onto the xy, xz, and yz planes
ax.plot(posiciones[:, 0], posiciones[:, 1], 0, color='black', linestyle='--', alpha=0.5)
ax.plot(posiciones[:, 0], posiciones[:, 2], 0, color='black', linestyle='--', alpha=0.7)
ax.plot(posiciones[:, 1], posiciones[:, 2], 0, color='black', linestyle='--', alpha=0.5)

# Set limits for each plane
#ax.set_xlim(0, 10000)
#ax.set_ylim(0, 10000)
#ax.set_zlim(0, 10000)

# Show the plot
plt.show()
