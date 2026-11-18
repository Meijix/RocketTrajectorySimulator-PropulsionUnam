"""Interfaz del simulador con el estilo de Propulsión UNAM.

    python -m Simulador.GUI.PropulsionGUI

Tiene las mismas funciones que ModernGUI.py y usa el mismo backend (backend.py y mapa.py),
con otra presentación: fondo negro, texto blanco, amarillo para la acción principal y
controles que responden al momento (el esquema, el CG y el margen cambian al escribir).

Este archivo solo abre la ventana. El código está en la carpeta `propulsion/`, un módulo
por tarea; su `__init__.py` dice qué hay en cada uno.
"""
import os
import sys

# Raíz del proyecto en el path, para poder ejecutar también `python Simulador/GUI/PropulsionGUI.py`
RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)

from Simulador.GUI.propulsion.app import App  # noqa: E402

if __name__ == "__main__":
    App().mainloop()
