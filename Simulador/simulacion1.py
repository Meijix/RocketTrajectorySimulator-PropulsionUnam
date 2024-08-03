#Simulacion sin paracaidas del Xitle2
from Xitle import *
from Vuelo import *
from Integradores import *

#quitar el paracaidas
Xitle.parachute_added = False
#desactivar el paracaidas
Xitle.parachute_active1 = False

# Estado inicial
x0, y0, z0 = 0, 0, 0
vx0, vy0, vz0 = 0, 0, 0
theta0, omega0 = np.deg2rad(riel.angulo), 0
estado=np.array([x0, y0, z0, vx0, vy0, vz0, theta0, omega0])

#Parametros de la simulacion
dt=0.01 #[s]
t_max = 600 #[s]

#t=0
#it = 0

#Iniciar viento
viento_actual = Viento2D(vel_mean=10, vel_var=0.2)

vuelo1 = Vuelo(Xitle,atm_actual,viento_actual)
tiempos, sim, CPs, CGs, masavuelo = vuelo1.simular_vuelo(estado,t_max, dt)

Tvecs, Dvecs, Nvecs, accels, palancas, accangs, Gammas, Alphas, torcas, Cds, Machs, vientomags, vientodirs = vuelo1.calc_cantidades_secundarias(tiempos, sim)

posiciones = np.array([state[0:3] for state in sim])
velocidades = np.array([state[3:6] for state in sim])
thetas = np.array([state[6] for state in sim])
omegas = np.array([state[7] for state in sim])

#print(tiempo)
#print(posiciones)
print("Tiempo de salida del riel [s]",vuelo1.tiempo_salida_riel)
print("Tiempo de MECO [s]",Xitle.t_MECO)
print("Tiempo de apogeo [s]",vuelo1.tiempo_apogeo)
print("Tiempo de impacto [s]",vuelo1.tiempo_impacto)


max_altitude = max(posiciones[:, 2])
max_speed = max(np.linalg.norm(velocidades, axis=1))

print("APOGEO:", max_altitude, "metros")
print("Máxima velocidad:", max_speed, "m/s")
print("Equivalente a:",max_speed/340, "Mach")