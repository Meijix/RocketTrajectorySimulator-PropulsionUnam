#Graficar los resultados de la simulacion
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import json

from angulos import *
#from condiciones_init import *
from dibujarCohete import *
from funciones import *

#Para usar si se va a simular apenas
#Cambiar el vuelo a graficar
#vuelo_graficar=vuelo1
#vuelo_graficar=vuelo_paracaidas

##########################################
# Funcion para graficar los tiempos importantes
def muestra_tiempos(tiempos, ax):
    ax.axvline(tiempo_salida_riel, color="orange", ls="--")
    ax.axvline(t_MECO, color="darkred", ls="--")
    if tiempo_apogeo is not None:
        ax.axvline(tiempo_apogeo, color="navy", ls="--")
    if tiempo_impacto is not None:
        ax.axvline(tiempo_impacto, color="0.2", ls="--")
    #if tiempo_despliegue is not None:
        #ax.axvline(tiempo_despliegue, color="green", ls="--")
    #ax.legend()
###############################################


###############################################
# Leer los datos de la simulación desde el archivo CSV
datos_simulacion = pd.read_csv('datos_simulacion.csv')
# Extarer los datos del csv
(tiempos, posiciones, velocidades, thetas, omegas, CPs, CGs, masavuelo,estabilidad,
viento_vuelo_mags, viento_vuelo_dirs, viento_vuelo_vecs, wind_xs, wind_ys, wind_zs,
Dmags, Nmags, Tmags, Dxs, Dys, Dzs, Nxs, Nys, Nzs, Txs, Tys, Tzs, Tvecs, Dvecs, Nvecs,
accels, palancas, accangs, Gammas, Alphas, torcas, Cds, Machs) = extraer_datoscsv(datos_simulacion)

#########################################
# Leer los datos de la simulación desde el archivo JSON
with open('datos_simulacion.json', 'r') as f:
    datos = json.load(f)
# Extraer los datos del json
(d_ext, t_MECO, tiempo_salida_riel, tiempo_apogeo, tiempo_impacto,
    max_altitude, max_speed, max_acceleration_linear, max_acceleration_angular) = extraer_datosjson(datos)

############################################
import time 
inicio = time.time()
#print("Posiciones (x,y,z):",posiciones[1,:])
print("Graficando...")
# GRAFICAS
############################################
#VIENTO
#Magnitudes en el tiempo
plt.figure(figsize=(8, 6))
plt.plot(tiempos, viento_vuelo_mags)
plt.xlabel('Tiempo (s)')
plt.ylabel('Magnitud del viento (m/s)')
plt.title('Magnitud del viento en el tiempo')
muestra_tiempos(tiempos, plt)
#plt.show()

#Histograma de las magnitudes
plt.figure(figsize=(8, 6))
plt.hist(viento_vuelo_mags, bins=20)
plt.xlabel('Magnitud del viento (m/s)')
plt.ylabel('Frecuencia')
plt.title('Histograma de la magnitud del viento')
#plt.show()

#Direcciones en el tiempo
plt.figure(figsize=(8, 6))
plt.plot(tiempos, viento_vuelo_dirs)
plt.xlabel('Tiempo (s)')
plt.ylabel('Dirección del viento (grados)')
plt.title('Dirección del viento en el tiempo')
muestra_tiempos(tiempos, plt)
#plt.show()

#Histograma de las direcciones
plt.figure(figsize=(8, 6))
plt.hist(viento_vuelo_dirs, bins=20)
plt.xlabel('Dirección del viento (grados)')
plt.ylabel('Frecuencia')
plt.title('Histograma de la dirección del viento')
#plt.show()

#Rosa de los vientos
#plt.figure(figsize=(8, 6))
#ax = plt.subplot(111, polar=True)
#ax.set_theta_zero_location("N")
#ax.set_theta_direction(-1)
#bars = ax.bar(np.deg2rad(viento_vuelo_dirs), viento_vuelo_mags, width=0.5, bottom=0.0)
#plt.title('Rosa de los vientos')
#ax.set_xticklabels(['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'])
#plt.show()

