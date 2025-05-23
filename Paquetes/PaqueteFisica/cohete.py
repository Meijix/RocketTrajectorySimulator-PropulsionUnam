#En este SCRIPT: Clase COHETE 
#Se crea la clase COHETE, con sus atributos y métodos

#Importar librerias
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy.interpolate import interp1d
import math
from math import pi

#Importar otros scripts

#from Componentes import *
class Cohete:

    def __init__(self, nombre, tipo, componentes, componentes_externos, tabla_Cd_fpath, tabla_empuje_fpath, tabla_masa_fpath, riel):

        self.nombre = nombre
        self.d_ext = None
        self.tipo = tipo    # El tipo de cohete (string)
        self.componentes = componentes   # Una lista de objetos Componente (o derivados)
        self.num_comp = len(self.componentes)
        self.componentes_externos = componentes_externos
        self.riel = riel

        self.t = None
        self.state = None # [x,y,z,vx,vy,vz,pitch,velang]
        self.posicion = None
        self.velocidad = None
        self.pitch = None
        self.velang = None

        self.masa = None
        self.CG = None
        self.CP = None
        self.CN = None
        self.Ix = None
        self.A = None

        self.CdTable = None
        self.motorThrustTable = None

        self.calc_A()
        self.calc_masa()
        self.calc_mom_inercia_total()
        self.calc_CP()
        self.calc_CN()

        self.longtotal = self.componentes["Boattail"].bottom[2]

        print("Cd path:", tabla_Cd_fpath)
        print("Empuje path:", tabla_empuje_fpath)
        print("Masa path:", tabla_masa_fpath)
        # Cargar las tablas de empuje y masa del motor

        self.cargar_tablas_motor(tabla_empuje_fpath, tabla_masa_fpath)
        self.cargar_tabla_Cd(tabla_Cd_fpath)

        self.parachute_added = False
        self.parachute_active1 = None
        self.parachute1 = None

    def calcular_propiedades(self):
        # Recalculate the properties of the rocket
        self.calc_masa()
        self.calc_CG()
        self.calc_CP()
        self.calc_CN()
        self.calc_A()

    def agregar_paracaidas(self, parachute_n):
      self.parachute_added = True
      self.parachute_active1 = False
      self.parachute1 = parachute_n

    #def activar_paracaidas(self, parachute_n):
      #self.parachute_active1 = True

    # Calcular el área transversal efectiva del cohete (según fuselaje)
    # Método calc_A corregido en Paquetes/PaqueteFisica/cohete.py
    # Método calc_A corregido en Paquetes/PaqueteFisica/cohete.py
    def calc_A(self):
        """Calcula el área de referencia del cohete (sección transversal máxima)."""
        radio_ref = None
        # Intentar usar el diámetro de la base de la nariz
        nariz = self.componentes.get("Nariz")
        if nariz and hasattr(nariz, 'diam'):
            radio_ref = nariz.diam / 2.0
            print(f"Usando radio de la nariz para área: {radio_ref}")

        # Si no hay nariz o no tiene diámetro, buscar el primer componente externo con diámetro
        elif self.componentes_externos:
            for comp in self.componentes_externos.values():
                if hasattr(comp, 'diam_ext'): # Para Cilindros
                    radio_ref = comp.diam_ext / 2.0
                    print(f"Usando radio de {comp.nombre} para área: {radio_ref}")
                    break
                elif hasattr(comp, 'dF'): # Para Boattail (diámetro frontal)
                    radio_ref = comp.dF / 2.0
                    print(f"Usando radio frontal de {comp.nombre} para área: {radio_ref}")
                    break
                # Añadir más casos si otros tipos de componentes definen el diámetro externo

        # Si aún no se encuentra, usar self.d_ext si está definido
        if radio_ref is None and self.d_ext is not None:
            print(f"Usando self.d_ext para área: {self.d_ext}")
            radio_ref = self.d_ext / 2.0

        # Calcular el área o asignar 0 si no se pudo determinar el radio
        if radio_ref is not None:
            self.A = math.pi * radio_ref**2
        else:
            print("Error Crítico: No se pudo determinar el radio de referencia para calcular el área del cohete.")
            self.A = 0 # O lanzar un error: raise ValueError("No se puede calcular el área del cohete")

        # Calcula la masa total del cohete sumando las masas de sus componentes
    def calc_masa(self):
      self.masa = 0.0
      for comp in self.componentes.values():
        self.masa += comp.masa

    # Calcula el centro de gravedad con base en las masas y posiciones de sus componentes
    def calc_CG(self):
      if self.masa is None: self.calc_masa()
      self.CG = np.array((0.0, 0.0, 0.0))
      for comp in self.componentes.values():
        self.CG += (comp.posicion + comp.CG) * comp.masa
      self.CG /= self.masa

    # Calcular el momento de inercial total en torno a un eje "horizontal" (perpendicular al eje longitudinal) respecto al CG de todo el cohete
    # Se aplica el teorema de ejes paralelos para combinar los momentos de inercia de los componentes individuales
    def calc_mom_inercia_total(self):
      self.Ix = 0.0
      if self.CG is None: self.calc_CG()
      for comp in self.componentes.values():
        self.Ix += comp.Ix + comp.masa*np.linalg.norm((comp.posicion + comp.CG) - self.CG)**2

    def calc_CP(self):
      self.CP = np.array((0.0, 0.0, 0.0))
      CN_tot = 0.0
      for comp in self.componentes.values():
        self.CP += (comp.posicion + comp.CP) * comp.CN
        CN_tot += comp.CN
      self.CP /= CN_tot

    def calc_CN(self):
      self.CN = 0
      for comp in self.componentes.values():
        # print(comp.nombre, comp.CN)
        self.CN += comp.CN

    def cargar_tabla_Cd(self, tabla_Cd_fpath):
      self.CdTable = pd.read_csv(tabla_Cd_fpath)

    #Se debe hacer general para agregar cualquier curva de motor 
    #desde la simulacion
    def cargar_tablas_motor(self, tabla_empuje_fpath, tabla_masa_fpath):

      self.motorThrustTable = pd.read_csv(tabla_empuje_fpath) #Importar la curva de empuje
      # self.motorThrustTable = pd.read_csv("pruebaestaica28mayo2024.csv")
      self.t_MECO = self.motorThrustTable['time'].max() #tiempo en que se acaba el empuje

      self.motorMassTable = pd.read_csv(tabla_masa_fpath)
      self.motorMassTable['time'] = self.motorMassTable['Time (s)']
      self.motorMassTable['oxi'] = self.motorMassTable['Oxidizer Mass (kg)']
      self.motorMassTable['grano'] = self.motorMassTable['Fuel Mass (kg)']

      # Calcular el área de la curva empuje vs tiempo utilizando la regla del trapecio
      #Vamos a probar otro tipo de integracion para mejorarlo?
      self.I_total = np.trapz(y=self.motorThrustTable['thrust'], x=self.motorThrustTable['time'])

    def calc_Cd(self, mach):
      return np.interp(mach, self.CdTable['mach'], self.CdTable['cd'])

    def calc_empuje_magn(self, t):
      if t > self.t_MECO:
        return 0
      else:
        # Realizar interpolación
        return np.interp(t, self.motorThrustTable['time'], self.motorThrustTable['thrust'])

    def actualizar_masas_motor(self, t):
      p = len(self.motorMassTable['time'])
      if t > self.t_MECO:
        #Actualizar la masa del componente
        self.componentes['oxidante'].masa = self.motorMassTable['oxi'][p-1]
        self.componentes['grano'].masa = self.motorMassTable['grano'][p-1]
      else:
        self.componentes['oxidante'].masa = np.interp(t, self.motorMassTable['time'], self.motorMassTable['oxi'])
        self.componentes['grano'].masa = np.interp(t, self.motorMassTable['time'], self.motorMassTable['grano'])

    def actualizar_masa(self, t):
      # Actualizar masa de motor
      self.actualizar_masas_motor(t)
      #Calcular masa del cohete copleto (con el nuevo motor)
      self.calc_masa()
      #Calcular CG
      self.calc_CG()
      self.calc_mom_inercia_total()
    
#Clase para Paracaidas
class Parachute:
    def __init__(self, cd, area_trans):
        self.cd = cd
        self.Area_trans = area_trans