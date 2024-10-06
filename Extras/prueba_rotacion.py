import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib import transforms
import numpy as np
from matplotlib.animation import FuncAnimation

x_cm, y_cm = 3, 0.5
edge_color = 'b'
alpha = '0.8'

fig = plt.figure()

body_l = 6
body_w = 1
nose_l = 1.5
fin_w1 = 1.5
fin_w2 = 2
fin_h = 0.5

parts = []

# Body
points = np.array([(0,0), (0,body_w), (body_l,body_w), (body_l, 0)])
body = patches.Polygon(points, facecolor=alpha, edgecolor=edge_color )

# Nose cone
points = np.array([(body_l,0), (body_l,body_w), (body_l+nose_l,body_w/2)])
nose_cone = patches.Polygon(points, facecolor=alpha, edgecolor=edge_color)

# Aletas
fin_d = (fin_w2 - fin_w1)/2
points = np.array([(0, 0), (fin_d, fin_h), (fin_d+fin_w1, fin_h), (fin_w2, 0)])
points1 = np.copy(points)
points1[:, 1] += body_w
fin1 = patches.Polygon(points1, facecolor=alpha, edgecolor=edge_color)
points2 = np.copy(points)
points2[:, 1] *= -1
fin2 = patches.Polygon(points2, facecolor=alpha, edgecolor=edge_color)

#Boattail
points = np.array([(0,0), (0,body_w), (-0.5, body_w-0.1), (-0.5, 0.1)])
boattail = patches.Polygon(points, facecolor=alpha, edgecolor=edge_color)


parts = [body, nose_cone, fin1, fin2, boattail]

for p in parts:
  plt.gca().add_artist(p)

plt.xlim(-10, 10)
plt.ylim(-10, 10)
plt.gca().set_aspect("equal")

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