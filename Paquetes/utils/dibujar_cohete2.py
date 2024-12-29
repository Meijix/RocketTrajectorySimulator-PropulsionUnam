import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib import transforms
from matplotlib.animation import FuncAnimation

def dibujar_cohete(ax, angle=0, x_cm=0, y_cm=0):
    """
    Dibuja un cohete en un gráfico especificando su centro de gravedad (x_cm, y_cm)
    y el ángulo de rotación alrededor de dicho centro.
    """
    # Colores
    color_cohete = 'navy'
    color_borde = 'silver'

    # Dimensiones del cohete
    body_l = 6
    body_w = 1
    nose_l = 1.5
    fin_w1 = 1.5
    fin_w2 = 2
    fin_h = 0.5
    boattail_length = 0.3
    
    # Partes del cohete
    parts = []
    
    # Cuerpo
    points = np.array([(0, 0), (0, body_w), (body_l, body_w), (body_l, 0)])
    body = patches.Polygon(points, facecolor=color_cohete, edgecolor=color_borde)
    parts.append(body)
    
    # Cono de la nariz
    points = np.array([(body_l, 0), (body_l, body_w), (body_l + nose_l, body_w / 2)])
    nose_cone = patches.Polygon(points, facecolor=color_cohete, edgecolor=color_borde)
    parts.append(nose_cone)
    
    # Aletas
    fin_d = (fin_w2 - fin_w1) / 2
    points = np.array([(0, 0), (fin_d, fin_h), (fin_d + fin_w1, fin_h), (fin_w2, 0)])
    
    # Aleta superior
    points1 = np.copy(points)
    points1[:, 1] += body_w
    fin1 = patches.Polygon(points1, facecolor=color_cohete, edgecolor=color_borde)
    parts.append(fin1)
    
    # Aleta inferior
    points2 = np.copy(points)
    points2[:, 1] *= -1
    fin2 = patches.Polygon(points2, facecolor=color_cohete, edgecolor=color_borde)
    parts.append(fin2)
    
    # Boattail
    points = np.array([
        (0, 0), 
        (0, body_w), 
        (-boattail_length, body_w - 0.1), 
        (-boattail_length, 0.1)
    ])
    boattail = patches.Polygon(points, facecolor=color_cohete, edgecolor=color_borde)
    parts.append(boattail)
    
    # Añadir partes al eje
    for part in parts:
        ax.add_patch(part)
    
    # Aplicar transformación: mover al CM y rotar alrededor de él
    trans = (transforms.Affine2D()
             .translate(-body_l / 2, -body_w / 2)  # Trasladar el cohete al origen del CM
             .rotate_deg(angle)                   # Rotar el cohete
             .translate(x_cm, y_cm)               # Mover al centro de gravedad
             + ax.transData)
    
    for part in parts:
        part.set_transform(trans)
    
    return parts

# Función de animación
def actualizar(frame, ax, parts, x_cm, y_cm):
    """
    Actualiza la rotación del cohete en cada cuadro.
    """
    angle = frame  # Rotación incremental en cada frame
    trans = (transforms.Affine2D()
             .translate(-6 / 2, -1 / 2)  # Dimensiones del cuerpo del cohete
             .rotate_deg(angle)
             .translate(x_cm, y_cm)
             + ax.transData)
    for part in parts:
        part.set_transform(trans)
    return parts

# Configuración del gráfico
fig, ax = plt.subplots()
ax.set_xlim(-10, 10)
ax.set_ylim(-10, 10)
ax.set_aspect('equal')

# Dibuja el cohete en la posición inicial
x_cm, y_cm = 0, 0  # Centro de gravedad
parts = dibujar_cohete(ax, angle=0, x_cm=x_cm, y_cm=y_cm)

# Crear animación
anim = FuncAnimation(fig, actualizar, frames=np.arange(0, 360, 2), 
                     fargs=(ax, parts, x_cm, y_cm), interval=50)

# Mostrar la animación
plt.show()
