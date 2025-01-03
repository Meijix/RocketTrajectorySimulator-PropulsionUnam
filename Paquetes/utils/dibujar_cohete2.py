import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib import transforms
from matplotlib.animation import FuncAnimation

def dibujar_cohete2(ax, angle=0, x_cm=0, y_cm=0, body_l=3.3, body_w=0.16, nose_l=0.81, fin_tip=0.2, fin_root=0.3, fin_h=0.2, boattail_length=0.15, boat_rear=0.12):
    """
    Dibuja un cohete en un gráfico especificando su centro de gravedad (x_cm, y_cm),
    el ángulo de rotación, y el escalado del cohete.
    """
    # Colores
    color_cohete = 'midnightblue'
    color_borde = 'lavender'
    # Partes del cohete
    parts = []
    
    # Cono de la nariz
    points = np.array([(0, 0), (nose_l, body_w/2), (nose_l, -body_w / 2)])
    nose_cone = patches.Polygon(points, facecolor=color_cohete, edgecolor=color_borde)
    parts.append(nose_cone)

    # Cuerpo
    points = np.array([(nose_l, body_w/2), (nose_l, -body_w / 2), (nose_l+body_l, -body_w / 2),(nose_l+body_l, body_w/2), ])
    body = patches.Polygon(points, facecolor=color_cohete, edgecolor=color_borde)
    parts.append(body)
    
    
    # Aletas
    inicio_aletas = nose_l + body_l
    fin_d = (fin_root - fin_tip) / 2
    # Puntos de la aleta superior
    points = np.array([(inicio_aletas, body_w/2), (inicio_aletas-fin_root, body_w/2), (inicio_aletas-fin_root+fin_d, (body_w/2)+fin_h), (inicio_aletas-fin_d, (body_w/2)+fin_h)])
    

    fin1 = patches.Polygon(points, facecolor=color_cohete, edgecolor=color_borde)
    parts.append(fin1)
    
    # Aleta inferior
    points2 = np.copy(points)
    points2[:, 1] *= -1
    fin2 = patches.Polygon(points2, facecolor=color_cohete, edgecolor=color_borde)
    parts.append(fin2)
    
    # Boattail
    points = np.array([
        (inicio_aletas, body_w/2),
        (inicio_aletas, -body_w/2),
        (inicio_aletas+boattail_length, -boat_rear/2),
        (inicio_aletas+boattail_length, boat_rear/2)
    ])
    boattail = patches.Polygon(points, facecolor=color_cohete, edgecolor=color_borde)
    parts.append(boattail)
    
    # Añadir partes al eje
    for part in parts:
        ax.add_patch(part)
    
    # Aplicar transformación inicial
    trans = (transforms.Affine2D()
            #.translate(-body_l / 2, -body_w / 2)  # Trasladar el cohete al origen relativo
            #.translate(x_cm, y_cm) 
            .rotate_deg(angle)      # Rotar alrededor del centro de gravedad    
            + ax.transData)
    for part in parts:
        part.set_transform(trans)
    
    return parts

# Función de animación
def actualizar(ax, parts, x_cm, y_cm, angle):
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
        parts = dibujar_cohete2(ax, angle=0, x_cm=x_cm, y_cm=y_cm)
        anim = FuncAnimation(fig, actualizar, frames=np.arange(0, 360, 2), 
                            fargs=(ax, parts, x_cm, y_cm), interval=50)
        plt.draw()

if __name__ == '__main__':
    # Configuración inicial del gráfico
    fig, ax = plt.subplots()
    ax.set_xlim(0, 5)
    ax.set_ylim(-0.5, 0.5)
    ax.set_aspect('equal')
    #linea horizontal en y=0
    ax.axhline(0, color='black', lw=1)

    # Variables globales
    x_cm, y_cm = 2, 0  # Centro de gravedad inicial
    scale = 1          # Escala inicial
    parts = dibujar_cohete2(ax, angle=0, x_cm=x_cm, y_cm=y_cm)
    '''
    # Crear animación inicial
    anim = FuncAnimation(fig, actualizar, frames=np.arange(0, 360, 2), 
                        fargs=(ax, parts, x_cm, y_cm, scale), interval=50)

    # Conectar evento de clic
    fig.canvas.mpl_connect('button_press_event', on_click)
    '''
    # Mostrar el gráfico interactivo
    plt.show()
