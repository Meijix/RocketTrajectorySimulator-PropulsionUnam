import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

from matplotlib import transforms
from matplotlib.animation import FuncAnimation

from Simulador.utils.dibujar_cohete2 import dibujar_cohete2


fig,parts = dibujar_cohete2()

def update(frame):
    global angle, xpos, ypos
    angle += 3
    xpos += 0.02
    ypos += 0.02
    #print(angle)
    trans = transforms.Affine2D().translate(-x_cm, -y_cm) + transforms.Affine2D().rotate_deg(angle) + transforms.Affine2D().translate(xpos, ypos) + plt.gca().transData
    for p in parts:
    p.set_transform(trans)

angle = 0
xpos, ypos = 0, 0

animation = FuncAnimation(fig, update, interval=30, repeat=False, blit=False)


plt.show()