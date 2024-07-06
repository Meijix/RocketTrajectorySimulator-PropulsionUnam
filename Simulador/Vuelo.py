class Vuelo:

    def __init__(self, vehiculo_actual, atm_actual, viento_actual):

        self.vehiculo = vehiculo_actual #Vehiculo actual
        self.atm = atm_actual #atmosfera actual
        self.viento = viento_actual
        self.parachute1 = vehiculo_actual.parachute1 #paracaidas

        #hacer una lista de etapas de vuelo
        #self. etapas = [enriel , motorON, apogeo, droguerec, mainrec]
        #para cada etapa guardar el tiempo en que ocurrio y sus valores máximos

    def simular_vuelo(self, estado, t_max, dt):
      CPs=[]
      CGs=[]

      t = 0
      it = 0

      self.vehiculo.cargar_estado(estado)

      #CAMBIO DE METODO DE INTEGRACIÓN
      #Integracion = Euler(Xitle.fun_derivs)
      Integracion = RungeKutta4(self.vehiculo.fun_derivs)
      #Integracion = RKF45(self.vehiculo.fun_derivs)
      #Integracion = Leapfrog(self.vehiculo.fun_derivs)


      sim=[estado] #lista de estados de vuelo
      tiempos=[0] #lista de tiempos

      self.vehiculo.actualizar_masa(t)
      masavuelo=[self.vehiculo.masa]

      ultima_altitud = None
      self.tiempo_salida_riel = None
      self.tiempo_apogeo = None
      self.tiempo_impacto = None

      while t <= t_max:

        nuevo_estado = Integracion.step(t, estado, dt)
        self.vehiculo.cargar_estado(nuevo_estado)

        it += 1
        t+= dt

        self.vehiculo.parachute_active1 = False
        #print(self.vehiculo.parachute_active1)

        tiempos.append(t)
        estado = nuevo_estado


        CPs.append(self.vehiculo.CP)
        CGs.append(self.vehiculo.CG)

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

        #Agrega el nuevo estado a la lista
        sim.append(estado)


        #self.vehiculo.parachute_added = False

      return tiempos, sim, CPs, CGs, masavuelo

    def calc_cantidades_secundarias(self, tiempos, estados):

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

      vientomag = []
      vientodir = []

      #print(tiempos)

      for i in range(len(tiempos)-1):

        # Desempaquetar vector de estado
        state = estados[i]
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

        #vectores para velocidad considerando el viento
        if pos[2] <= 1000: #10 m
          v_viento = np.array([0,0,0])
          vientomag.append(0)
          vientodir.append(0)
        else:
          viento_actual = Viento2D(vel_mean=10, vel_var=0.2)
          v_viento = viento_actual.vector
          vientomag.append(viento_actual.magnitud)
          vientodir.append(viento_actual.direccion)
        #v_viento = np.array([0,0,0])



        v_rel =  v_viento - vhat
        v_rel_hat = v_rel / np.linalg.norm(v_rel)
        #v_viento = viento_actual.vector
        #v_viento = np.array([0,0,0])
        v_rel =  v_viento - vhat
        v_rel_hat = v_rel / np.linalg.norm(v_rel)
        #print(v_rel_hat)

        #print(vhat, v_viento, v_rel, v_rel_hat)


        #Guardar Fuerzas:Empuje,Arrastre y Normal
        Tvec = self.vehiculo.empuje(tiempos[i], zbhat)

        Dvec, Nvec, Cd, mach = self.vehiculo.calc_aero(pos, vel, vhat, alpha)
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

      return Tvecs, Dvecs, Nvecs, accels, palancas, accangs, Gammas, Alphas, torcas, Cds, Machs, vientomag, vientodir

    def muestra_tiempos(self):
      plt.axvline(self.tiempo_salida_riel, color="orange", ls="--")
      plt.axvline(Xitle.t_MECO, color="darkred", ls="--")
      plt.axvline(self.tiempo_apogeo, color="navy", ls="--")
      plt.axvline(self.tiempo_impacto, color="0.2", ls="--")
