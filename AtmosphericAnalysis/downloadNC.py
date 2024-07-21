# Install and load required packages
if(!require("RNCEP")) install.packages("RNCEP")
if(!require("lubridate")) install.packages("lubridate")
if(!require("tidyverse")) install.packages("tidyverse")
if(!require("sf")) install.packages("sf")

library(RNCEP)
library(lubridate)
library(tidyverse)
library(sf)

# Define the necessary arguments
month_range <- c(1,12)     # period of months
year_range <- c(2023,2023) # period of years

lat_range <- c(-120, -60)  # latitude range for Mexico and United States
lon_range <- c(-170, -60)  # longitude range for Mexico and United States

# Download wind data (uwnd and vwnd) for 2023
data_uwnd <- NCEP.gather("uwnd",    # name of the variable
                         850, # pressure level 850hPa
                         month_range, year_range,
                         lat_range, lon_range,
                         return.units = TRUE,
                         reanalysis2=TRUE)

data_vwnd <- NCEP.gather("vwnd",    # name of the variable
                         850, # pressure level 850hPa
                         month_range, year_range,
                         lat_range, lon_range,
                         return.units = TRUE,
                         reanalysis2=TRUE)