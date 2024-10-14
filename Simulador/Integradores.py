import numpy as np
import matplotlib.pyplot as plt

# 1. Método de Euler
class Euler:
    def __init__(self, fun_derivs):
        self.fun_derivadas = fun_derivs

    def step(self, t, state, dt):
        #Aplicar método de Euler para obtener nuevo estado
        state_new = state + (dt * self.fun_derivadas(t, state))
        return state_new, dt
    
#2. Runge-Kutta 4
class RungeKutta4:
    def __init__(self, fun_derivs):
        self.fun_derivadas = fun_derivs
    
    def step(self, t, state, dt):
        k1 = self.fun_derivadas(t, state)
        k2 = self.fun_derivadas(t + dt/2, state + k1 * dt/2)
        k3 = self.fun_derivadas(t + dt/2, state + k2 * dt/2)
        k4 = self.fun_derivadas(t + dt, state + k3 * dt)
        new_state = state + dt * (k1 + 2*k2 + 2*k3 + k4) / 6
        return new_state, dt

# 3. Runge-Kutta 2
class RungeKutta2:
    def __init__(self, fun_derivs):
        self.fun_derivadas = fun_derivs

    def step(self, t, state, dt):
        k1 = self.fun_derivadas(t, state)
        k2 = self.fun_derivadas(t + dt, state + k1 * dt)
        new_state = state + dt * (k1 + k2) / 2
        return new_state, dt
        
# 4. Método de Runge-Kutt-Fehlberg 45
class RKF45:
    def __init__(self, fun_derivs):
        self.fun_derivadas = fun_derivs
        self.tol=1e-3
        self.S= 0.8

    def step(self, t, state, dt):
        tol=self.tol
        #S=self.S #no se ocupa???

        retry = True
        while retry:
            k1 = dt*self.fun_derivadas(t, state)
            k2 = dt*self.fun_derivadas(t + dt/4, state + (k1/4))
            k3 = dt*self.fun_derivadas(t + (dt*3/8), state + (k1*3/32) + (k2*9/32) )
            k4 = dt*self.fun_derivadas(t + (dt*12/13), state + (k1*1932/2197) - (k2*7200/2197) + (k3*7296/2197))
            k5 = dt*self.fun_derivadas(t + dt, state + (k1*439/216) - (k2*8) + (k3*3680/513) - (k4*845/4104))
            k6 = dt*self.fun_derivadas(t + dt/2, state - (k1*8/27) + (k2 *2) -  (k3*3544/2565) + (k4*1859/4104) - (k5*11/40))

            ykp = state + 25/216*k1 + 1408/2565*k3 + 2197/4101*k4 - k5/5
            zkp = state + 16/135*k1 + 6656/12825*k3 + 28561/56430*k4 - 9/50*k5 + 2/55*k6

            errs = np.abs(zkp - ykp)
            errmax = max(errs)
            #print("errmax={} {} tol={}".format(errmax, ">" if errmax>tol else "<", tol))
            # print("dt_nuevo=", dt_nuevo)

            if errmax < tol:
                # Errores aceptables, ya no iterar más, aumentar dt
                #print("Error aceptable")
                retry = False
            else:
                # Errores demasiado grandes, reducir dt y repetir paso
                #print("Error no aceptable, repitiendo iteración")
                dt_nuevo = dt * (tol / (2*errmax))**0.25
                retry = True
                dt = dt_nuevo

        return zkp, dt
    
#Metodo de Euler adaptivo
class AdaptiveEuler:
    def __init__(self, fun_derivs):
        self.fun_derivadas = fun_derivs
        self.tol = 1e-3
        self.S = 0.8

    def step(self, t, state, dt):
        retry = True
        tol = self.tol
        S = self.S
        
        while retry:
            # Estimar el paso de Euler con un paso completo
            state_full = state + dt * self.fun_derivadas(t, state)

            # Estimar el paso de Euler con dos pasos a la mitad
            dt_half = dt / 2
            state_half = state + dt_half * self.fun_derivadas(t, state)
            state_half = state_half + dt_half * self.fun_derivadas(t + dt_half, state_half)

            # Calcular el error
            error = np.linalg.norm(state_half - state_full)

            # Calcular nuevo tamaño de paso basado en el error
            if error < tol:
                # Si el error es aceptable, incrementar el tamaño del paso
                dt_new = S * dt * (tol / error) ** 0.5
                retry = False  # No necesitamos repetir el paso
                return state_full, dt_new
            else:
                # Si el error es demasiado grande, reducir el tamaño del paso y repetir
                dt_new = S * dt * (tol / error) ** 0.5
                dt = dt_new  # Actualizar dt para el próximo intento
