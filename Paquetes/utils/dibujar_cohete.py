import matplotlib.pyplot as plt
import numpy as np
import sys
import os

# Agregar la ruta del directorio que contiene los paquetes al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from Simulador.src.Xitle import Xitle

def dibujar_cohete(x, y, theta, tamaño, ax):
  theta = theta-90

  #Falta arreglar las proporciones
  altura= tamaño
  longitud = tamaño/12
  long_nose = longitud*4

  # Calcular las esquinas del rectángulo antes de la rotación
  esquina1 = np.array([-longitud / 2, 0])
  esquina2 = np.array([longitud / 2, 0])
  esquina3 = np.array([longitud / 2, altura])
  esquina4 = np.array([-longitud / 2, altura])

  # Matriz de rotación
  theta_rad = np.deg2rad(theta)
  matriz_rotacion = np.array([[np.cos(theta_rad), -np.sin(theta_rad)],
                              [np.sin(theta_rad), np.cos(theta_rad)]])

  # Rotar las esquinas y trasladar al centro (x, y)
  esquina1_rotada = matriz_rotacion @ esquina1 + np.array([x, y])
  esquina2_rotada = matriz_rotacion @ esquina2 + np.array([x, y])
  esquina3_rotada = matriz_rotacion @ esquina3 + np.array([x, y])
  esquina4_rotada = matriz_rotacion @ esquina4 + np.array([x, y])

  #Mostrar esquinas
  #ax.scatter(esquina1[0],esquina1[1])
  #ax.scatter(esquina2[0],esquina2[1])
  #ax.scatter(esquina3[0],esquina3[1])
  #ax.scatter(esquina4[0],esquina4[1])

  # Dibujar el rectángulo (cuerpo del cohete)
  ln, = ax.plot([esquina1_rotada[0], esquina2_rotada[0]], [esquina1_rotada[1], esquina2_rotada[1]], 'k-')
  ax.plot([esquina2_rotada[0], esquina3_rotada[0]], [esquina2_rotada[1], esquina3_rotada[1]], 'k-')
  ax.plot([esquina3_rotada[0], esquina4_rotada[0]], [esquina3_rotada[1], esquina4_rotada[1]], 'k-')
  ax.plot([esquina4_rotada[0], esquina1_rotada[0]], [esquina4_rotada[1], esquina1_rotada[1]], 'k-')

  # Dibujar el triángulo (punta del cohete)
  punta1 = np.array([0, altura + long_nose])
  punta2 = esquina3_rotada
  punta3 = esquina4_rotada

  punta1 = matriz_rotacion @ punta1 + np.array([x, y])
  punta2 = esquina3_rotada
  punta3 = esquina4_rotada
  ax.plot([punta1[0], punta2[0]], [punta1[1], punta2[1]], 'k-')
  ax.plot([punta2[0], punta3[0]], [punta2[1], punta3[1]], 'k-')
  ax.plot([punta3[0], punta1[0]], [punta3[1], punta1[1]], 'k-')

  # Dibujar los trapecios (aletas)
  aleta_base = altura / 4
  aleta_ancho = longitud #/ 2
  aleta_offset = altura /10

