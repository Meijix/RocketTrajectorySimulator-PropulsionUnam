# Plots, animations and comparisons

These scripts work on flights that were already simulated, or compare integration methods with each other. Most of them read the files in `Simulador/Resultados/OutputFiles/VueloLibre-DOP853-100/`, so run a free flight first if that folder is out of date.

```bash
python -m Simulador.src.VueloLibre
```

## Visualizacion

### Graficas.py

[Graficas.py](../Simulador/Visualizacion/Graficas.py) reads `datos.csv` and `datos.json` of one flight and shows its plots one after another. The folder to plot is set in the variables `archivo_csv` and `archivo_json` at the top.

```bash
python -m Simulador.Visualizacion.Graficas
```

The plots cover the wind (speed and direction in time, histograms, wind rose), the trajectory and its three projections, position and velocity, pitch angle and rates, the three forces, the positions of CG and CP with the static margin in calibers, and the mass. Vertical lines mark rail exit, burnout, apogee and impact.

### Animations

[anim_trayectoria.py](../Simulador/Visualizacion/anim_trayectoria.py) animates the trajectory of the rocket. [anim_ang.py](../Simulador/Visualizacion/anim_ang.py) animates the rocket rotating with its pitch angle next to the angle curves, and saves the result as `cohete_rotacion.mp4` in the output folder. Saving needs ffmpeg installed.

[anim_completa.py](../Simulador/Visualizacion/anim_completa.py) was meant to combine both, with the rocket turning along its path. I did not finish it and it does not show the rocket rotating.

### compare_integ.py

[compare_integ.py](../Simulador/Visualizacion/compare_integ.py) flies the same rocket under the same conditions and wind with the nine methods of the catalog.

```bash
python -m Simulador.Visualizacion.compare_integ
```

The reference is DOP853 with a maximum step five times smaller than `dt` from the conditions module. For each method the script records apogee, apogee and impact times, top speed, number of steps, derivative evaluations, run time, and three differences with the reference (apogee, impact time and the root mean square of the height over the whole flight).

It writes `tabla_integradores.csv` and a `figuras/` folder to `Simulador/Resultados/OutputFiles/ComparacionIntegradores/`. The figures show height, speed, pitch angle and pitch rate against time for all methods, and bar charts of apogee, apogee time, impact time and top speed.

## Resultados

[Simulador/Resultados/](../Simulador/Resultados/) holds the saved runs under `OutputFiles/` and two scripts.

[real_vs_simulada.py](../Simulador/Resultados/real_vs_simulada.py) plots the simulated height against the measured curve in [AlturavsTiempo-Xitle2.csv](../Archivos/AlturavsTiempo-Xitle2.csv) and marks both apogees. It subtracts 10 s from the measured time to line up ignition.

[listas_resultados.py](../Simulador/Resultados/listas_resultados.py) prints the lengths, masses, centers of gravity and centers of pressure of every Xitle II component and draws the rocket with them.

The folders in `OutputFiles/` whose names end in 0, 110 or `inestable`, the `Simulaciones parametricas` folder and the `ResultadosVisuales/` folder are results from earlier versions of the code. Only the folders ending in 100 and `ComparacionIntegradores` match the current code.

## Simple cases

[Simulador/CasosSimples/Simples/](../Simulador/CasosSimples/Simples/) has three problems with known solutions. They test the nine methods on their own, apart from the rocket model.

| Script | Problem |
| --- | --- |
| [caso1.py](../Simulador/CasosSimples/Simples/caso1.py) | vertical motion under constant gravity |
| [caso2.py](../Simulador/CasosSimples/Simples/caso2.py) | gravity and linear drag |
| [caso3.py](../Simulador/CasosSimples/Simples/caso3.py) | gravity and quadratic drag |

```bash
python Simulador/CasosSimples/Simples/caso1.py
```

Each script calls `resolver` from the [catalog](integrators.md#solving-a-problem). Fixed-step methods run with six steps from 0.01 to 0.5 s. Adaptive methods run with those values as the maximum step and once more with a free step. The run stops when the object reaches the ground.

Each script saves its output in the folder that shares its name. `tabla_metodos.csv` has one row per method and step with the number of steps, derivative evaluations, run time and the errors in position and velocity against the analytical solution. `figuras/` holds every plot, numbered in the order shown.

The loose images in those folders were made by an earlier version that had six methods and labelled Dormand-Prince as RK45 without the distinction.

The folder `no funcional` holds my first attempt at these cases. Those scripts do not run with the current packages.

## Parameter sweeps

[Simulador/VarParams/](../Simulador/VarParams/) has two scripts I left unfinished. [variacion_parametros.py](../Simulador/VarParams/variacion_parametros.py) was meant to run several flights while changing the initial mass and the wind, and [comparacion.py](../Simulador/VarParams/comparacion.py) to plot them together. They import modules from paths that no longer exist (`Simulador.utils` and `Simulador.PaqueteFisica`) and do not run as they are.

To sweep a parameter today, the shortest path is a loop over `backend.ejecutar_simulacion` with a modified parameter dictionary, as the [interface page](gui.md#running-a-flight-without-the-window) shows.
