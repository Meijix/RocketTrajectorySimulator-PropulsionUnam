from Atmosfera import *

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy.interpolate import interp1d
import math
from math import pi


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

        self.longtotal = boattail.bottom[2]

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
      self.CdTable = pd.read_csv('cdmachXitle.csv')

    def cargar_tablas_motor(self):

      #self.motorThrustTable = pd.read_csv('MegaPunisherBien.csv') #Importar la curva de empuje
      self.motorThrustTable = pd.read_csv("pruebaestaica28mayo2024.csv")
      self.t_MECO = self.motorThrustTable['time'].max() #tiempo en que se acaba el empuje

      self.motorMassTable = pd.read_csv('MegaPunisherFatMasadot.csv')
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


    def fun_derivs(self, t, state):

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


      #vectores para velocidad considerando el viento
      if pos[2] <= 1000:
        v_viento = np.array([0,0,0])
      else:
        viento_actual =Viento2D( 5, 0.02)
        v_viento = viento_actual.vector
      #v_viento = np.array([0,0,0])
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