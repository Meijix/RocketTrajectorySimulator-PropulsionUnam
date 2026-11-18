# Integrators

[Paquetes/PaqueteEDOs/](../Paquetes/PaqueteEDOs/) has two files. [integradores.py](../Paquetes/PaqueteEDOs/integradores.py) contains the methods I wrote for the thesis. [metodos.py](../Paquetes/PaqueteEDOs/metodos.py) is a catalog of those methods together with the SciPy ones, and a single function to run any of them.

## The step interface

Every integrator class is built with the derivative function `f(t, state)` and has one method.

```python
nuevo_estado, dt_usado = integrador.step(t, estado, dt)
```

`dt_usado` is the step that was taken. Fixed-step methods return the `dt` they received. Adaptive methods may shrink it, and they leave the step they recommend for the next call in `integrador.dt_sugerido`.

## Classes

| Class | Method | Order | Step |
| --- | --- | --- | --- |
| `Euler` | explicit Euler | 1 | fixed |
| `RungeKutta2` | Heun, the explicit trapezoid rule | 2 | fixed |
| `RungeKutta4` | classical Runge-Kutta | 4 | fixed |
| `RKF45` | Runge-Kutta-Fehlberg 4(5) | 5, with an order 4 error estimate | adaptive |
| `EulerAdaptativo` | Euler with step doubling | 1 | adaptive |
| `HeunAdaptativo` | embedded Euler-Heun pair | 2, with an order 1 error estimate | adaptive |

`AdaptiveEuler` is an alias of `EulerAdaptativo` for older scripts. The last two classes are not in the catalog and the flight simulator does not offer them.

`RKF45` uses the Fehlberg coefficients as printed in Burden and Faires. It advances with the fifth-order solution and uses the difference with the fourth-order one as the error estimate.

## Step control

The adaptive classes share the base class `_Adaptativo`. For each attempt it scales the error of every variable by `atol + rtol * |y|` and takes the largest value. The step is accepted when that scaled error is at most 1. The next step is the current one times

```text
q = S * (1 / (2 * error)) ** (1 / (p + 1))
```

where `p` is the order of the lower-order formula and `S` is a safety factor of 0.9. The factor `q` is kept between 0.1 and 4. A rejected step is repeated with a smaller size, and the counter `rechazados` records how many times that happened.

## Catalog

`METODOS` is a dictionary keyed by short name. Each entry is a `Metodo` record with the short name, the key the flight simulator uses, the name in the literature, the order, the step type, the origin and the kind of method.

| Short name | Flight key | Method | Origin |
| --- | --- | --- | --- |
| Euler | `Euler` | explicit Euler | mine |
| RK2 | `RungeKutta2` | Heun | mine |
| RK4 | `RungeKutta4` | classical Runge-Kutta | mine |
| RKF45 | `RKF45` | Runge-Kutta-Fehlberg 4(5) | mine |
| RK23 | `RK23` | Bogacki-Shampine 3(2) | SciPy |
| RK45 | `RK45` | Dormand-Prince 5(4) | SciPy |
| DOP853 | `DOP853` | Dormand-Prince 8(5,3) | SciPy |
| BDF | `BDF` | backward differentiation, order 1 to 5 | SciPy |
| LSODA | `LSODA` | Adams and BDF with automatic switching | SciPy |

The SciPy `RK45` is Dormand-Prince and not Fehlberg. Both are pairs of order 4 and 5 with different coefficients. A test checks this so the names cannot drift again.

The lists `FIJOS`, `ADAPTATIVOS` and `CLAVES_VUELO` are derived from the catalog. The interface, the comparison scripts and the tests read them, so a name means the same method everywhere.

`metodo(nombre)` finds an entry by short name or by flight key. `etiqueta(nombre)` returns a legend text such as `RK45 · Dormand-Prince 5(4)`. `tabla_metodos()` returns the catalog as a list of dictionaries.

## Solving a problem

`resolver` integrates `y' = f(t, y)` with any method in the catalog.

```python
from Paquetes.PaqueteEDOs.metodos import resolver

sol = resolver("RKF45", f, (0, 20), y0)            # adaptive, free step
sol = resolver("RK45", f, (0, 20), y0, dt=0.1)     # adaptive, maximum step 0.1
sol = resolver("RK4", f, (0, 20), y0, dt=0.1)      # fixed step 0.1
```

For fixed-step methods `dt` is required. For adaptive methods it is the maximum step, and leaving it out lets the step vary without a cap.

`events` takes a function `g(t, y)` with a `direction` attribute, as in `solve_ivp`. Integration stops when `g` crosses zero. Adaptive methods return the crossing point. My RKF45 finds it by bisection on a cubic Hermite interpolant of the last step. Fixed-step methods drop the step that crosses and end at the last point before the event.

The function repeats the integration three times by default and reports the shortest run time. It returns a `Solucion` with these fields.

| Field | Contents |
| --- | --- |
| `t` | times, including the initial one |
| `y` | states with shape (dimension, n), as in `solve_ivp` |
| `pasos` | accepted steps |
| `nfev` | derivative evaluations |
| `tiempo` | run time in seconds |
| `rechazados` | rejected steps, for RKF45 |
| `termino_por_evento` | whether an event ended the run |

`tabla_comparacion` builds the results table that the simple test cases save, with one row per method and step mode.

## Use in the flight simulator

The flight class does not go through `resolver`. It needs to open the parachute at apogee and save points at fixed intervals, so [vuelo.py](../Paquetes/PaqueteFisica/vuelo.py) has its own loops for my methods and for `solve_ivp`. It takes the method by its flight key. The [physics page](physics.md#integration) describes those loops.

Running `python Paquetes/PaqueteEDOs/integradores.py` solves a small linear system with one of my methods and four SciPy methods and plots them against the exact solution.
