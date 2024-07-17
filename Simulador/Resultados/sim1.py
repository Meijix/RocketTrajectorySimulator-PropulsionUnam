#Simulacion sin paracaidas del Xitle2
from Simulador.Xitle import *
from sim1 import *
from Listas_results import *



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

vuelo1 = Vuelo(Xitle,atm_actual,viento_actual)
tiempos, sim, CPs, CGs, masavuelo = vuelo1.simular_vuelo(estado,t_max, dt)

Tvecs, Dvecs, Nvecs, accels, palancas, accangs, Gammas, Alphas, torcas, Cds, Machs, vientomags, vientodirs = vuelo1.calc_cantidades_secundarias(tiempos, sim)

posiciones = np.array([state[0:3] for state in sim])
velocidades = np.array([state[3:6] for state in sim])
thetas = np.array([state[6] for state in sim])
omegas = np.array([state[7] for state in sim])

#print(tiempo)
#print(posiciones)
print(vuelo1.tiempo_salida_riel)
print(vuelo1.tiempo_apogeo)
print(vuelo1.tiempo_impacto)