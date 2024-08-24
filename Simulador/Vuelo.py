#En este SCRIPT: Clase Vuelo
#Se crea la clase Vuelo, con sus metodos para simular el vuelo 
#y calcular cantidades relevantes
from Integradores import *
from funciones import *
#from condiciones_init import *
#from Xitle import *
from Viento import Viento2D

class Vuelo:

    def __init__(self, vehiculo_actual, atm_actual, viento_actual):

        self.vehiculo = vehiculo_actual #Vehiculo actual
        self.atmosfera = atm_actual #atmosfera actual
        self.viento = viento_actual
        self.parachute1 = vehiculo_actual.parachute1 #paracaidas

        #hacer una lista de etapas de vuelo
        #self. etapas = [enriel , motorON, apogeo, droguerec, mainrec]
        #para cada etapa guardar el tiempo en que ocurrio y sus valores máximos

    def calc_arrastre_normal(self, pos, vel, alpha):
      altura = pos[2] #self.posicion[2]
      vel_mag = np.linalg.norm(vel)
      #print(altura)
      _, rho, _, cs = self.atmosfera.calc_propiedades(altura)
      mach =  vel_mag / cs #mach variable
      Cd = self.vehiculo.calc_Cd(mach)
      CN = self.vehiculo.CN
      A = self.vehiculo.A
      # DEBUG: aumentar Cd
      # Cd *= 5
      f_arrastre = 0.5 * rho * Cd * A * vel_mag**2
      f_normal = 0.5 * rho * CN * A * vel_mag**2 * np.sin(alpha)**2

      if self.vehiculo.parachute_active1 == True:
        coef_par = self.vehiculo.parachute1.cd
        area_par = self.vehiculo.parachute1.Area_trans
        f_paracaidas = 0.5 * rho * coef_par * area_par * vel_mag**2
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

    def calc_angles(self, pos, vel, theta):
        # Ángulo de vuelo (flight path angle)
        r = np.linalg.norm(pos)
        if r <= self.vehiculo.riel.longitud:
          gamma = theta
        else:
          gamma = math.atan2(vel[2], vel[0])
        # Angulo de ataque
        alpha = theta - gamma
        return gamma, alpha

    def calc_empuje(self, t, zbhat):
      Tmag = self.vehiculo.calc_empuje(t)
      #Calcular las componentes del empuje
      #La direccion del empuje es en sentido a la velocidad
      Tvec = Tmag * zbhat
      return Tvec

    def calc_aero(self, pos, v_rel, alpha):
      if np.linalg.norm(v_rel) == 0 or pos[2] > self.atmosfera.h_max:
        return np.zeros(3), np.zeros(3)
      else:
        #si todavía esta en la atmosfera definida
        #print(self.calc_arrastre_normal(pos,vel,alpha))
        v_rel_hat = normalized(v_rel)
        Dmag, Nmag, Cd, mach = self.calc_arrastre_normal(pos, v_rel, alpha)
        #print(Cd,mach)
        #print(Dmag,"mag arrastre")
        #Fuerza normal
        #Falta la variacion, que sea funcion de theta (pitch)
        Dvec = - Dmag * v_rel_hat
        #print(vhat, Dvec)
        nhat = np.array((v_rel_hat[2], v_rel_hat[1], -v_rel_hat[0]))
        # Tal vez invertir el vector para que la componente x tenga el
        # mismo signo que la componente x de -vhat
        # DEBUG: apagar normal
        Nmag = 0
        Nvec = Nmag * nhat
        return Dvec, Nvec

    def accangular(self, theta, Dvec, Nvec, Gvec):
      # Calcular brazo de momentos
      # r es un vector que apunta del CG al CP, en coords de cuerpo del cohete,
      # donde la nariz es el origen y el eje Z apunta hacia la cola
      palanca_b = self.vehiculo.CP - self.vehiculo.CG
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
      #Torca = Torca*10
      accang = Torca / self.vehiculo.Ix # se debe usar el momento de inercia actualizado
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

      # Vectores unitarios para la nariz y la velocidad (no necesariamente estan alineadas)
      zbhat = np.array((np.cos(theta), 0, np.sin(theta))) #para el empuje
      vhat = np.array((np.cos(gamma), 0, np.sin(gamma))) #para fuerzas aerodinamicas

      # vectores para velocidad considerando el viento
      v_viento = self.viento.vector
      #print(v_viento)
      v_rel =  np.array(vel) - v_viento
      # if np.linalg.norm(vel) > 0:
      #   print(normalized(vel), v_viento, normalized(v_rel))

      # Fuerzas aerodinámica: Arrastre y fuerza normal
      #Para considerar el viento: cambiar vhat por v_rel_hat??
      #print(self.calc_aero(pos, vel, v_rel_hat, alpha))
      #Dvec, Nvec, Cd, mach = self.calc_aero(pos, vel, vhat, alpha)
      # Dmag, Nmag, Cd,mach=self.calc_arrastre_normal(pos, v_rel, alpha)
      #print("Vectores de arrastre y normal",Dvec, Nvec)
      Dvec, Nvec = self.calc_aero(pos, v_rel, alpha)

      #Calcular las componentes del empuje
      Tvec = self.calc_empuje(t, zbhat)
      #print(Tvec)

      # Gravedad
      grav = calc_gravedad(z)
      Gvec = np.array([0,0,-grav])

      # Aceleración resultante de todas las fuerzas
      accel = Gvec + Dvec/self.vehiculo.masa + Nvec/self.vehiculo.masa + Tvec/self.vehiculo.masa

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
      #########################################
      #CAMBIO DE METODO DE INTEGRACIÓN
      #Integracion = Euler(Xitle.fun_derivs)
      Integracion = RungeKutta4(self.fun_derivs)
      # Integracion = RKF45(self.vehiculo.fun_derivs)
      #Integracion = Leapfrog(self.vehiculo.fun_derivs)
      ##########################################
      
      sim=[estado] #lista de estados de vuelo
      tiempos=[0] #lista de tiempos

      self.vehiculo.actualizar_masa(t)
      masavuelo=[self.vehiculo.masa]

      self.vehiculo.parachute_active1 = False
      #print(self.vehiculo.parachute_active1)

      ultima_altitud = 0
      self.tiempo_salida_riel = None
      self.tiempo_apogeo = None
      self.tiempo_impacto = None

      while t <= t_max:

        # -------------------------
        # Integracion numérica del estado actual
        nuevo_estado = Integracion.step(t, estado, dt)

        # Avanzar estado
        it += 1
        t += dt
        estado = nuevo_estado

        # -------------------------
        # Actualizar variables (viento, masa del vehiculo, etc)

        # Actualizar masa del vehiculo
        self.vehiculo.actualizar_masa(t)

        # Actualizar viento_actual
        wind = Viento2D(vel_mean=10, vel_var=2)
        wind.actualizar_viento()
        v_viento = wind.vector

        #FASE 1. VUELO EN RIEL
        if self.tiempo_salida_riel is None:
          r = np.linalg.norm(estado[0:3])
          if r > self.vehiculo.riel.longitud:
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

        #CAIDA: Terminar simulación cuando cae al piso
        if estado[2] < 0 and t > 1:
          self.tiempo_impacto = t
          break

        # -------------------------
        # Guardar cantidades en listas

        #Agrega el nuevo estado a la lista
        sim.append(nuevo_estado)
        tiempos.append(t)

        #Guardar centros de presión y centros de gravedad
        CPs.append(self.vehiculo.CP)
        CGs.append(self.vehiculo.CG)

        #Guardar magnitudes y direcciones del viento
        viento_vuelo_vecs.append(v_viento)
        viento_vuelo_mags.append(self.viento.magnitud)
        viento_vuelo_dirs.append(self.viento.direccion)
       
        #Agregar nueva masa a la lista
        masavuelo.append(self.vehiculo.masa)    

        #self.vehiculo.parachute_added = False

        #CALCULAR CANTIDADES SECUNDARIAS
        # Desempaquetar vector de estado      
        pos = nuevo_estado[0:3]
        vel = nuevo_estado[3:6]
        #velocidadvector.append(vel)
        theta = nuevo_estado[6]   # En radianes internamente siempre
        omega = nuevo_estado[7] #omeg a= theta dot
        r = np.linalg.norm(pos)
        v = np.linalg.norm(vel)
        z = pos[2] #Coordenada z

        #Guardar Angulos
        gamma, alpha = self.calc_angles(pos, vel, theta)
        Gammas.append(gamma)
        Alphas.append(alpha)

        # Vectores unitarios de dirección
        zbhat = np.array((np.cos(theta), 0, np.sin(theta)))
        vhat = np.array((np.cos(gamma), 0, np.sin(gamma)))

        #Guardar Fuerzas:Empuje,Arrastre y Normal
        Tvec = self.calc_empuje(t, zbhat)

        vrel = np.array(vel) - v_viento
        Dmag, Nmag, Cd, mach = self.calc_arrastre_normal(pos, vrel, alpha)
        Dvec, Nvec = self.calc_aero(pos, vrel, alpha)
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
        palanca, accang, torca = self.accangular( theta, Dvec, Nvec, Gvec)
        palancas.append(palanca)
        accangs.append(accang)
        torcas.append(torca)

        #Indicar el avance en la simulacion
        if it%1000==0:
          print(f"Iteracion {it}, t={t:.1f} s, altitud={altitud:.1f} m, vel vert={estado[5]:.1f}")

      return tiempos, sim, CPs, CGs, masavuelo, viento_vuelo_mags, viento_vuelo_dirs, viento_vuelo_vecs, Tvecs, Dvecs, Nvecs, accels, palancas, accangs, Gammas, Alphas, torcas, Cds, Machs

    def muestra_tiempos(self):
      plt.axvline(self.tiempo_salida_riel, color="orange", ls="--")
      plt.axvline(self.vehiculo.t_MECO, color="darkred", ls="--")
      if self.tiempo_apogeo is not None:
        plt.axvline(self.tiempo_apogeo, color="navy", ls="--")
      if self.tiempo_impacto is not None:
        plt.axvline(self.tiempo_impacto, color="0.2", ls="--")
