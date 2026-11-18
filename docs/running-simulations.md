# Running a flight from scripts

[Simulador/src/](../Simulador/src/) defines the Xitle II, the launch conditions and two scripts that run a flight and save it.

```bash
python -m Simulador.src.VueloLibre        # no parachute
python -m Simulador.src.VueloParacaidas   # drogue parachute at apogee
```

## Launch conditions

[condiciones_init.py](../Simulador/src/condiciones_init.py) is the place to change how a flight is run. It defines these names at module level, and the other scripts import them.

| Name | Value in the repository | Meaning |
| --- | --- | --- |
| `riel` | 10 m at 83 degrees | launch rail |
| `azimut_riel` | 220 | compass bearing the rail leans toward |
| `latitud_cord`, `longitud_cord`, `altitud_cord` | Spaceport America | launch site |
| `viento_actual` | profile of the flight day, seed 2024 | wind |
| `atmosfera_actual` | standard atmosphere plus 20 K at 1395 m | atmosphere |
| `estado` | at rest on the rail | initial state |
| `dt` | 0.01 | step in seconds, or maximum step for adaptive methods |
| `t_max` | 400 | time limit in seconds |
| `dt_out` | equal to `dt` | interval between saved points for my integrators |
| `integrador_actual` | `DOP853` | integrator key |

To change the integrator, set `integrador_actual` to any key from the [catalog](integrators.md#catalog). To use a constant wind, replace `viento_actual` with a `Viento` built by hand. A commented line in the file shows an example. To use the sea level standard atmosphere, set `atmosfera_actual = atmosfera()`.

`dt_out` should be a multiple of `dt`. If it is smaller, it limits the step of my integrators.

## Conditions of the flight day

[dia_de_vuelo.py](../Simulador/src/dia_de_vuelo.py) reads [condiciones_2024-06-22.json](../Archivos/DatosVuelo/condiciones_2024-06-22.json), which stores the site, the atmosphere and the wind of the real flight with the source of each value.

| Function | Result |
| --- | --- |
| `cargar_condiciones()` | the file as a dictionary |
| `crear_atmosfera(condiciones)` | an `atmosfera` for the site altitude, temperature offset and pressure |
| `perfil_de_viento(condiciones, azimut_riel)` | wind levels as heights above the site, with directions converted to simulator angles |
| `crear_viento(condiciones, azimut_riel, semilla)` | a `Viento` with that profile plus gusts |

## Rocket definition

[XitleFile.py](../Simulador/src/XitleFile.py) builds the Xitle II. It creates each component with its mass, position and dimensions, chains the external ones by placing each at the `bottom` of the one before, and collects them in two dictionaries. Then it creates the `Cohete` named `Xitle` with the static test thrust curve, the Cd table and the motor mass table, and attaches a drogue parachute with Cd 0.8 and area 0.7 m².

Importing the module builds the rocket, so `from Simulador.src.XitleFile import Xitle` is enough to get it. Running the file prints its center of gravity, center of pressure, length, mass and total impulse.

To simulate a different rocket, copy this file, change the components and import the new object in the flight script.

[XitleFileMod.py](../Simulador/src/XitleFileMod.py) is a copy with the masses shifted toward the tail and smaller fins. It gives an unstable rocket named `XitleMod`, which I used to show what the simulator does with a negative static margin.

[vehiculo_general.py](../Simulador/src/vehiculo_general.py) is an earlier version of the same definition with every dimension in a named variable. It uses a different thrust curve (`MegaPunisherBien.csv`) and none of the current scripts import it.

## Flight scripts

[VueloLibre.py](../Simulador/src/VueloLibre.py) removes the parachute from the rocket, creates a `Vuelo` with the atmosphere and wind from the conditions module, calls `simular_vuelo`, and saves the result. A commented line switches the rocket to `XitleMod`.

[VueloParacaidas.py](../Simulador/src/VueloParacaidas.py) does the same with a parachute of Cd 1.2 and area 0.802 m² that opens at apogee.

Both print the run time. A free flight with DOP853 and a step of 0.01 s takes around ten seconds.

## Output files

Each script writes two files to `Simulador/Resultados/OutputFiles/<flight type>-<integrator>-100/`. With the default settings those folders are `VueloLibre-DOP853-100` and `VueloParacaidas-DOP853-100`. A new run overwrites the previous one in the same folder.

`datos.csv` has one row per saved time.

| Columns | Contents |
| --- | --- |
| `t` | time in seconds |
| `x`, `y`, `z` | position in metres |
| `vx`, `vy`, `vz` | velocity in m/s |
| `thetas`, `omegas` | pitch angle in radians and pitch rate |
| `CPs`, `CGs` | center of pressure and center of gravity, in metres from the nose tip |
| `masavuelo` | mass in kg |
| `viento_mags`, `viento_dirs`, `wind_xs`, `wind_ys`, `wind_zs` | wind speed, direction and components |
| `Tmags`, `Dmags`, `Nmags` | magnitudes of thrust, drag and normal force in newtons |
| `Txs` to `Nzs` | components of the three forces |
| `accels`, `accangs` | linear acceleration vector and angular acceleration |
| `palancas`, `torcas` | lever arm and torque |
| `Gammas`, `Alphas` | flight path angle and angle of attack in radians |
| `Cds`, `Machs` | drag coefficient and Mach number |

The columns `viento_vecs`, `accels` and `palancas` hold whole vectors written as text.

`datos.json` holds the summary.

| Key | Contents |
| --- | --- |
| `nombre cohete` | rocket name |
| `d_ext` | outer diameter |
| `t_MECO` | burnout time |
| `tiempo_salida_riel`, `tiempo_apogeo`, `tiempo_impacto` | event times |
| `max_altitude`, `max_speed` | apogee and top speed |
| `max_acceleration_linear`, `max_acceleration_angular` | largest accelerations |

The plotting and animation scripts read these two files. The [analysis page](analysis-scripts.md) describes them.
