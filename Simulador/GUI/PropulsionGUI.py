"""Interfaz del simulador con el estilo de Propulsión UNAM.

    python -m Simulador.GUI.PropulsionGUI

Tiene las mismas funciones que ModernGUI.py y usa el mismo backend (backend.py y mapa.py),
con otra presentación: fondo negro, texto blanco, amarillo para la acción principal y
controles que responden al momento (el esquema, el CG y el margen cambian al escribir).

Este archivo solo abre la ventana. El código está en la carpeta `propulsion/`, un módulo
por tarea; su `__init__.py` dice qué hay en cada uno.
"""
import multiprocessing
import os
import sys

# Raíz del proyecto en el path, para poder ejecutar también `python Simulador/GUI/PropulsionGUI.py`
RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)


def autoprueba(espera=300):
    """Abre la ventana, corre un vuelo y la cierra. Devuelve 0 si todo salió bien.

    Sirve para comprobar un ejecutable recién construido (`PropulsionGUI --autoprueba`): que
    encuentra sus archivos de datos y que la simulación corre en su proceso aparte.
    """
    import time
    from Simulador.GUI.propulsion.app import App

    app = App()
    app.vars["integrator"].set("LSODA")
    app.simular()
    inicio = time.time()
    while (app.tarea is None or not app.tarea.done()) and time.time() - inicio < espera:
        app.update()
        time.sleep(0.05)
    for _ in range(40):          # deja que la ventana reciba el resultado
        app.update()
        time.sleep(0.05)
    resumen = app.pestanas["Resultados"].resumen
    if resumen is None:
        print("Autoprueba fallida:", app.estado.cget("text"))
        codigo = 1
    else:
        print(f"Autoprueba correcta: apogeo {resumen['apogeo']:.0f} m, "
              f"mapa de fondo {'descargado' if resumen.get('mapa') else 'no disponible'}")
        codigo = 0
    app.cerrar()
    return codigo


def main():
    if "--autoprueba" in sys.argv:
        sys.exit(autoprueba())
    from Simulador.GUI.propulsion.app import App
    App().mainloop()


if __name__ == "__main__":
    multiprocessing.freeze_support()   # necesario en el ejecutable: la simulación corre en otro proceso
    main()
