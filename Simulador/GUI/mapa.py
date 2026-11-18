"""Mapa del vuelo: fondo real de OpenStreetMap y mapa interactivo para el navegador.

No depende de tkinter. Dos salidas:

    descargar_mosaico(...)   imagen del mapa (teselas de OpenStreetMap unidas) para dibujarla
                             con matplotlib dentro de la interfaz.
    escribir_html(...)       archivo HTML con un mapa interactivo (Leaflet) que se abre en
                             el navegador.

Las dos necesitan conexión a internet; sin ella, el mosaico devuelve None y la interfaz
dibuja la trayectoria sobre un fondo en blanco.
"""
import io
import json
import math
import os
import tempfile
import urllib.request

import numpy as np

TAM_TESELA = 256
URL_TESELAS = "https://tile.openstreetmap.org/{z}/{x}/{y}.png"
ATRIBUCION = "© Colaboradores de OpenStreetMap"
AGENTE = "RocketSim-GUI/1.0 (simulador de trayectorias de cohetes)"


def a_pixeles(latitud, longitud, zoom):
    """Coordenadas de píxel (proyección Web Mercator) de un punto, al nivel de zoom dado."""
    n = TAM_TESELA * 2 ** zoom
    x = (np.asarray(longitud, dtype=float) + 180.0) / 360.0 * n
    lat = np.radians(np.asarray(latitud, dtype=float))
    y = (1.0 - np.arcsinh(np.tan(lat)) / math.pi) / 2.0 * n
    return x, y


