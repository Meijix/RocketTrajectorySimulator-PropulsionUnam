#EN ESTE SCRIPT: CLASE ATMOSFERA

import numpy as np
import matplotlib.pyplot as plt


# Constantes universales
GravUn = 6.67430E-11  # m^3/kg/s^2 Constante de gravitación universal
R_Tierra = 6371000 #[m] Radio de la Tierra
M_tierra = 5.972168e24  #[kg] Masa de la Tierra


# Gravedad estándar con la que está definida la ISA (equilibrio hidrostático en altura geopotencial)
g0 = 9.80665  #[m/s^2]

class atmosfera:
    """Atmósfera estándar (ISA) por capas, ajustable al sitio y al día del lanzamiento.

    Sin argumentos es la ISA al nivel del mar. Para un lanzamiento real:

        altitud_sitio   altitud del sitio de lanzamiento sobre el nivel del mar (m). La
                        altura z del simulador se mide desde el sitio, así que las
                        propiedades se evalúan en z + altitud_sitio.
        delta_T         diferencia de temperatura respecto a la ISA (K), la misma a toda
                        altura ("ISA + delta_T"). Un día caluroso tiene delta_T > 0.
        presion_sitio   presión medida en el sitio (Pa). Si no se da, se usa la de la ISA
                        a esa altitud.

    La presión se obtiene integrando el equilibrio hidrostático desde el sitio con el
    perfil de temperatura ISA + delta_T, y la densidad con la ecuación de gas ideal.
    """

    def __init__(self, altitud_sitio=0.0, delta_T=0.0, presion_sitio=None):

      # Constantes
      self.M = 0.0289644 #[kg/mol] Masa molar del aire
      self.cp = 1.4 #Relación de calor especifico
      self.Rg = 287.05287; #[J/K kg] constante gaseosa del aire

      # Capas de la atmósfera estándar:
      # (altura geopotencial base [m], presión base [Pa], temperatura base [K],
      #  velocidad del sonido base [m/s], densidad base [kg/m3], gradiente de temperatura [K/m])
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

      # Condiciones del sitio y del día
      self.altitud_sitio = altitud_sitio
      self.delta_T = delta_T
      # Altura máxima de vuelo (sobre el sitio) hasta la que está definida la atmósfera
      self.h_max = self.h_limite[-1] - altitud_sitio

      # Presión de referencia: la del sitio, a la altura geopotencial del sitio
      self._h_ref = self.altitud_geopot(altitud_sitio)
      self._p_ref = 1.0
      p_isa_sitio = self._presion_desde(0.0, 101325.0, self._h_ref, delta_T=0.0)
      self.presion_sitio = p_isa_sitio if presion_sitio is None else presion_sitio
      self._p_ref = self.presion_sitio

    def altitud_geopot(self, altura_z):
      return (R_Tierra * altura_z)/(R_Tierra+altura_z)

    def _capa(self, h):
      """Índice de la capa que contiene la altura geopotencial h."""
      for i in range(len(self.h_limite) - 1):
        if h <= self.h_limite[i + 1]:
          return i
      return len(self.h_limite) - 2

    def _temperatura(self, h, delta_T=None):
      """Temperatura ISA + delta_T a la altura geopotencial h."""
      delta_T = self.delta_T if delta_T is None else delta_T
      capa = self.capas[self._capa(h)]
      return capa[2] + capa[5] * (h - capa[0]) + delta_T

    def _presion_desde(self, h_a, p_a, h_b, delta_T=None):
      """Presión en h_b integrando el equilibrio hidrostático desde (h_a, p_a), capa por capa."""
      delta_T = self.delta_T if delta_T is None else delta_T
      sentido = 1 if h_b >= h_a else -1
      h, p = h_a, p_a
      while h != h_b:
        i = self._capa(h + sentido * 1e-9)
        base, techo = self.h_limite[i], self.h_limite[i + 1]
        h_sig = min(h_b, techo) if sentido > 0 else max(h_b, base)
        if h_sig == h:
          # Fuera del rango de las capas (por debajo de 0 m o por encima de la última):
          # se extrapola con la capa del extremo
          h_sig = h_b
        L = self.capas[i][5]
        T1, T2 = self._temperatura(h, delta_T), self._temperatura(h_sig, delta_T)
        if L == 0:
          p *= np.exp(-g0 * (h_sig - h) / (self.Rg * T1))
        else:
          p *= (T2 / T1) ** (-g0 / (L * self.Rg))
        h = h_sig
      return p

    def determinar_capa(self, altura_z):
      """Capa ISA a la altura z sobre el sitio (None si está por encima de la atmósfera definida)."""
      h = self.altitud_geopot(altura_z + self.altitud_sitio)
      if h > self.h_limite[-1]:
        return None
      return self.capas[self._capa(h)]

    def calc_propiedades(self, altura_z):
      """Temperatura [K], densidad [kg/m3], presión [Pa] y velocidad del sonido [m/s] a la altura z sobre el sitio."""
      h = self.altitud_geopot(altura_z + self.altitud_sitio)
      h = min(h, self.h_limite[-1])        # por encima de la última capa se usan sus valores

      T = self._temperatura(h)
      presion = self._presion_desde(self._h_ref, self._p_ref, h)
      rho = presion / (self.Rg * T)
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