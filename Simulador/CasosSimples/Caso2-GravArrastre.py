#Caso 2: Gravedad + Arrastre cuadratico y masa cte

import numpy as np
import matplotlib.pyplot as plt
#from scipy.integrate import odeint
from IntegradoresCasos import *


def der_gravedad_arrastre(t, state):
    _, v = state
    Drag = (D_mag/m)* (v**2) *np.sign(v)
    derivs = np.array((v, -g - Drag))
    #print(derivs)
    return derivs
import numpy as np

def sol_analitica_gravedad_arrastre(z0, v0, t, m, g, D_mag):
    k = np.sqrt(g * D_mag / m)
    
    v = (v0 + (g / k)) * np.exp(-k * t) - (g / k)
    z = z0 + (v0 + (g / k)) * (1 - np.exp(-k * t)) / k - g * t / k
    
    return z, v

def simular_dinamica(estado, t_max, dt):
    #print(estado)
    t = 0.0
    it = 0
    #########################################
    #CAMBIO DE METODO DE INTEGRACIÓN
    Integracion = Euler(der_gravedad_arrastre) #ocupa dt=0.005
    #Integracion = RungeKutta4(der_gravedad_arrastre) #ocupa dt=0.1
    # Integracion = RKF45(der_gravedad_arrastre)
    #Integracion = RungeKutta2(der_gravedad_arrastre)
    ##########################################
    
    sim=[estado] #lista de estados de vuelo
    tiempos=[0] #lista de tiempos
    while t < t_max:
        #print(t)
        # Integracion numérica del estado actual
        #el dt_new se usa para que el inetgrador actualize el paso de tiempo
        nuevo_estado = Integracion.step(t, estado, dt)
        # nuevo_estado, dt_new = Integracion.step(t, estado, dt, tol=1e-5)
        # print(dt_new)
        # dt = dt_new
        #print(dt_new,dt)
        #print("dt= ", dt)

        # Avanzar estado
        it += 1
        t += dt
        estado = nuevo_estado

        sim.append(estado)
        tiempos.append(t)

        #Indicar el avance en la simulacion
        if it%500==0:
            print(f"Iteracion {it}, t={t:.1f} s, altitud={estado[0]:.1f} m, vel vert={estado[1]:.1f}")
        
        if estado[0] < 0:
            break

    return tiempos, sim



#Solucion de ese caso
# Estado inicial
z0 = 0
v0 = 80

#no afecta la masa la dinamica
m = 5.0 #masa cte
g = 9.81 #Aceleracion de gravedad cte
rho = 1.225
A = 1
cd = 0.45
D_mag = 0.5 * cd * A * rho

estado=np.array([z0, v0])
#print(estado)

#Parametros de la simulacion
dt = 0.01 #0.1 #[s]
t_max = 80 #[s]
divisiones = t_max+1

#Simulacion
tiempos, simulacion = simular_dinamica(estado, t_max, dt)

pos_simul = [sim[0] for sim in simulacion]
vel_simul = [sim[1] for sim in simulacion]

#Solucion analitica
pos_analitica = []
vel_analitica = []

for t in tiempos:
    pos, vel = sol_analitica_gravedad_arrastre(z0, v0, t, m, g, D_mag)
    pos_analitica.append(pos)
    vel_analitica.append(vel)

#print(pos_analitica, pos_simul)
#print(vel_analitica, vel_simul)
#print(tiempos)

#Graficar
plt.figure(figsize=(8, 6))
plt.scatter(tiempos, pos_simul, label='Numérica', color="C1")
plt.plot(tiempos, pos_analitica, label='Analitica', ls='-')
plt.title('Posición vertical [m/s]')
plt.xlabel('Tiempo [s]')
plt.ylabel('Posicion [m]')
plt.legend()

plt.figure(figsize=(8, 6))
plt.scatter(tiempos, vel_simul, label="Numérica", color="C1")
plt.plot(tiempos, vel_analitica, label='Analitica', ls='-')
plt.title('Velocidad vertical [m/s]')
plt.xlabel('Tiempo [s]')
plt.ylabel('Velocidad [m/s]')
plt.legend()

plt.show()


#Calcular y graficar el error numerico
#error en metros
error_pos = [pos_simul[i] - pos_analitica[i] for i in range(len(tiempos))]
error_vel = [vel_simul[i] - vel_analitica[i] for i in range(len(tiempos))]

#error relativo
error_pos_rel = [abs(error_pos[i]/pos_analitica[i]) for i in range(len(tiempos))]
error_vel_rel = [abs(error_vel[i]/vel_analitica[i]) for i in range(len(tiempos))]

plt.figure(figsize=(8, 6))
plt.plot(tiempos, error_pos, label='Error z(t)')
plt.plot(tiempos, error_vel, label='Error v(t)')
plt.title("Error absoluto")
plt.xlabel('Tiempo [s]')
plt.ylabel('Errorres absolutos [m],[m/s]')
plt.legend()

plt.figure(figsize=(8, 6))
plt.plot(tiempos, error_pos_rel, label='Error z(t)')
plt.plot(tiempos, error_vel_rel, label='Error v(t)')
plt.title("Error relativo")
plt.xlabel('Tiempo [s]')
plt.ylabel('Errores relativos')
plt.legend()

plt.show()