def _elegir_zoom(lat_min, lat_max, lon_min, lon_max, max_teselas):
    """Mayor zoom con el que la zona cabe en a lo más max_teselas x max_teselas teselas."""
    for zoom in range(17, 1, -1):
        xs, ys = a_pixeles([lat_max, lat_min], [lon_min, lon_max], zoom)
        nx = int(xs[1] // TAM_TESELA) - int(xs[0] // TAM_TESELA) + 1
        ny = int(ys[1] // TAM_TESELA) - int(ys[0] // TAM_TESELA) + 1
        if nx <= max_teselas and ny <= max_teselas:
            return zoom
    return 2


def descargar_mosaico(latitudes, longitudes, margen=0.35, max_teselas=4, espera=6.0):
    """Descarga las teselas que cubren los puntos dados (con un margen alrededor).

    Devuelve un diccionario con la imagen (arreglo alto x ancho x 3), el zoom y la extensión
    en píxeles para matplotlib (`extent` de imshow), o None si no se pudo descargar.
    """
    lat_min, lat_max = float(np.min(latitudes)), float(np.max(latitudes))
    lon_min, lon_max = float(np.min(longitudes)), float(np.max(longitudes))
    # Margen: una fracción del tamaño de la zona, con un mínimo de unos 300 m
    d_lat = max((lat_max - lat_min) * margen, 0.003)
    d_lon = max((lon_max - lon_min) * margen, 0.003)
    lat_min, lat_max, lon_min, lon_max = lat_min - d_lat, lat_max + d_lat, lon_min - d_lon, lon_max + d_lon

    zoom = _elegir_zoom(lat_min, lat_max, lon_min, lon_max, max_teselas)
    xs, ys = a_pixeles([lat_max, lat_min], [lon_min, lon_max], zoom)
    tx0, tx1 = int(xs[0] // TAM_TESELA), int(xs[1] // TAM_TESELA)
    ty0, ty1 = int(ys[0] // TAM_TESELA), int(ys[1] // TAM_TESELA)

    try:
        from matplotlib.image import imread
        filas = []
        for ty in range(ty0, ty1 + 1):
            fila = []
            for tx in range(tx0, tx1 + 1):
                solicitud = urllib.request.Request(URL_TESELAS.format(z=zoom, x=tx, y=ty),
                                                   headers={"User-Agent": AGENTE})
                with urllib.request.urlopen(solicitud, timeout=espera) as respuesta:
                    tesela = imread(io.BytesIO(respuesta.read()), format="png")
                if tesela.ndim == 2:                       # escala de grises
                    tesela = np.stack([tesela] * 3, axis=-1)
                fila.append(tesela[:, :, :3])
            filas.append(np.concatenate(fila, axis=1))
        imagen = np.concatenate(filas, axis=0)
    except Exception as error:                              # sin internet, servidor caído, etc.
        print(f"No se pudo descargar el mapa de fondo: {error}")
        return None

    return {
        "imagen": imagen,
        "zoom": zoom,
        # extent de imshow: (izquierda, derecha, abajo, arriba) en píxeles de Web Mercator
        "extent": (tx0 * TAM_TESELA, (tx1 + 1) * TAM_TESELA, (ty1 + 1) * TAM_TESELA, ty0 * TAM_TESELA),
        "limites": (float(xs[0]), float(xs[1]), float(ys[1]), float(ys[0])),
        "atribucion": ATRIBUCION,
    }


_PLANTILLA_HTML = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>Mapa del vuelo</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
  html, body { height: 100%; margin: 0; font-family: system-ui, sans-serif; }
  #mapa { height: 100%; }
  #panel { position: absolute; z-index: 1000; top: 10px; right: 10px; background: #fff; padding: 10px 14px;
           border-radius: 8px; box-shadow: 0 1px 6px rgba(0,0,0,.35); font-size: 13px; line-height: 1.5; max-width: 320px; }
  #panel b { display: inline-block; min-width: 92px; }
  .linea { display: inline-block; width: 22px; height: 0; border-top: 3px solid; vertical-align: middle; margin-right: 6px; }
</style>
</head>
<body>
<div id="mapa"></div>
<div id="panel"></div>
<script>
const datos = __DATOS__;
const mapa = L.map('mapa');
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
            {maxZoom: 19, attribution: '&copy; Colaboradores de OpenStreetMap'}).addTo(mapa);
L.control.scale({imperial: false}).addTo(mapa);

function punto(p, color, titulo) {
  return L.circleMarker([p.lat, p.lon], {radius: 8, color: '#fff', weight: 2, fillColor: color, fillOpacity: 1})
          .addTo(mapa).bindPopup('<b>' + titulo + '</b><br>' + p.lat.toFixed(5) + ', ' + p.lon.toFixed(5) + (p.nota ? '<br>' + p.nota : ''));
}
const capas = [L.polyline(datos.trayectoria, {color: '#1f4fd8', weight: 3}).addTo(mapa)];
let panel = '<div><span class="linea" style="border-color:#1f4fd8"></span>Trayectoria simulada</div>';
if (datos.real) {
  capas.push(L.polyline(datos.real.trayectoria, {color: '#c8102e', weight: 3, dashArray: '6 6'}).addTo(mapa));
  punto(datos.real.ultimo, '#c8102e', 'Vuelo real: último punto GPS');
  panel += '<div><span class="linea" style="border-color:#c8102e;border-top-style:dashed"></span>Vuelo real (GPS)</div>';
}
punto(datos.lanzamiento, '#1a7f37', 'Sitio de lanzamiento').openPopup();
punto(datos.apogeo, '#e6a700', 'Apogeo simulado');
punto(datos.impacto, '#1f4fd8', 'Impacto simulado');
mapa.fitBounds(L.featureGroup(capas).getBounds().pad(0.25));
panel += '<hr style="border:0;border-top:1px solid #ddd">' + datos.resumen.map(f => '<div><b>' + f[0] + '</b> ' + f[1] + '</div>').join('');
document.getElementById('panel').innerHTML = panel;
</script>
</body>
</html>
"""


def escribir_html(datos, ruta=None):
    """Escribe el mapa interactivo y devuelve la ruta del archivo HTML.

    `datos` es un diccionario con las claves lanzamiento, apogeo e impacto ({lat, lon, nota}),
    trayectoria (lista de [lat, lon]), resumen (lista de [etiqueta, texto]) y, opcionalmente,
    real ({trayectoria, ultimo}) con el vuelo medido.
    """
    if ruta is None:
        ruta = os.path.join(tempfile.gettempdir(), "mapa_vuelo_cohete.html")
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(_PLANTILLA_HTML.replace("__DATOS__", json.dumps(datos, ensure_ascii=False)))
    return ruta
