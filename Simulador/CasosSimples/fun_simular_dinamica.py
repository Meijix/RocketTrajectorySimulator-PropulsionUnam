from scipy.integrate import solve_ivp

def simular_dinamica(estado, t_max, dt, integrador, fun_derivada):
    sim = [estado]
    #print("Estado:",estado)
    tiempos = [0]
    t = 0.0
    it = 1

    Integracion = integrador(fun_derivada)
    #print("Integracion:",Integracion)

    while t < t_max:
        # Integracion numérica del estado actual (un paso)
        nuevo_estado, dt = Integracion.step(t, estado, dt)
        #print("Nuevo estado:",nuevo_estado)
        # Avanzar estado
        it += 1
        t += dt
        estado = nuevo_estado

        sim.append(estado)
        tiempos.append(t)

        #Indicar el avance en la simulacion
        if it%500==0:
            print(f"Iteracion {it}, t={t:.1f} s, altitud={estado[0]:.1f} m, vel vert={estado[1]:.1f}")
        #Terminar cuando llegue al suelo
        if estado[0] < 0:
            break

    return tiempos, sim


###########################################
#Funcion para simular la dinamica 
#usando solve_ivp de python
'''
def simular_python(estado, t_max, integrador, fun_derivada):
    # Resolvemos el sistema de ecuaciones diferenciales
    solucion = solve_ivp(fun_derivada, [0, t_max], estado, method=integrador)
    # Extraemos los tiempos y las soluciones
    tiempos = solucion.t
    sim = solucion.y
    return tiempos, sim
'''

from scipy.integrate import solve_ivp

def simular_python(estado, t_max, integrador, fun_derivada):
    # Definir la función de evento
    def evento_cero(t, y):
        if t > 1e-8:  # Excluir el caso en que el tiempo es inicial
            return y[0]  # Monitorea la solución que debe alcanzar cero
        return 1  # Retorna un valor diferente de cero para no disparar el evento
    
    evento_cero.terminal = True  # Detener la integración si el evento ocurre
    evento_cero.direction = 0   # Detectar el cruce en cualquier dirección

    # Resolver con solve_ivp
    solucion = solve_ivp(fun_derivada, [0, t_max], estado, method=integrador, events=evento_cero, dense_output=True)
    # Extraer tiempos, soluciones y eventos
    tiempos = solucion.t
    sim = solucion.y
    eventos = solucion.t_events  # Tiempos donde ocurrieron los eventos

    return tiempos, sim



if __name__== "__main__":
    print("Este modulo no debe ejecutarse directamente")
    #ejemplo de uso de la funcion simular_python
    estado = [20, 0]
    t_max = 50
    integrador = 'RK45'
    fun_derivada = lambda t, y: [y[1], -9.8]
    tiempos, sim = simular_python(estado, t_max, integrador, fun_derivada)
    print("Tiempos:",tiempos)
    print("Simulacion:",sim)
    print("Fin del ejemplo")
    ####Graficaer la simulacion
    import matplotlib.pyplot as plt
    plt.plot(tiempos, sim[0])
    plt.xlabel('Tiempo [s]')
    plt.ylabel('Altitud [m]')
    plt.show()