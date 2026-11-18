# Utilities

[Paquetes/utils/](../Paquetes/utils/) holds helper functions shared by the physics code, the scripts and the interface.

## funciones.py

[funciones.py](../Paquetes/utils/funciones.py) has the physical constants, two small math helpers and the functions that save and load results.

`normalized(vec)` returns a unit vector and fails on a zero vector. `calc_gravedad(altura)` returns the acceleration of gravity at a height above sea level from the inverse square law.

`guardar_datos_csv` writes the full trajectory of a flight to `Simulador/Resultados/OutputFiles/<flight type>-<integrator>-<efficiency>/datos.csv`. `guardar_datos_json` writes the summary of the same flight to `datos.json` in that folder. The [scripts page](running-simulations.md#output-files) lists the columns and keys. The efficiency in the folder name is always 100 now. Earlier versions scaled thrust by a factor, and the folders ending in 0 and 110 date from then.

`extraer_datoscsv` takes the DataFrame read from `datos.csv` and returns its columns as 37 arrays in a fixed order. `extraer_datosjson` does the same for the nine values of the summary. The plotting scripts unpack these tuples.

`muestra_tiempos` draws vertical lines on a plot at rail exit, burnout, apogee and impact.

`guardar_animacion` saves a matplotlib animation as mp4 through ffmpeg, or as gif through ImageMagick, with a progress bar.

`obtener_path_archivo` joins path parts to the repository root. The rocket definition uses it to find the tables in `Archivos/`.

## geografia.py

[geografia.py](../Paquetes/utils/geografia.py) converts between simulator coordinates and geographic coordinates. It uses a flat local approximation with an Earth radius of 6371 km, which is enough for flights of a few kilometres.

| Function | Result |
| --- | --- |
| `direccion_viento_simulador(direccion_desde, azimut_riel)` | the wind angle the `Viento` class expects, from a weather direction |
| `desplazamiento_este_norte(x, y, azimut_riel)` | east and north displacement in metres |
| `a_geograficas(x, y, latitud_sitio, longitud_sitio, azimut_riel)` | latitude and longitude of a simulator point |
| `distancia_y_rumbo(lat1, lon1, lat2, lon2)` | distance in metres and bearing from north between two points |

## figuras.py

[figuras.py](../Paquetes/utils/figuras.py) has one function. `guardar_figuras_al_mostrar(carpeta)` replaces `plt.show` so that each open figure is saved to the folder before it is shown. Files are numbered in the order the script shows them and named after the figure title, for example `01-altura-vs-tiempo.png`. The comparison scripts call it once at the top.

## angulos.py

[angulos.py](../Paquetes/utils/angulos.py) has `normalize_angle`, which wraps an angle in degrees to the range from -180 to 180, and `nice_angle`, which converts an array of radians to wrapped degrees for plotting.

## dibujar_cohete2.py

[dibujar_cohete2.py](../Paquetes/utils/dibujar_cohete2.py) draws a side view of a rocket on a matplotlib axis out of polygons for the nose, body, two fins and boattail. `dibujar_cohete2` creates the patches and returns them. `acomodar_cohete2` moves and rotates them about the center of gravity, which the animations call on every frame. Running the file shows a rocket at 90 degrees.
