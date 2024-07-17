#from cohete import*
from Xitle import *

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