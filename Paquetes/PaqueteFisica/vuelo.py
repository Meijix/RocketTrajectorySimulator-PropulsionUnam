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
from Paquetes.PaqueteEDOs.integradores import Euler, RungeKutta2, RungeKutta4, RKF45, AdaptiveEuler

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
        self.apogeo = None
        self.impacto = None

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
        CNalpha = self.vehiculo.CN
        A = self.vehiculo.A
        # DEBUG: aumentar Cd
        # Cd *= 5
        f_arrastre = (0.5 * rho * vel_mag**2) * A * Cd 
        # f_normal = 0.5 * rho * CN * A * vel_mag**2 * np.sin(alpha)**2
        # f_normal = 0.5 * rho * CN * A * vel_mag**2 * np.sin(alpha)**2
        f_normal = (0.5 * rho * vel_mag**2) * A * abs(np.sin(alpha)) * CNalpha

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
        Nhat = -np.sign(alpha) * np.array((v_rel_hat[2], v_rel_hat[1], -v_rel_hat[0]))
        # Nmag = 0    # DEBUG: apagar normal
        Nvec = Nmag * Nhat
        # print("alpha=", degrees(alpha))
        # print("Arrastre:", Dmag, Dvec)
        # print("Normal:", Nmag, Nvec)
        # input()
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

        # vectores para velocidad considerando el viento
        v_viento = self.viento.vector
        #print(v_viento)

        # Fuerzas aerodinámica: Arrastre y fuerza normal
        #print("Vectores de arrastre y normal",Dvec, Nvec)
        v_rel = vel - v_viento
        Dvec, Nvec = self.calc_aero(pos, v_rel, theta)

        #Calcular las componentes del empuje
        Tvec = self.calc_empuje(t, theta)
        #print(Tvec)

        # Gravedad
        grav = calc_gravedad(z)
        Gvec = np.array([0,0,-grav])

        # Aceleración resultante de todas las fuerzas
        accel = Gvec + Dvec/self.vehiculo.masa + Nvec/self.vehiculo.masa + Tvec/self.vehiculo.masa

        # Parte angular
        r = np.linalg.norm(pos)
        #esto esta bien?
        if r <= self.vehiculo.riel.longitud:
            omega = 0
            accang = 0
        else:
            #Velocidad angular
            velang = omega
            # aceleracion angular
            _, accang, _ = self.accangular(theta, Dvec, Nvec, Gvec)

        # PRUEBA: apagar parte angular
        # omega = 0
        # accang= 0

        derivs = np.concatenate((vel, accel, [omega], [accang]))
        #print(derivs)

        return derivs

    def simular_vuelo(self, estado, t_max, dt, dt_out, integrador):

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

        propios_integ = ['Euler', 'RungeKutta2', 'RungeKutta4', 'RKF45', 'AdaptiveEuler']
        python_integ = ['RK45', 'RK23', 'DOP853', 'LSODA', 'BDF', 'Radau']
        
        ##########################################
        # print("t=", t)
            # -------------------------
            # Integraccion con metodos propios
            # -------------------------
        if integrador in propios_integ:
            print("Integrador propio detectado")
            it = 0
            next_tout = dt_out
            t = 0.0
            ultima_altitud = 0

            sim=[estado] #lista de estados de vuelo
            tiempos=[0] #lista de tiempos

            #Actualizar masa del vehiculo
            print("Actualizando masa")
            self.vehiculo.actualizar_masa(t)
            masavuelo=[self.vehiculo.masa]

            self.vehiculo.parachute_active1 = False
            #print(self.vehiculo.parachute_active1)

            #Iniciar ciclo
            while t <= t_max:
                

                if t + dt > next_tout:
                    dt = next_tout - t
                else:
                    pass
                #########################################
                #CAMBIO DE METODO DE INTEGRACIÓN
                print("Integrando")
                if integrador == 'Euler':
                    Integracion = Euler(self.fun_derivs) #ocupa dt=0.005
                elif integrador == 'RungeKutta2':
                    Integracion = RungeKutta2(self.fun_derivs)
                elif integrador == 'RungeKutta4':
                    Integracion = RungeKutta4(self.fun_derivs)
                elif integrador == 'RKF45':
                    Integracion = RKF45(self.fun_derivs)
                elif integrador == 'AdaptiveEuler':
                    Integracion = AdaptiveEuler(self.fun_derivs)
                
                #el dt_new se usa para que el inetgrador actualize el paso de tiempo
                nuevo_estado, dt = Integracion.step(t, estado, dt)
                #else:
                #nuevo_estado, dt = Integracion.step(t, estado, dt, tol=1e-4, S=0.9)
                # print("dt_new={}".format(dt_new))
                #dt = dt_new
                #print("dt= ", dt)

                # Avanzar estado
                print("Avanzando estado")
                it += 1
                t += dt
                estado = nuevo_estado

            # -------------------------
            # Actualizar variables (viento, masa del vehiculo, etc)

            # Actualizar masa del vehiculo
            print("Actualizando masa 2")
            self.vehiculo.actualizar_masa(t)

            # Actualizar viento_actual
            #self.viento.actualizar_viento2D()
            print("Actualizando viento")
            self.viento.actualizar_viento3D()
            #print("Nuevos vientos", self.viento)
            v_viento = self.viento.vector

            #FASE 1. VUELO EN RIEL
            print("Revisando vuelo en riel")
            if self.tiempo_salida_riel is None:
                r = np.linalg.norm(estado[0:3])
                if r > self.vehiculo.riel.longitud:
                    self.tiempo_salida_riel = t
            
            #FASE 2. MECO

            # APOGEO: Determinar tiempo de apogeo
            print("Revisando apogeo")
            altitud = estado[2]
            if self.tiempo_apogeo is None and altitud > 5 and altitud < ultima_altitud:
                self.tiempo_apogeo = t
                self.apogeo = altitud

            ultima_altitud = altitud

            #FASE3.RECUPERACIÓN
            #FALTA IMPLEMENTAR RECUPERACION DE DOS ETAPAS JE
            #activar el paracaidas en el apogeo
            print("Revisando recuperacion")
            if self.tiempo_apogeo is not None and self.vehiculo.parachute_added == True:
                #print(self.vehiculo.parachute_active1,"antes")
                self.vehiculo.parachute_active1 = True
                #print(self.vehiculo.parachute_active1,"despues")
                #print("Se ha abierto el paracaídas")
                #self.vehiculo.activar_paracaidas(self.vehiculo.parachute1)
            else:
                pass

            #CAIDA: Terminar simulación cuando cae al piso
            print("Revisando caida")
            if estado[2] < 0 and t > 1:
                self.tiempo_impacto = t

            # -------------------------
            # Guardar cantidades en listas
            if t >= next_tout:

                next_tout += dt_out

            #Agrega el nuevo estado a la lista
            print("Guardando datos")
            sim.append(nuevo_estado)
            tiempos.append(t)

            #Guardar centros de presión y centros de gravedad
            CPs.append(self.vehiculo.CP[2])
            CGs.append(self.vehiculo.CG[2])

            #Guardar magnitudes y direcciones del viento
            viento_vuelo_vecs.append(v_viento)
            viento_vuelo_mags.append(self.viento.magnitud_total)
            viento_vuelo_dirs.append(self.viento.direccion_total)
            
            #Agregar nueva masa a la lista
            masavuelo.append(self.vehiculo.masa)    

            #CALCULAR CANTIDADES SECUNDARIAS
            # Desempaquetar vector de estado      
            pos = nuevo_estado[0:3]
            vel = nuevo_estado[3:6]
            theta = nuevo_estado[6]   # En radianes internamente siempre
            omega = nuevo_estado[7] #omeg a= theta dot
            r = np.linalg.norm(pos)
            #v = np.linalg.norm(vel)
            z = pos[2] #Coordenada z

            vrel = np.array(vel) - v_viento
            #print("viento relativo: ", vrel)

            #Guardar Angulos
            gamma = math.atan2(vel[2], vel[0])
            alpha = self.calc_alpha(vrel, theta)
            Gammas.append(gamma)
            Alphas.append(alpha)

            #Guardar Fuerzas:Empuje,Arrastre y Normal
            Tvec = self.calc_empuje(t, theta)
            _, _, Cd, mach = self.calc_arrastre_normal(pos, vrel, alpha)
            Dvec, Nvec = self.calc_aero(pos, vrel, theta)
            Tvecs.append(Tvec)
            Dvecs.append(Dvec)
            Nvecs.append(Nvec)
            Cds.append(Cd)
            Machs.append(mach)

            # Gravedad
            grav = calc_gravedad(z)
            #Cambiar la direccion de la gravedad cuando esta en el riel
            #if r< #longitud del riel
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
            if it%2500==0:
                print('Simulando con método propio')
                print(f"Iter= {it}, t={t:.1f} s, dt={dt:g}, altitud={altitud:.1f} m, vel vert={estado[5]:.1f}")
        # -------------------------
        # Integración con scipy solve_ivp
        # -------------------------
        elif integrador in python_integ:
            print("Integrador python detectado")
            solucion = solve_ivp(self.fun_derivs, (t, t+dt), estado, method=integrador, dense_output=True, first_step=dt, max_step=dt)

            time = solucion.t
            sol_estado = solucion.y
            #print(estado)
            #print(t)

            # -------------------------
            # Actualizar variables (viento, masa del vehiculo, etc)
            for i in range(len(time)):
                t = time[i]
                estado = sol_estado[:,i]

                # Actualizar masa del vehiculo
                self.vehiculo.actualizar_masa(t)

                # Actualizar viento_actual
                #self.viento.actualizar_viento2D()
                self.viento.actualizar_viento3D()
                #print("Nuevos vientos", self.viento)
                v_viento = self.viento.vector

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
                #FALTA IMPLEMENTAR RECUPERACION DE DOS ETAPAS JE
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

                #Guardar centros de presión y centros de gravedad
                CPs.append(self.vehiculo.CP[2])
                CGs.append(self.vehiculo.CG[2])

                #Guardar magnitudes y direcciones del viento
                viento_vuelo_vecs.append(v_viento)
                viento_vuelo_mags.append(self.viento.magnitud_total)
                viento_vuelo_dirs.append(self.viento.direccion_total)
                
                #Agregar nueva masa a la lista
                masavuelo.append(self.vehiculo.masa)    

                #CALCULAR CANTIDADES SECUNDARIAS
                # Desempaquetar vector de estado      
                pos = nuevo_estado[0:3]
                vel = nuevo_estado[3:6]
                theta = nuevo_estado[6]   # En radianes internamente siempre
                omega = nuevo_estado[7] #omeg a= theta dot
                r = np.linalg.norm(pos)
                #v = np.linalg.norm(vel)
                z = pos[2] #Coordenada z

                vrel = np.array(vel) - v_viento
                #print("viento relativo: ", vrel)

                #Guardar Angulos
                gamma = math.atan2(vel[2], vel[0])
                alpha = self.calc_alpha(vrel, theta)
                Gammas.append(gamma)
                Alphas.append(alpha)

                #Guardar Fuerzas:Empuje,Arrastre y Normal
                Tvec = self.calc_empuje(t, theta)
                _, _, Cd, mach = self.calc_arrastre_normal(pos, vrel, alpha)
                Dvec, Nvec = self.calc_aero(pos, vrel, theta)
                Tvecs.append(Tvec)
                Dvecs.append(Dvec)
                Nvecs.append(Nvec)
                Cds.append(Cd)
                Machs.append(mach)

                # Gravedad
                grav = calc_gravedad(z)
                #Cambiar la direccion de la gravedad cuando esta en el riel
                #if r< #longitud del riel
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
                if it%2500==0:
                    print('Simulando con scipy.solve_ivp')
                    print(f"Iter= {it}, t={t:.1f} s, dt={dt:g}, altitud={altitud:.1f} m, vel vert={estado[5]:.1f}")
        else:
            raise ValueError(f"Integrador '{integrador}' no reconocido")

        return tiempos, sim, CPs, CGs, masavuelo, viento_vuelo_mags, viento_vuelo_dirs, viento_vuelo_vecs, Tvecs, Dvecs, Nvecs, accels, palancas, accangs, Gammas, Alphas, torcas, Cds, Machs
