from numpy import *
import numpy as np

def normalize_angle(angle_deg):
    while angle_deg > 180:
        angle_deg -= 360
    while angle_deg < -180:
        angle_deg += 360
    return angle_deg

def nice_angle(angle_rad):
    return np.array([normalize_angle(x) for x in np.rad2deg(angle_rad)])