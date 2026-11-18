# Physics package

[Paquetes/PaqueteFisica/](../Paquetes/PaqueteFisica/) contains the model of the rocket and its surroundings. Each file holds one class or one family of classes.

| File | Contents |
| --- | --- |
| [componentes.py](../Paquetes/PaqueteFisica/componentes.py) | `Componente` and its subclasses `Cono`, `Cilindro`, `Aletas`, `Boattail` |
| [cohete.py](../Paquetes/PaqueteFisica/cohete.py) | `Cohete` and `Parachute` |
| [atmosfera.py](../Paquetes/PaqueteFisica/atmosfera.py) | `atmosfera` |
| [viento.py](../Paquetes/PaqueteFisica/viento.py) | `Viento` |
| [riel.py](../Paquetes/PaqueteFisica/riel.py) | `Torrelanzamiento` |
| [vuelo.py](../Paquetes/PaqueteFisica/vuelo.py) | `Vuelo` |
| [atmosfera_alex.py](../Paquetes/PaqueteFisica/atmosfera_alex.py) | an earlier atmosphere script by a teammate, kept for reference and not imported anywhere |

## Components

A component has a name, a mass and the position of its front end, given as a three-entry array whose z entry is the distance from the nose tip. On creation it computes four things in its own coordinates.

| Attribute | Meaning |
| --- | --- |
| `CG` | center of gravity |
| `CP` | center of pressure |
| `CN` | normal force coefficient slope |
| `Ix` | moment of inertia about a transverse axis through its own CG |

`Cono` is the nose. Its CG sits at three quarters of its length from the tip. Its CP depends on the shape, with a factor of 2/3 for a cone (`conica`), 0.466 for an ogive (`ogiva`), 0.5 for a parabola (`parabolica`) and 0.333 for an ellipse (`eliptica`). Its `CN` is 2 for every shape.

`Cilindro` is a tube with an outer and an inner diameter. It serves for body tubes and, with inner diameter zero, for solid internal parts such as avionics, payload and packed parachutes. A cylinder contributes no normal force.

`Aletas` is the whole fin set. It takes the body diameter, the number of fins, the semispan, the root and tip chords and `X_R`, the distance the leading edge moves back between root and tip. `CP` and `CN` follow the Barrowman formulas, including the body interference factor. The last argument, `mid_sweep`, is ignored. I kept it so older calls still work, and the sweep now comes from `X_R`.

`Boattail` is the tail cone. Its `CN` is negative because the body narrows, which moves the center of pressure of the rocket forward.

Each component also has a `bottom` attribute, the position of its rear end. The scripts use `bottom[2]` to place the next component.

## Rocket

`Cohete` receives a name, a type string, the dictionary of all components, the dictionary of external components, the paths of the three tables and the rail.

```python
Xitle = Cohete("Xitle", "hibrido", componentes, componentes_externos,
               tabla_Cd_fpath, tabla_empuje_fpath, tabla_masa_fpath, riel)
```

The component dictionary must contain the keys `Nariz`, `Boattail`, `oxidante` and `grano`. The first gives the reference area, the second gives the total length, and the last two are the propellant masses that change during the burn.

The rocket adds up its components to get these values.

| Attribute | How it is computed |
| --- | --- |
| `masa` | sum of component masses |
| `CG` | mass-weighted average of component CGs |
| `Ix` | sum of component inertias moved to the rocket CG with the parallel axis theorem |
| `CP` | average of component CPs weighted by `CN` |
| `CN` | sum of component `CN` |
| `A` | cross section of the nose base |

### Motor tables

`cargar_tablas_motor` reads the thrust curve (columns `time` and `thrust`) and the mass table (columns `Time (s)`, `Oxidizer Mass (kg)` and `Fuel Mass (kg)`). It stores the burnout time `t_MECO` and the total impulse `I_total`, integrated with the trapezoid rule.

The two tables of the Xitle II do not last the same. The mass table comes from a motor simulation of 10 s and the thrust curve from a static test of 21.6 s. When the durations differ by more than 5 %, the rocket sets `masa_segun_impulso` and ignores the time axis of the mass table. It keeps the first and last masses and burns propellant in proportion to the impulse delivered so far. When the durations match, it interpolates the mass table as given.

`calc_empuje_magn(t)` interpolates the thrust and returns zero after burnout. `calc_Cd(mach)` interpolates the drag table (columns `mach` and `cd`).

`actualizar_masa(t)` sets the oxidizer and grain masses for time `t` and then recomputes mass, CG and inertia. The flight calls it inside every derivative evaluation, so every integrator sees the right mass at every stage.

### Parachute

`Parachute(cd, area_trans)` holds a drag coefficient and an area. `agregar_paracaidas` attaches one to the rocket and sets `parachute_added`. The flight switches `parachute_active1` on at apogee. The rocket supports one parachute.

## Atmosphere

`atmosfera()` with no arguments is the International Standard Atmosphere at sea level, built from eight layers up to 84.852 km. Three optional arguments adapt it to a launch.

| Argument | Meaning |
| --- | --- |
| `altitud_sitio` | site altitude above sea level in metres |
| `delta_T` | temperature offset from the standard, in kelvin, applied at every height |
| `presion_sitio` | measured pressure at the site in pascals |

