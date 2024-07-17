#Simulacion CON paracaidas del Xitle2
from Xitle import *
from Vuelo import *
from Integradores import *
# Estado inicial
x0, y0, z0 = 0, 0, 0
vx0, vy0, vz0 = 0, 0, 0
theta0, omega0 = np.deg2rad(riel.angulo), 0
estado=np.array([x0, y0, z0, vx0, vy0, vz0, theta0, omega0])

#Parametros de la simulacion
dt=0.01 #[s]
t_max = 600 #[s]

Mainchute = Parachute(1.2, 0.802) #Crear paracaidas principal
#print(Xitle.parachute_active1)
Xitle.agregar_paracaidas(Mainchute)
#print(Xitle.parachute_active1)
#print(Xitle.parachute_added)
#como le hago para agregar dos paracaidas??? el drogue y el main
vuelo_paracaidas = Vuelo(Xitle,atm_actual,viento_actual)
tiempos, sim, CPs, CGs, masavuelo = vuelo_paracaidas.simular_vuelo(estado,t_max, dt)

Tvecs, Dvecs, Nvecs, accels, palancas, accangs, Gammas, Alphas, torcas, Cds, Machs, vientomags, vientodirs = vuelo_paracaidas.calc_cantidades_secundarias(tiempos, sim)
posiciones = np.array([state[0:3] for state in sim])
velocidades = np.array([state[3:6] for state in sim])
thetas = np.array([state[6] for state in sim])
omegas = np.array([state[7] for state in sim])

#print(tiempo)
#print(posiciones)
print("Tiempo de salida del riel [s]",vuelo_paracaidas.tiempo_salida_riel)
print("Tiempo de MECO [s]",Xitle.t_MECO)
print("Tiempo de apogeo [s]",vuelo_paracaidas.tiempo_apogeo)
print("Tiempo de impacto [s]",vuelo_paracaidas.tiempo_impacto)


max_altitude = max(posiciones[:, 2])
max_speed = max(np.linalg.norm(velocidades, axis=1))

print("APOGEO:", max_altitude, "metros")
print("Máxima velocidad:", max_speed, "m/s")
print("Equivalente a:",max_speed/340, "Mach")