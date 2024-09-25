#En este SCRIPT: Clase Viento2D
import random
import numpy as np
from numpy import *
import matplotlib.pyplot as plt
import matplotlib.animation as animation

class Viento:

    def __init__(self, vel_base= 10, vel_mean=3, vel_var=0.02):
        
        #Parametros viento base
        self.vel_base = vel_base
        self.dir_base = 180 #0--de izquierda a der, 180-- der hacia izquierda
        self.giro_base = 0 #El vector base esta en el plano XY
        
        #Parametros viento variable
        self.vel_mean = vel_mean
        self.vel_var = vel_var

        #Valores aleatorios generados
        self.magnitud = None
        self.direccion = None
        self.giro = None

        self.vector_base = None
        self.vector_rafagoso = None
        self.vector = None
        ###################
    def random_values(self):
        self.magnitud = random.normal(self.vel_mean, self.vel_var)
        self.direccion = random.uniform(-45, 45) #kappa
        #self.direccion = random.rand(0,180)
        self.giro = random.uniform(0,180) #phi
        #self.angulo = random.uniform(0,180)
        #Elegir hacia que lado sopla con 0.5 de probabilidad
        #if (random.random() >= 0.5):
        #  self.direccion *= -1


    def actualizar_viento2D(self):
        self.random_values()
        self.vector_base = self.vel_base * np.array([np.cos(np.deg2rad(self.dir_base)),0, np.sin(np.deg2rad(self.dir_base))])
        self.vector_rafagoso = self.magnitud * np.array([np.cos(np.deg2rad(self.direccion)),0, np.sin(np.deg2rad(self.direccion))])
        self.vector = self.vector_base + self.vector_rafagoso

    def actualizar_viento3D(self):
        self.random_values()
        self.vector_base = self.vel_base * np.array([np.cos(self.giro_base)*np.cos(self.dir_base), np.sin(self.giro_base)*np.cos(self.dir_base) , np.sin(self.dir_base)])
        self.vector_rafagoso = self.magnitud * np.array([np.cos(self.giro)*np.cos(self.direccion), np.sin(self.giro)*np.cos(self.direccion) , np.sin(self.direccion)])

        ###DEBUG: No agregar viento rafagoso
        self.vector = self.vector_base #+ self.vector_rafagoso

    def __repr__(self):
        return f"Viento(magnitud={self.vel_base+self.magnitud}, direccion={self.dir_base+self.direccion})"




##################################################################################

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

#Falta funcion que actualiza el viento
#def update_viento(self, gust_type, magnitude, duration, t_init, t_fin):

    #return viento_variation, time
    

if __name__ == "__main__":
    #Creacion del viento actual de prueba
    viento = Viento(vel_base= 10, vel_mean=3, vel_var=0.2)
    #viento.actualizar_viento2D()

    viento.actualizar_viento3D()
    print("Vector 1 de viento:")
    print(viento)
    print(viento.vector) 

    viento.actualizar_viento3D()
    print("Vector 2 de viento:")
    print(viento)
    print(viento.vector)  
        
    #Descomentar para graficar el vector viento 
    # Get the x and z components of the wind vector
    vx = viento.vector[0]
    vz = viento.vector[2]

    # Create a plot
    fig, ax = plt.subplots()

    # Plot the wind vector as an arrow
    ax.arrow(0, 0, vx, vz, head_width=0.5, head_length=0.5, color='r', zorder=10)

    # Set the limits of the plot
    ax.set_xlim([-15, 15])
    ax.set_ylim([-15, 15])

    # Add labels and title
    ax.set_xlabel('x (m)')
    ax.set_ylabel('z (m)')
    ax.set_title('Vector de viento')

    # Show the plot
    plt.show()

    '''

    ############################
    # Ejemplo de uso de rafagas
    rafaga_escalon = RafagaEscalon(t_inicio=2, duracion=4, magnitud=5)
    rafaga_rampa = RafagaRampaLineal(t_inicio=2, duracion=4, magnitud=5)
    rafaga_coseno = Rafaga1Coseno(t_inicio=2, duracion=4, magnitud=5)

    tiempos = np.linspace(0, 12, 100)
    velocidades_escalon = [rafaga_escalon.get_velocidad(t)[0] for t in tiempos]
    velocidades_rampa = [rafaga_rampa.get_velocidad(t)[0] for t in tiempos]
    velocidades_coseno = [rafaga_coseno.get_velocidad(t)[0] for t in tiempos]

    print(velocidades_escalon)
    print(velocidades_rampa)
    print(velocidades_coseno)

    plt.plot(tiempos, velocidades_escalon, label='Escalón')
    plt.plot(tiempos, velocidades_rampa, label='Rampa Lineal')
    plt.plot(tiempos, velocidades_coseno, label='1-Coseno')
    plt.xlabel('Tiempo (s)')
    plt.ylabel('Velocidad de la ráfaga (m/s)')
    plt.title('Ráfagas de viento')
    plt.legend()
    plt.grid(True)
    plt.show()

    #con que frecuencia se tiene que implementar en la simulacion completa
    #para juntar el viento y rafagas se multiplica el vector viento unitario 
    # por la magnitud de la velocidad de la rafaga?
    # Direcciones de las ráfagas
    direcciones = [rafaga_escalon.direccion, rafaga_rampa.direccion, rafaga_coseno.direccion]

    # Gráfico de las direcciones
    plt.figure(figsize=(8, 6))
    ax = plt.subplot(111, polar=True)
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)
    bars = ax.bar(np.deg2rad(direcciones), [1]*len(direcciones), width=0.5, bottom=0.0)

    # Etiquetas y título
    plt.title('Rosa de los vientos de las ráfagas')
    ax.set_xticklabels(['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'])

    # Mostrar el gráfico
    plt.show()

    ###################
    # Simulación de viento con ráfagas
    dt = 0.1
    tiempo_total = 50
    tiempos = np.arange(0, tiempo_total, dt)

    # Lista para almacenar los vectores de viento en cada instante de tiempo
    vectores_viento = []

    # Viento base
    viento_base = Viento2D(vel_mean=1, vel_var=0.05)

    # Ráfagas
    rafagas = [
        RafagaEscalon(t_inicio=0, duracion=4, magnitud=5),
        RafagaRampaLineal(t_inicio=15, duracion=3, magnitud=8),
        Rafaga1Coseno(t_inicio=22, duracion=2, magnitud=3)
    ]

    # Simulación
    for t in tiempos:
        vector_viento = viento_base.vector.copy()
        for rafaga in rafagas:
            magnitud_rafaga, direccion_rafaga = rafaga.get_velocidad(t)
            vector_rafaga = magnitud_rafaga * np.array([np.cos(np.deg2rad(direccion_rafaga)), 0, np.sin(np.deg2rad(direccion_rafaga))])
            vector_viento += vector_rafaga
        vectores_viento.append(vector_viento)

    plt.plot(tiempos, np.array(vectores_viento)[:, 0])
    plt.xlabel('Tiempo (s)')
    plt.ylabel('Velocidad del viento (m/s)')
    plt.title('Simulación de viento con ráfagas')
    plt.grid(True)

    plt.show()
    #se debe apagar la rafaga cuando no este activada y regresar al viento normal
    #agregar boolean de rafaga_activa
    '''


