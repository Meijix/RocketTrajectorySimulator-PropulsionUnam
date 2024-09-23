import numpy as np

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


# Simulación
estado = np.array([z0, v0])