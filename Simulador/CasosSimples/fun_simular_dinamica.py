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

def simular_python(estado, t_max, integrador, fun_derivada):
    t = 0.0
    tiempos, sim = solve_ivp(fun_derivada, [t, t_max], estado, method=integrador)
    return tiempos, sim
