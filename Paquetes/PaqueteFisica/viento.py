# SCRIPT FINAL: Clase Viento3D - Version depurada

import numpy as np
import matplotlib.pyplot as plt

class Viento:
    def __init__(self, vel_base=4.0, vel_mean=1.0, vel_var=0.02, ang_base=0.0, var_ang=15.0):
        # Parametros viento base
        self.vel_base = vel_base              # Magnitud base del viento (m/s)
        self.dir_base = ang_base               # Direccion base en grados (horizontal)
        self.giro_base = 0.0                   # Inclinacion base (elevacion), en grados

        # Parametros viento variable
        self.vel_mean = vel_mean               # Media de la magnitud aleatoria
        self.vel_var = vel_var                 # Varianza de la magnitud aleatoria
        self.var_ang = var_ang                  # Varianza angular (dispersión en grados)

        # Valores actuales
        self.vector = None                     # Vector viento total [vx, vy, vz]
        self.magnitud_total = None             # Magnitud total actual
        self.direccion_total = None            # Direccion horizontal total actual (0-359)

    def random_values(self):
        self.magnitud_rafaga = np.random.normal(self.vel_mean, self.vel_var)
        self.direccion_rafaga = np.random.normal(self.dir_base, self.var_ang)
        self.giro_rafaga = np.random.uniform(0, 180)

    def actualizar_viento3D(self):
        self.random_values()

        # Vector base (viento constante)
        base = self.vel_base * np.array([
            np.cos(np.deg2rad(self.giro_base)) * np.cos(np.deg2rad(self.dir_base)),
            np.sin(np.deg2rad(self.giro_base)) * np.cos(np.deg2rad(self.dir_base)),
            np.sin(np.deg2rad(self.dir_base))
        ])

        # Vector rafagoso (perturbacion aleatoria)
        rafaga = self.magnitud_rafaga * np.array([
            np.cos(np.deg2rad(self.giro_rafaga)) * np.cos(np.deg2rad(self.direccion_rafaga)),
            np.sin(np.deg2rad(self.giro_rafaga)) * np.cos(np.deg2rad(self.direccion_rafaga)),
            np.sin(np.deg2rad(self.direccion_rafaga))
        ])

        # Suma de vectores
        self.vector = base + rafaga
        self.magnitud_total = np.linalg.norm(self.vector)

        # Calculo del angulo horizontal (XY)
        x = self.vector[0]
        z = self.vector[2]
        self.direccion_total = (np.rad2deg(np.arctan2(z, x))) % 360

    def __repr__(self):
        return f"Viento(magnitud={self.magnitud_total:.2f} m/s, direccion={self.direccion_total:.1f} grados)"


# =============================================================================
# Clases de Ráfagas (comentadas temporalmente)
# =============================================================================
"""
class Rafaga:
    def __init__(self, t_inicio, duracion, magnitud):
        self.t_inicio = t_inicio
        self.duracion = duracion
        self.magnitud = magnitud
        self.direccion = np.random.uniform(0, 360)

    def get_velocidad(self, t):
        if t < self.t_inicio or t > self.t_inicio + self.duracion:
            return 0, 0
        else:
            return self.magnitud, self.direccion

class RafagaEscalon(Rafaga):
    def get_velocidad(self, t):
        if t < self.t_inicio or t > self.t_inicio + self.duracion:
            return 0, 0
        else:
            return self.magnitud, self.direccion

class RafagaRampaLineal(Rafaga):
    def get_velocidad(self, t):
        if t < self.t_inicio:
            return 0, 0
        elif t > self.t_inicio + self.duracion:
            return self.magnitud, self.direccion
        else:
            velocidad = self.magnitud * (t - self.t_inicio) / self.duracion
            return velocidad, self.direccion

class Rafaga1Coseno(Rafaga):
    def get_velocidad(self, t):
        if t < self.t_inicio or t > self.t_inicio + self.duracion:
            return 0, 0
        else:
            velocidad = self.magnitud * (1 - np.cos(2 * np.pi * (t - self.t_inicio) / self.duracion)) / 2
            return velocidad, self.direccion
"""


# =============================================================================
# Prueba de variacion temporal del viento
# =============================================================================

if __name__ == "__main__":

    # Crear viento moderado-ligero
    viento = Viento(vel_base=4.0, vel_mean=1.0, vel_var=0.2, ang_base=0.0, var_ang=10.0)

    # Simular durante 120 segundos a 1 Hz
    tiempos = np.arange(0, 120, 1)
    magnitudes = []
    direcciones = []

    for t in tiempos:
        viento.actualizar_viento3D()
        magnitudes.append(viento.magnitud_total)
        direcciones.append(viento.direccion_total)

    # Graficar resultados
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

    ax1.plot(tiempos, magnitudes, label='Magnitud (m/s)')
    ax1.set_ylabel('Velocidad (m/s)')
    ax1.grid()
    ax1.legend()

    ax2.plot(tiempos, direcciones, label='Dirección (grados)', color='orange')
    ax2.set_ylabel('Dirección (°)')
    ax2.set_xlabel('Tiempo (s)')
    ax2.grid()
    ax2.legend()

    plt.suptitle('Variación del Viento (Moderado-Ligero)')
    plt.show()
