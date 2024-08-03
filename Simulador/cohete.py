#En este SCRIPT: Clase COHETE 
#Se crea la clase COHETE, con sus atributos y métodos

#Importar otros scripts
from Atmosfera1 import atm_actual,calc_gravedad
#from Componentes import *
from Viento import *
from riel import riel

#Importar librerias
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy.interpolate import interp1d
import math
from math import pi

class Cohete:

    def __init__(self, nombre, tipo, componentes,componentes_externos):

        self.nombre = nombre
        self.tipo = tipo    # El tipo de cohete (string)
        self.componentes = componentes   # Una lista de objetos Componente (o derivados)
        self.num_comp = len(self.componentes)
        self.componentes_externos = componentes_externos

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


        self.calc_A()
        self.calc_masa()
        self.calc_mom_inercia_total()
        self.calc_CP()
        self.calc_CN()

        self.boattail=self.componentes["Boattail"]
        self.longtotal = self.boattail.bottom[2]

        self.cargar_tablas_motor()
        self.cargar_tabla_Cd()

        self.parachute_added = False
        self.parachute_active1 = None
        self.parachute1 = None

    def agregar_paracaidas(self, parachute_n):
      self.parachute_added = True
      self.parachute_active1 = False
      self.parachute1 = parachute_n

    #def activar_paracaidas(self, parachute_n):
      #self.parachute_active1 = True

    def cargar_estado(self,estado):
      self.state = estado
      self.posicion = estado[0:3]
      self.velocidad = estado[3:5]
      self.pitch = estado[6]
      self.velang = estado[7]

    # Calcular el área transversal efectiva del cohete (según fuselaje)
    def calc_A(self):
      self.A = pi * self.componentes['coples'].rad_ext**2

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
        self.CN += comp.CN

    def vuela(self):
      print("Vuela porfavor")

    def cargar_tabla_Cd(self):
      self.CdTable = pd.read_csv(r'C:\Users\Natalia\OneDrive\Tesis\GithubCode\3DOF-Rocket-PU\Archivos\cdmachXitle.csv')

    def cargar_tablas_motor(self):

      #self.motorThrustTable = pd.read_csv('MegaPunisherBien.csv') #Importar la curva de empuje
      self.motorThrustTable = pd.read_csv(r'C:\Users\Natalia\OneDrive\Tesis\GithubCode\3DOF-Rocket-PU\Archivos\pruebaestaica28mayo2024.csv')
      self.t_MECO = self.motorThrustTable['time'].max() #tiempo en que se acaba el empuje

      self.motorMassTable = pd.read_csv(r'C:\Users\Natalia\OneDrive\Tesis\GithubCode\3DOF-Rocket-PU\Archivos\MegaPunisherFatMasadot.csv')
      self.motorMassTable['time'] = self.motorMassTable['Time (s)']
      self.motorMassTable['oxi'] = self.motorMassTable['Oxidizer Mass (kg)']
      self.motorMassTable['grano'] = self.motorMassTable['Fuel Mass (kg)']

      # Calcular el área de la curva empuje vs tiempo utilizando la regla del trapecio
      #Vamos a probar otro tipo de integracion para mejorarlo?
      self.I_total = np.trapz(y=self.motorThrustTable['thrust'], x=self.motorThrustTable['time'])

    def calc_empuje(self, t):
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

    def calc_arrastre_normal(self, pos, vel, alpha):
      altura = pos[2] #self.posicion[2]
      vel_mag = np.linalg.norm(vel)
      #print(altura)
      T, rho, presion, cs = atm_actual.calc_propiedades(altura)
      mach =  vel_mag / cs #mach variable
      Cd = np.interp(mach, self.CdTable['mach'], self.CdTable['cd'])
      # DEBUG: aumentar Cd
      # Cd *= 5

      f_arrastre = 0.5 * rho * Cd * self.A * vel_mag**2
      f_normal = 0.5 * rho * self.CN * self.A  * vel_mag**2 * np.sin(alpha) * np.sin(alpha)

      if self.parachute_active1 == True:
        coef_par = self.parachute1.cd
        area_par = self.parachute1.Area_trans
        f_paracaidas = 0.5 *rho* coef_par * area_par * vel_mag**2
        f_arrastre = f_arrastre  + f_paracaidas
      else:
        pass
        #print(f_paracaidas)

      # if alpha == 0:
      #   f_normal = 0.5 * rho * self.CN * self.A  * vel_mag**2
      # else:
      #   f_normal = 0.5 * rho * np.sin(alpha)/alpha * self.CN * self.A  * vel_mag**2

      #print(f_arrastre, "arrastre")
      #print(f_normal, "normal")
      return f_arrastre, f_normal, Cd, mach

    def actualizar_masa(self, t):
      # Actualizar masa de motor
      self.actualizar_masas_motor(t)
      #Calcular masa del cohete copleto (con el nuevo motor)
      self.calc_masa()
      #Calcular CG
      self.calc_CG()

    def calc_angles(self, pos, vel, theta):
        # Ángulo de vuelo (flight path angle)
        r = np.linalg.norm(pos)
        if r <= riel.longitud:
          gamma = theta
        else:
          gamma = math.atan2(vel[2], vel[0])
        # Angulo de ataque
        alpha = theta - gamma
        return gamma, alpha

    def empuje(self, t, zbhat):
      Tmag = self.calc_empuje(t)
      #Calcular las componentes del empuje
      #La direccion del empuje es en sentido a la velocidad
      Tvec = Tmag * zbhat
      return Tvec

    def calc_aero(self, pos, vel, vhat, alpha):
      if pos[2] <= 85000: #si todavía esta en la atmosfera definida
        #print(self.calc_arrastre_normal(pos,vel,alpha))
        Dmag, Nmag, Cd, mach = self.calc_arrastre_normal(pos, vel, alpha)
        #print(Cd,mach)
        #print(Dmag,"mag arrastre")
        #Fuerza normal
        #Falta la variacion, que sea funcion de theta (pitch)
        Dvec = - Dmag * vhat
        #print(vhat, Dvec)
        nhat = np.array((vhat[2], vhat[1], -vhat[0]))
        # Tal vez invertir el vector para que la componente x tenga el
        # mismo signo que la componente x de -vhat
        # DEBUG: apagar normal
        #Nmag = 0
        Nvec = Nmag * nhat
        return Dvec, Nvec, Cd, mach
      else:
        return np.zeros(3), np.zeros(3)

    def accangular(self, theta, Dvec, Nvec, Gvec):
      # Calcular brazo de momentos
      # r es un vector que apunta del CG al CP, en coords de cuerpo del cohete,
      # donde la nariz es el origen y el eje Z apunta hacia la cola
      palanca_b = self.CP - self.CG
      s = np.sin(theta)
      c = np.cos(theta)
      # Transformar a coordenadas del suelo
      M_rot = np.array([[s,0,-c],[0, 1, 0],[c, 0 , -s]])
      palanca = M_rot @ palanca_b   # palanca en coord del suelo

      #Calcular las torcas
      #print(Dvec,"arrastre")
      tau_D = np.cross(palanca, Dvec)

      tau_N = np.cross(palanca, Nvec)
      tau_tot = tau_D + tau_N
      #torcas.append((tau_D, tau_N))
      #torcas.append((tau_tot))
      #palancas.append(palanca)

      #suma de torcas/ momento de inercia total
      # se toma la componente y (perpendicular al plano de vuelo ZX) y se
      # multiplica por -1 porque el eje y apunta hacia "adentro"
      Torca = -tau_tot[1]
      Torca = Torca*10
      accang = Torca / self.Ix # se debe usar el momento de inercia actualizado
      #angaccels.append(accang)
      return palanca, accang, Torca


    def fun_derivs(self, t, state, v_viento):

      # state, posicion y velocidad son estados intermedios
      #no necsariamente los del cohete
      pos = state[0:3]
      vel = state[3:6]
      #velocidadvector.append(vel)
      theta = state[6]   # En radianes internamente siempre
      omega = state[7] #omeg a= theta dot
      # r = np.linalg.norm(pos)
      # v = np.linalg.norm(vel)
      z = pos[2] #Coordenada z

      accel = np.array([0,0,0])

      # Angulos
      gamma, alpha = self.calc_angles(pos, vel, theta)

      # Vectores unitarios para la nariz y la velocidad
      zbhat = np.array((np.cos(theta), 0, np.sin(theta)))
      vhat = np.array((np.cos(gamma), 0, np.sin(gamma)))

      v_rel =  v_viento - vhat
      v_rel_hat = v_rel / np.linalg.norm(v_rel)
      #v_viento = viento_actual.vector
      #v_viento = np.array([0,0,0])
      v_rel =  v_viento - vhat
      v_rel_hat = v_rel / np.linalg.norm(v_rel)
      #print(v_rel_hat)


      #Calcular las componentes del empuje
      Tvec = self.empuje(t, zbhat)
      #print(Tvec)

      # Arrastre y fuerza normal
      #Para considerar el viento: cambiar vhat por v_rel_hat??
      #print(self.calc_aero(pos, vel, v_rel_hat, alpha))
      Dvec, Nvec, Cd, mach = self.calc_aero(pos, vel, vhat, alpha)
      #print("Vectores de arrastre y normal",Dvec, Nvec)


      # Gravedad
      grav = calc_gravedad(z)
      Gvec = np.array([0,0,-grav])

      # Aceleración resultante de todas las fuerzas
      accel = Gvec + Dvec/self.masa + Nvec/self.masa + Tvec/self.masa

      #Velocidad angular
      velang = omega

      # aceleracion angular
      palanca, accang, torca = self.accangular(theta, Dvec, Nvec, Gvec)

      # PRUEBA: apagar parte angular
      # omega = 0
      # accang= 0

      derivs = np.concatenate((vel, accel, [omega], [accang]))
      #print(derivs)

      return derivs
    
class Parachute:
    def __init__(self, cd, area_trans):
        self.cd = cd
        self.Area_trans = area_trans