# Aleta izquierda
  aleta1_1 = esquina1
  aleta1_2 = aleta1_1 + np.array([0, aleta_base])
  aleta1_3 = aleta1_2+ np.array([-aleta_ancho, -aleta_offset])
  aleta1_4 = aleta1_1+ np.array([-aleta_ancho, -aleta_offset])

  # Rotar y trasladar las esquinas de la aleta
  aleta1_1_rotada = matriz_rotacion @ aleta1_1 + np.array([x, y])
  aleta1_2_rotada = matriz_rotacion @ aleta1_2 + np.array([x, y])
  aleta1_3_rotada = matriz_rotacion @ aleta1_3 + np.array([x, y])
  aleta1_4_rotada = matriz_rotacion @ aleta1_4 + np.array([x, y])

  ax.plot([aleta1_1_rotada[0], aleta1_2_rotada[0]], [aleta1_1_rotada[1], aleta1_2_rotada[1]], 'k-')
  ax.plot([aleta1_2_rotada[0], aleta1_3_rotada[0]], [aleta1_2_rotada[1], aleta1_3_rotada[1]], 'k-')
  ax.plot([aleta1_3_rotada[0], aleta1_4_rotada[0]], [aleta1_3_rotada[1], aleta1_4_rotada[1]], 'k-')
  ax.plot([aleta1_4_rotada[0], aleta1_1_rotada[0]], [aleta1_4_rotada[1], aleta1_1_rotada[1]], 'k-')

  # Aleta derecha (espejo de la izquierda)
  aleta2_1 = esquina2
  aleta2_2 = aleta2_1 + np.array([0, aleta_base])
  aleta2_3 = aleta2_2 + np.array([aleta_ancho, -aleta_offset])
  aleta2_4 = aleta2_1 + np.array([aleta_ancho, -aleta_offset])

  # Rotar y trasladar las esquinas de la aleta derecha
  aleta2_1_rotada = matriz_rotacion @ aleta2_1 + np.array([x, y])
  aleta2_2_rotada = matriz_rotacion @ aleta2_2 + np.array([x, y])
  aleta2_3_rotada = matriz_rotacion @ aleta2_3 + np.array([x, y])
  aleta2_4_rotada = matriz_rotacion @ aleta2_4 + np.array([x, y])

  ax.plot([aleta2_1_rotada[0], aleta2_2_rotada[0]], [aleta2_1_rotada[1], aleta2_2_rotada[1]], 'k-')
  ax.plot([aleta2_2_rotada[0], aleta2_3_rotada[0]], [aleta2_2_rotada[1], aleta2_3_rotada[1]], 'k-')
  ax.plot([aleta2_3_rotada[0], aleta2_4_rotada[0]], [aleta2_3_rotada[1], aleta2_4_rotada[1]], 'k-')
  ax.plot([aleta2_4_rotada[0], aleta2_1_rotada[0]], [aleta2_4_rotada[1], aleta2_1_rotada[1]], 'k-')

  #Falta agregar dibujo del boattail
  # Boattail
  aleta_trasera_base = longitud  # Ajusta la altura de la aleta trasera
  aleta_trasera_long = longitud  # Ajusta el ancho de la aleta trasera
  aleta_trasera_offset = longitud /6  # Ajusta la inclinación de la aleta trasera

  aleta4_1 = esquina1
  aleta4_2 = esquina2
  aleta4_3 = aleta4_1 + np.array([aleta_trasera_offset, -aleta_trasera_long])
  aleta4_4 = aleta4_2 + np.array([-aleta_trasera_offset, -aleta_trasera_long])

  # Rotar y trasladar las esquinas del boattail
  aleta4_1_rotada = matriz_rotacion @ aleta4_1 + np.array([x, y])
  aleta4_2_rotada = matriz_rotacion @ aleta4_2 + np.array([x, y])
  aleta4_4_rotada = matriz_rotacion @ aleta4_3 + np.array([x, y])
  aleta4_3_rotada = matriz_rotacion @ aleta4_4 + np.array([x, y])

  # Mostrar las esquinas del boattail
  #ax.scatter(aleta4_1_rotada[0],aleta4_1_rotada[1])
  #ax.scatter(aleta4_2_rotada[0],aleta4_2_rotada[1])
  #ax.scatter(aleta4_3_rotada[0],aleta4_3_rotada[1])
  #ax.scatter(aleta4_4_rotada[0],aleta4_4_rotada[1])

  ax.plot([aleta4_1_rotada[0], aleta4_2_rotada[0]], [aleta4_1_rotada[1], aleta4_2_rotada[1]], 'k-')
  ax.plot([aleta4_2_rotada[0], aleta4_3_rotada[0]], [aleta4_2_rotada[1], aleta4_3_rotada[1]], 'k-')
  ax.plot([aleta4_3_rotada[0], aleta4_4_rotada[0]], [aleta4_3_rotada[1], aleta4_4_rotada[1]], 'k-')
  ax.plot([aleta4_4_rotada[0], aleta4_1_rotada[0]], [aleta4_4_rotada[1], aleta4_1_rotada[1]], 'k-')

if __name__ == "__main__":
    # Dibujar un cohete
    #dibujar_cohete(0, 0, 0, 5)
    dibujar_cohete(plt,0, 0, 45, 5)
    plt.gca().set_aspect("equal")
    plt.show()