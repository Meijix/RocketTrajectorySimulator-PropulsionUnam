from scipy.integrate import solve_ivp
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
        self.tol=1e-2
        self.S= 0.9

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

#############################################
#Metodo de Euler adaptivo
class AdaptiveEuler:
    def __init__(self, fun_derivs):
        self.fun_derivadas = fun_derivs
        self.tol = 1e-4
        self.S = 0.9

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

#Metodo de Runge-Kutta 4 adaptivo
class AdaptiveRungeKutta4:
    def __init__(self, fun_derivs):
        self.fun_derivadas = fun_derivs
        self.tol = 1
        self.S = 0.9

    def step(self, t, state, dt):
        retry = True
        tol = self.tol
        S = self.S

        while retry:
            # Estimar el paso de Runge-Kutta 4 con un paso completo
            k1 = self.fun_derivadas(t, state)
            k2 = self.fun_derivadas(t + 0.5 * dt, state +
                                    0.5 * dt * k1)
            k3 = self.fun_derivadas(t + 0.5 * dt, state +
                                    0.5 * dt * k2)
            k4 = self.fun_derivadas(t + dt, state + dt * k3)
            state_full = state + dt * (k1 + 2 * k2 + 2 * k3 + k4) / 6

            # Estimar el paso de Runge-Kutta 4 con dos pasos a la mitad
            dt_half = dt / 2
            k1_half = self.fun_derivadas(t, state)
            k2_half = self.fun_derivadas(t + 0.5 * dt_half, state + 0.5 * dt_half * k1_half)
            k3_half = self.fun_derivadas(t + 0.5 * dt_half, state + 0.5 * dt_half * k2_half)
            k4_half = self.fun_derivadas(t + dt_half, state + dt_half * k3_half)
            state_half = state + dt_half * (k1_half + 2 * k2_half + 2 * k3_half + k4_half) / 6
            state_half = state_half + dt_half * (k1_half + 2 * k2_half + 2 * k3_half + k4_half) / 6
            # Calcular el error
            error = np.linalg.norm(state_half - state_full)
            # Calcular nuevo tamaño de paso basado en el error
            if error < tol:
                # Si el error es aceptable, incrementar el tamaño del paso
                print('Error aceptable--Incrementando tamaño del paso')
                dt_new = S * dt * (tol / error) ** 0.5
                retry = False  # No necesitamos repetir el paso
                print('Avanzando...con dt_new', dt_new)
                return state_full, dt_new
            else:
                # Si el error es demasiado grande, reducir el tamaño del paso y repetir
                print('Error no aceptable--Reduciendo tamaño del paso')
                dt_new = S * dt * (tol / error) ** 0.5
                dt = dt_new  # Actualizar dt para el próximo intento

#Metodo de Runge-Kutta 2 adaptivo
class AdaptiveRungeKutta2:
    def __init__(self, fun_derivs):
        self.fun_derivadas = fun_derivs
        self.tol = 1e-4
        self.S = 0.9

    def step(self, t, state, dt):
        # Estimar el paso de Runge-Kutta 2 con un paso completo
        k1 = self.fun_derivadas(t, state)
        k2 = self.fun_derivadas(t + dt, state + dt * k1)
        state_full = state + dt * (k1 + k2) / 2
        # Calcular el error
        error = np.linalg.norm(k2 - k1)
        # Calcular nuevo tamaño de paso basado en el error
        if error < self.tol:
            # Si el error es aceptable, incrementar el tamaño del paso
            dt_new = self.S * dt * (self.tol / error) ** 0.5
            return state_full, dt_new
        else:
            # Si el error es demasiado grande, reducir el tamaño del paso y repetir
            dt_new = self.S * dt * (self.tol / error) ** 0.5
            return state, dt_new
