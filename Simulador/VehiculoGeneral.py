
from condiciones_init import *
from Componentes import *
from cohete import *
from math import *

#Dimensiones principales del cohete
diam_ext = 0.152
espesor = 0.003
############################
#Creación de los componentes individuales
############################
#1. Nariz
nariz_masa = 0.8
nariz_longitud = 0.81
nariz_tipo = "ogiva"
#La nariz siempre esta en el 0 de SP
#nariz_posicion = np.array([0.0, 0.0, 0.0])

#2. Coples
coples_masa = 1.5
coples_longitud = 0.176
#coples_posicion = np.array([0.0,0.0, nariz.bottom[2]])

#3.Tubo de recuperacion
tubo_recup_masa = 2.3
tubo_recup_longitud = 0.92
#tubo_recup_posicion = np.array([0.0, 0.0, coples.bottom[2]])

#4.Transferidor de carga
transfer_masa = 1
transfer_longitud = 0.25
#transfer_posicion = np.array([0.0, 0.0, tubo_recup.bottom[2]])

#5.Tanque vacio
tanquevacio_masa = 8.7
tanquevacio_longitud = 1.25
#tanquevacio_posicion = np.array([0.0, 0.0, transfer.bottom[2]])

#6. Valvulas
valvulas_masa = 2.4
valvulas_longitud = 0.167
#valvulas_posicion = np.array([0.0, 0.0, tanquevacio.bottom[2]])

#7. Camara de combustion
CC_masa = 4.3
CC_longitud = 0.573
CC_diam_ext = diam_ext
CC_diam_int = 0.102
#CC_posicion = np.array([0.0, 0.0,valvulas.bottom[2]])

#8. Boattail
boattail_masa = 0.251
boattail_longitud = 0.12
boattail_diam_int = 0.132
#boattail_posicion = np.array([0.0, 0.0, CC.bottom[2]])

#Componentes inernos que se definen como CILINDROS SOLIDOS
#9. Avionica
avionica_masa = 1.8
avionica_longitud = 0.21
avionica_diam_ext = 0.14
avionica_diam_int = 0
#avionica_posicion = np.array([0.0, 0.0, 0.20])

#10. Carga Util (CU)
CU_masa = 4.3
CU_longitud = 0.3
CU_diam_ext = 0.14
CU_diam_int = 0
#CU_posicion = np.array([0.0, 0.0, 0.50])

#11. Droguechute
drogue_masa = 0.6
drogue_longitud = 0.17
drogue_diam_ext = 0.14
drogue_diam_int = 0
#drogue_posicion = np.array([0.0, 0.0, 1.0])

#12. Mainchute
main_masa = 1.7
main_longitud = 0.30
main_diam_ext = 0.14
main_diam_int = 0
#main_posicion = np.array([0.0, 0.0, 1.4])

#13. Aletas
aletas_masa = 1.1
aletas_longitud = 0.11
aletas_n = 4
aletas_cuerda = 0.3
aletas_altura = 0.1
aletas_base = 0.2
aletas_angulo = 25
#aletas_posicion = np.array([0.0, 0.0, CC.bottom[2]])

#14. Oxidante
oxidante_masa = 12.0
oxidante_longitud = 1.33
oxidante_diam_ext = 0.1461
oxidante_diam_int = 0
#oxidante_posicion = np.array([0.0, 0.0, transfer.bottom[2]])

#15. Grano
grano_masa = 4.0
grano_longitud = 0.505
grano_diam_ext = 0.158
grano_diam_int = 0.334
#grano_posicion = np.array([0.0, 0.0, valvulas.bottom[2]])


#Componentes externos
nariz = Cono("Nariz", 0.8 , np.array([0.0, 0.0, 0.0]), 0.81, diam_ext, "ogiva")
coples = Cilindro("Coples",1.5, np.array([0.0,0.0, nariz.bottom[2]]),0.176, diam_ext, diam_ext-espesor)
tubo_recup = Cilindro("Tubo recuperación", 2.3, np.array([0.0, 0.0, coples.bottom[2]]), 0.92, diam_ext, diam_ext-espesor)
transfer = Cilindro("Transferidor", 1, np.array([0.0, 0.0, tubo_recup.bottom[2]]), 0.25, diam_ext, diam_ext-espesor)
#tanquelleno = Cilindro("Tanquelleno", 22.0, np.array([0.0, 0.0, fuselaje.bottom[2]]), 1.33, diam_ext, 0)
tanquevacio = Cilindro("Tanquevacio", 8.7, np.array([0.0, 0.0, transfer.bottom[2]]), 1.25, diam_ext, diam_ext-espesor)
#NOX
valvulas = Cilindro("Valvulas", 2.4 , np.array([0.0, 0.0, tanquevacio.bottom[2]]), 0.167, diam_ext, diam_ext-espesor)
#Grano
CC = Cilindro("Camara de Combustión", 4.3, np.array([0.0, 0.0,valvulas.bottom[2]]),0.573,diam_ext, 0.102)

