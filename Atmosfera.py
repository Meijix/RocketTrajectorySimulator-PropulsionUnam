# Modelar la atmosfera: Temperatura, desidad, presion vs altura, viento

import numpy as np
import matplotlib.pyplot as plt

i = 0
fin = 0
g0 = 9.81 #[m/s^2]
lam0 = -6.5*10**(-3)
R = 287
lamb2 = 1*10**(-3)
lamb3 = 2.8*10**(-3)
lamb5 = -2.8*10**(-3)
lamb6 = -2*10**(-3)

# Iniciales
T0 = 288.15
P0 = 101325
rho0 = 1.225
z11 = 11000
T11 = 216.65
P11 = 22614.20668668
rho11 =0.36363089
z20 = 20000
T20 = T11
P20 = 5466.4820
rho20 =0.08789969
z32 = 32000
T32 = 228.65
P32 = 865.975166
rho32 = 0.01319393
z47 = 47000
T47 = 270.6472
P47 = 110.53935
rho47 = 0.00142263
z51 = 51000
T51 = T47
P51 = 66.7077319
rho51 = 0.00085852161



# Vectores

z = np.array([0.0])
T = np.array([T0]) # [K]
P = np.array([P0]) # [Pa]
rho = np.array([rho0]) # [kg.m^3]

while fin == 0:
    z = np.append(z, z[i] + 1)
    i += 1

    if z[i] >= 0 and z[i] <= 11000:
        Temp = T0 + (z[i] * lam0)
        Pres = P0 * (1 + (z[i] * lam0) / T0) ** (-g0 / (R * lam0))
        Den = rho0 * (1 + (z[i] * lam0) / T0) ** ((-g0 / (R * lam0)) - 1)

    elif z[i] >= 11001 and z[i] <= 20000:
        Temp == Temp
        Pres = P11 * np.exp(-(g0 / (R * T11)) * (z[i] - z11))
        Den = rho11 * np.exp(-(g0 / (R * T11)) * (z[i] - z11))

    elif z[i] >= 20001 and z[i] <= 32000:
        Temp = T20 + (z[i]-z20)*lamb2
        Pres = P20 * ((T20 + (z[i]-z20)*lamb2)/T20) ** (-g0/(lamb2*R))
        Den = ((rho0*P20)/P0)*(((T20/T0)+(((z[i]-z20)*lamb2)/T0))**((-g0/(lamb2*R))-1))*((T0/T20)**(-g0/(lamb2*R)))

    elif z[i] >= 32001 and z[i] <= 47000:
        Temp = T32 + (z[i]-z32)*lamb3
        Pres = P32 * ((T32 + (z[i]-z32)*lamb3)/T32) ** (-g0/(lamb3*R))
        Den = ((rho0*P32)/P0)*(((T32/T0)+(((z[i]-z32)*lamb3)/T0))**((-g0/(lamb3*R))-1))*((T0/T32)**(-g0/(lamb3*R)))

    elif z[i] >= 47001 and z[i] <= 51000:
        Temp == Temp
        Pres = P47 * np.exp(-(g0 / (R * T47)) * (z[i] - z47))
        Den = rho47 * np.exp(-(g0 / (R * T47)) * (z[i] - z47))

    elif z[i] >= 51001 and z[i] <= 71000:
        Temp = T51 + (z[i]-z51)*lamb5
        Pres = P51 * ((T51 + (z[i]-z51)*lamb5)/T51) ** (-g0/(lamb5*R))
        Den = ((rho0*P51)/P0)*(((T51/T0)+(((z[i]-z51)*lamb5)/T0))**((-g0/(lamb5*R))-1))*((T0/T51)**(-g0/(lamb5*R)))

    elif z[i] > 71000:
        fin = 1

    T = np.append(T, Temp)
    P = np.append(P, Pres)
    rho = np.append(rho, Den)


fig = plt.figure()
fig.clf()
ax = fig.subplots(1,3)

ax[0].plot(T,z)
ax[0].set_xlabel('Altura [m]')
ax[0].set_ylabel('Temperatura [K]')
ax[0].set_title('Temperatura')

ax[1].plot(z,P)
ax[1].set_xlabel('Altura [m]')
ax[1].set_ylabel('Presión [Pa]')
ax[1].set_title('Presión')


ax[2].plot(z,rho)
ax[2].set_xlabel('Altura [m]')
ax[2].set_ylabel('Densidad [kg.m^3]')
ax[2].set_title('Densidad')

fig.tight_layout()
plt.show()