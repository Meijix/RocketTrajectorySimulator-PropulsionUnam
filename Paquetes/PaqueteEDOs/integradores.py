"""Integradores de EDOs escritos para el simulador.

Todos comparten la misma interfaz:

    nuevo_estado, dt_usado = integrador.step(t, estado, dt)

`dt_usado` es el paso que realmente se dio (el tiempo avanza de t a t + dt_usado).
Los métodos de paso fijo devuelven el mismo dt que reciben. Los adaptativos pueden
reducirlo, y dejan en `integrador.dt_sugerido` el paso recomendado para el siguiente.

Nombres y su correspondencia teórica
------------------------------------
Propios (este archivo):
    Euler            Euler explícito, orden 1.
    RungeKutta2      Método de Heun (trapecio explícito), orden 2.
    RungeKutta4      Runge-Kutta clásico, orden 4.
    RKF45            Runge-Kutta-Fehlberg 4(5) (Fehlberg, 1969), paso adaptativo.
    EulerAdaptativo  Euler con duplicación de paso (estimación de error de Richardson).
    HeunAdaptativo   Par embebido Euler-Heun 1(2).

De SciPy (scipy.integrate.solve_ivp), que NO son los de arriba:
    'RK45'    Dormand-Prince 5(4) (Dormand y Prince, 1980). No es Fehlberg.
    'RK23'    Bogacki-Shampine 3(2).
    'DOP853'  Dormand-Prince de orden 8 con estimadores de orden 5 y 3 (código DOP853
              de Hairer, Nørsett y Wanner; coeficientes de Prince y Dormand, 1981).
    'LSODA'   Adams (no rígido) / BDF (rígido) con cambio automático (ODEPACK).
    'BDF'     Fórmulas de diferenciación hacia atrás de orden variable 1 a 5.
"""
from scipy.integrate import solve_ivp
import numpy as np
import matplotlib.pyplot as plt


# 1. Método de Euler
class Euler:
    orden = 1

    def __init__(self, fun_derivs):
        self.fun_derivadas = fun_derivs

    def step(self, t, state, dt):
        #Aplicar método de Euler para obtener nuevo estado
        state_new = state + (dt * self.fun_derivadas(t, state))
        return state_new, dt


# 2. Runge-Kutta 4 (clásico)
class RungeKutta4:
    orden = 4

    def __init__(self, fun_derivs):
        self.fun_derivadas = fun_derivs

    def step(self, t, state, dt):
        k1 = self.fun_derivadas(t, state)
        k2 = self.fun_derivadas(t + dt/2, state + k1 * dt/2)
        k3 = self.fun_derivadas(t + dt/2, state + k2 * dt/2)
        k4 = self.fun_derivadas(t + dt, state + k3 * dt)
        new_state = state + dt * (k1 + 2*k2 + 2*k3 + k4) / 6
        return new_state, dt


# 3. Runge-Kutta 2: método de Heun (trapecio explícito)
class RungeKutta2:
    orden = 2

    def __init__(self, fun_derivs):
        self.fun_derivadas = fun_derivs

    def step(self, t, state, dt):
        k1 = self.fun_derivadas(t, state)
        k2 = self.fun_derivadas(t + dt, state + k1 * dt)
        new_state = state + dt * (k1 + k2) / 2
        return new_state, dt


class _Adaptativo:
    """Control de paso común a los métodos adaptativos.

    El error de cada variable se mide relativo a su tolerancia, atol + rtol*|y|, y se toma
    el máximo. El paso se acepta si ese error escalado es <= 1. El nuevo paso es

        dt_nuevo = dt * q,   q = S * (1 / (2*error)) ** (1 / (p + 1))

    con p el orden de la fórmula de menor orden del par (para RKF45, p = 4: es la regla
    q = (tol / (2*error))**(1/4) de Burden y Faires, con el factor de seguridad S). q se
    limita a [q_min, q_max] para que el paso no cambie bruscamente.
    """
    def __init__(self, fun_derivs, rtol=1e-6, atol=1e-8, S=0.9, q_min=0.1, q_max=4.0, dt_min=1e-10):
        self.fun_derivadas = fun_derivs
        self.rtol, self.atol = rtol, atol
        self.S, self.q_min, self.q_max = S, q_min, q_max
        self.dt_min = dt_min
        self.dt_sugerido = None      # paso recomendado para el siguiente step
        self.rechazados = 0          # pasos repetidos por exceder la tolerancia

    def _intento(self, t, state, dt):
        """Devuelve (solución que se propaga, estimación del error local) para un paso dt."""
        raise NotImplementedError

    def step(self, t, state, dt):
        state = np.asarray(state, dtype=float)
        while True:
            nuevo, diferencia = self._intento(t, state, dt)
            escala = self.atol + self.rtol * np.maximum(np.abs(state), np.abs(nuevo))
            error = np.max(np.abs(diferencia) / escala)
            if error == 0:
                q = self.q_max
            else:
                q = self.S * (1.0 / (2.0 * error)) ** (1.0 / (self.orden_error + 1))
                q = min(self.q_max, max(self.q_min, q))
            if error <= 1.0 or dt <= self.dt_min:
                self.dt_sugerido = dt * q
                return nuevo, dt
            # Error demasiado grande: reducir el paso y repetir
            self.rechazados += 1
            dt = max(dt * min(q, 1.0), self.dt_min)


