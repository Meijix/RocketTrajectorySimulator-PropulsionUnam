import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib import transforms
import numpy as np
from matplotlib.animation import FuncAnimation

x_cm, y_cm = 2, 0.5

fig = plt.figure()

body_l = 4
body_w = 1
nose_l = 1
fin_w1 = 1.5
fin_w2 = 2
fin_h = 0.5

parts = []

# Body
points = np.array([(0,0), (0,body_w), (body_l,body_w), (body_l, 0)])
body = patches.Polygon(points, facecolor="0.9", edgecolor="r")

# Nose cone
points = np.array([(body_l,0), (body_l,body_w), (body_l+nose_l,body_w/2)])
nose_cone = patches.Polygon(points, facecolor="0.9", edgecolor="r")

# Aletas
fin_d = (fin_w2 - fin_w1)/2
points = np.array([(0, 0), (fin_d, fin_h), (fin_d+fin_w1, fin_h), (fin_w2, 0)])
points1 = np.copy(points)
points1[:, 1] += body_w
fin1 = patches.Polygon(points1, facecolor="0.9", edgecolor="r")
points2 = np.copy(points)
points2[:, 1] *= -1
fin2 = patches.Polygon(points2, facecolor="0.9", edgecolor="r")

parts = [body, nose_cone, fin1, fin2]

for p in parts:
  plt.gca().add_artist(p)

plt.xlim(-10, 10)
plt.ylim(-10, 10)
plt.gca().set_aspect("equal")

def update(frame):
  global angle, xpos, ypos
  angle += 10
  xpos += 0.05
  ypos += 0.05
  print(angle)
  trans = transforms.Affine2D().translate(-x_cm, -y_cm) + transforms.Affine2D().rotate_deg(angle) + transforms.Affine2D().translate(xpos, ypos) + plt.gca().transData
  for p in parts:
    p.set_transform(trans)

angle = 0
xpos, ypos = 0, 0
animation = FuncAnimation(fig, update, interval=30, repeat=False, blit=False)


plt.show()