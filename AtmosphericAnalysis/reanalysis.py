import netCDF4
import numpy as np
import matplotlib.pyplot as plt

# Open the netCDF file
nc = netCDF4.Dataset('ncep_ncar_reanalysis.nc', 'r')

# Extract the wind speed data
wspd = nc.variables['wspd'][:]

# Calculate the long-term mean wind speed
mean_wspd = np.mean(wspd, axis=0)

# Plot the mean wind speed
import matplotlib.pyplot as plt
plt.imshow(mean_wspd)
plt.colorbar()
plt.show()