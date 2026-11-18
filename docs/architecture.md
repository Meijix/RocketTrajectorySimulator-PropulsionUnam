# Architecture

## Layers

The repository has two layers. `Paquetes/` holds the library, which knows nothing about a particular rocket or launch. `Simulador/` holds everything that uses the library for the Xitle II, including the scripts, the graphical interface and the saved results.

```text
Paquetes/
  PaqueteFisica/   rocket, components, flight, atmosphere, wind, rail
  PaqueteEDOs/     my ODE integrators and the catalog of all nine methods
  utils/           saving and loading results, coordinates, drawing
Simulador/
  src/             Xitle II definition, launch conditions, flight scripts
  GUI/             window (ModernGUI.py), backend.py and mapa.py
  Visualizacion/   plots, animations, integrator comparison
  Resultados/      saved runs and the comparison with the measured flight
  VarParams/       parameter sweeps (unfinished)
  CasosSimples/    test problems with analytical solutions
Archivos/          thrust curves, Cd table, real flight data
Extras/            loose analysis scripts and prototypes
tests/             pytest suite
```

## How a flight is computed

A flight needs four objects.

1. A `Cohete` (rocket), built from a dictionary of components plus three CSV tables for thrust, drag coefficient and motor mass. It also holds the launch rail.
2. An `atmosfera` (atmosphere) for the site and the day.
3. A `Viento` (wind).
4. A `Vuelo` (flight), which receives the other three.

`Vuelo.simular_vuelo` takes the initial state, the maximum time, the step and the name of the integrator. It integrates until the rocket hits the ground and returns the times, the states and a set of derived quantities such as forces, Mach number and angle of attack.

There are two ways to reach that call. The scripts in [Simulador/src/](../Simulador/src/) import a rocket that is already built and write CSV and JSON files. The interface goes through [Simulador/GUI/backend.py](../Simulador/GUI/backend.py), which builds the same objects from the form fields and returns a pandas DataFrame. The tests use the backend too, so they exercise the same path as the window.

## State vector

The state has eight entries.

| Index | Name | Meaning | Unit |
| --- | --- | --- | --- |
| 0 | x | horizontal position along the rail azimuth | m |
| 1 | y | horizontal position across, to the left of x | m |
| 2 | z | height above the launch site | m |
| 3 to 5 | vx, vy, vz | velocity | m/s |
| 6 | theta | pitch angle from the horizontal | rad |
| 7 | omega | pitch rate | rad/s |

The rocket rotates only in the x-z plane. The y coordinate changes when a crosswind drags the rocket sideways, but there is no yaw or roll.

## Axes and conventions

The origin is the launch site. The x axis points in the horizontal direction the rail leans toward, y is horizontal and to the left of x, and z is up. The rail azimuth is a compass bearing measured clockwise from north, and [Paquetes/utils/geografia.py](../Paquetes/utils/geografia.py) uses it to turn x and y into latitude and longitude.

Positions along the rocket are measured from the nose tip toward the tail. Every component stores the position of its front end in that system, and its own center of gravity and center of pressure relative to that front end.

The wind class takes the direction the wind blows toward, measured from the x axis toward +y. Weather data gives the direction the wind comes from, measured from north. The function `direccion_viento_simulador` converts one into the other.

Angles are radians inside the physics code and degrees in the form fields, the conditions file and the exported tables. Everything else is in SI units.

## Imports

Most scripts add the repository root to `sys.path` before importing, so they work both as `python -m Simulador.src.VueloLibre` and as a plain file path. The packages are imported by their full name, for example `Paquetes.PaqueteFisica.vuelo`.