# 4. Método de Runge-Kutta-Fehlberg 4(5)
class RKF45(_Adaptativo):
    """Runge-Kutta-Fehlberg 4(5): seis etapas, soluciones embebidas de orden 4 y 5.

    Coeficientes de Fehlberg (1969), los mismos de Burden y Faires, "Análisis numérico".
    La diferencia entre las dos soluciones estima el error local de la de orden 4. Se
    propaga la de orden 5 (extrapolación local), como hacen la mayoría de las
    implementaciones; Fehlberg propagaba originalmente la de orden 4.
    """
    orden = 5
    orden_error = 4

    # Tabla de Butcher
    C = np.array([0, 1/4, 3/8, 12/13, 1, 1/2])
    A = [
        [],
        [1/4],
        [3/32, 9/32],
        [1932/2197, -7200/2197, 7296/2197],
        [439/216, -8, 3680/513, -845/4104],
        [-8/27, 2, -3544/2565, 1859/4104, -11/40],
    ]
    B4 = np.array([25/216, 0, 1408/2565, 2197/4104, -1/5, 0])
    B5 = np.array([16/135, 0, 6656/12825, 28561/56430, -9/50, 2/55])

    def _intento(self, t, state, dt):
        k = []
        for i in range(6):
            y = state + dt * sum(a * kj for a, kj in zip(self.A[i], k)) if i else state
            k.append(self.fun_derivadas(t + self.C[i] * dt, y))
        k = np.array(k)
        y4 = state + dt * (self.B4 @ k)
        y5 = state + dt * (self.B5 @ k)
        return y5, y5 - y4


#############################################
# 5. Euler adaptativo (duplicación de paso)
class EulerAdaptativo(_Adaptativo):
    """Euler con duplicación de paso: compara un paso dt con dos pasos dt/2.

    La diferencia estima el error del paso completo (orden 1). Se propaga la solución de
    los dos medios pasos, que es la más precisa.
    """
    orden = 1
    orden_error = 1

    def __init__(self, fun_derivs, rtol=1e-4, atol=1e-6, **kw):
        super().__init__(fun_derivs, rtol=rtol, atol=atol, **kw)

    def _intento(self, t, state, dt):
        f0 = self.fun_derivadas(t, state)
        completo = state + dt * f0
        medio = state + dt / 2 * f0
        medio = medio + dt / 2 * self.fun_derivadas(t + dt / 2, medio)
        return medio, medio - completo


# 6. Heun adaptativo: par embebido Euler-Heun 1(2)
class HeunAdaptativo(_Adaptativo):
    """Par embebido Euler (orden 1) - Heun (orden 2). Se propaga la solución de Heun.

    Esta clase se llamaba antes `DormanPrince853`, pero nunca fue ese método: el
    Dormand-Prince 8(5,3) real tiene 12 etapas y está disponible como 'DOP853' en SciPy.
    """
    orden = 2
    orden_error = 1

    def __init__(self, fun_derivs, rtol=1e-4, atol=1e-6, **kw):
        super().__init__(fun_derivs, rtol=rtol, atol=atol, **kw)

    def _intento(self, t, state, dt):
        k1 = self.fun_derivadas(t, state)
        k2 = self.fun_derivadas(t + dt, state + dt * k1)
        euler = state + dt * k1
        heun = state + dt * (k1 + k2) / 2
        return heun, heun - euler


# Nombre anterior, por compatibilidad con scripts existentes
AdaptiveEuler = EulerAdaptativo


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
    integrador = Euler(fun_derivadas_ejemplo)
    integrador = RungeKutta4(fun_derivadas_ejemplo)
    integrador = RKF45(fun_derivadas_ejemplo)
    #integrador = EulerAdaptativo(fun_derivadas_ejemplo)
    #integrador = HeunAdaptativo(fun_derivadas_ejemplo)

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
        estado_nuevo, dt_usado = integrador.step(t, state, min(dt, t_max - t))
        state = estado_nuevo
        t += dt_usado
        t_values.append(t)
        state_values.append(estado_nuevo)
        it += 1
        # Los métodos adaptativos proponen el siguiente paso
        dt = getattr(integrador, 'dt_sugerido', None) or dt

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
    axs[0].plot(t_values, x_values_LOSDA, label='LSODA', color='green', linestyle='-.')
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
    axs[1].plot(t_values, y_values_LOSDA, label='LSODA', color='green', linestyle='-.')
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