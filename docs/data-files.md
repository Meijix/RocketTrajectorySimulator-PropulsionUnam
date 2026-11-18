# Data files

[Archivos/](../Archivos/) holds the input tables of the simulator and the records of the real flight of the Xitle II on 22 June 2024 at Spaceport America.

## Tables the simulator reads

| File | Columns | Use |
| --- | --- | --- |
| [cdmachXitle.csv](../Archivos/cdmachXitle.csv) | `mach`, `cd` | drag coefficient against Mach number |
| [CurvasEmpuje/pruebaestaica28mayo2024.csv](../Archivos/CurvasEmpuje/pruebaestaica28mayo2024.csv) | `time`, `thrust` | thrust curve from the static test of 28 May 2024, 21.6 s long |
| [CurvasEmpuje/MegaPunisherFatMasadot.csv](../Archivos/CurvasEmpuje/MegaPunisherFatMasadot.csv) | `Time (s)`, `Oxidizer Mass (kg)`, `Fuel Mass (kg)` | propellant masses from a motor simulation, 10 s long |

Time is in seconds, thrust in newtons and mass in kilograms. The rocket reads these three files when it is created. The interface can load other files in their place as long as they have the same column names.

The mass table is shorter than the thrust curve, so the rocket uses only its first and last rows. The [physics page](physics.md#motor-tables) explains how the mass is spread over the burn.

## Other thrust curves

`CurvasEmpuje/MegaPunisherBien.csv` and `CurvasEmpuje/curvapunisherFat.csv` are simulated thrust curves of the same motor. The first one was the input before the static test data existed. `CurvasEmpuje/Copia de llenadoSpaceport2024.csv` is the ground system log of the tank filling at the competition, with load cell and pressure readings.

## Conditions of the flight day

[DatosVuelo/condiciones_2024-06-22.json](../Archivos/DatosVuelo/condiciones_2024-06-22.json) stores what the simulator needs to reproduce the day of the launch.

| Section | Contents |
| --- | --- |
| `sitio` | name, latitude, longitude and altitude of the site |
| `lanzamiento` | date, local time, rail azimuth and elevation |
| `vuelo_medido` | measured apogee and the coordinates of the apogee and the last GPS point |
| `atmosfera` | surface temperature, site pressure, temperature offset from the standard atmosphere, humidity |
| `viento` | gust parameters and six wind levels with altitude, speed and direction |

Each section has a note with the source of its values. The site comes from the first GPS point of the tracker. The weather values come from the Open-Meteo reanalysis and forecast archive, so they are model data and not measurements at the pad. The rail elevation was not recorded, and 83 degrees is the value that reproduces the GPS track.

Wind directions in this file follow the weather convention, the direction the wind comes from in degrees clockwise from north.

## Records of the real flight

| File | Contents |
| --- | --- |
| [DatosVuelo/FTW.csv](../Archivos/DatosVuelo/FTW.csv) | Featherweight GPS tracker log with position, altitude in feet, horizontal and vertical speed |
| [DatosVuelo/ASYB.csv](../Archivos/DatosVuelo/ASYB.csv) | telemetry from the team flight computer with altitude, pressure, temperature, acceleration and rotation |
| [DatosVuelo/DatosExperimentalesLimpios.csv](../Archivos/DatosVuelo/DatosExperimentalesLimpios.csv) | both records cleaned and placed side by side |
| [AlturavsTiempo-Xitle2.csv](../Archivos/AlturavsTiempo-Xitle2.csv) | height in kilometres against time |
| `DatosVuelo/Copia de FthrWtTRAKR_fw2kml_06-22-2024_12_37_13.kml` | the GPS track for Google Earth |

The Excel files next to them are the spreadsheets where I cleaned and analysed the same records.

The interface reads `FTW.csv` to draw the real track on the map. It takes the part of the log from the last point on the ground before the climb to the last point received.

## OpenRocket

[VueloOpenRocket.csv](../Archivos/VueloOpenRocket.csv) and [OpenRocketViento.csv](../Archivos/OpenRocketViento.csv) are exports of OpenRocket simulations of the Xitle II, without and with wind. I use them as a second reference next to the measured flight.

## Scripts in this folder

[DatosVuelo/DatosVuelo.py](../Archivos/DatosVuelo/DatosVuelo.py) plots height and speed of the measured flight, my simulation and the OpenRocket export on the same axes and marks the apogee and the top speed of each.

[DatosVuelo/vientoVSnoviento.py](../Archivos/DatosVuelo/vientoVSnoviento.py) compares two saved simulations, one from the folder ending in 110 and one from the folder ending in 100, to show the effect of the wind on height and horizontal displacement.