'''
#Vectores viento en el tiempo
#Falta corregir esta grafica
# Vectores viento en el tiempo
fig, ax = plt.subplots()
for i in range(len(tiempos)):
    ax.arrow(0, 0, wind_xs[i], wind_zs[i], head_width=0.5, head_length=0.5, color='pink', zorder=10, alpha=0.3)

ax.set_xlim([-15, 15])
ax.set_ylim([-15, 15])
ax.set_xlabel('x (m)')
ax.set_ylabel('z (m)')
ax.set_title('Vector de viento')
plt.show()
'''
###########################
#####GRAFICAS DEL COHETE
############################
#Grafica 0. Trayectoria y orientacion con cohete en diferentes puntos
plt.xlabel('Alcance (m)')
plt.ylabel('Altura (m)')
plt.title('Trayectoria del cohete Xitle en el tiempo')
plt.plot(posiciones[:, 0], posiciones[:, 2], color='purple')
plt.gca().set_aspect("equal")

# Dibujar el cohete cada x segundos
x = 10
x = x * 100

for i in range(0, len(tiempos), x):
  dibujar_cohete(posiciones[i, 0], posiciones[i, 2], np.rad2deg(thetas[i]), 200)  # Ajusta longitud y altura según sea necesario
  #dibujar_cohete(posiciones[i, 0], posiciones[i, 2], thetas[i], 500)

# plt.show()

# GRAFICA 1. Posiciones
plt.figure(figsize=(10, 6))
plt.title("Posición en el tiempo")
plt.xlabel("Tiempo (s)")
plt.ylabel("Posición (m)")
plt.plot(tiempos[:], posiciones[:, 0], label="X")
plt.plot(tiempos[:], posiciones[:, 1], label="Y")
plt.plot(tiempos[:], posiciones[:, 2], label="Z")
muestra_tiempos(tiempos, plt)
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
muestra_tiempos(tiempos, plt)
plt.legend()
plt.grid(True)
# Mostrar las gráficas
# plt.show()

# GRAFICA 3. Angulos contra el tiempo
plt.figure(figsize=(10, 6))
plt.title("Comportamiento angular en el tiempo")
plt.xlabel("Tiempo (s)")
plt.ylabel("Ángulo (grados)")
plt.plot(tiempos[:], nice_angle(thetas), label="Theta")
plt.plot(tiempos[:], nice_angle(omegas), label="Omega", alpha=0.5)
muestra_tiempos(tiempos, plt)
plt.axhline(riel.angulo, ls="--", color="lightgray")
plt.axhline(-90, ls="--", color="lightgray")
plt.legend()
plt.grid(True)
# plt.xlim(150,300); plt.ylim(-20, 20)
# plt.show()


#GRAFICA 4. Fuerzas (magnitudes)
plt.figure()
plt.title("Fuerzas en el tiempo")
plt.plot(tiempos[:], Tmags, label= "Empuje")
plt.plot(tiempos[:], Nmags,label="Normal")
plt.plot(tiempos[:], Dmags, label= "Arrastre")
muestra_tiempos(tiempos, plt)
if tiempo_apogeo is not None:
    plt.xlim(0,tiempo_apogeo+10)
plt.legend()
# plt.show()

# GRAFICA 5. Componentes de las fuerzas
plt.figure(figsize=(18,4))

plt.subplot(1, 3, 1)
plt.title("Empuje [N]")
plt.ylabel("Newtons")
plt.plot(tiempos[:], Txs, label="X")
plt.plot(tiempos[:], Tys, label="Y")
plt.plot(tiempos[:], Tzs, label="Z")
muestra_tiempos(tiempos, plt)
plt.xlim(0,t_MECO+1)
plt.legend()

plt.subplot(1, 3, 2)
plt.title("Arrastre [N]")
#plt.ylabel("Newtons")
plt.plot(tiempos[:], Dxs, label="X")
plt.plot(tiempos[:], Dys, label="Y")
plt.plot(tiempos[:], Dzs, label="Z")
muestra_tiempos(tiempos, plt)
if tiempo_apogeo is not None:
    plt.xlim(0,tiempo_apogeo+1)
plt.legend()

plt.subplot(1, 3, 3)
plt.title("Normal [N]")
#plt.ylabel("Newtons")
plt.plot(tiempos[:], Nxs, label="X")
plt.plot(tiempos[:], Nys, label="Y")
plt.plot(tiempos[:], Nzs, label="Z")
muestra_tiempos(tiempos, plt)
if tiempo_apogeo is not None:
    plt.xlim(0,tiempo_apogeo+1)
#plt.ylim(-6,2.2)
plt.legend()
# plt.show()

#GRAFICA 6. Estabilidad
plt.figure(figsize=(18,4))

plt.subplot(1, 2, 1)
plt.plot(tiempos[:], CGs[:],label="CG")
plt.plot(tiempos[:], CPs[:],label="CP")
#plt.plot(tiempos[:],estabilidad[:], label = "estabilidad")
plt.title("Posición axial del CG y del CP")
plt.xlabel("Tiempo (s)")
plt.ylabel("Posición axial (m)")
muestra_tiempos(tiempos, plt)
plt.legend()

