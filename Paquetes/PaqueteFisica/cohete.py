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

        # Recuperacion. Paracaidas 1 (drogue): se abre en el apogeo.
        self.parachute_added = False
        self.parachute_active1 = None
        self.parachute1 = None
        # Paracaidas principal: se abre durante el descenso, a una altura dada sobre el sitio.
        self.main_added = False
        self.main_active = False
        self.parachute_main = None
        self.altura_despliegue_main = None

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

    def agregar_paracaidas_principal(self, parachute_n, altura_despliegue):
      """Paracaidas principal: se abre al bajar por la altura indicada [m sobre el sitio].

      Con drogue y principal el descenso es en dos etapas: rapido con el drogue desde el
      apogeo y lento con el principal cerca del suelo. Si el apogeo queda por debajo de esa
      altura, el principal se abre en el apogeo.
      """
      if altura_despliegue <= 0:
        raise ValueError("La altura de despliegue del paracaidas principal debe ser mayor que 0.")
      self.main_added = True
      self.main_active = False
      self.parachute_main = parachute_n
      self.altura_despliegue_main = altura_despliegue

    def quitar_paracaidas(self):
      """Deja el cohete sin recuperacion (vuelo libre)."""
      self.parachute_added = False
      self.parachute_active1 = False
      self.main_added = False
      self.main_active = False

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

      # Tablas como arreglos de numpy (se interpolan en cada evaluacion de las derivadas)
      self._t_empuje = self.motorThrustTable['time'].to_numpy(dtype=float)
      self._empuje = self.motorThrustTable['thrust'].to_numpy(dtype=float)
      self._t_masa = self.motorMassTable['time'].to_numpy(dtype=float)
      self._masa_oxi = self.motorMassTable['oxi'].to_numpy(dtype=float)
      self._masa_grano = self.motorMassTable['grano'].to_numpy(dtype=float)

      # Calcular el área de la curva empuje vs tiempo utilizando la regla del trapecio
      # np.trapz se eliminó en NumPy 2.0 (ahora np.trapezoid); se soportan ambas versiones
      trapecio = getattr(np, 'trapezoid', None) or np.trapz
      self.I_total = trapecio(y=self._empuje, x=self._t_empuje)

      # Geometria del oxidante con el tanque lleno. Al consumirse, el liquido que queda ocupa
      # la parte trasera del tanque (el empuje lo asienta contra el fondo): la columna se
      # acorta desde arriba y su fondo no se mueve.
      oxidante = self.componentes['oxidante']
      self._oxi_long_llena = float(oxidante.long)
      self._oxi_fondo = float(oxidante.posicion[2] + oxidante.long)

      # Geometria del grano de combustible sin quemar. El grano es un cilindro hueco que se
      # quema desde su canal central: el radio exterior y la longitud no cambian y el canal se
      # ensancha. Con densidad constante, la masa es proporcional a (r_ext^2 - r_int^2).
      grano = self.componentes['grano']
      self._grano_r_ext = float(grano.rad_ext)
      self._grano_r_int0 = float(grano.rad_int)
      self.grano_con_regresion = 0 <= self._grano_r_int0 < self._grano_r_ext
      if not self.grano_con_regresion:
        print(f"Aviso: el grano tiene diametro interior ({grano.diam_int} m) mayor o igual que el exterior "
              f"({grano.diam_ext} m). No se modelara el ensanchamiento de su canal.")

      # Coherencia entre las dos tablas. El propelente debe consumirse mientras hay empuje.
      # Si la tabla de masa dura otra cosa que la curva de empuje (por ejemplo, viene de una
      # simulacion del motor y el empuje de una prueba estatica), su escala de tiempo no
      # sirve: en ese caso se conservan las masas inicial y final de la tabla, pero el
      # propelente se consume en proporcion al impulso entregado, m(t) = m0 - dm * I(t)/I_total
      # (equivale a suponer un impulso especifico constante).
      self.masa_segun_impulso = abs(self._t_masa[-1] - self.t_MECO) > 0.05 * self.t_MECO
      if self.masa_segun_impulso:
        tramos = 0.5 * (self._empuje[1:] + self._empuje[:-1]) * np.diff(self._t_empuje)
        self._fraccion_impulso = np.concatenate(([0.0], np.cumsum(tramos))) / self.I_total
        print(f"Aviso: la tabla de masa del motor dura {self._t_masa[-1]:.2f} s y la curva de empuje {self.t_MECO:.2f} s. "
              "El propelente se consumira en proporcion al impulso entregado.")

    def cargar_tabla_Cd(self, tabla_Cd_fpath):
      self.CdTable = pd.read_csv(tabla_Cd_fpath)
      self._mach = self.CdTable['mach'].to_numpy(dtype=float)
      self._cd = self.CdTable['cd'].to_numpy(dtype=float)

    def calc_Cd(self, mach):
      return np.interp(mach, self._mach, self._cd)

    def calc_empuje_magn(self, t):
      if t > self.t_MECO:
        return 0
      else:
        # Realizar interpolación
        return np.interp(t, self._t_empuje, self._empuje)

    def actualizar_masas_motor(self, t):
      oxidante, grano = self.componentes['oxidante'], self.componentes['grano']
      if self.masa_segun_impulso:
        # Fraccion del impulso total entregada hasta t (0 al encender, 1 al apagarse)
        f = np.interp(t, self._t_empuje, self._fraccion_impulso)
        oxidante.masa = self._masa_oxi[0] + f * (self._masa_oxi[-1] - self._masa_oxi[0])
        grano.masa = self._masa_grano[0] + f * (self._masa_grano[-1] - self._masa_grano[0])
      else:
        # np.interp mantiene el ultimo valor de la tabla despues del final
        oxidante.masa = np.interp(t, self._t_masa, self._masa_oxi)
        grano.masa = np.interp(t, self._t_masa, self._masa_grano)
      # Columna de oxidante: su longitud es proporcional a la masa que queda. Con ella cambian
      # su centro de gravedad (baja hacia el fondo del tanque) y su momento de inercia propio.
      masa_llena = self._masa_oxi[0]
      fraccion = min(max(oxidante.masa / masa_llena, 0.0), 1.0) if masa_llena > 0 else 0.0
      oxidante.long = self._oxi_long_llena * fraccion
      oxidante.posicion = np.array((0.0, 0.0, self._oxi_fondo - oxidante.long))
      oxidante.bottom = oxidante.posicion + oxidante.long
      oxidante.calc_CG()
      # Grano: el canal se ensancha a medida que se quema,
      #   r_int^2 = r_ext^2 - (r_ext^2 - r_int0^2) * masa / masa_inicial
      if self.grano_con_regresion and self._masa_grano[0] > 0:
        queda = min(max(grano.masa / self._masa_grano[0], 0.0), 1.0)
        grano.rad_int = math.sqrt(self._grano_r_ext**2 - (self._grano_r_ext**2 - self._grano_r_int0**2) * queda)
        grano.diam_int = 2 * grano.rad_int
      # El momento de inercia propio de cada componente depende de su masa y de su forma
      oxidante.calc_Ix()
      grano.calc_Ix()

    def flujo_masico(self, t):
      """Masa de propelente que sale por la tobera por unidad de tiempo [kg/s] en el instante t."""
      if t < 0 or t > self.t_MECO:
        return 0.0
      if self.masa_segun_impulso:
        consumido = (self._masa_oxi[0] - self._masa_oxi[-1]) + (self._masa_grano[0] - self._masa_grano[-1])
        return consumido * self.calc_empuje_magn(t) / self.I_total
      if t > self._t_masa[-1]:
        return 0.0
      # Derivada numerica de la tabla de masa
      if not hasattr(self, '_flujo_tabla'):
        self._flujo_tabla = -np.gradient(self._masa_oxi + self._masa_grano, self._t_masa)
      return float(np.interp(t, self._t_masa, self._flujo_tabla))

    def coef_amortiguamiento_aero(self):
      """Suma de CN_i * (x_i - x_CG)^2 sobre los componentes con fuerza normal [m^2].

      x_i es el centro de presion de cada componente. Es el factor geometrico del momento de
      amortiguamiento aerodinamico del cabeceo; depende del CG, que cambia durante el quemado.
      """
      x_cg = self.CG[2]
      return sum(comp.CN * (comp.posicion[2] + comp.CP[2] - x_cg)**2
                 for comp in self.componentes.values() if comp.CN)

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
    """Paracaidas: coeficiente de arrastre, area y modelo de inflado.

    El paracaidas no se abre de golpe. Su area de arrastre crece desde cero hasta Cd*A
    durante un tiempo de llenado
        t_llenado = k_llenado * D / v
    donde D es el diametro del paracaidas y v la velocidad respecto al aire en el momento
    de abrirse (formula del tiempo de llenado de Knacke, "Parachute Recovery Systems Design
    Manual"; k_llenado vale alrededor de 8 para paracaidas circulares planos). Durante el
    llenado,
        Cd*A(t) = Cd*A * (tiempo transcurrido / t_llenado) ** exponente
    Con exponente = 2 el area crece como el cuadrado del tiempo, es decir, el diametro
    inflado crece a ritmo constante. k_llenado = 0 da la apertura instantanea.
    """
    T_LLENADO_MAX = 3.0   # [s] tope del tiempo de llenado (si se abre casi sin velocidad)

    def __init__(self, cd, area_trans, k_llenado=8.0, exponente=2.0):
        self.cd = cd
        self.Area_trans = area_trans
        self.k_llenado = k_llenado
        self.exponente = exponente
        self.diametro = math.sqrt(4.0 * area_trans / math.pi)

    def tiempo_llenado(self, velocidad):
        """Tiempo que tarda en inflarse si se abre a la velocidad dada [s]."""
        if self.k_llenado <= 0:
            return 0.0
        if velocidad <= 0:
            return self.T_LLENADO_MAX
        return min(self.k_llenado * self.diametro / velocidad, self.T_LLENADO_MAX)

    def area_arrastre(self, transcurrido, t_llenado):
        """Cd*A [m2] cuando ha pasado `transcurrido` segundos desde que empezo a abrirse."""
        if transcurrido < 0:
            return 0.0
        if t_llenado <= 0 or transcurrido >= t_llenado:
            return self.cd * self.Area_trans
        return self.cd * self.Area_trans * (transcurrido / t_llenado) ** self.exponente
