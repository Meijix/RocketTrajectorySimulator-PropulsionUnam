#EN ESTE SCRIPT: CLASE ATMOSFERA Y FUNCION DE GRAVEDAD

import numpy as np
from numpy import *
import matplotlib.pyplot as plt

# Constantes universales
GravUn = 6.67430E-11  # m^3/kg/s^2 Constante de gravitación universal
Rg = 8.31447   #[J/(mol·K)] Constante universal de los gases
R_Tierra = 6371000 #[m] Radio de la Tierra
M_tierra = 5.972168e24  #[kg] Masa de la Tierra

def calc_gravedad(altura_z):
  return GravUn * M_tierra / (altura_z + R_Tierra)**2

#Calcular la gravedad en la superficie
g0 = calc_gravedad(0)
print("Gravedad en el suelo: ",g0, "[m/s^2]")

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
        return None

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
        rho = rho0 * (T/T0)**(-g0/(L*self.Rg))
        presion = P0 * (T/T0)**(-g0/(L*self.Rg)-1)

      cs = np.sqrt(self.cp*self.Rg*T)

      return (T, rho, presion, cs)


#Creacion del objeto
atm_actual = atmosfera()
T, rho, presion, cs = atm_actual.calc_propiedades(10000)
print("Propiedades atmosfericas a 10 km")
print("Temperatura: ",T,"[K]", T-273.15,"[grados]")
print("Densidad: ",rho, "[]")
print("Presion: ",presion,"[Pa]")
print("Vel del sonido:",cs, "[m/s^2]")