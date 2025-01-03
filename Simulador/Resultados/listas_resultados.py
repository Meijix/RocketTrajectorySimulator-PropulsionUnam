##Listas de resultados importantes
import matplotlib.pyplot as plt
import sys
import os
import numpy as np

# Agregar la ruta del directorio que contiene los paquetes al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

#from cohete import*
from Simulador.src.XitleFile import Xitle
from Paquetes.utils.dibujar_cohete2 import dibujar_cohete2

CG_list=[]
CP_list=[]
Ix_list=[]
long_list=[]
long_ext_list=[]
masas_list=[]

for comp in Xitle.componentes.values():
    long_list.append(0.0)
    long_list.append(comp.bottom[2])

print("\nLongitudes")
for comp in Xitle.componentes.values():
    print(comp.nombre, comp.bottom[2])

#Lista de longitudes de los componentes externos 
#Se empieza a medir desde la punta de la nariz
avance = 0
for comp in Xitle.componentes_externos.values():
    #Separacion entre componentes
    avance += comp.long
    long_ext_list.append(avance)
    #CG de los componentes
    pos_CG = comp.posicion[2] + comp.CG[2]
    CG_list.append(pos_CG)
    #CP de los componentes
    pos_CP = comp.posicion[2] + comp.CP[2]
    CP_list.append(pos_CP)


print("\nMasas")
for comp in Xitle.componentes.values():
    masas_list.append(comp.masa)
    print(comp.nombre, comp.masa)

masas_list.append(Xitle.masa)
print(Xitle.nombre, Xitle.masa)

print("\nCentros de gravedad")
for comp in Xitle.componentes.values():
    
    print(comp.nombre, pos_CG)

CG_list.append(Xitle.CG[2])
print(Xitle.nombre, Xitle.CG[2])

print("\nCentros de presión")
for comp in Xitle.componentes.values():
    print(comp.nombre, comp.posicion[2] + comp.CP[2], comp.CN)

CP_list.append(Xitle.CP[2])
print(Xitle.nombre, Xitle.CP[2])

print("\nMomentos de inercia")
for comp in Xitle.componentes.values():
    print(comp.nombre, comp.Ix)
print(Xitle.nombre, Xitle.Ix, "[kg m^2]")

print("\n Datos generales")
print("La longitud total de Xitle es", Xitle.longtotal, "[m]")
print("La masa total de Xitle es", Xitle.masa, "[kg]")
print("El impulso total del motor es", Xitle.I_total)

p=len(CG_list)-1
y = np.zeros_like(CG_list)
y_long = np.zeros_like(long_list)
y_ext = np.zeros_like(long_ext_list)

#Longitud de los componentes para el dibujo
long_nariz=Xitle.componentes['Nariz'].long
long_fuselaje=Xitle.long_fuselaje
root_aletas=Xitle.componentes['Aletas'].C_r
tip_aletas=Xitle.componentes['Aletas'].C_t
long_boat=Xitle.componentes['Boattail'].long
fin_height=Xitle.componentes['Aletas'].span
rear_boat=Xitle.componentes['Boattail'].dR

# Crear figura
fig, ax = plt.subplots(figsize=(10, 4))  # Ajustar el tamaño de la figura
dibujar_cohete2(ax, angle=0, x_cm=Xitle.CG[2], y_cm=0, body_l=long_fuselaje, body_w=Xitle.d_ext, nose_l=long_nariz, fin_tip= tip_aletas, fin_root=root_aletas, fin_h=fin_height, boattail_length=long_boat, boat_rear=rear_boat)

# Dibujar elementos del cohete

#plt.scatter(long_list, y_long, color='gold', marker="|", s=500) #label="Separacion entre componentes")
plt.scatter(long_ext_list, y_ext, color='gold', marker="|", s=500)  # label="Separacion entre componentes")
plt.scatter(CG_list[:p], y[:p], color='darkorange', s=50, alpha=0.8, marker="P", label="CGs componentes")  # CGs de los componentes
plt.scatter(CP_list[:p], y[:p], color='yellowgreen', s=50, alpha=0.8, marker="X", label="CPs componentes")       # CPs de los componentes
plt.scatter(CG_list[-1], y[-1], color='red', marker="P", s=150, label="CG total")  # CG del cohete completo
plt.scatter(CP_list[-1], y[-1], color='dodgerblue', marker="X", s=150, label="CP total")  # CP del cohete completo

# Estética del gráfico
ax.set_aspect("equal")  # Asegurar proporción igual en el eje
plt.title("Visualización del vehiculo", fontsize=12, weight='bold')
plt.xlabel("Longitud (m)")
plt.ylabel("Eje transversal (m)")
plt.ylim(-0.5, 0.5)  # Limitar el eje y
plt.legend(loc="best", fontsize=8)  # Colocar la leyenda automáticamente
plt.grid(True, linestyle='--', alpha=0.7)  # Agregar una cuadrícula suave
plt.tight_layout()  # Ajustar márgenes

# Mostrar el gráfico
plt.show()