## Metodo Dormand-Prince 853
class DormanPrince853:
    def __init__(self, fun_derivs, tol=1e-4, S=0.9):
        self.fun_derivadas = fun_derivs
        self.tol = tol
        self.S = S

    def step(self, t, state, dt):
        # Estimar el paso de Runge-Kutta 2 con un paso completo
        k1 = self.fun_derivadas(t, state)
        k2 = self.fun_derivadas(t + dt, state + dt * k1)
        state_full = state + dt * (k1 + k2) / 2
        # Calcular el error
        error = np.linalg.norm(k2 - k1)
        # Calcular nuevo tamaño de paso basado en el error
        if error < self.tol:
            # Si el error es aceptable, incrementar el tamaño del paso
            dt_new = self.S * dt * (self.tol / error) ** 0.5
            return state_full, dt_new
        else:
            # Si el error es demasiado grande, reducir el tamaño del paso y repetir
            dt_new = self.S * dt * (self.tol / error) ** 0.5
            return state, dt_new


if __name__ == '__main__':
    #Ejemplo para los metodos adptivos
    #FUNCION SIMPLE DE DERIVADAS
    # Definir la función de derivadas
    def fun_derivadas_ejemplo(t, state):
        # Derivadas de x, y, z
        x = state[0]
        y = state[1]
        z = state[2]
        dxdt = -y
        dydt = x
        dzdt = -z
        return np.array([dxdt, dydt, dzdt])
    
    def sol_exacta(t, state0):
        x0,y0,z0 = state0
        x = x0* np.cos(t)+ y0*np.sin(t)
        y = -x0* np.sin(t)+ y0*np.cos(t)
        z = z0* np.exp(-t)
        return np.array([x, y, z])
    


    #Elegir el integrador
    #integrador = AdaptiveEuler(fun_derivadas)
    #integrador = RKF45(fun_derivadas)
    integrador = Euler(fun_derivadas_ejemplo)
    integrador = RungeKutta4(fun_derivadas_ejemplo)
    integrador = RKF45(fun_derivadas_ejemplo)
    #integrador = AdaptiveEuler(fun_derivadas_ejemplo) ##masomenos funciona
    #integrador = AdaptiveRungeKutta4(fun_derivadas_ejemplo) ##este metodo no funciona
    #integrador = AdaptiveRungeKutta2(fun_derivadas_ejemplo) ##este metodo no funciona
    #integrador = DormanPrince853(fun_derivadas_ejemplo) ##este metodo no funciona

    #state = np.array([1, 0])
    # Definir las condiciones iniciales
    state0 = np.array([1, 2, 3])
    t = 0
    dt = 0.01
    t_max = 10
    it = 1
    t_values = []
    state_values = []
    print('Estado inicial:', state0)
    state = state0

    while t < t_max:
        estado_nuevo, dt_new = integrador.step(t, state, dt)
        #print(f'Iteración {it}: t={t:.2f}, state={state}')
        #print('dt_new', dt_new)
        state = estado_nuevo
        t_values.append(t)
        state_values.append(estado_nuevo)
        it += 1
        t += dt_new

    #Solucion exacta
    time = np.linspace(0, t_max, 10000)
    sol = sol_exacta(time, state0)
    x_exacta = sol[0]
    y_exacta = sol[1]
    z_exacta = sol[2]


    #imprime el ultimo array
    print('Estado final artesanal:', state_values[-1])
    #print('estados:', state_values)
    # Extraer las coordenadas x, y, z
    x_values = [state[0] for state in state_values]
    y_values = [state[1] for state in state_values]
    z_values = [state[2] for state in state_values]

    #####################################
    #print(t_values)

    state_values_LOSDA = solve_ivp(fun_derivadas_ejemplo, (0, t_max), state0, t_eval=t_values, method='LSODA').y.T
    state_values_RK23 = solve_ivp(fun_derivadas_ejemplo, (0, t_max), state0, t_eval=t_values, method='RK23').y.T
    state_values_RK45 = solve_ivp(fun_derivadas_ejemplo, (0, t_max), state0, t_eval=t_values, method='RK45').y.T
    state_values_DOP853 = solve_ivp(fun_derivadas_ejemplo, (0, t_max), state0, t_eval=t_values, method='DOP853').y.T

    print('Estado final LOSDA:', state_values_LOSDA[-1])
    print('Estado final RK23:', state_values_RK23[-1])
    print('Estado final RK45:', state_values_RK45[-1])
    print('Estado final DOP853:', state_values_DOP853[-1])

    #Extraer las coordenadas x, y, z
    x_values_LOSDA = state_values_LOSDA[:, 0]
    y_values_LOSDA = state_values_LOSDA[:, 1]
    z_values_LOSDA = state_values_LOSDA[:, 2]

    #Extraer las coordenadas x, y, z
    x_values_RK23 = state_values_RK23[:, 0]
    y_values_RK23 = state_values_RK23[:, 1]
    z_values_RK23 = state_values_RK23[:, 2]

    #Extraer las coordenadas x, y, z
    x_values_RK45 = state_values_RK45[:, 0]
    y_values_RK45 = state_values_RK45[:, 1]
    z_values_RK45 = state_values_RK45[:, 2]

    #Extraer las coordenadas x, y, z
    x_values_DOP853 = state_values_DOP853[:, 0]
    y_values_DOP853 = state_values_DOP853[:, 1]
    z_values_DOP853 = state_values_DOP853[:, 2]


    # Graficar 
    # Crear subgráficas para cada coordenada
    fig, axs = plt.subplots(3, 1, figsize=(8, 12))

    # Gráfica para la coordenada x
    axs[0].plot(t_values, x_values, label='artesanal', color='blue')
    axs[0].plot(time, x_exacta, label='exacta', color='red', linestyle='--')
    axs[0].plot(t_values, x_values_LOSDA, label='LOSDA', color='green', linestyle='-.')
    axs[0].plot(t_values, x_values_RK23, label='RK23', color='purple', linestyle=':')
    axs[0].plot(t_values, x_values_RK45, label='RK45', color='orange', linestyle='-.')
    axs[0].plot(t_values, x_values_DOP853, label='DOP853', color='black', linestyle=':')
    #axs[0].set_xlabel('Tiempo')
    axs[0].set_ylabel('x')
    axs[0].set_title('Coordenada x')
    axs[0].legend()
    axs[0].grid(True)

    # Gráfica para la coordenada y
    axs[1].plot(t_values, y_values, label='artesanal', color='blue')
    axs[1].plot(time, y_exacta, label='exacta', color='red', linestyle='--')
    axs[1].plot(t_values, y_values_LOSDA, label='LOSDA', color='green', linestyle='-.')
    axs[1].plot(t_values, y_values_RK23, label='RK23', color='purple', linestyle=':')
    axs[1].plot(t_values, y_values_RK45, label='RK45', color='orange', linestyle='-.')
    axs[1].plot(t_values, y_values_DOP853, label='DOP853', color='black', linestyle=':')
    #axs[1].set_xlabel('Tiempo')
    axs[1].set_ylabel('y')
    axs[1].set_title('Coordenada y')
    axs[1].legend()
    axs[1].grid(True)

    # Gráfica para la coordenada z
    axs[2].plot(t_values, z_values, label='artesanal', color='blue')
    axs[2].plot(time, z_exacta, label='exacta', color='red', linestyle='--')
    axs[2].plot(t_values, z_values_LOSDA, label='LOSDA', color='green', linestyle='-.')
    axs[2].plot(t_values, z_values_RK23, label='RK23', color='purple', linestyle=':')
    axs[2].plot(t_values, z_values_RK45, label='RK45', color='orange', linestyle='-.')
    axs[2].plot(t_values, z_values_DOP853, label='DOP853', color='black', linestyle=':')
    axs[2].set_xlabel('Tiempo')
    axs[2].set_ylabel('z')
    axs[2].set_title('Coordenada z')
    axs[2].legend()
    axs[2].grid(True)

    # Ajustar el layout para que no se solapen las subgráficas
    plt.tight_layout()

    # Mostrar la gráfica
    plt.show()