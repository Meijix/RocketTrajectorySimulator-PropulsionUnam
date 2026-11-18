# SCRIPT FINAL: Clase Viento3D - Version depurada

import numpy as np
import matplotlib.pyplot as plt

class Viento:
    """Viento horizontal con ráfagas.

    Ejes (los mismos del simulador): x apunta en la dirección horizontal hacia la que se
    inclina el riel (hacia donde vuela el cohete), y es la dirección horizontal
    perpendicular, z es la vertical.

    Dirección del viento (ang_base): ángulo, en grados y en el plano horizontal, de la
    dirección HACIA la que sopla el viento, medido desde el eje x:
          0°  viento de cola (empuja al cohete en su dirección de vuelo)
        180°  viento de frente
         90° / 270°  viento cruzado (hacia +y / hacia -y)
    Por ejemplo, 230° es un viento principalmente de frente con una parte cruzada.

    El viento se sortea cada dt_rafaga segundos y se interpola entre muestras:
        rapidez   = vel_base + ráfaga,  ráfaga ~ Normal(vel_mean, vel_var), nunca negativa
        dirección = Normal(ang_base, var_ang)   -> el viento cambia un poco de dirección
        la ráfaga se inclina además un ángulo Uniforme(-20°, 20°) respecto a la horizontal,
        lo que da una componente vertical pequeña y de media cero.
    El viento medio es entonces horizontal, de rapidez vel_base + vel_mean y dirección ang_base.

    Perfil con la altura (opcional): `perfil` es una lista de (altura sobre el sitio [m],
    rapidez [m/s], dirección [grados, misma convención]). Si se da, el viento base se
    interpola entre esos niveles según la altura del cohete, en lugar de ser constante
    (por debajo del primer nivel y por encima del último se usa el más cercano). Las
    ráfagas se suman igual.
    """
    ELEVACION_RAFAGA = 20.0   # inclinación máxima de la ráfaga respecto a la horizontal (grados)

    def __init__(self, vel_base=4.0, vel_mean=1.0, vel_var=0.02, ang_base=0.0, var_ang=15.0, dt_rafaga=1.0, semilla=None, perfil=None):
        # Parametros viento base
        self.vel_base = vel_base              # Rapidez base del viento (m/s)
        self.dir_base = ang_base               # Direccion base en grados (horizontal, hacia donde sopla, desde el eje x)

        # Parametros viento variable
        self.vel_mean = vel_mean               # Media de la rafaga (m/s), se suma a la rapidez base
        self.vel_var = vel_var                 # Desviacion estandar de la rafaga (m/s)
        self.var_ang = var_ang                  # Desviacion estandar de la direccion (grados)

        # Valores actuales
        self.vector = None                     # Vector viento total [vx, vy, vz]
        self.magnitud_total = None             # Magnitud total actual
        self.direccion_total = None            # Direccion horizontal total actual (0-359)

        # Serie temporal de rafagas (para que el viento sea funcion de t)
        self.dt_rafaga = dt_rafaga             # Intervalo entre muestras aleatorias de rafaga (s)
        self.semilla = semilla                 # None = rafagas distintas en cada simulacion
        self.rng = np.random.default_rng(semilla)
        self._muestras = []                    # (rafaga, desviacion de direccion, inclinacion) sorteadas en t = k*dt_rafaga

        # Perfil del viento base con la altura
        self.perfil = perfil
        if perfil:
            niveles = sorted(perfil)
            self._perfil_z = np.array([n[0] for n in niveles], dtype=float)
            angulos = np.deg2rad([n[2] for n in niveles])
            self._perfil_vx = np.array([n[1] for n in niveles]) * np.cos(angulos)
            self._perfil_vy = np.array([n[1] for n in niveles]) * np.sin(angulos)

    def random_values(self):
        """Sortea la ráfaga, la desviación de la dirección y la inclinación de la ráfaga."""
        self.magnitud_rafaga = self.rng.normal(self.vel_mean, self.vel_var)
        self.desviacion_direccion = self.rng.normal(0.0, self.var_ang)
        self.direccion_rafaga = self.dir_base + self.desviacion_direccion
        self.giro_rafaga = self.rng.uniform(-self.ELEVACION_RAFAGA, self.ELEVACION_RAFAGA)
        return np.array([self.magnitud_rafaga, self.desviacion_direccion, self.giro_rafaga])

    def viento_base(self, z=None):
        """Rapidez [m/s] y dirección [grados] del viento base a la altura z sobre el sitio."""
        if self.perfil and z is not None:
            vx = np.interp(z, self._perfil_z, self._perfil_vx)
            vy = np.interp(z, self._perfil_z, self._perfil_vy)
            rapidez = float(np.hypot(vx, vy))
            direccion = float(np.rad2deg(np.arctan2(vy, vx))) if rapidez > 1e-9 else self.dir_base
            return rapidez, direccion
        return self.vel_base, self.dir_base

    def _vector(self, muestra, z=None):
        """Vector de viento [vx, vy, vz]: viento base a la altura z más la ráfaga sorteada."""
        rafaga, desviacion, giro = muestra
        rapidez_base, direccion_base = self.viento_base(z)
        azimut = np.deg2rad(direccion_base + desviacion)
        elevacion = np.deg2rad(giro)
        horizontal = max(rapidez_base + rafaga * np.cos(elevacion), 0.0)
        vertical = rafaga * np.sin(elevacion)
        return np.array([horizontal * np.cos(azimut), horizontal * np.sin(azimut), vertical])

    def _fijar_vector(self, vector):
        self.vector = vector
        self.magnitud_total = np.linalg.norm(self.vector)
        # Direccion horizontal hacia la que sopla (plano XY), en grados desde el eje x
        self.direccion_total = (np.rad2deg(np.arctan2(self.vector[1], self.vector[0]))) % 360

    def reiniciar_rafagas(self):
        """Descarta la serie de rafagas al empezar una simulacion.

        Con semilla, cada simulacion repite exactamente la misma serie (reproducible);
        sin semilla, se sortea una serie nueva.
        """
        self._muestras = []
        if self.semilla is not None:
            self.rng = np.random.default_rng(self.semilla)

    def vector_en(self, t, z=None):
        """Viento total en el tiempo t (s) y, si hay perfil, a la altura z (m sobre el sitio).

        Las rafagas se sortean una sola vez cada dt_rafaga segundos y se interpolan
        linealmente entre muestras. Asi el viento es una funcion continua de t: da el
        mismo valor cada vez que se pide el mismo t, que es lo que necesitan los
        integradores (evaluan las derivadas varias veces por paso y pueden repetir pasos).
        Tambien actualiza self.vector, self.magnitud_total y self.direccion_total.
        """
        s = max(t, 0.0) / self.dt_rafaga
        k = int(s)
        while len(self._muestras) < k + 2:
            self._muestras.append(self.random_values())
        w = s - k
        muestra = (1 - w) * self._muestras[k] + w * self._muestras[k + 1]
        self._fijar_vector(self._vector(muestra, z))
        return self.vector

    def actualizar_viento3D(self):
        # Sorteo instantaneo (independiente del tiempo). La simulacion usa vector_en(t, z).
        self._fijar_vector(self._vector(self.random_values()))

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
    viento = Viento(vel_base=4.0, vel_mean=1.0, vel_var=0.2, ang_base=230.0, var_ang=2.0)

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
