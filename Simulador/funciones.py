
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy.interpolate import interp1d
import math
from math import pi
import random

#Funcion para normalizar vectores
def normalized(vec):
  assert np.linalg.norm(vec) > 0
  return vec / np.linalg.norm(vec)