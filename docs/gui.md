# Graphical interface

[Simulador/GUI/](../Simulador/GUI/) has four files.

| File | Role |
| --- | --- |
| [ModernGUI.py](../Simulador/GUI/ModernGUI.py) | the window, built with customtkinter |
| [backend.py](../Simulador/GUI/backend.py) | turns form values into simulator objects and results |
| [mapa.py](../Simulador/GUI/mapa.py) | map background and interactive map |
| [GUI.py](../Simulador/GUI/GUI.py) | the previous interface, kept for reference |

```bash
python -m Simulador.GUI.ModernGUI
```

The window only collects values and draws results. All the computation is in the backend, which does not import tkinter, so it can be tested and used from a script without opening a window.

## Backend

### Parameters

The backend works with one flat dictionary of parameters. `PARAMS_XITLE` holds the default for every field, which is the Xitle II as defined in [XitleFile.py](../Simulador/src/XitleFile.py) and the conditions of its real flight. `RUTAS_XITLE` holds the paths of the three data tables under the keys `thrust`, `drag` and `mass`.

Field names carry a prefix for the component and a suffix for the quantity, such as `nose_len`, `coples_mass` or `cc_diam_ext`. Lengths are in metres, masses in kilograms and angles in degrees. A `_pos_z` field is the distance from the nose tip to the front of the component.

A few fields are text. `integrator` takes a flight key from the list `INTEGRADORES`. `recovery` takes one of the two entries of `RECUPERACION`, free flight or drogue at apogee. `wind_mode` takes one of the two entries of `VIENTOS`, the profile of the flight day or a constant wind. `wind_seed` and `atm_pressure_hpa` may be left empty, which means a different wind on each run and the standard pressure for the site altitude.

### Functions

| Function | Result |
| --- | --- |
| `validar_parametros(params)` | raises `ValueError` with a readable message if a value makes no physical sense |
| `construir_cohete(params, rutas)` | a `Cohete` |
| `crear_atmosfera(params)` | an `atmosfera` |
| `crear_viento(params)` | a `Viento`, from the day profile or from the constant wind fields |
| `analizar_estabilidad(params, rutas)` | per-component table plus mass, CG, CP and static margin at liftoff and with empty tanks |
| `ejecutar_simulacion(params, rutas, estado_cb, con_mapa)` | a DataFrame with the trajectory and a summary dictionary |
| `vuelo_real()` | the GPS track of the real flight read from `FTW.csv` |
| `datos_mapa_interactivo(df, resumen)` | the data the interactive map needs |

`construir_cohete` skips internal components whose mass is zero. That is how the inert motor mass field works, since it is zero for the Xitle II.

### Running a flight without the window

```python
from Simulador.GUI import backend

params = dict(backend.PARAMS_XITLE, integrator="LSODA", wind_seed=1)
df, resumen = backend.ejecutar_simulacion(params, backend.RUTAS_XITLE)
print(resumen["apogeo"], resumen["lat_impacto"], resumen["lon_impacto"])
```

The DataFrame has one row per saved time. Its columns are `t`, position, velocity, `theta` and `alpha` in degrees, `omega`, `velocidad`, `aceleracion`, `acel_angular`, `masa`, `CG`, `CP`, `margen` in calibers, `mach`, `cd`, `gamma`, the three force magnitudes `empuje`, `arrastre` and `normal`, the wind, and `latitud` and `longitud` of each point.

The summary has the event times, apogee, top speed and Mach, largest acceleration, rail exit speed, impact speed, distance and bearing of the impact, and the coordinates of launch, apogee and impact. If the launch site is within 1 km of the real one, `resumen["vuelo_real"]` holds the GPS track so the map can draw both. With `con_mapa=True` the summary also carries the downloaded map image.

## Map

`descargar_mosaico` downloads the OpenStreetMap tiles that cover a set of points, joins them into one image and returns it with the pixel extent that matplotlib needs. It picks the highest zoom at which the area fits in a grid of four by four tiles. Without a connection it returns `None` and the interface draws the track on a blank background.

`a_pixeles` converts latitude and longitude to Web Mercator pixels at a given zoom. The interface uses it to draw the track over the image.

`escribir_html` writes a page with a Leaflet map that shows the simulated track, the launch, apogee and impact points, and the real track when there is one. By default the file goes to the system temporary folder, and the interface opens it in the browser.

## Window

`App` is the main window. It has six tabs and a row of buttons.

| Tab | Class | Contents |
| --- | --- | --- |
| Cohete | `RocketTab` | one frame of fields per component |
| Tablas de Datos | `DataTablesTab` | load and plot the thrust, Cd and motor mass tables |
| Simulación | `SimulationEnvironmentTab` | site, atmosphere, wind, rail, step, integrator, recovery |
| Análisis (CG-CP) | `StabilityTab` | per-component table and static margin |
| Resultados | `ResultsTab` | flight summary, six plots and CSV export |
| Mapa | `MapTab` | track over the map, impact coordinates, link to the interactive map |

The buttons run the simulation, redraw the rocket sketch, and save or load the whole configuration as JSON. The saved file is the parameter dictionary plus the three table paths.

When the run button is pressed, the window validates the parameters and submits `ejecutar_simulacion` to a separate process. It checks every 200 ms whether the process has finished and keeps responding in the meantime. I run it in a process because calling the simulator from a thread of the interface is not safe with Tk.

The small map in the simulation tab uses `tkintermapview`, which crashes with Tk 9. The module checks the Tk version on import and shows the coordinates as text in that case. The map tab draws with matplotlib and works with any version.

## Previous interface

`GUI.py` was the first interface. It is not maintained and may not match the current physics package. `ModernGUI.py` replaced it.
