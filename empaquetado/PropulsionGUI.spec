# Receta de PyInstaller para el ejecutable de PropulsionGUI.
#
#     pip install pyinstaller
#     pyinstaller empaquetado/PropulsionGUI.spec
#
# El resultado queda en dist/: PropulsionGUI.app en macOS y la carpeta PropulsionGUI/ (con
# PropulsionGUI.exe o PropulsionGUI adentro) en Windows y Linux. PyInstaller no construye para
# otro sistema: cada ejecutable se construye en el sistema donde se va a usar.
import os
import sys

from PyInstaller.utils.hooks import collect_data_files

RAIZ = os.path.abspath(os.path.join(SPECPATH, ".."))

# Archivos de datos que la interfaz lee al arrancar, en la misma ruta relativa que en el repositorio
DATOS = [
    "Archivos/cdmachXitle.csv",
    "Archivos/estructura_xitle.json",
    "Archivos/CurvasEmpuje/pruebaestaica28mayo2024.csv",
    "Archivos/CurvasEmpuje/MegaPunisherFatMasadot.csv",
    "Archivos/DatosVuelo/condiciones_2024-06-22.json",
    "Archivos/DatosVuelo/FTW.csv",
]
datas = [(os.path.join(RAIZ, ruta), os.path.dirname(ruta)) for ruta in DATOS]
datas += collect_data_files("customtkinter")   # temas y fuentes de customtkinter

a = Analysis(
    [os.path.join(RAIZ, "Simulador", "GUI", "PropulsionGUI.py")],
    pathex=[RAIZ],
    datas=datas,
    # Paquetes instalados que la interfaz no usa
    excludes=["tkintermapview", "seaborn", "pytest", "IPython", "PyQt5", "PyQt6", "PySide2", "PySide6"],
)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name="PropulsionGUI", console=False, upx=False)
coll = COLLECT(exe, a.binaries, a.datas, name="PropulsionGUI", upx=False)

if sys.platform == "darwin":
    app = BUNDLE(coll, name="PropulsionGUI.app", bundle_identifier="mx.unam.propulsion.simulador",
                 info_plist={"CFBundleDisplayName": "Simulador de vuelo", "NSHighResolutionCapable": True})
