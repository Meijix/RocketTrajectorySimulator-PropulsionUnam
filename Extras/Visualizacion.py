import pygame
import math 
import random
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Inicializar Pygame
pygame.init()

# Definir colores
negro = (0, 0, 0)
blanco = (255, 255, 255)
rojo = (255, 0, 0)
verde = (191,255,0)

# Dimensiones del cohete
ancho_cohete = 50
alto_cohete = 100
ancho_llama = 10
alto_llama = 30

# Posición inicial del cohete
x_cohete = 200
y_cohete = 400

# Velocidad del cohete
velocidad_cohete = 1

# **Crear la pantalla**
pantalla = pygame.display.set_mode((800, 600))  # Ajusta el tamaño de la pantalla según tus preferencias
# Dimensiones de la pantalla
ancho_pantalla = 800
alto_pantalla = 600

# Dimensiones del cohete
ancho_cohete = 20
alto_cohete = 80
ancho_llama = 10
alto_llama = 30

# Posición inicial del cohete
x_cohete = ancho_pantalla // 2 - ancho_cohete // 2
y_cohete = alto_pantalla - alto_cohete

# Velocidad inicial del cohete
velocidad_x = 0
velocidad_y = 0

# Gravedad
gravedad = 0.1

# Ángulo de inclinación del cohete
angulo = 0

# Potencia de empuje del motor
potencia_motor = 0

# Bucle principal del juego
while True:
    # Revisar eventos del teclado
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                velocidad_x -= 1
            if event.key == pygame.K_RIGHT:
                velocidad_x += 1
            if event.key == pygame.K_UP:
                potencia_motor += 1
            if event.key == pygame.K_DOWN:
                potencia_motor -= 1

    # Calcular la aceleración del cohete
    aceleracion_x = 0
    aceleracion_y = gravedad - potencia_motor * 0.01

    # Calcular las nuevas velocidades
    velocidad_x += aceleracion_x
    velocidad_y += aceleracion_y

    # Limitar la velocidad horizontal
    velocidad_x = max(-5, min(5, velocidad_x))

    # Aplicar la velocidad al movimiento
    x_cohete += velocidad_x
    y_cohete += velocidad_y

    # Limitar la posición del cohete en la pantalla
    x_cohete = max(0, min(ancho_pantalla - ancho_cohete, x_cohete))
    y_cohete = max(0, min(alto_pantalla - alto_cohete, y_cohete))

    # Calcular la rotación del cohete
    angulo_objetivo = math.atan2(velocidad_y, velocidad_x)
    angulo = angulo * 0.9 + angulo_objetivo * 0.1

    # Borrar la pantalla
    pantalla.fill(negro)

    # Dibujar el suelo
    pygame.draw.rect(pantalla, verde, (0, alto_pantalla - 20, ancho_pantalla, 20))

    # Dibujar el cohete
    cohete_centro = (x_cohete + ancho_cohete // 2, y_cohete + alto_cohete // 2)
    puntos_cohete = [
        (cohete_centro[0], cohete_centro[1] - alto_cohete // 2),
        (cohete_centro[0] + ancho_cohete // 2 - ancho_llama // 2, cohete_centro[1] + alto_cohete // 2),
        (cohete_centro[0] - ancho_cohete // 2 + ancho_llama // 2, cohete_centro[1] + alto_cohete // 2),
        (cohete_centro[0] - ancho_cohete // 2, cohete_centro[1] - alto_cohete // 2)
    ]
    pygame.draw.polygon(pantalla, blanco, puntos_cohete)

    # Dibujar la llama del cohete
    #pygame.draw.rect(pantalla, rojo, (cohete_centro[0] + ancho_cohete // 2 - ancho_cohete))         