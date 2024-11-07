#EN ESTE SCRIPT: CLASE ATMOSFERA

import numpy as np
from numpy import *
import matplotlib.pyplot as plt

#Archivos importados
from Simulador.utils.funciones import *

class atmosfera:

    def __init__(self):

      # Constantes
      self.M = 0.0289644 #[kg/mol] Masa molar del aire
      self.cp = 1.4 #Relación de calor especifico
      self.Rg = 287.05287; #[J/K kg] constante gaseosa del aire

      # Capas de la atmósfera
      self.capas = {
        0: (0, 101325, 288.15, 340.29,1.225,-0.0065),#Troposfera
        1: (11000, 22632, 216.65, 295.31,0.3639,0.0), #Tropopausa
        2: (20000, 5474.9, 216.65, 295.31,0.088,0.001), #Estratosfera
        3: (32000, 868.02, 228.65, 296.82,0.0132,0.0028),
        4: (47000, 110.91, 270.65, 294.15,0.002, 0.0),#Estratopausa
        5: (51000, 66.939, 270.65, 294.15,0.002, -0.0028),#Mesosfera
        6: (71000, 3.9564, 214.65, 294.15,0.002, -0.002),
        7: (84852, 0.3734, 186.87, 294.15,0.0, 0.0),#Mesopausa
      }

      # Alturas límite de las capas
      self.h_limite = [0, 11000, 20000, 32000, 47000, 51000, 71000, 84852]

      self.h_max = self.h_limite[-1]

    def altitud_geopot(self, altura_z):
      return (R_Tierra * altura_z)/(R_Tierra+altura_z)

    def determinar_capa(self, altura_z):

      h = self.altitud_geopot(altura_z)

      # Retornar None si estamos más arriba de la última capa o negativa
      if h > self.h_limite[-1]:
        print("Fuera de la atmósfera")
        return None

      # Determina la capa en la que se encuentra la altura h
      for i in range(len(self.capas)-1):
        if h <= self.h_limite[i + 1]:
          capa = self.capas[i]
          return capa

    def calc_propiedades(self, altura_z):

      h = self.altitud_geopot(altura_z)

      capa = self.determinar_capa(altura_z)
      if capa is None:
        return self.capas[7] #los valores de la ultima capa

      # Calcula los valores
      #capa[0]: Altura geopotencial h
      #capa[1]: Presión base de la capa
      #capa[2]: Temperatura base de la capa
      #capa[3]: Velocidad del sonido en la base de la capa
      #capa[4]: Densidad base de la capa
      #capa[5]: Gradiente adiabatico
      h0 = capa[0]
      P0 = capa[1]
      T0 = capa[2]
      C0 = capa[3]
      rho0 = capa[4]
      L = capa[5]

      if L == 0:
        T = T0
        rho = rho0*np.exp((-g0/(self.Rg*T))*(h-h0))
        presion = P0 * np.exp((-g0/(self.Rg*T))*(h-h0))
      else:
        T = T0 + L*(h-h0)
        rho = rho0 * (T/T0)**(-g0/(L*self.Rg)-1)
        presion = P0 * (T/T0)**(-g0/(L*self.Rg))

      cs = np.sqrt(self.cp*self.Rg*T)

      return (T, rho, presion, cs)



if __name__ == "__main__":
  #Creacion del objeto
  atmosfera_prueba = atmosfera()
  #Propiedades a 10 km
  T, rho, presion, cs = atmosfera_prueba.calc_propiedades(10000)
  print("Propiedades atmosfericas a 10 km")
  print("Temperatura: ",T,"[K]", T-273.15,"[grados]")
  print("Densidad: ",rho, "[]")
  print("Presion: ",presion,"[Pa]")
  print("Vel del sonido:",cs, "[m/s^2]")

  #Graficar propiedades hasta 10 km
  alturas = np.linspace(0,80000,100)
  temperaturas = []
  densidades = []
  presiones = []
  velocidades = []
  
  for altura in alturas:
    T, rho, presion, cs = atmosfera_prueba.calc_propiedades(altura)
    temperaturas.append(T)
    densidades.append(rho)
    presiones.append(presion)
    velocidades.append(cs)

  fig, ax = plt.subplots(2, 2, figsize=(8, 6))

  ax[0, 0].plot(temperaturas, alturas, label="Temperatura")
  ax[0, 0].set_title("Temperatura")
  ax[0, 0].set_xlabel("Temperatura (K)")
  ax[0, 0].set_ylabel("Altura (m)")

  ax[0, 1].plot(velocidades, alturas, label="Velocidad del sonido")
  ax[0, 1].set_title("Velocidad del sonido")
  ax[0, 1].set_xlabel("Velocidad del sonido (m/s)")
  ax[0, 1].set_ylabel("Altura (m)")

  ax[1, 0].plot(densidades, alturas, label="Densidad")
  ax[1, 0].set_title("Densidad")
  ax[1, 0].set_xlabel("Densidad")
  ax[1, 0].set_ylabel("Altura (m)")

  ax[1, 1].plot(presiones, alturas, label="Presión")
  ax[1, 1].set_title("Presión")
  ax[1, 1].set_xlabel("Presión (Pa)")
  ax[1, 1].set_ylabel("Altura (m)")

  # Agregar líneas horizontales para las capas de la atmósfera
  for i in range(2):
    for j in range(2):
      for h in atmosfera_prueba.h_limite:
        ax[i, j].axhline(h, color='gray', linestyle='--')

  plt.show()