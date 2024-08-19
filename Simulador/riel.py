import numpy as np
from numpy import *

class Torrelanzamiento:
  def __init__(self, longitud, angulo):
    self.longitud = longitud #[m]
    self.angulo = angulo #[grados]


if __name__ == "__main__":
  #riel = Torrelanzamiento(5, 88)
  #riel = Torrelanzamiento(5, 45)
  riel = Torrelanzamiento(10, 80)
  print("Riel de lanzamiento:",riel.longitud,"m", riel.angulo, "º")
  