# Tests

The suite in [tests/](../tests/) uses pytest.

```bash
pip install -r requirements-dev.txt
python -m pytest tests
```

It takes about half a minute. Most of that time goes into the full flights.

## Shared setup

[conftest.py](../tests/conftest.py) adds the repository root to the path and selects the matplotlib backend that draws without windows.

It defines `volar(**cambios)`, which simulates the Xitle II through the interface backend with LSODA and wind seed 1, changing only the parameters passed in. Two session fixtures, `vuelo_libre` and `vuelo_paracaidas`, hold a free flight and a parachute flight. They are simulated once and shared by every test that asks for them.

## Files

| File | What it checks |
| --- | --- |
| [test_atmosfera.py](../tests/test_atmosfera.py) | the atmosphere against tabulated standard values, the site altitude, the pressure levels of the flight day, and that a hot day gives thinner air |
| [test_integradores.py](../tests/test_integradores.py) | my integrators on projectile motion, their order of convergence, the Fehlberg coefficients and order conditions, and that the adaptive ones change their step |
| [test_metodos.py](../tests/test_metodos.py) | the catalog has nine methods with the right names, the simulator and the interface offer the same list, and `resolver` handles free step, maximum step, fixed step and events |
| [test_geografia.py](../tests/test_geografia.py) | the coordinate conversions, the wind direction conversion, the Web Mercator pixels and the interactive map file |
| [test_vuelo.py](../tests/test_vuelo.py) | full flights |
| [test_gui_backend.py](../tests/test_gui_backend.py) | the default parameters reproduce the Xitle II, the stability analysis, and the validation messages |

## Flight tests

[test_vuelo.py](../tests/test_vuelo.py) is the longest file. Its tests fall into a few groups.

The first group checks that a flight makes physical sense. Mass decreases during the burn and stays constant afterward, the events happen in order, the apogee is within a plausible range, and the parachute slows the descent.

The second group compares integrators. Several methods must agree with the reference flight within a tolerance, two runs in a row must give identical results, and my fixed-step methods must take the number of steps that `dt` and `dt_out` imply.

The third group covers the wind. A seed makes the wind repeatable, the mean wind is horizontal and points in the base direction, the direction conventions hold, and a profile changes the wind with height.

The fourth group covers the site. The impact coordinates are consistent with the distance and bearing, the simulated impact falls near the last GPS point of the real flight, a launch from another site does not show the real track, and a higher site raises the apogee.

The last group pins down fixes to the model. On the rail the rocket neither sinks nor leaves the axis. Propellant is consumed during the whole burn and in proportion to the impulse. The inertia drops as propellant is used. The fin centroid matches the trapezoid formula. The normal force restores the rocket for any angle of attack.

## Running part of the suite

```bash
python -m pytest tests/test_integradores.py
python -m pytest tests -k viento
```

The integrator, catalog and atmosphere tests do not simulate a flight and finish in a few seconds.
