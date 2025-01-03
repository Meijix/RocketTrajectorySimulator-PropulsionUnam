import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib import transforms
from matplotlib.animation import FuncAnimation

def dibujar_cohete2(ax, angle=0, x_cm=0, y_cm=0, body_l=5, body_w=5/6, nose_l=5/4, fin_w1=5/4, fin_w2=5/3, fin_h=5/8, boattail_length=5/9, boat_rear=5/2):
    """
    Dibuja un cohete en un gráfico especificando su centro de gravedad (x_cm, y_cm),
    el ángulo de rotación, y el escalado del cohete.
    """
    # Colores
    color_cohete = 'midnightblue'
    color_borde = 'lavender'
    
    '''
    # Dimensiones del cohete escaladas
    body_l = long # Longitud del cuerpo
    body_w = long / 6 # Ancho del cuerpo
    nose_l = long / 4 # Longitud de la nariz
    fin_w1 = long / 4 # Root chord de la aleta
    fin_w2 = long / 3 # Tip chord de la aleta
    fin_h = long / 8 # Altura de la aleta- span??
    boattail_length = long / 9  # Longitud del boattail  
    '''
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
        (0, -body_w/2), 
        (0, body_w/2), 
        (-boattail_length, -boat_rear/2), 
        (-boattail_length, boat_rear/2)
    ])
    boattail = patches.Polygon(points, facecolor=color_cohete, edgecolor=color_borde)
    parts.append(boattail)
    
    # Añadir partes al eje
    for part in parts:
        ax.add_patch(part)
    
    # Aplicar transformación inicial
    trans = (transforms.Affine2D()
            .translate(-body_l / 2, -body_w / 2)  # Trasladar el cohete al origen relativo
            .translate(x_cm, y_cm) 
            .rotate_deg(angle)      # Rotar alrededor del centro de gravedad    
            + ax.transData)
    for part in parts:
        part.set_transform(trans)
    
    return parts

# Función de animación
def actualizar(frame, ax, parts, x_cm, y_cm, angle):
    """
    Actualiza la rotación del cohete en cada cuadro.
    """
    # Rotación incremental en cada frame
    trans = (transforms.Affine2D()
             .rotate_deg(angle)      # Rotar alrededor del centro de gravedad
             .translate(x_cm, y_cm)  # Mover al centro de gravedad
             + ax.transData)
    for part in parts:
        part.set_transform(trans)
    return parts

# Manejar clic del usuario para posicionar el cohete
def on_click(event):
    """
    Evento que captura el clic del usuario para posicionar el cohete.
    """
    global x_cm, y_cm, parts, anim
    if event.inaxes is not None:
        x_cm, y_cm = event.xdata, event.ydata  # Nueva posición
        ax.clear()  # Limpia el eje para redibujar
        ax.set_xlim(-20, 20)
        ax.set_ylim(-20, 20)
        ax.set_aspect('equal')
        parts = dibujar_cohete2(ax, angle=0, x_cm=x_cm, y_cm=y_cm, long=5)
        anim = FuncAnimation(fig, actualizar, frames=np.arange(0, 360, 2), 
                             fargs=(ax, parts, x_cm, y_cm, scale), interval=50)
        plt.draw()

if __name__ == '__main__':
    # Configuración inicial del gráfico
    fig, ax = plt.subplots()
    ax.set_xlim(-20, 20)
    ax.set_ylim(-20, 20)
    ax.set_aspect('equal')

    # Variables globales
    x_cm, y_cm = 0, 0  # Centro de gravedad inicial
    scale = 1          # Escala inicial
    parts = dibujar_cohete2(ax, angle=0, x_cm=x_cm, y_cm=y_cm, long=5)

    # Crear animación inicial
    anim = FuncAnimation(fig, actualizar, frames=np.arange(0, 360, 2), 
                        fargs=(ax, parts, x_cm, y_cm, scale), interval=50)

    # Conectar evento de clic
    fig.canvas.mpl_connect('button_press_event', on_click)

    # Mostrar el gráfico interactivo
    plt.show()
