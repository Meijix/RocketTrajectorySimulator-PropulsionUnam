# Code documentation

These pages describe how the simulator is put together, one section of the code per page. The main [README](../README.md) covers installation, usage and the comparison with the real flight. I wrote these pages for someone who wants to read or change the code.

| Page | Code it covers |
| --- | --- |
| [Architecture](architecture.md) | How the folders fit together, the state vector, axes and units |
| [Physics package](physics.md) | [Paquetes/PaqueteFisica/](../Paquetes/PaqueteFisica/) |
| [Integrators](integrators.md) | [Paquetes/PaqueteEDOs/](../Paquetes/PaqueteEDOs/) |
| [Utilities](utilities.md) | [Paquetes/utils/](../Paquetes/utils/) |
| [Running a flight from scripts](running-simulations.md) | [Simulador/src/](../Simulador/src/) and the output files |
| [Graphical interface](gui.md) | [Simulador/GUI/](../Simulador/GUI/) |
| [Plots, animations and comparisons](analysis-scripts.md) | [Simulador/Visualizacion/](../Simulador/Visualizacion/), [Simulador/Resultados/](../Simulador/Resultados/), [Simulador/VarParams/](../Simulador/VarParams/) and [Simulador/CasosSimples/](../Simulador/CasosSimples/) |
| [Data files](data-files.md) | [Archivos/](../Archivos/) |
| [Tests](tests.md) | [tests/](../tests/) |
| [Extras](extras.md) | [Extras/](../Extras/) |
| [Xitle II design report](reporte-xitle2.md) | what the simulator says about the rocket and its 2024 flight, in Spanish |

The code, its comments and its variable names are in Spanish. Each page gives the Spanish name next to its meaning the first time it appears.

All commands in these pages run from the repository root.