boattail = Boattail("Boattail", 0.251, np.array([0.0, 0.0, CC.bottom[2]]), 0.12, diam_ext, 0.132, espesor)

#Componentes internos
avionica = Cilindro("Aviónica", 1.8, np.array([0.0, 0.0, 0.20]), 0.21, 0.14, 0)
CU = Cilindro("CU", 4.3, np.array([0.0, 0.0, 0.50]), 0.3, 0.14, 0)
drogue = Cilindro("Drogue", 0.6, np.array([0.0, 0.0, 1.0]), 0.17, 0.14, 0)
main = Cilindro("Main", 1.7, np.array([0.0, 0.0, 1.4]), 0.30, 0.14, 0)
aletas= Aletas("Aletas", 1.1, np.array([0.0, 0.0, CC.bottom[2]]), diam_ext, 4, 0.11, 0.3, 0.1, 0.2, 25)

#Combustibles del cohete
oxidante = Cilindro("Oxidante", 12.0, np.array([0.0, 0.0, transfer.bottom[2]]), 1.33, 0.1461, 0)
grano = Cilindro("Grano", 4.0 , np.array([0.0, 0.0, valvulas.bottom[2]]), 0.505 , 0.158, 0.334)

# Tablas de Cd, empuje y masa
tabla_Cd_fpath = '../Archivos/cdmachXitle.csv'
tabla_Cd_fpath = r'C:\Users\Natalia\OneDrive\Tesis\GithubCode\3DOF-Rocket-PU\Archivos\cdmachXitle.csv'

tabla_empuje_fpath = '../Archivos/MegaPunisherBien.csv'
tabla_empuje_fpath = r'C:\Users\Natalia\OneDrive\Tesis\GithubCode\3DOF-Rocket-PU\Archivos\MegaPunisherBien.csv'
tabla_masa_fpath = '../Archivos/MegaPunisherFatMasadot.csv'

tabla_masa_fpath = r'C:\Users\Natalia\OneDrive\Tesis\GithubCode\3DOF-Rocket-PU\Archivos\MegaPunisherFatMasadot.csv'

#Lista de componentes y creación del vehículo completo
#Debe ser un diccionario con un nombre corto para cada componente
componentes = {'Nariz': nariz ,'coples': coples,'Tubo recuperación': tubo_recup, 'Transferidor de carga': transfer, 'Aviónica': avionica, 'Carga Útil': CU, 'drogue': drogue,
               'main': main, 'tanquevacio': tanquevacio,
               'oxidante': oxidante, 'valvulas': valvulas, 'grano': grano, 'Cámara Combustión': CC, 'Aletas': aletas, 'Boattail': boattail}

componentes_externos = {'Nariz': nariz ,'coples': coples,'Tubo recuperación': tubo_recup, 'Transferidor de carga': transfer, 'tanquevacio': tanquevacio,
               'oxidante': oxidante, 'valvulas': valvulas, 'grano': grano, 'Cámara Combustión': CC, 'Boattail': boattail}

Xitle = Cohete("Xitle", "hibrido", componentes, componentes_externos, tabla_Cd_fpath, tabla_empuje_fpath, tabla_masa_fpath, riel)
Xitle.d_ext=diam_ext
#print(Xitle)

if __name__ == "__main__":
    #NOTA: en los bottom de todos los componentes tambien se esta sumando la longitud a los ejes x y
    #print(boattail.bottom)
    print("\n Datos generales")
    print("El centro de gravedad es:",Xitle.CG[2], "metros")
    print("El centro de presión es:", Xitle.CP[2], "metros")
    #print(Xitle.CN)
    print("La longitud total de Xitle es", Xitle.longtotal, "[m]")
    print("La masa inicial total es:",Xitle.masa, "kg")
    print("El impulso total es:", Xitle.I_total, "N s")
    print("El área transversal del cohete es:", Xitle.A, "m^2")
    print("El diámetro exterior del cohete es:", Xitle.d_ext, "m")