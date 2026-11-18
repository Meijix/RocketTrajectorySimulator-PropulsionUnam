#En este SCRIPT: Clase Vuelo
#Se crea la clase Vuelo, con sus metodos para simular el vuelo y calcular cantidades relevantes
import numpy as np
import math
#Importar paquetes propios de carpeta superior Paquetes
import sys
import os
from scipy.integrate import solve_ivp

# Agregar la ruta del directorio que contiene los paquetes al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
#print(sys.path)


#Importar funciones
from Paquetes.utils.funciones import normalized, calc_gravedad
#Importar integradores
from Paquetes.PaqueteEDOs.integradores import Euler, RungeKutta2, RungeKutta4, RKF45

#Porque se corre la simulacion en este script?
class Vuelo:

    def __init__(self, vehiculo_actual, atm_actual, viento_actual):

        self.vehiculo = vehiculo_actual #Vehiculo actual
        self.atmosfera = atm_actual #atmosfera actual
        self.viento = viento_actual
        self.parachute1 = None #vehiculo_actual.parachute1 #paracaidas

        self.tiempo_salida_riel = None
        self.tiempo_apogeo = None
        self.tiempo_impacto = None
        self.tiempo_despliegue_main = None   # instante en que se abre el paracaidas principal
        self.apertura_drogue = None          # (instante de apertura, tiempo de llenado) del drogue
        self.apertura_main = None            # idem del paracaidas principal
        self.t_actual = 0.0                  # instante que se esta evaluando
        self.fuerza_paracaidas = 0.0
        self.apogeo = None
        self.impacto = None
        self.pasos = 0          # pasos de integracion de la ultima simulacion
        self.evaluaciones = 0   # evaluaciones de fun_derivs de la ultima simulacion
        self.amortiguamiento = True   # incluir los momentos de amortiguamiento del cabeceo

        #hacer una lista de etapas de vuelo
        #self. etapas = [enriel , motorON, apogeo, droguerec, mainrec]
        #para cada etapa guardar el tiempo en que ocurrio y sus valores máximos

    def _area_arrastre(self, paracaidas, apertura):
        """Cd*A de un paracaidas en el instante actual; `apertura` es (instante de apertura, tiempo de llenado)."""
        if apertura is None:              # activado a mano, sin registro de apertura: abierto del todo
            return paracaidas.cd * paracaidas.Area_trans
        t_apertura, t_llenado = apertura
        return paracaidas.area_arrastre(self.t_actual - t_apertura, t_llenado)

    def _registrar_apertura(self, paracaidas, t, estado):
        """(instante de apertura, tiempo de llenado) segun la velocidad respecto al aire al abrirse."""
        estado = np.asarray(estado, dtype=float)
        velocidad = np.linalg.norm(estado[3:6] - self.viento.vector_en(t, estado[2]))
        return (t, paracaidas.tiempo_llenado(velocidad))

    def calc_arrastre_normal(self, pos, vel, alpha):
        altura = pos[2] #self.posicion[2]
        vel_mag = np.linalg.norm(vel)
        #print(altura)
        _, rho, _, cs = self.atmosfera.calc_propiedades(altura)
        mach =  vel_mag / cs #mach variable
        Cd = self.vehiculo.calc_Cd(mach)
        CNalpha = self.vehiculo.CN
        A = self.vehiculo.A
        # DEBUG: aumentar Cd
        # Cd *= 5
        f_arrastre = (0.5 * rho * vel_mag**2) * A * Cd 
        # f_normal = 0.5 * rho * CN * A * vel_mag**2 * np.sin(alpha)**2
        # f_normal = 0.5 * rho * CN * A * vel_mag**2 * np.sin(alpha)**2
        f_normal = (0.5 * rho * vel_mag**2) * A * abs(np.sin(alpha)) * CNalpha

        # Paracaidas abiertos: cada uno suma su arrastre (el drogue sigue abierto con el principal)
        # Su area de arrastre crece durante el llenado (ver la clase Parachute)
        f_paracaidas = 0.0
        if self.vehiculo.parachute_active1 == True:
            f_paracaidas += 0.5 * rho * self._area_arrastre(self.vehiculo.parachute1, self.apertura_drogue) * vel_mag**2
        if self.vehiculo.main_active:
            f_paracaidas += 0.5 * rho * self._area_arrastre(self.vehiculo.parachute_main, self.apertura_main) * vel_mag**2
        f_arrastre += f_paracaidas
        self.fuerza_paracaidas = f_paracaidas   # fuerza de los paracaidas en esta evaluacion [N]
        #print(f_paracaidas)

        # if alpha == 0:
        #   f_normal = 0.5 * rho * self.CN * self.A  * vel_mag**2
        # else:
        #   f_normal = 0.5 * rho * np.sin(alpha)/alpha * self.CN * self.A  * vel_mag**2

        #print(f_arrastre, "arrastre")
        #print(f_normal, "normal")
        return f_arrastre, f_normal, Cd, mach

    def calc_empuje(self, t, theta):
        #Calcular las componentes del empuje
        #La direccion del empuje es longitudinal hacia la nariz
        zbhat = np.array((np.cos(theta), 0, np.sin(theta)))
        Tmag = self.vehiculo.calc_empuje_magn(t)
        Tvec = Tmag * zbhat
        return Tvec

    def calc_alpha(self, v_rel, theta):
        # Ángulo de ataque (relativo al viento)
        gamma_rel = math.atan2(v_rel[2], v_rel[0])
        alpha = theta - gamma_rel
        return alpha

    def calc_aero(self, pos, v_rel, theta):
        if np.linalg.norm(v_rel) == 0 or pos[2] > self.atmosfera.h_max:
            return np.zeros(3), np.zeros(3)
        else:
        #si todavía esta en la atmosfera definida
        #print(self.calc_arrastre_normal(pos,vel,alpha))
            v_rel_hat = normalized(v_rel)
            alpha = self.calc_alpha(v_rel, theta)
        
        Dmag, Nmag, Cd, mach = self.calc_arrastre_normal(pos, v_rel, alpha)
        #print(Cd,mach)
        #print(Dmag,"mag arrastre")
        #Fuerza normal
        #Falta la variacion, que sea funcion de theta (pitch)
        Dvec = - Dmag * v_rel_hat
        # La normal siempre produce un momento de giro estabilizador (siempre
        # y cuando el CP esté atrás del CG)
        # La normal vive en el plano de cabeceo (XZ) y es perpendicular a la velocidad
        # relativa proyectada en ese plano. (Antes llevaba ademas la componente y de la
        # velocidad, que no es perpendicular a nada y empujaba al cohete de lado.)
        v_plano = math.hypot(v_rel_hat[0], v_rel_hat[2])
        if v_plano > 0:
            # sign(sin(alpha)) y no sign(alpha): alpha no esta acotado a (-180, 180] grados
            Nhat = -np.sign(np.sin(alpha)) * np.array((v_rel_hat[2], 0.0, -v_rel_hat[0])) / v_plano
        else:
            Nhat = np.zeros(3)
        # Nmag = 0    # DEBUG: apagar normal
        Nvec = Nmag * Nhat
        # print("alpha=", degrees(alpha))
        # print("Arrastre:", Dmag, Dvec)
        # print("Normal:", Nmag, Nvec)
        # input()
        return Dvec, Nvec

    def torca_amortiguamiento(self, t, state, v_rel):
        """Momento que se opone a la velocidad angular de cabeceo [N m]: M = -(C_aero + C_chorro) * omega.

        Amortiguamiento aerodinamico. Cuando el cohete gira con velocidad angular omega, un
        componente a distancia d del CG se mueve de lado a velocidad omega*d, lo que cambia
        su angulo de ataque local en omega*d/v y su fuerza normal en q*A*CN*omega*d/v. Esa
        fuerza, con brazo d, da un momento contrario al giro. Sumando sobre los componentes:
            C_aero = (1/2) * rho * v * A * suma( CN_i * (x_i - x_CG)^2 )

        Amortiguamiento por el chorro. Los gases que salen por la tobera se llevan momento
        angular; con flujo masico mdot y la salida de la tobera a distancia l del CG:
            C_chorro = mdot * l^2
        Solo actua mientras el motor esta encendido.

        (Coeficientes de amortiguamiento de Mandell, Caporaso y Bengen, "Topics in Advanced
        Model Rocketry", MIT Press, 1973, usados tambien por OpenRocket.)
        """
        omega = state[7]
        z = state[2]
        c_aero = 0.0
        if z <= self.atmosfera.h_max:
            _, rho, _, _ = self.atmosfera.calc_propiedades(z)
            c_aero = 0.5 * rho * np.linalg.norm(v_rel) * self.vehiculo.A * self.vehiculo.coef_amortiguamiento_aero()
        c_chorro = 0.0
        if t is not None:
            brazo_tobera = self.vehiculo.longtotal - self.vehiculo.CG[2]
            c_chorro = self.vehiculo.flujo_masico(t) * brazo_tobera**2
        return -(c_aero + c_chorro) * omega

    def accangular(self, theta, Dvec, Nvec, Gvec, Tvec, state, t=None):
        # Calcular brazo de momentos
        # r es un vector que apunta del CG al CP, en coords de cuerpo del cohete,
        grav = Gvec[2] # gravedad en z
        m= self.vehiculo.masa
        vel=state[3:6]
        omega=state[7] #velocidad angular

        # Calcular psi correctamente
        v_rel = vel - self.viento.vector
        psi = np.arctan2(v_rel[2], v_rel[0])
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

        v = np.linalg.norm(vel)
        ax = (Tvec[0] + Dvec[0] + Nvec[0]) / m
        ay = (Tvec[2] + Dvec[2] + Nvec[2] - grav) / m
        
        # Calcular la velocidad angular (psi_dot) usando la fórmula de la
        #psi_dot = (vel[0] * ay - vel[2] * ax) / (vel[0]**2 + vel[2]**2)

        #alpha = theta - psi
        #alpha_dot = omega - psi_dot

        #k_amort = 0.7
        # Calcular la amortiguación angular
        #M_amort = -k_amort * alpha_dot

        tau_tot = tau_D + tau_N  #+ np.array([0, M_amort, 0]) 
        #torcas.append((tau_D, tau_N))
        #torcas.append((tau_tot))
        #palancas.append(palanca)

        #suma de torcas/ momento de inercia total
        # se toma la componente y (perpendicular al plano de vuelo ZX) y se
        # multiplica por -1 porque el eje y apunta hacia "adentro"
        Torca = -tau_tot[1]
        # Amortiguamiento del cabeceo (aerodinamico y por el chorro del motor)
        if self.amortiguamiento:
            Torca += self.torca_amortiguamiento(t, state, v_rel)
        #Torca = Torca*10
        accang = Torca / self.vehiculo.Ix # se debe usar el momento de inercia actualizado
        #angaccels.append(accang)
        return palanca, accang, Torca

    def en_riel(self, pos):
        """El cohete sigue en el riel mientras no ha recorrido su longitud."""
        return np.linalg.norm(pos) <= self.vehiculo.riel.longitud

    def restringir_al_riel(self, pos, vel, theta, accel):
        """Aceleracion de un cohete guiado por el riel.

        El riel absorbe las fuerzas perpendiculares a su eje (la componente lateral del peso,
        el viento), asi que solo queda la componente de la aceleracion a lo largo del eje. La
        base del riel sostiene al cohete: mientras el empuje no vence al peso, no se mueve.
        """
        eje = np.array((np.cos(theta), 0.0, np.sin(theta)))
        a_eje = float(np.dot(accel, eje))
        en_la_base = np.dot(pos, eje) <= 0 and np.dot(vel, eje) <= 0
        if en_la_base and a_eje < 0:
            a_eje = 0.0
        return a_eje * eje

    def fun_derivs(self, t, state):
        # state, posicion y velocidad son estados intermedios
        #no necsariamente los del cohete
        self.evaluaciones += 1   # numero de evaluaciones de las derivadas (costo de la integracion)
        self.t_actual = t
        pos = state[0:3]
        vel = state[3:6]
        #velocidadvector.append(vel)
        theta = state[6]   # En radianes internamente siempre
        omega = state[7] #omeg a= theta dot
        # r = np.linalg.norm(pos)
        # v = np.linalg.norm(vel)
        z = pos[2] #Coordenada z

        accel = np.array([0,0,0])

        # Masa, CG e inercia del cohete en el tiempo t (consumo de propelente).
        # Se actualiza aqui, dentro de las derivadas, para que todos los integradores
        # (propios y solve_ivp) vean la masa correcta en cada evaluacion.
        self.vehiculo.actualizar_masa(t)

        # vectores para velocidad considerando el viento (funcion de t)
        v_viento = self.viento.vector_en(t, z)
        #print(v_viento)

        # Fuerzas aerodinámica: Arrastre y fuerza normal
        #print("Vectores de arrastre y normal",Dvec, Nvec)
        v_rel = vel - v_viento
        # Calcular psi (dirección de trayectoria)
        psi = np.arctan2(v_rel[2], v_rel[0])
        Dvec, Nvec = self.calc_aero(pos, v_rel, theta)

        #Calcular las componentes del empuje
        Tvec = self.calc_empuje(t, theta)
        #print(Tvec)

        # Gravedad
        grav = calc_gravedad(z + self.atmosfera.altitud_sitio)   # z se mide desde el sitio de lanzamiento
        Gvec = np.array([0,0,-grav])

        # Aceleración resultante de todas las fuerzas
        accel = Gvec + Dvec/self.vehiculo.masa + Nvec/self.vehiculo.masa + Tvec/self.vehiculo.masa

        # Parte angular
        if self.en_riel(pos):
            # En el riel el cohete no gira y solo puede deslizarse a lo largo de su eje
            omega = 0
            accang = 0
            accel = self.restringir_al_riel(pos, vel, theta, accel)
        else:
            # aceleracion angular
            _, accang, _ = self.accangular(theta, Dvec, Nvec, Gvec, Tvec, state, t)

        derivs = np.concatenate((vel, accel, [omega], [accang]))
        #print(derivs)

        return derivs

    def _evento_apogeo(self, t, state):
        # Cruce por cero (hacia abajo) de la velocidad vertical. Solo cuenta por encima
        # de 5 m para no confundirlo con el arranque en el riel (vz = 0 en t = 0).
        return state[5] if state[2] > 5 else 1.0

    def _evento_impacto(self, t, state):
        # Cruce por cero (hacia abajo) de la altitud, ignorando el primer segundo
        return state[2] if t > 1 else 1.0

    def _en_apogeo(self, t, estado):
        """Registra el apogeo y abre el drogue (y el principal, si el apogeo queda bajo su altura)."""
        altitud = estado[2]
        self.tiempo_apogeo = t
        self.apogeo = altitud
        if self.vehiculo.parachute_added:
            self.vehiculo.parachute_active1 = True
            self.apertura_drogue = self._registrar_apertura(self.vehiculo.parachute1, t, estado)
        if self._main_pendiente() and altitud <= self.vehiculo.altura_despliegue_main:
            self._abrir_main(t, estado)

    def _main_pendiente(self):
        """Hay paracaidas principal y todavia no se ha abierto."""
        return self.vehiculo.main_added and not self.vehiculo.main_active

    def _abrir_main(self, t, estado):
        self.vehiculo.main_active = True
        self.tiempo_despliegue_main = t
        self.apertura_main = self._registrar_apertura(self.vehiculo.parachute_main, t, estado)

    def _integrar_scipy(self, estado, t_max, dt, integrador):
        """Integra con solve_ivp por fases: ascenso hasta el apogeo, descenso con el drogue
        hasta la altura del paracaidas principal y descenso final hasta el impacto.

        Los paracaidas se abren entre fases, de modo que si afectan a la trayectoria.
        La integracion termina en el impacto (o en t_max si no lo hay).
        """
        tiempos = np.array([0.0])
        sim = np.array([estado], dtype=float)
        t0, y0 = 0.0, np.array(estado, dtype=float)

        def evento(funcion):
            g = lambda t, y: funcion(t, y)
            g.direction, g.terminal = -1, True
            return g

        while t0 < t_max:
            # Eventos de esta fase, con el impacto siempre al final
            fase = []
            if self.tiempo_apogeo is None:
                fase.append(("apogeo", evento(self._evento_apogeo)))
            elif self._main_pendiente():
                altura = self.vehiculo.altura_despliegue_main
                fase.append(("main", evento(lambda t, y: y[2] - altura)))
            fase.append(("impacto", evento(self._evento_impacto)))

            paso = min(dt, t_max - t0)
            solucion = solve_ivp(self.fun_derivs, (t0, t_max), y0, method=integrador,
                                 events=[g for _, g in fase], first_step=paso, max_step=dt)
            if solucion.status == -1:
                raise RuntimeError(f"solve_ivp ({integrador}) fallo: {solucion.message}")

            # El primer punto de cada fase repite el ultimo de la anterior
            tiempos = np.concatenate((tiempos, solucion.t[1:]))
            sim = np.concatenate((sim, solucion.y.T[1:]))
            t0, y0 = solucion.t[-1], solucion.y[:, -1]

            ocurridos = [nombre for (nombre, _), ts in zip(fase, solucion.t_events) if len(ts) > 0]
            if "impacto" in ocurridos:
                self.tiempo_impacto = t0
                break
            if "apogeo" in ocurridos:
                self._en_apogeo(t0, y0)
                continue
            if "main" in ocurridos:
                self._abrir_main(t0, y0)
                continue
            break   # se alcanzo t_max sin eventos

        return tiempos.tolist(), sim.tolist()

    def _integrar_propio(self, estado, t_max, dt, dt_out, integrador):
        """Integra con los metodos propios: Euler, RungeKutta2, RungeKutta4 (paso fijo) y RKF45 (adaptativo).

        dt      paso de integracion. En los metodos de paso fijo es el paso que se usa
                siempre; en RKF45 es el paso inicial y el paso maximo.
        dt_out  intervalo entre los puntos que se guardan. Para caer exactamente en cada
                tiempo de salida se acorta solo el paso que lo cruzaria, sin cambiar dt.
                Por eso conviene que dt_out sea multiplo de dt: si dt_out < dt, el paso
                efectivo queda limitado a dt_out.
        El numero de pasos dados queda en self.pasos.
        """
        clases = {'Euler': Euler, 'RungeKutta2': RungeKutta2, 'RungeKutta4': RungeKutta4, 'RKF45': RKF45}
        Integracion = clases[integrador](self.fun_derivs)
        adaptativo = hasattr(Integracion, 'dt_sugerido')

        eps = 1e-9 * max(dt, dt_out)          # tolerancia para comparar tiempos
        t = 0.0
        estado = np.array(estado, dtype=float)
        tiempos, sim = [t], [estado.copy()]
        n_out = 1                             # el siguiente tiempo de salida es n_out*dt_out
        dt_siguiente = dt
        self.pasos = 0

        while t < t_max - eps:
            next_tout = min(n_out * dt_out, t_max)
            h = min(dt_siguiente, dt, next_tout - t)
            if next_tout - (t + h) < eps:     # no dejar un resto diminuto antes de la salida
                h = next_tout - t

            nuevo_estado, usado = Integracion.step(t, estado, h)
            self.pasos += 1
            t_nuevo = t + usado
            en_salida = abs(t_nuevo - next_tout) < eps
            if en_salida:
                t_nuevo = next_tout
            if adaptativo:
                dt_siguiente = Integracion.dt_sugerido
            altitud = nuevo_estado[2]

            # Apogeo
            if self.tiempo_apogeo is None and altitud > 5 and altitud < estado[2]:
                self._en_apogeo(t_nuevo, nuevo_estado)       # abre el drogue
            # Paracaidas principal: al bajar por su altura de despliegue
            elif self.tiempo_apogeo is not None and self._main_pendiente() and altitud <= self.vehiculo.altura_despliegue_main:
                self._abrir_main(t_nuevo, nuevo_estado)

            # Impacto: se interpola linealmente dentro del paso hasta z = 0
            if altitud < 0 and t_nuevo > 1:
                z_antes = estado[2]
                f = z_antes / (z_antes - altitud) if z_antes > 0 else 0.0
                estado_impacto = estado + f * (nuevo_estado - estado)
                estado_impacto[2] = 0.0
                self.tiempo_impacto = t + f * (t_nuevo - t)
                tiempos.append(self.tiempo_impacto)
                sim.append(estado_impacto)
                break

            t, estado = t_nuevo, nuevo_estado
            if en_salida:
                tiempos.append(t)
                sim.append(estado.copy())
                n_out += 1

            if self.pasos % 2500 == 0:
                print(f"Paso={self.pasos}, t={t:.1f}s, dt={usado:g}, altitud={altitud:.1f}m, vel vert={estado[5]:.1f}")

        return tiempos, sim

    def simular_vuelo(self, estado, t_max, dt, dt_out, integrador):
        # Listas de integradores
        propios_integ = ['Euler', 'RungeKutta2', 'RungeKutta4', 'RKF45']
        python_integ = ['RK45', 'RK23', 'DOP853', 'LSODA', 'BDF']

        # Estado inicial de la simulacion (permite repetir vuelos con el mismo objeto)
        self.tiempo_salida_riel = None
        self.tiempo_apogeo = None
        self.tiempo_impacto = None
        self.apogeo = None
        self.impacto = None
        self.vehiculo.parachute_active1 = False
        self.vehiculo.main_active = False
        self.tiempo_despliegue_main = None
        self.apertura_drogue = None
        self.apertura_main = None
        self.vehiculo.actualizar_masa(0.0)
        self.viento.reiniciar_rafagas()
        self.pasos = 0
        self.evaluaciones = 0

        if integrador in propios_integ:
            print(f"Integrador propio detectado: {integrador}")
            tiempos, sim = self._integrar_propio(estado, t_max, dt, dt_out, integrador)
        elif integrador in python_integ:
            print(f"Integrador Python detectado: {integrador}")
            tiempos, sim = self._integrar_scipy(estado, t_max, dt, integrador)
            self.pasos = len(tiempos) - 1
        else:
            raise ValueError(f"Integrador '{integrador}' no reconocido")

        # Cantidades derivadas, evaluadas sobre la trayectoria ya integrada con las
        # mismas funciones de t (masa, viento, paracaidas) que uso la integracion
        Tvecs, Dvecs, Nvecs = [], [], []
        accels, palancas, accangs, torcas = [], [], [], []
        Gammas, Alphas = [], []
        Cds, Machs = [], []
        CPs, CGs, masavuelo = [], [], []
        viento_vuelo_mags, viento_vuelo_dirs, viento_vuelo_vecs = [], [], []

        self.fuerzas_paracaidas = []   # fuerza de los paracaidas en cada punto guardado [N]
        for t, estado in zip(tiempos, sim):
            estado = np.asarray(estado)
            pos = estado[0:3]
            vel = estado[3:6]
            theta = estado[6]
            altitud = pos[2]

            self.t_actual = t
            self.vehiculo.actualizar_masa(t)
            self.vehiculo.parachute_active1 = bool(
                self.vehiculo.parachute_added
                and self.tiempo_apogeo is not None and t >= self.tiempo_apogeo)
            self.vehiculo.main_active = bool(
                self.vehiculo.main_added
                and self.tiempo_despliegue_main is not None and t >= self.tiempo_despliegue_main)
            v_viento = self.viento.vector_en(t, altitud)

            # Salida del riel
            if self.tiempo_salida_riel is None and np.linalg.norm(pos) > self.vehiculo.riel.longitud:
                self.tiempo_salida_riel = t

            masavuelo.append(self.vehiculo.masa)
            CPs.append(self.vehiculo.CP[2])
            CGs.append(self.vehiculo.CG[2])
            viento_vuelo_vecs.append(v_viento)
            viento_vuelo_mags.append(self.viento.magnitud_total)
            viento_vuelo_dirs.append(self.viento.direccion_total)

            vrel = vel - v_viento
            gamma = math.atan2(vel[2], vel[0])
            alpha = self.calc_alpha(vrel, theta)
            Gammas.append(gamma)
            Alphas.append(alpha)

            Tvec = self.calc_empuje(t, theta)
            _, _, Cd, mach = self.calc_arrastre_normal(pos, vrel, alpha)
            Dvec, Nvec = self.calc_aero(pos, vrel, theta)
            self.fuerzas_paracaidas.append(self.fuerza_paracaidas)
            Tvecs.append(Tvec)
            Dvecs.append(Dvec)
            Nvecs.append(Nvec)
            Cds.append(Cd)
            Machs.append(mach)

            grav = calc_gravedad(altitud + self.atmosfera.altitud_sitio)
            Gvec = np.array([0, 0, -grav])

            accel = Gvec + Dvec/self.vehiculo.masa + Nvec/self.vehiculo.masa + Tvec/self.vehiculo.masa
            palanca, accang, torca = self.accangular(theta, Dvec, Nvec, Gvec, Tvec, estado, t)
            if self.en_riel(pos):
                accel = self.restringir_al_riel(pos, vel, theta, accel)
                accang = 0.0
            accels.append(accel)
            palancas.append(palanca)
            accangs.append(accang)
            torcas.append(torca)

        return tiempos, sim, CPs, CGs, masavuelo, viento_vuelo_mags, viento_vuelo_dirs, viento_vuelo_vecs, Tvecs, Dvecs, Nvecs, accels, palancas, accangs, Gammas, Alphas, torcas, Cds, Machs
