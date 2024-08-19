#En este SCRIPT: Clase Vuelo
#Se crea la clase Vuelo, con sus metodos para simular el vuelo 
#y calcular cantidades relevantes
from Integradores import *
#from condiciones_init import *
#from Xitle import *

class Vuelo:

    def __init__(self, vehiculo_actual, atm_actual):

        self.vehiculo = vehiculo_actual #Vehiculo actual
        self.atm = atm_actual #atmosfera actual
        self.parachute1 = vehiculo_actual.parachute1 #paracaidas

        #hacer una lista de etapas de vuelo
        #self. etapas = [enriel , motorON, apogeo, droguerec, mainrec]
        #para cada etapa guardar el tiempo en que ocurrio y sus valores máximos

    def simular_vuelo(self, estado, t_max, dt):

      Tvecs = []
      Dvecs = []
      Nvecs = []

      accels=[]
      palancas=[]
      accangs=[]
      torcas = []

      Gammas = []
      Alphas = []

      Cds=[]
      Machs=[]

      CPs=[]
      CGs=[]
      masavuelo=[]

      viento_vuelo_mags=[]
      viento_vuelo_dirs=[]
      viento_vuelo_vecs=[]


      t = 0.0
      it = 0

      self.vehiculo.cargar_estado(estado)

      #CAMBIO DE METODO DE INTEGRACIÓN
      #Integracion = Euler(Xitle.fun_derivs)
      Integracion = RungeKutta4(self.vehiculo.fun_derivs)
      # Integracion = RKF45(self.vehiculo.fun_derivs)
      #Integracion = Leapfrog(self.vehiculo.fun_derivs)


      sim=[estado] #lista de estados de vuelo
      tiempos=[0] #lista de tiempos

      self.vehiculo.actualizar_masa(t)
      masavuelo=[self.vehiculo.masa]

      ultima_altitud = 0
      self.tiempo_salida_riel = None
      self.tiempo_apogeo = None
      self.tiempo_impacto = None

      while t <= t_max:

        # Actualizar viento_actual
        global viento_actual
        #Prueba:Viento constante
        # viento_actual = Viento2D(vel_mean=10, vel_var=0)
        # viento_actual = Viento2D(vel_mean=0, vel_var=0)
        #es necesario aqui o solo en fun_derivs????
        v_viento = viento_actual.vector
        #v_viento = np.array([0,0,0])

        nuevo_estado = Integracion.step(t, estado, dt)
        #print(nuevo_estado)
        self.vehiculo.cargar_estado(nuevo_estado)

        it += 1
        t+= dt

        self.vehiculo.parachute_active1 = False
        #print(self.vehiculo.parachute_active1)

        tiempos.append(t)
        estado = nuevo_estado

        #Guardar centros de presión y centros de gravedad
        CPs.append(self.vehiculo.CP)
        CGs.append(self.vehiculo.CG)

        #Guardar magnitudes y direcciones del viento
        viento_vuelo_vecs.append(v_viento)
        viento_vuelo_mags.append(viento_actual.magnitud)
        viento_vuelo_dirs.append(viento_actual.direccion)

        self.vehiculo.actualizar_masa(t)
        #Agregar nueva masa a la lista
        masavuelo.append(self.vehiculo.masa)

        #FASE 1. VUELO EN RIEL
        if self.tiempo_salida_riel is None:
          r = np.linalg.norm(estado[0:3])
          if r > riel.longitud:
            self.tiempo_salida_riel = t
       #FASE 2. MECO

        # APOGEO: Determinar tiempo de apogeo
        altitud = estado[2]
        if self.tiempo_apogeo is None and altitud > 5 and altitud < ultima_altitud:
          self.tiempo_apogeo = t
          self.apogeo = altitud

        ultima_altitud = altitud

       #FASE3.RECUPERACIÓN
        #activar el paracaidas en el apogeo
        if self.tiempo_apogeo is not None and self.vehiculo.parachute_added == True:
          #print(self.vehiculo.parachute_active1,"antes")
          self.vehiculo.parachute_active1 = True
          #print(self.vehiculo.parachute_active1,"despues")
          #print("Se ha abierto el paracaídas")
          #self.vehiculo.activar_paracaidas(self.vehiculo.parachute1)
        else:
          pass

        #Agrega el nuevo estado a la lista
        sim.append(estado)


        #CAIDA: Terminar simulación cuando cae al piso
        if estado[2] < 0 and t > 1:
          self.tiempo_impacto = t
          break

        #self.vehiculo.parachute_added = False

        #CALCULAR CANTIDADES SECUNDARIAS
        # Desempaquetar vector de estado
        state = estado
        pos = state[0:3]
        vel = state[3:6]
        #velocidadvector.append(vel)
        theta = state[6]   # En radianes internamente siempre
        omega = state[7] #omeg a= theta dot
        r = np.linalg.norm(pos)
        v = np.linalg.norm(vel)
        z = pos[2] #Coordenada z

        #Guardar Angulos
        gamma, alpha = self.vehiculo.calc_angles(pos, vel, theta)
        Gammas.append(gamma)
        Alphas.append(alpha)

        # Vectores unitarios de dirección
        zbhat = np.array((np.cos(theta), 0, np.sin(theta)))
        vhat = np.array((np.cos(gamma), 0, np.sin(gamma)))

        #Guardar Fuerzas:Empuje,Arrastre y Normal
        Tvec = self.vehiculo.empuje(t, zbhat)

        vrel = np.array(vel) - v_viento
        Dmag, Nmag, Cd, mach = self.vehiculo.calc_arrastre_normal(pos, vrel, alpha)
        Dvec, Nvec = self.vehiculo.calc_aero(pos, vrel, alpha)
        Tvecs.append(Tvec)
        Dvecs.append(Dvec)
        Nvecs.append(Nvec)
        Cds.append(Cd)
        Machs.append(mach)

        # Gravedad
        grav = calc_gravedad(z)
        Gvec = np.array([0,0,-grav])

        # Aceleración resultante
        masa = self.vehiculo.masa
        accel = Gvec + Dvec/masa + Nvec/masa + Tvec/masa
        accels.append(accel)

        # aceleracion angular
        palanca, accang, torca = self.vehiculo.accangular( theta, Dvec, Nvec, Gvec)
        palancas.append(palanca)
        accangs.append(accang)
        torcas.append(torca)


        #Indicar el avance en la simulacion
        if it%1000==0:
          print(f"Iteracion {it}, t={t:.1f} s, altitud={altitud:.1f} m, vel vert={estado[5]:.1f}")

      return tiempos, sim, CPs, CGs, masavuelo, viento_vuelo_mags, viento_vuelo_dirs, viento_vuelo_vecs, Tvecs, Dvecs, Nvecs, accels, palancas, accangs, Gammas, Alphas, torcas, Cds, Machs

    def muestra_tiempos(self):
      plt.axvline(self.tiempo_salida_riel, color="orange", ls="--")
      plt.axvline(Xitle.t_MECO, color="darkred", ls="--")
      if self.tiempo_apogeo is not None:
        plt.axvline(self.tiempo_apogeo, color="navy", ls="--")
      if self.tiempo_impacto is not None:
        plt.axvline(self.tiempo_impacto, color="0.2", ls="--")
