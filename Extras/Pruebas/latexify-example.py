import latexify
import math
import numpy as np

@latexify.expression
def solve(a, b, c):
    return (-b + math.sqrt(b**2 - 4*a*c)) / (2*a)

print(solve(1, 4, 3))  # Invoking the function works as expected.
print(solve)  # Printing the function shows the underlying LaTeX source.
solve  # Displays the expression.

# Elif or nested else-if are unrolled.
@latexify.function
def der_gravedad_arrastre(t, state):
    v = state[1]
    if v == 0:
        Drag = 0
    else:
        Drag = (D_mag/m) * (v**2) * np.sign(v)
    
    derivs = np.array((v, -g - Drag))
    #print(derivs)
    return derivs

der_gravedad_arrastre
print(der_gravedad_arrastre)