`calc_propiedades(z)` returns temperature, density, pressure and speed of sound at height `z` above the site. It converts the geometric altitude to geopotential altitude, takes the temperature from the layer table plus the offset, and gets the pressure by integrating hydrostatic equilibrium layer by layer starting from the site pressure. Density comes from the ideal gas law. Above the last layer it returns the values of the layer top, and `h_max` tells the flight where aerodynamic forces stop.

## Wind

`Viento` produces a horizontal wind with gusts as a function of time and height.

| Argument | Meaning |
| --- | --- |
| `vel_base` | base speed in m/s |
| `ang_base` | direction the wind blows toward, in degrees from the x axis |
| `vel_mean`, `vel_var` | mean and standard deviation of the gust added to the base speed |
| `var_ang` | standard deviation of the direction in degrees |
| `dt_rafaga` | seconds between gust samples, 1 by default |
| `semilla` | seed for the random generator |
| `perfil` | optional list of (height above site, speed, direction) levels |

With `ang_base` at 0 the wind pushes the rocket along its flight direction. At 180 it is a headwind, and at 90 or 270 it is a crosswind.

Every `dt_rafaga` seconds the class draws a gust speed, a direction deviation and a tilt of up to 20 degrees from the horizontal. `vector_en(t, z)` interpolates between the two nearest samples, so asking for the same time twice gives the same wind. Integrators need that because they evaluate the derivatives several times per step and may repeat a step. If a profile was given, the base wind is interpolated between its levels at height `z`.

`reiniciar_rafagas` clears the samples at the start of each simulation. With a seed, each run repeats the same gust series. Without one, each run draws a new series.

## Rail

`Torrelanzamiento(longitud, angulo)` stores the rail length in metres and its elevation in degrees. The rail logic itself lives in the flight class.

## Flight

`Vuelo(vehiculo, atmosfera, viento)` holds the equations of motion and the integration loop.

### Forces

`fun_derivs(t, state)` returns the derivative of the state. It updates the rocket mass, gets the wind at that time and height, and subtracts it from the velocity to get the velocity relative to the air. Then it adds four accelerations.

- Thrust acts along the rocket axis, `(cos theta, 0, sin theta)`.
- Drag has magnitude `0.5 * rho * v² * A * Cd` and points against the relative velocity. When the parachute is open its own drag is added.
- The normal force has magnitude `0.5 * rho * v² * A * CN * |sin alpha|`, where alpha is the angle of attack. It lies in the pitch plane, perpendicular to the relative velocity, on the side that turns the nose back toward the airflow.
- Gravity follows the inverse square law with the height above sea level.

The angular acceleration comes from the torque of drag and normal force about the center of gravity. The lever arm is the vector from CG to CP, rotated from body coordinates to ground coordinates. The torque divided by `Ix` gives the pitch acceleration.

### On the rail

The rocket counts as on the rail while its distance from the origin is at most the rail length. During that phase it does not rotate, and `restringir_al_riel` keeps only the component of the acceleration along the rail axis. If the rocket is at the base and that component is negative, the acceleration is set to zero, so the rocket waits until thrust exceeds its weight.

### Integration

`simular_vuelo(estado, t_max, dt, dt_out, integrador)` resets the flight, picks the integration routine by name and then computes the derived quantities.

For `Euler`, `RungeKutta2`, `RungeKutta4` and `RKF45` it calls `_integrar_propio`. The step `dt` is the fixed step for the first three and the initial and maximum step for RKF45. Points are saved every `dt_out` seconds, and only the step that would cross a save time is shortened. Apogee is the first step above 5 m where the height decreases. Impact is found by linear interpolation inside the step where z turns negative.

For `RK45`, `RK23`, `DOP853`, `LSODA` and `BDF` it calls `_integrar_scipy`, which runs `solve_ivp` in two phases. The first phase ends at the apogee event, where the vertical velocity crosses zero downward above 5 m. The parachute opens there if the rocket has one. The second phase ends at the impact event, where z crosses zero after the first second. Here `dt` is the maximum step and `dt_out` is not used.

After integrating, the method walks along the saved trajectory and evaluates forces, angles and mass at each point with the same functions the integration used. It returns a tuple of 19 lists.

| Position | Name | Contents |
| --- | --- | --- |
| 0 | `tiempos` | times |
| 1 | `sim` | states |
| 2, 3 | `CPs`, `CGs` | axial positions of CP and CG |
| 4 | `masavuelo` | mass |
| 5, 6, 7 | `viento_vuelo_mags`, `viento_vuelo_dirs`, `viento_vuelo_vecs` | wind speed, direction and vector |
| 8, 9, 10 | `Tvecs`, `Dvecs`, `Nvecs` | thrust, drag and normal force vectors |
| 11 | `accels` | linear acceleration |
| 12 | `palancas` | lever arm from CG to CP |
| 13 | `accangs` | angular acceleration |
| 14, 15 | `Gammas`, `Alphas` | flight path angle and angle of attack |
| 16 | `torcas` | torque |
| 17, 18 | `Cds`, `Machs` | drag coefficient and Mach number |

The flight object also keeps `tiempo_salida_riel`, `tiempo_apogeo`, `tiempo_impacto` and `apogeo`, plus `pasos` and `evaluaciones`, the number of steps and of derivative evaluations of the last run.
