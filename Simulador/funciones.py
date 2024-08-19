
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy.interpolate import interp1d
import math
from math import pi
import random


# Constantes universales
GravUn = 6.67430E-11  # m^3/kg/s^2 Constante de gravitación universal
Rg = 8.31447   #[J/(mol·K)] Constante universal de los gases
R_Tierra = 6371000 #[m] Radio de la Tierra
M_tierra = 5.972168e24  #[kg] Masa de la Tierra

# Funciones
#Funcion para normalizar vectores
def normalized(vec):
  assert np.linalg.norm(vec) > 0
  return vec / np.linalg.norm(vec)

def calc_gravedad(altura_z):
  return GravUn * M_tierra / (altura_z + R_Tierra)**2

#Calcular la gravedad en la superficie
g0 = calc_gravedad(0)
#print(g0)