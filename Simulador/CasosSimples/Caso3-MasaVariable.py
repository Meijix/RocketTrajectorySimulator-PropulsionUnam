# Caso 3: Gravedad + Empuje constante y masa variable

import numpy as np
import matplotlib.pyplot as plt
from Integradores import *

# Función para la masa variable
def masa_variable(t, m0, beta):
    return m0 * np.exp(-beta * t)

# Función para la derivada del sistema
def der_gravedad_empuje_masa_var(t, state):
    z, v = state
    m = masa_variable(t, m0, beta)
    F_empuje = F0
    Drag = (D_mag/m) * (v**2)
    derivs = np.array((v, F_empuje/m - g - Drag))
    return derivs

# Función para la solución analítica
def sol_analitica_gravedad_empuje_masa_var(z0, v0, t, m0, beta, F0):
    m = masa_variable(t, m0, beta)
    v = v0 + (F0/m0) * (1 - np.exp(-beta * t)) - g * t
    z = z0 + v0 * t + (F0/(2*m0*beta)) * (1 - np.exp(-2*beta * t)) - (g/2) * t**2
    return z, v



def simular_dinamica(estado, t_max, dt):
    #print(estado)
    t = 0.0
    it = 0
    #########################################
    #CAMBIO DE METODO DE INTEGRACIÓN
    # Integracion = Euler(der_gravedad_masa_cte) #ocupa dt=0.005
    Integracion = RungeKutta4(der_gravedad_empuje_masa_var) #ocupa dt=0.1
    # Integracion = RKF45(der_gravedad_masa_cte)
    #Integracion = RungeKutta2(self.fun_derivs)
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


# Parámetros del sistema
m0 = 5.0  # masa inicial
beta = 0.1  # tasa de cambio de masa
F0 = 10.0  # empuje constante
g = 9.81  # aceleración de gravedad
rho = 1.225
A = 1
cd = 0.45
D_mag = 0.5 * cd * A * rho

# Estado inicial
z0 = 0
v0 = 80

# Parámetros de la simulación
dt = 0.01  # paso de tiempo
t_max = 80  # tiempo máximo
divisiones = t_max + 1

# Simulación
estado = np.array([z0, v0])
tiempos, simulacion = simular_dinamica(estado, t_max, dt)

pos_simul = [sim[0] for sim in simulacion]
vel_simul = [sim[1] for sim in simulacion]

# Solución analítica
pos_analitica = []
vel_analitica = []

for t in tiempos:
    pos, vel = sol_analitica_gravedad_empuje_masa_var(z0, v0, t, m0, beta, F0)
    pos_analitica.append(pos)
    vel_analitica.append(vel)

# Graficar
plt.figure(figsize=(8, 6))
plt.scatter(tiempos, pos_simul, label='Numérica', color="C1")
plt.plot(tiempos, pos_analitica, label='Analitica', ls='-')
plt.title('Posición vertical [m/s]')
plt.xlabel('Tiempo [s]')
plt.ylabel('Posición [m]')
plt.legend()

plt.figure(figsize=(8, 6))
plt.scatter(tiempos, vel_simul, label="Numérica", color="C1")
plt.plot(tiempos, vel_analitica, label='Analitica', ls='-')
plt.title('Velocidad vertical [m/s]')
plt.xlabel('Tiempo [s]')
plt.ylabel('Velocidad [m/s]')
plt.legend()

plt.show()