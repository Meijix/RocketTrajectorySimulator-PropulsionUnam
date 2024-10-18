##Listas de resultados importantes

import matplotlib.pyplot as plt

#from cohete import*
from Simulador.src.Xitle import *
from Simulador.utils.dibujarCohete import *

CG_list=[]
CP_list=[]
Ix_list=[]
long_list=[]
masas_list=[]

for comp in Xitle.componentes.values():
  long_list.append(0.0)
  long_list.append(comp.bottom[2])

print("\nMasas")
for comp in Xitle.componentes.values():
  masas_list.append(comp.masa)
  print(comp.nombre, comp.masa)

masas_list.append(Xitle.masa)
print(Xitle.nombre, Xitle.masa)

print("\nCentros de gravedad")
for comp in Xitle.componentes.values():
  CG_list.append(comp.posicion[2]+comp.CG[2])
  print(comp.nombre, comp.posicion[2] + comp.CG[2])

CG_list.append(Xitle.CG[2])
print(Xitle.nombre, Xitle.CG[2])

print("\nCentros de presión")
for comp in Xitle.componentes.values():
  CP_list.append(comp.posicion[2]+comp.CP[2])
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


print(CG_list)
print(CP_list)
print(long_list)
p=len(CG_list)-1



y = np.zeros_like(CG_list)
y_long = np.zeros_like(long_list)

'''
plt.figure(figsize=(12,1.5))
plt.plot(long_list,y_long,color= 'lightblue',alpha=0.9)
plt.scatter(long_list,y_long,color='navy',marker="|")
plt.scatter(CG_list[:p],y[:p],color='darkorange')#CGs de los componentes
plt.scatter(CP_list[:p],y[:p],color='green') #CPs de los componentes
plt.scatter(CG_list[-1],y[-1],color='red',marker="*", s=100) #CG del cohete complfuncompleto
plt.scatter(CP_list[-1],y[-1],color='blue',marker= "*", s=100) #CP del cohete complfuncompleto

plt.title("CG y CP posicionados de los componentes en Cohete Xitle2")
plt.show()
'''
# Dibujar un cohete
dibujar_cohete(4.2, 0, 180, 3.5)


print(CG_list)
print(CP_list)
print(long_list)
p=len(CG_list)-1

#plt.plot(long_list,y_long,color= 'lightblue',alpha=0.9)
plt.scatter(long_list,y_long,color='navy',marker="|", s=500)
plt.scatter(CG_list[:p],y[:p],color='darkorange', s=25, alpha=0.7, marker="P")#CGs de los componentes
plt.scatter(CP_list[:p],y[:p],color='green', s=25, alpha= 0.7, marker="X") #CPs de los componentes
plt.scatter(CG_list[-1],y[-1],color='red',marker="P", s=100) #CG del cohete complfuncompleto
plt.scatter(CP_list[-1],y[-1],color='blue',marker= "X", s=100) #CP del cohete complfuncompleto

plt.gca().set_aspect("equal")
plt.show()