plt.subplot(1, 2, 2)
plt.plot(tiempos[:], estabilidad[:], color="C2",label="estabilidad")
plt.title("Estabilidad (calibres)")
#plt.xlim(0,tiempo_apogeo+10)
plt.legend()
plt.show()

# GRAFICA 7. Theta, Velocidad y aceleración angular (derivada de theta)
plt.figure(figsize=(16,5))

plt.subplot(1, 4, 1)
plt.plot(tiempos[:], nice_angle(thetas))
#plt.xlim(0,vuelo1.tiempo_apogeo+10)
muestra_tiempos(tiempos, plt)
plt.title("Ángulo de inclinación (Pitch)")#pitch (theta)

plt.subplot(1, 4, 2)
plt.plot(tiempos[:], nice_angle(omegas))
plt.axhline(0, ls="--", color="lightgray")
#plt.xlim(0,vuelo1.tiempo_apogeo+10)
muestra_tiempos(tiempos, plt)
plt.title("Velocidad angular(omega)")

plt.subplot(1, 4, 3)
plt.plot(tiempos[:], nice_angle(accangs))
#plt.xlim(0,vuelo1.tiempo_apogeo+10)
muestra_tiempos(tiempos, plt)
plt.title("Aceleración angular")

plt.subplot(1, 4, 4)
plt.plot(tiempos[:],)
#plt.plot(tiempos[:], palancas[:,0],label= "comp x")
#plt.plot(tiempos[:], palancas[:,1],label="comp y")
#plt.plot(tiempos[:], palancas[:,2], label = "comp z")
plt.title("Componentes del brazo de momento")
plt.xlim(0,tiempo_apogeo+10)
muestra_tiempos(tiempos, plt)
#plt.legend()
#plt.show()


#GRAFICA 8. Angulos
plt.figure(figsize=(14,4))
plt.title("Ángulos en el tiempo")
plt.xlabel("Tiempo (s)")
plt.ylabel("Ángulo (grados º)")
plt.plot(tiempos[:], [normalize_angle(x) for x in np.rad2deg(thetas)], label = 'Ángulo de inclinación (theta)')#pitch
plt.plot(tiempos[:], [normalize_angle(x) for x in np.rad2deg(Gammas)], label = 'Ángulo de vuelo (gamma)')#FPA
plt.plot(tiempos[:], [normalize_angle(x) for x in np.rad2deg(Alphas)],label = 'Ángulo de ataque (alpha)')
if tiempo_apogeo is not None:
    plt.axvline(tiempo_apogeo, color="0.5")
plt.axhline(0, ls="--", color="gray")
plt.axhline(riel.angulo, ls="--", color="lightgray")
plt.axhline(-90, ls="--", color="lightgray")
#plt.xlim(0,tiempo_apogeo+20)
muestra_tiempos(tiempos, plt)
plt.legend()
# plt.xlim(0,100)
#plt.ylim(75,80.5)
# plt.show()

#GRAFICA 9. Variacion de masa
plt.figure()
plt.xlabel('Tiempo (s)')
plt.ylabel('Masa (kg)')
plt.title('Masa del cohete Xitle en el tiempo')
if tiempo_apogeo is not None:
    plt.xlim(0,tiempo_apogeo+5)
muestra_tiempos(tiempos, plt)
plt.plot(tiempos, masavuelo)
# plt.show()

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

'''
#################\
#ANIMACIONES
#ANIMACION 1. Trayectoria
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

def dib_cohete(x, y, ax):
    ax.clear()
    ax.set_xlim(-10, 110)
    ax.set_ylim(-10, 110)
    ax.set_title('Trayectoria del cohete')
    ax.plot(x, y, 'bo-')
def animar_cohete():
    fig, ax = plt.subplots()
    x = posiciones[:, 0]
    y = posiciones[:, 2]

    # Parámetros de la simulación
    num_frames = len(tiempos)  # número de frames de la animación
    velocidad_simulacion = 0.1  # velocidad de la simulación (segundos)

    def update(frame):
        ax.clear()
        ax.set_xlim(-10, 110)
        ax.set_ylim(-10, 110)
        ax.set_title('Trayectoria del cohete')
        ax.plot(x[:frame], y[:frame], 'bo-')
        dibujar_cohete(x[frame], y[frame], ax)
        return ax

    ani = animation.FuncAnimation(fig, update, frames=num_frames, interval=50, blit=True)
    plt.show()
'''