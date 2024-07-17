import numpy as np
from numpy import *
import matplotlib.pyplot as plt
class Componente:
    def __init__(self, nombre, masa, posicion):
        self.nombre = nombre
        self.masa = masa
        self.posicion = posicion # Se refiere a la posicion de la parte frontal del component en el sistema de coordenadas del cohete
        self.CG = None
        self.CP = None
        self.Ix = 0     # Momento de inercia en torno a un eje "horizontal" (perpendicular al eje longitudinal) que pasa por el CG del componente


# Cilindro con la punta hacia arriba
class Cono(Componente):

    # Las coordenadas locales se miden desde la punta hacia abajo
    def __init__(self, nombre, masa, posicion, longitud, diametro, geometria):
        super().__init__(nombre, masa, posicion)  # Solo se pasan 3 argumentos a la clase base
        self.long = longitud
        self.bottom = self.posicion + self.long
        self.diam = diametro
        self.geom = geometria
        self.rad = self.diam/2
        self.CG = None
        self.CP = None
        self.CN = None
        self.Ix = None
        self.calc_CG()
        self.calc_CP()
        self.calc_Ix()

    # Posicioón del centro de gravedad en coordenadas locales
    def calc_CG(self):
      self.CG = np.array((0.0, 0.0, (3/4) * self.long))

    # Calcula centro de presión en coordenadas locales
    def calc_CP(self):
      # Coeficientes de presión aerodinámica
      if self.geom == "conica":
        k = 2/3
      elif self.geom == "ogiva":
        k = 0.466
      elif self.geom == "parabolica":
        k = 0.5
      elif self.geom == "eliptica":
        k = 0.333
      else:
        raise Exception("Error: geometría '{}' no está en la lista".format(self.geom))
      self.CP = np.array((0.0, 0.0, k * self.long))
      self.CN = 2.0

    # Calcula momento de inercia con respecto a su centro de gravedad
    def calc_Ix(self):
      self.Ix = self.masa * ((3/20)*self.rad**2+(3/80)*self.long**2)

class Cilindro(Componente):

    def __init__(self, nombre, masa, posicion, longitud, diametroexterior, diametrointerior):
        super().__init__(nombre, masa, posicion)  # Solo se pasan 3 argumentos a la clase base
        self.long = longitud #Longitud del tubo
        self.bottom = self.posicion + self.long
        self.diam_ext = diametroexterior #Diametro exterior del tubo
        self.diam_int = diametrointerior #Diametro interior del tubo
        self.rad_ext = self.diam_ext/2
        self.rad_int = self.diam_int/2
        self.CG = None
        self.CP = None
        self.CN = None
        self.Ix = None
        self.calc_CG()
        self.calc_CP()
        self.calc_Ix()

    def calc_CG(self):
      self.CG = np.array((0.0, 0.0, (1/2) * self.long))

    def calc_CP(self):
      self.CP = np.array((0.0, 0.0, 0.0))
      self.CN = 0

    def calc_Ix(self):
      self.Ix = (1/12) * self.masa * ((3*(self.rad_int**2 + self.rad_ext**2)) + self.long**2)


class Aletas(Componente): #Incluye el arreglo de aletas completo

    def __init__(self, nombre, masa, posicion, diametro, numf, semispan, C_r, C_t, X_R,mid_sweep):
        super().__init__(nombre, masa, posicion)  # Solo se pasan 3 argumentos a la clase base

        self.diam_fus = diametro
        self.rad_fus = self.diam_fus/2

        self.numf = numf             #[1] Numero de Aletas
        self.semispan = semispan     #[m] Fin semi span
        self.span = self.semispan  # son lo mismo? checar la def
        self.C_r = C_r           #[m] Root-chord length
        self.C_t = C_t           #[m] Tip-chord length
        self.bottom = self.posicion + self.C_r

        self.X_R = X_R            #[m] Distancia del inicio de las aletas al Tip-chord
        self.mid_sweep = mid_sweep
        self.mid_chord_span = self.span / np.cos(self.mid_sweep)
        self.tip_le = self.C_r / 2 + self.span * np.tan(self.mid_sweep) - self.C_t / 2  # tip leading edge
        self.leading_sweep = np.arctan(self.tip_le / self.span)
        self.gamma = self.leading_sweep

        self.CG = None
        self.CP = None
        self.CN = None
        self.Ix = None
        self.calc_CG()
        self.calc_CP()
        self.calc_Ix()

    def calc_CG(self):

      self.CG = np.array((0.0, 0.0, 0.0))
      self.CG[2]=(self.C_r**2 + self.C_r * self.C_t + self.C_t**2 + (3 * (self.C_r + self.C_t) * self.rad_fus + (self.C_r + 2 * self.C_t) * self.span) * np.tan(self.gamma)) / (3 * (self.C_r + self.C_t))

    def calc_CP(self):
      theta = np.arctan(1/self.semispan*(self.X_R+ 0.5*(self.C_t-self.C_r)))
      l = self.semispan/ np.cos(theta)
      raiz = np.sqrt(1+(2*l/(self.C_r + self.C_t))**2)

      self.CP = np.array((0.0, 0.0, 0.0))
      #coordenada z del
      self.CP[2] = (self.X_R/3)*((self.C_r+ 2*self.C_t)/(self.C_r + self.C_t))+ 1/6 * ((self.C_r + self.C_t) - (self.C_r*self.C_t/(self.C_r + self.C_t)))
      self.CN = (1+ (self.rad_fus/(self.semispan+self.rad_fus)))*((4*self.numf*((self.semispan/(self.rad_fus*2))**2))/(1+raiz))

    def calc_Ix(self):
      Ix_m = (1 / (18 * (self.C_r + self.C_t)**2)) * (self.C_r**4 + 2 * self.C_r**3 * self.C_t + 2 * self.C_r * self.C_t**3 + self.C_t **4 - (self.C_r**2 + 4 * self.C_r * self.C_t + self.C_t**2) * self.span * np.tan(self.gamma) * (self.C_r - self.C_t - self.span * np.tan(self.gamma)))
      self.Ix = self.masa * Ix_m


class Boattail(Componente):

    def __init__(self, nombre, masa, posicion, longitud, diamF_boat, diamR_boat, espesor):

        super().__init__(nombre, masa, posicion)  # Solo se pasan 3 argumentos a la clase base
        self.long = longitud #Longitud del tubo
        self.bottom = self.posicion + self.long
        self.dF = diamF_boat  # [m] Boat-tail diametro frontal
        self.dR = diamR_boat   # [m] Boat-tail diametro trasero
        self.e = espesor #espesor
        self.radF = self.dF/2
        self.radR = self.dR/2

        self.A_ref = np.pi * self.dF**2 / 4

        self.CG = None
        self.CP = None
        self.CN = None
        self.Ix = None
        self.calc_CG()
        self.calc_CP()
        self.calc_Ix()

    def calc_CG(self):
      self.CG = np.array((0.0, 0.0, 0.0))
      self.CG[2]= (self.long / 3) * (self.radF + 2 * self.radR) / (self.radF + self.radR)

    def calc_CP(self):
      self.CP = np.array((0.0, 0.0, 0.0))
      dimrel= self.dF/self.dR
      #self.CP[2] = (self.long / 3) * ((self.dF + 2 * self.dR) / (self.dR + self.dF))
      self.CP[2]=(self.long/3)*(1+((1-dimrel)/(1-dimrel**2)))
      self.CN = (2/self.dF**2)*(self.dR**2-self.dF**2)

    def calc_Ix(self):
      self.Ix = self.masa * (0.5 * (self.radF**2 + self.radR**2))