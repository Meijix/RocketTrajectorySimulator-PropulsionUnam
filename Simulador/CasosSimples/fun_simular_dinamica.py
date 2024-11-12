
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
        print("Estado[0]:",estado[0])
        if estado[0] < 0:
            break

    return tiempos, sim


'''
def simular_dinamica(estado, t_max, dt):
    #print(estado)
    t = 0.0
    it = 0
    #########################################
    #CAMBIO DE METODO DE INTEGRACIÓN
    Integracion = Euler(der_gravedad_arrastre) #ocupa dt=0.005
    #Integracion = RungeKutta4(der_gravedad_arrastre) #ocupa dt=0.1
    # Integracion = RKF45(der_gravedad_arrastre)
    #Integracion = RungeKutta2(der_gravedad_arrastre)
    ##########################################
    
    sim=[estado] #lista de estados de vuelo
    tiempos=[0] #lista de tiempos
    while t < t_max:
        #print(t)
        # Integracion numérica del estado actual
        #el dt_new se usa para que el inetgrador actualize el paso de tiempo
        nuevo_estado = Integracion.step(t, estado, dt)
        # nuevo_estado, dt_new = Integracion.step(t, estado, dt, tol=1e-5)
        # print(dt_new)
        # dt = dt_new
        #print(dt_new,dt)
        #print("dt= ", dt)

        # Avanzar estado
        it += 1
        t += dt
        estado = nuevo_estado

        sim.append(estado)
        tiempos.append(t)

        #Indicar el avance en la simulacion
        if it%500==0:
            print(f"Iteracion {it}, t={t:.1f} s, altitud={estado[0]:.1f} m, vel vert={estado[1]:.1f}")
        
        if estado[0] < 0:
            break

    return tiempos, sim


'''