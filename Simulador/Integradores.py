import numpy as np
import matplotlib.pyplot as plt
from numpy import *

class Euler:
    def __init__(self, fun_derivs):
        self.fun_derivadas = fun_derivs

    def step(self, t, state, dt):
        #Aplicar método de Euler para obtener nuevo estado
        state_new = state + (dt * self.fun_derivadas(t, state))
        return state_new
    

class RungeKutta4:
    def __init__(self, fun_derivs):
        self.fun_derivadas = fun_derivs

    def step(self, t, state, dt):
        k1 = self.fun_derivadas(t, state)
        k2 = self.fun_derivadas(t + dt/2, state + k1 * dt/2)
        k3 = self.fun_derivadas(t + dt/2, state + k2 * dt/2)
        k4 = self.fun_derivadas(t + dt, state + k3 * dt)
        new_state = state + dt * (k1 + 2*k2 + 2*k3 + k4) / 6
        return new_state
    
# 3. Método de Runge-Kutt-Fehlberg 45
class RKF45:
    def __init__(self, fun_derivs):
        self.fun_derivadas = fun_derivs

    def step(self, t, state, dt, tol=1e-4, S=0.9):

        retry = True
        while retry:
          k1 = self.fun_derivadas(t, state)
          k2 = self.fun_derivadas(t + dt/4, state + (k1 * dt/4))
          k3 = self.fun_derivadas(t + (dt*3/8), state + (k1*3/32) + (k2*9/32) )
          k4 = self.fun_derivadas(t + (dt*12/13), state + (k1*1932/2197) - (k2*7200/2197) + (k3*7296/2197))
          k5 = self.fun_derivadas(t + dt, state + (k1*439/216) - (k2*8) + (k3*3680/513) - (k4*845/4104))
          k6 = self.fun_derivadas(t + dt/2, state - (k1*8/27) + (k2 *2) -  (k3*3544/2565) + (k4 *1859/4104) - (k5 *11/40))

          ykp = state + dt * (25/216*k1 + 1408/2565*k3 + 2197/4101*k4 - k5/5)
          zkp = state + dt * (16/135*k1 + 6656/12825*k3 + 28561/56430*k4 - 9/50*k5 + 2/55*k6)

          errs = np.abs(zkp - ykp)
          errmax = max(errs)

          if errmax < 1:
            # Errores aceptables, ya no iterar más, aumentar dt
            dt_nuevo = min(S*dt*errmax**0.25, 5*dt)
            retry = False
          else:
            # Errores demasiado grandes, reducir dt y repetir paso
            dt_nuevo = max(S*dt*errmax**0.4, dt/10)
            retry = True

        return zkp, dt_nuevo