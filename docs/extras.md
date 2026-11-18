# Extras

[Extras/](../Extras/) collects scripts I wrote while exploring the data or trying ideas. The simulator does not import any of them. Some run as they are and some depend on files or paths that are not in the repository.

## DatosVuelo

These three scripts look at the records of the real flight in [Archivos/DatosVuelo/](../Archivos/DatosVuelo/).

| Script | What it does |
| --- | --- |
| [analizar_FW.py](../Extras/DatosVuelo/analizar_FW.py) | plots vertical speed from the GPS tracker and differentiates it to get vertical acceleration |
| [analizar_vueloASYB.py](../Extras/DatosVuelo/analizar_vueloASYB.py) | plots the telemetry altitude, checks how uneven the sampling is and resamples it at equal intervals |
| [analizar_ambas.py](../Extras/DatosVuelo/analizar_ambas.py) | loads both records and a saved simulation and plots them together |

## DatosMotor

[Motor.py](../Extras/DatosMotor/Motor.py) loads the thrust curve and the motor mass table and plots them. It expects column names that differ from the ones in the current files, so the plots fail until those names are changed.

[HacerEng.py](../Extras/DatosMotor/HacerEng.py) converts a motor simulation output into a two-column thrust file. It reads from a path on my own computer.

## Pruebas

[prueba_rotacion.py](../Extras/Pruebas/prueba_rotacion.py) and [animRot_prueba.py](../Extras/Pruebas/animRot_prueba.py) are the first tests of drawing a rocket with matplotlib patches and rotating it. The drawing code in [Paquetes/utils/dibujar_cohete2.py](../Paquetes/utils/dibujar_cohete2.py) grew out of them.

[latexify-example.py](../Extras/Pruebas/latexify-example.py) tries the `latexify` package to turn Python functions into LaTeX. It needs that package installed, and it is not in the requirements.

## Visual

[simulador_cohetes.py](../Extras/Visual/simulador_cohetes.py) is a small tkinter window with a point-mass rocket model, written before the real interface existed.

[JuegoVisual.py](../Extras/Visual/JuegoVisual.py) is a pygame sketch of a rocket moving on screen. It needs pygame, which is not in the requirements.

## NoImplementadoAun

[angulos_euler.py](../Extras/NoImplementadoAun/angulos_euler.py) builds rotation matrices about the three axes and recovers Euler angles from a matrix. I wrote it as a first step toward six degrees of freedom.

[calculos_estructurales.py](../Extras/NoImplementadoAun/calculos_estructurales.py) is a placeholder for structural calculations and contains only an import.
