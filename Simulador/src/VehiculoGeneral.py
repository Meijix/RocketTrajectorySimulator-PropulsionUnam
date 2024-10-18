
from Simulador.src.condiciones_init import *
from Simulador.PaqueteFisica.Componentes import *
from Simulador.PaqueteFisica.cohete import *
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
avionica_posicion = 0.20

#10. Carga Util (CU)
CU_masa = 4.3
CU_longitud = 0.3
CU_diam_ext = 0.14
CU_posicion = 0.50

#11. Droguechute
drogue_masa = 0.6
drogue_longitud = 0.17
drogue_diam_ext = 0.14
drogue_posicion = 1.0

#12. Mainchute
main_masa = 1.7
main_longitud = 0.30
main_diam_ext = 0.14
main_posicion = 1.4

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
nariz = Cono("Nariz", nariz_masa , np.array([0.0, 0.0, 0.0]), nariz_longitud , diam_ext, nariz_tipo)
coples = Cilindro("Coples", coples_masa, np.array([0.0,0.0, nariz.bottom[2]]),coples_longitud, diam_ext, diam_ext-espesor)
tubo_recup = Cilindro("Tubo recuperación", tubo_recup_masa, np.array([0.0, 0.0, coples.bottom[2]]), tubo_recup_longitud, diam_ext, diam_ext-espesor)
transfer = Cilindro("Transferidor", transfer_masa, np.array([0.0, 0.0, tubo_recup.bottom[2]]), transfer_longitud, diam_ext, diam_ext-espesor)
#tanquelleno = Cilindro("Tanquelleno", 22.0, np.array([0.0, 0.0, fuselaje.bottom[2]]), 1.33, diam_ext, 0)
tanquevacio = Cilindro("Tanquevacio", tanquevacio_masa, np.array([0.0, 0.0, transfer.bottom[2]]), tanquevacio_longitud, diam_ext, diam_ext-espesor)
#NOX
valvulas = Cilindro("Valvulas", valvulas_masa , np.array([0.0, 0.0, tanquevacio.bottom[2]]), valvulas_longitud, diam_ext, diam_ext-espesor)
#Grano
CC = Cilindro("Camara de Combustión", CC_masa, np.array([0.0, 0.0,valvulas.bottom[2]]),CC_longitud,diam_ext, CC_diam_int)

boattail = Boattail("Boattail", boattail_masa, np.array([0.0, 0.0, CC.bottom[2]]), boattail_longitud, diam_ext, boattail_diam_int, espesor)

#Componentes internos
avionica = Cilindro("Aviónica", avionica_masa, np.array([0.0, 0.0, avionica_posicion]), avionica_longitud, avionica_diam_ext, 0)
CU = Cilindro("CU", CU_masa, np.array([0.0, 0.0, CU_posicion]), CU_longitud, CU_diam_ext, 0)
drogue = Cilindro("Drogue", drogue_masa, np.array([0.0, 0.0, drogue_posicion]), drogue_longitud, drogue_diam_ext, 0)
main = Cilindro("Main", main_masa, np.array([0.0, 0.0, main_posicion]), main_longitud, main_diam_ext, 0)

aletas= Aletas("Aletas", aletas_masa, np.array([0.0, 0.0, CC.bottom[2]]), diam_ext, aletas_n, aletas_longitud, aletas_cuerda, aletas_altura, aletas_base, aletas_angulo)

#Combustibles del cohete
oxidante = Cilindro("Oxidante", oxidante_masa, np.array([0.0, 0.0, transfer.bottom[2]]), oxidante_longitud, oxidante_diam_ext, 0)
grano = Cilindro("Grano", grano_masa , np.array([0.0, 0.0, valvulas.bottom[2]]), grano_longitud , grano_diam_ext, grano_diam_int)

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

Vehiculo = Cohete("Xitle", "hibrido", componentes, componentes_externos, tabla_Cd_fpath, tabla_empuje_fpath, tabla_masa_fpath, riel)
Vehiculo.d_ext=diam_ext
#print(Xitle)

if __name__ == "__main__":
    #NOTA: en los bottom de todos los componentes tambien se esta sumando la longitud a los ejes x y
    #print(boattail.bottom)
    print("\n Datos generales")
    print("Nombre del cohete: ", Vehiculo.nombre)
    print("El centro de gravedad es:",Vehiculo.CG[2], "metros")
    print("El centro de presión es:", Vehiculo.CP[2], "metros")
    #print(Xitle.CN)
    print("La longitud total de Xitle es", Vehiculo.longtotal, "[m]")
    print("La masa inicial total es:",Vehiculo.masa, "kg")
    print("El impulso total es:", Vehiculo.I_total, "N s")
    print("El área transversal del cohete es:", Vehiculo.A, "m^2")
    print("El diámetro exterior del cohete es:", Vehiculo.d_ext, "m")