import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib import transforms

#Se le podrian pasar las mediidas del cohete_actual
def dibujar_cohete2(ax=None):
    #Colores
    color_cohete='navy'
    color_borde='silver'
    # Crear figura
    fig = plt.figure()
    ax = fig.add_subplot(111)
    
    # Dimensiones del cohete
    body_l = 6
    body_w = 1
    nose_l = 1.5
    fin_w1 = 1.5
    fin_w2 = 2
    fin_h = 0.5
    boattail_lenght = 0.3
    
    parts = []
    
    # Cuerpo del cohete
    points = np.array([(0,0), (0,body_w), (body_l,body_w), (body_l, 0)])
    body = patches.Polygon(points, facecolor=color_cohete, edgecolor=color_borde)
    
    # Cono de la nariz
    points = np.array([(body_l,0), (body_l,body_w), (body_l+nose_l,body_w/2)])
    nose_cone = patches.Polygon(points, facecolor=color_cohete, edgecolor=color_borde)
    
    # Aletas
    fin_d = (fin_w2 - fin_w1)/2
    points = np.array([(0, 0), (fin_d, fin_h), (fin_d+fin_w1, fin_h), (fin_w2, 0)])
    points1 = np.copy(points)
    points1[:, 1] += body_w
    fin1 = patches.Polygon(points1, facecolor=color_cohete, edgecolor=color_borde)
    points2 = np.copy(points)
    points2[:, 1] *= -1
    fin2 = patches.Polygon(points2, facecolor=color_cohete, edgecolor=color_borde)
    
    # Boattail (parte trasera)
    points = np.array([(0,0), (0,body_w), (-boattail_lenght, body_w-0.1), (-boattail_lenght, 0.1)])
    boattail = patches.Polygon(points, facecolor=color_cohete, edgecolor=color_borde)
    
    # Añadir todas las partes
    parts = [body, nose_cone, fin1, fin2, boattail]
    
    for p in parts:
        plt.gca().add_artist(p)
    
    # Configurar los límites y aspecto del gráfico
    plt.xlim(-10, 10)
    plt.ylim(-10, 10)
    plt.gca().set_aspect("equal")
    
    return fig, parts

#Función para rotar el cohete en el cm
def rotar_cohete(fig, parts, x_cm,y_cm,angle,ax=None):
    #Transaladar y rotar el cohete
    trans = transforms.Affine2D().translate(-x_cm, -y_cm) + transforms.Affine2D().rotate_deg(angle)  + plt.gca().transData #+ transforms.Affine2D().translate(xpos, ypos)
    for p in parts:
        p.set_transform(trans)
    return fig, parts 


# Ejemplo de uso:
fig, parts = dibujar_cohete2()
#usar rotar_cohete para rotar el cohete
fig, parts = rotar_cohete(fig, parts,3,0.5,30)

plt.show()