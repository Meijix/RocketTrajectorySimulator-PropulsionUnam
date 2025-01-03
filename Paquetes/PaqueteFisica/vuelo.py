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
        Tmag = self.vehiculo.calc_empuje_magn(t)#*0.7 #factor de eficiencia
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
        # Inicialización de listas para almacenar resultados
        Tvecs, Dvecs, Nvecs = [], [], []
        accels, palancas, accangs, torcas = [], [], [], []
        Gammas, Alphas = [], []
        Cds, Machs = [], []
        CPs, CGs, masavuelo = [], [], []
        viento_vuelo_mags, viento_vuelo_dirs, viento_vuelo_vecs = [], [], []

        # Listas de integradores
        propios_integ = ['Euler', 'RungeKutta2', 'RungeKutta4']#, 'RKF45', 'AdaptiveEuler']
        python_integ = ['RK45', 'RK23', 'DOP853', 'LSODA', 'BDF']

        # Métodos propios de integración
        if integrador in propios_integ:
            print(f"Integrador propio detectado: {integrador}")
            t, it, next_tout = 0.0, 0, dt_out
            #sim, tiempos = [estado], [0]
            sim, tiempos= [], []
            ultima_altitud = 0

            # Actualización inicial de la masa
            self.vehiculo.actualizar_masa(t)
            #masavuelo.append(self.vehiculo.masa)
            self.vehiculo.parachute_active1 = False

            # Selección del integrador
            integradores = {
                'Euler': Euler(self.fun_derivs),
                'RungeKutta2': RungeKutta2(self.fun_derivs),
                'RungeKutta4': RungeKutta4(self.fun_derivs),
                'RKF45': RKF45(self.fun_derivs),
                'AdaptiveEuler': AdaptiveEuler(self.fun_derivs),
            }
            Integracion = integradores[integrador]

            #print(f"Iniciando ciclo con {integrador}")
            while t <= t_max:
                
                if t + dt > next_tout:
                    dt = next_tout - t

                nuevo_estado, dt = Integracion.step(t, estado, dt)
                t += dt
                estado = nuevo_estado

                # Actualizar variables
                self.vehiculo.actualizar_masa(t)
                self.viento.actualizar_viento3D()
                v_viento = self.viento.vector

                # Fases del vuelo
                r = np.linalg.norm(estado[0:3])
                altitud = estado[2]

                # Salida del riel
                if self.tiempo_salida_riel is None and r > self.vehiculo.riel.longitud:
                    self.tiempo_salida_riel = t

                # Apogeo
                if self.tiempo_apogeo is None and altitud > 5 and altitud < ultima_altitud:
                    self.tiempo_apogeo = t
                    self.apogeo = altitud

                ultima_altitud = altitud

                # Recuperación
                if self.tiempo_apogeo is not None and self.vehiculo.parachute_added:
                    self.vehiculo.parachute_active1 = True

                # Impacto
                if estado[2] < 0 and t > 1:
                    self.tiempo_impacto = t
                    break

                # Guardar datos
                if t >= next_tout:
                    next_tout += dt_out

                masavuelo.append(self.vehiculo.masa)
                sim.append(nuevo_estado)
                tiempos.append(t)
                CPs.append(self.vehiculo.CP[2])
                CGs.append(self.vehiculo.CG[2])
                viento_vuelo_vecs.append(v_viento)
                viento_vuelo_mags.append(self.viento.magnitud_total)
                viento_vuelo_dirs.append(self.viento.direccion_total)

                # Cálculos secundarios
                pos = estado[0:3]
                vel = estado[3:6]
                theta = estado[6]
                vrel = np.array(vel) - v_viento

                gamma = math.atan2(vel[2], vel[0])
                alpha = self.calc_alpha(vrel, theta)
                Gammas.append(gamma)
                Alphas.append(alpha)

                Tvec = self.calc_empuje(t, theta)
                _, _, Cd, mach = self.calc_arrastre_normal(pos, vrel, alpha)
                Dvec, Nvec = self.calc_aero(pos, vrel, theta)
                Tvecs.append(Tvec)
                Dvecs.append(Dvec)
                Nvecs.append(Nvec)
                Cds.append(Cd)
                Machs.append(mach)

                grav = calc_gravedad(altitud)
                Gvec = np.array([0, 0, -grav])

                accel = Gvec + Dvec/self.vehiculo.masa + Nvec/self.vehiculo.masa + Tvec/self.vehiculo.masa
                accels.append(accel)

                palanca, accang, torca = self.accangular(theta, Dvec, Nvec, Gvec)
                palancas.append(palanca)
                accangs.append(accang)
                torcas.append(torca)

                if it % 2500 == 0:
                    print(f"Iter={it}, t={t:.1f}s, dt={dt:g}, altitud={altitud:.1f}m, vel vert={estado[5]:.1f}")
                it += 1

        # Métodos de Python (solve_ivp)
        elif integrador in python_integ:
            print(f"Integrador Python detectado: {integrador}")
            solucion = solve_ivp(self.fun_derivs, (0, t_max), estado, method=integrador, dense_output=True, first_step=dt, max_step=dt)

            tiempos = solucion.t.tolist()
            sim = solucion.y.T.tolist()
            ultima_altitud = 0

            for k, t in enumerate(tiempos):
                estado = solucion.y[:, k]

                # Actualizar variables
                self.vehiculo.actualizar_masa(t)
                self.viento.actualizar_viento3D()
                v_viento = self.viento.vector

                r = np.linalg.norm(estado[0:3])
                altitud = estado[2]

                if self.tiempo_salida_riel is None and r > self.vehiculo.riel.longitud:
                    self.tiempo_salida_riel = t

                if self.tiempo_apogeo is None and altitud > 5 and altitud < ultima_altitud:
                    self.tiempo_apogeo = t
                    self.apogeo = altitud

                ultima_altitud = altitud

                if self.tiempo_apogeo is not None and self.vehiculo.parachute_added:
                    self.vehiculo.parachute_active1 = True

                if altitud < 0 and t > 1:
                    self.tiempo_impacto = t
                    iteracion_final = k
                    break

                # Guardar datos
                CPs.append(self.vehiculo.CP[2])
                CGs.append(self.vehiculo.CG[2])
                viento_vuelo_vecs.append(v_viento)
                viento_vuelo_mags.append(self.viento.magnitud_total)
                viento_vuelo_dirs.append(self.viento.direccion_total)
                masavuelo.append(self.vehiculo.masa)

                pos = estado[0:3]
                vel = estado[3:6]
                theta = estado[6]
                vrel = np.array(vel) - v_viento

                gamma = math.atan2(vel[2], vel[0])
                alpha = self.calc_alpha(vrel, theta)
                Gammas.append(gamma)
                Alphas.append(alpha)

                Tvec = self.calc_empuje(t, theta)
                _, _, Cd, mach = self.calc_arrastre_normal(pos, vrel, alpha)
                Dvec, Nvec = self.calc_aero(pos, vrel, theta)
                Tvecs.append(Tvec)
                Dvecs.append(Dvec)
                Nvecs.append(Nvec)
                Cds.append(Cd)
                Machs.append(mach)

                grav = calc_gravedad(altitud)
                Gvec = np.array([0, 0, -grav])

                accel = Gvec + Dvec/self.vehiculo.masa + Nvec/self.vehiculo.masa + Tvec/self.vehiculo.masa
                accels.append(accel)

                palanca, accang, torca = self.accangular(theta, Dvec, Nvec, Gvec)
                palancas.append(palanca)
                accangs.append(accang)
                torcas.append(torca)
                

            #solo tiempos y sim hasta el impacto
            tiempos=tiempos[:iteracion_final]
            sim=sim[:iteracion_final]

        else:
            raise ValueError(f"Integrador '{integrador}' no reconocido")

        return tiempos, sim, CPs, CGs, masavuelo, viento_vuelo_mags, viento_vuelo_dirs, viento_vuelo_vecs, Tvecs, Dvecs, Nvecs, accels, palancas, accangs, Gammas, Alphas, torcas, Cds, Machs
