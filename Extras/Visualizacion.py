import pygame

# Inicializar Pygame
pygame.init()

# Definir colores
negro = (0, 0, 0)
blanco = (255, 255, 255)
rojo = (255, 0, 0)

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

# Bucle principal del juego
while True:
    # Revisar eventos del teclado
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

    # **Crear la pantalla**
    pantalla = pygame.display.set_mode((800, 600))  # Ajusta el tamaño de la pantalla según tus preferencias

    # Borrar la pantalla
    pantalla.fill(negro)

    # Dibujar el cuerpo del cohete
    pygame.draw.rect(pantalla, blanco, (x_cohete, y_cohete, ancho_cohete, alto_cohete))

    # Dibujar la llama del cohete
    pygame.draw.rect(pantalla, rojo, (x_cohete + ancho_cohete // 2 - ancho_llama // 2, y_cohete + alto_cohete, ancho_llama, alto_llama))

    # Actualizar la posición del cohete
    y_cohete -= velocidad_cohete

    # Limitar la posición del cohete en la pantalla
    if y_cohete < 0:
        y_cohete = 0

    # Actualizar la pantalla
    pygame.display.flip()

    # Controlar la velocidad del juego
    pygame.time.Clock().tick(60)