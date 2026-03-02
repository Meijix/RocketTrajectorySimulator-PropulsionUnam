# Plan de Mejoras Avanzadas de la GUI

## Vision: Software Completo de Simulacion de Cohetes Suborbitales

Este documento detalla las mejoras necesarias para que la GUI pase de ser un simulador funcional a un **software profesional completo** comparable con OpenRocket y RASAero II, adaptado para equipos universitarios de coheteria.

---

## Estado Actual vs. Software Profesional

### Lo que YA tenemos (implementado)

| Categoria | Features |
|-----------|----------|
| Definicion del cohete | 80+ campos, 15 componentes, valores Xitle II |
| Simulacion | Conectada al backend 3-DOF, 5 integradores, threading |
| Resultados | 5 vistas de graficas (20+ plots), resumen numerico |
| Exportacion | CSV, JSON, PNG a 200 DPI |
| Estabilidad | Calculo CG/CP Barrowman, tabla por componente, semaforo |
| Validacion | Tiempo real en 80+ campos, pre-simulacion |
| Usabilidad | Tooltips, atajos, log, guardar/cargar config, reset |

### Lo que nos FALTA (comparado con OpenRocket/RASAero)

| Categoria | OpenRocket lo tiene | Nosotros |
|-----------|-------------------|----------|
| Disenador visual drag-and-drop | Si | No (solo campos de texto) |
| Renderizado 3D del cohete | Si | Solo esquema 2D basico |
| Animacion de vuelo | Si | No |
| Base de datos de motores | Si (ThrustCurve.org) | No (solo CSV manual) |
| Base de datos de materiales | Si | No |
| Simulacion Monte Carlo | Si | No (planeado Fase 4) |
| Comparacion de simulaciones | Si | No |
| Zona de impacto en mapa | Si | No |
| Reporte PDF | Parcial | No |
| Analisis de seguridad | Parcial | No |
| Graficas en vivo durante sim | No | No |
| Datos meteorologicos reales | No | No |
| Multi-idioma | Si (15+) | Solo espanol |
| Undo/Redo | Si | No |
| Importar .ork / .rse | Si | No |

---

## Mejoras Organizadas por Prioridad

### PRIORIDAD 1: Impacto inmediato en usabilidad

Estas mejoras transforman la experiencia del usuario sin requerir cambios en el motor de simulacion.

---

#### 1.1 Graficas en vivo durante la simulacion

**Problema:** El usuario ve solo una barra de progreso durante la simulacion. No sabe si algo va mal hasta que termina.

**Solucion:**
- [ ] Crear clase `LivePlotFrame` con 2 graficas en miniatura (altitud y velocidad vs tiempo)
- [ ] Modificar `run_real_simulation()` para aceptar un callback `on_data_point(t, z, vel)` ademas del progress callback
- [ ] El callback envia datos cada 50 pasos de integracion via `self.after()` (thread-safe)
- [ ] Las graficas se redibujan usando `ax.set_data()` + `canvas.draw_idle()` (eficiente, sin recrear la figura)
- [ ] Mostrar indicadores numericos en vivo: altitud actual, velocidad actual, Mach actual, fase de vuelo
- [ ] Detectar y mostrar eventos en tiempo real: "MECO a t=3.2s", "Apogeo a t=15.1s"
- [ ] Agregar boton "Cancelar Simulacion" que setea un flag `self._cancel_requested` revisado por el integrador

**Implementacion tecnica:**
```
vuelo.simular_vuelo() actualmente no acepta callbacks.
Opcion A: Modificar simular_vuelo() para aceptar on_step callback.
Opcion B: Wrapper que ejecuta la simulacion en pasos y reporta entre pasos.
Opcion B es mejor porque no modifica el backend.
```

---

#### 1.2 Zona de impacto y prediccion de aterrizaje en el mapa

**Problema:** El mapa solo muestra el punto de lanzamiento. No muestra donde caera el cohete.

**Solucion:**
- [ ] Despues de la simulacion, calcular coordenadas GPS del punto de impacto:
  ```
  lat_impacto = lat_launch + (y_final / 111320)
  lon_impacto = lon_launch + (x_final / (111320 * cos(lat_launch)))
  ```
- [ ] Agregar marcador rojo "Punto de Impacto" en el mapa
- [ ] Dibujar linea de trayectoria proyectada sobre el mapa (vista cenital)
- [ ] Dibujar circulo de incertidumbre basado en variabilidad del viento
- [ ] Si hay Monte Carlo: dibujar elipse de dispersion con los puntos de impacto
- [ ] Agregar boton "Ver Trayectoria en Mapa" en la pestana de resultados
- [ ] Mostrar distancia y azimut del punto de impacto respecto al lanzamiento

---

#### 1.3 Reporte PDF automatico

**Problema:** Para competencias y documentacion, los equipos necesitan reportes formales con graficas y datos.

**Solucion:**
- [ ] Agregar dependencia `fpdf2` a requirements.txt
- [ ] Crear clase `ReportGenerator` con metodo `generate_pdf(config, results_df, plots_dir)`
- [ ] Estructura del reporte:
  - **Portada:** Logo, nombre del cohete, fecha, nombre del equipo
  - **Seccion 1: Configuracion del Cohete**
    - Tabla de componentes (nombre, masa, longitud, posicion)
    - Diagrama 2D del cohete (embebido como imagen)
    - Masa total, longitud total
  - **Seccion 2: Analisis de Estabilidad**
    - Tabla CG/CP/CN por componente
    - Margen estatico
    - Semaforo de estabilidad
  - **Seccion 3: Parametros de Simulacion**
    - Sitio de lanzamiento (lat, lon, alt)
    - Modelo de viento
    - Riel (longitud, angulo)
    - Integrador, dt, t_max
  - **Seccion 4: Resultados del Vuelo**
    - Tabla resumen (apogeo, vel max, mach max, accel max, t vuelo, dist impacto)
    - Grafica de altitud vs tiempo
    - Grafica de velocidad vs tiempo
    - Grafica de Mach vs tiempo
    - Trayectoria 3D
  - **Seccion 5: Fuerzas y Aerodinamica**
    - Graficas de fuerzas (empuje, arrastre, normal)
    - Cd vs Mach
    - Alpha vs tiempo
  - **Pie de pagina:** Generado por Rocket-Sim UNAM v1.0, fecha
- [ ] Boton "Generar Reporte PDF" en la pestana de resultados
- [ ] Dialogo para ingresar nombre del cohete y equipo antes de generar

---

#### 1.4 Comparacion lado a lado de simulaciones

**Problema:** Cuando el usuario cambia un parametro, no puede comparar facilmente los resultados con la simulacion anterior.

**Solucion:**
- [ ] Crear clase `SimulationHistory` que almacena los ultimos N DataFrames en memoria
- [ ] Cada simulacion se guarda con etiqueta (ej: "Sim #1: dt=0.01, DOP853")
- [ ] Nueva pestana "Comparar" o sub-vista en "Resultados"
- [ ] Selector multiple: checkboxes para elegir que simulaciones superponer
- [ ] Graficas superpuestas con colores distintos y leyenda automatica
- [ ] Tabla comparativa de metricas lado a lado:
  ```
  | Metrica        | Sim #1  | Sim #2  | Diferencia |
  |----------------|---------|---------|------------|
  | Apogeo (m)     | 3245    | 3312    | +67 (+2.1%)|
  | Vel. Max (m/s) | 287     | 291     | +4 (+1.4%) |
  ```
- [ ] Boton "Exportar Comparacion CSV"
- [ ] Opcion de cargar simulaciones previamente guardadas (CSV) para comparar

---

#### 1.5 Undo/Redo para parametros

**Problema:** Si el usuario cambia varios parametros y quiere volver atras, tiene que recordar los valores anteriores.

**Solucion:**
- [ ] Implementar pila de estados `UndoStack` con snapshots del diccionario de parametros
- [ ] Guardar snapshot cada vez que el usuario ejecuta "Actualizar Cohete" o "Ejecutar Simulacion"
- [ ] `Ctrl+Z` para undo (restaurar snapshot anterior)
- [ ] `Ctrl+Y` para redo
- [ ] Maximo 20 niveles de undo
- [ ] Mostrar indicador "Undo disponible (3 pasos)" en la barra de estado

---

### PRIORIDAD 2: Features para competencias de coheteria

Estas mejoras hacen que el simulador sea util para equipos en competencias como IREC, Spaceport America Cup, SAE Aero.

---

#### 2.1 Analisis de seguridad y zonas de exclusion

**Problema:** Las competencias requieren analisis de seguridad: energia cinetica al impacto, radio de exclusion, velocidad de descenso.

**Solucion:**
- [ ] Nueva seccion "Analisis de Seguridad" en la pestana de resultados
- [ ] Calcular y mostrar:
  - **Energia cinetica al impacto:** `KE = 0.5 * m * v_impacto^2` (en Joules y ft-lbs)
  - **Velocidad de descenso con paracaidas:** `v_desc = sqrt(2*m*g / (rho*Cd*A))`
  - **Velocidad de descenso sin paracaidas (caso de fallo)**
  - **Radio de exclusion recomendado** basado en apogeo y viento maximo
  - **Drift maximo con viento** (distancia horizontal durante descenso)
  - **Shock load del paracaidas** al desplegarse: `F_shock = CdS * rho * v^2 / 2`
  - **Numero de Mach maximo** y si excede regimen transonico
- [ ] Clasificacion de riesgo: "Baja KE < 75 J" / "Media 75-200 J" / "Alta > 200 J"
- [ ] Verificar que la velocidad de descenso con main < 30 fps (9.1 m/s) - requisito tipico de competencia
- [ ] Verificar que la velocidad de descenso con drogue < 100 fps (30 m/s)

---

#### 2.2 Base de datos de motores (ThrustCurve.org)

**Problema:** El usuario tiene que buscar y descargar CSVs de empuje manualmente.

**Solucion:**
- [ ] Crear directorio `Archivos/Motores/` con motores comunes pre-cargados:
  - Motores hibridos populares (HyperTEK, Contrail, custom UNAM)
  - Motores solidos comerciales (Cesaroni, AeroTech, Animal Motor Works)
- [ ] Selector de motor en la GUI: dropdown con motores disponibles
- [ ] Parser de archivos .eng (formato RASP) para importar motores de ThrustCurve.org
- [ ] Mostrar propiedades del motor seleccionado:
  - Impulso total (N-s), empuje medio (N), tiempo de quema (s)
  - Clasificacion (L, M, N, O...)
  - Masa del propelente, masa inerte
  - Grafica de empuje en miniatura
- [ ] Boton "Descargar de ThrustCurve.org" que abre el navegador en la pagina correcta
- [ ] Cache local de motores descargados

---

#### 2.3 Base de datos de materiales

**Problema:** El usuario ingresa masas manualmente. No puede calcular masa a partir de dimensiones y material.

**Solucion:**
- [ ] Crear diccionario `MATERIALES` con propiedades:
  ```python
  MATERIALES = {
      "Aluminio 6061-T6": {"densidad": 2700, "resistencia": 276e6, "color": "#C0C0C0"},
      "Fibra de carbono": {"densidad": 1600, "resistencia": 600e6, "color": "#333333"},
      "Fibra de vidrio": {"densidad": 1900, "resistencia": 200e6, "color": "#F5F5DC"},
      "PLA (impresion 3D)": {"densidad": 1240, "resistencia": 50e6, "color": "#FFD700"},
      "ABS": {"densidad": 1040, "resistencia": 40e6, "color": "#F0F0F0"},
      "Acero AISI 304": {"densidad": 8000, "resistencia": 215e6, "color": "#808080"},
      "Madera balsa": {"densidad": 170, "resistencia": 10e6, "color": "#DEB887"},
  }
  ```
- [ ] Dropdown de material en cada componente cilindrico
- [ ] Checkbox "Calcular masa automaticamente" que usa: `masa = densidad * volumen`
  - Cilindro hueco: `V = pi * L * (R_ext^2 - R_int^2)`
  - Cono: `V = pi/3 * L * R^2 * t / R` (pared delgada)
- [ ] Mostrar masa calculada vs masa ingresada manualmente

---

#### 2.4 Disenador visual del cohete mejorado

**Problema:** El dibujo 2D actual es estatico y no refleja proporciones reales ni permite interaccion.

**Solucion:**
- [ ] **Dibujo proporcional en tiempo real:**
  - Redibujar automaticamente al cambiar cualquier dimension (debounce 500ms con `after_cancel/after`)
  - Escala correcta basada en dimensiones reales (no estimaciones)
  - Mostrar cotas de longitud de cada componente
  - Mostrar diametros con lineas de acotacion
- [ ] **Colores segun material o tipo de componente** (configurable)
- [ ] **Vista de corte transversal:**
  - Mostrar interior del cohete (motor, oxidante, avionica, paracaidas)
  - Toggle entre vista externa y vista de corte
- [ ] **Tabla de masas resumen:**
  - Widget al lado del dibujo con: Componente | Masa | % del total
  - Barra horizontal proporcional a la masa de cada componente
  - Masa total en la parte inferior
- [ ] **Click en componente para seleccionar:**
  - Al hacer click en un componente del dibujo, resaltar y scrollear a sus campos de entrada
  - Tooltip en el dibujo con nombre y masa del componente

---

#### 2.5 Animacion de vuelo

**Problema:** El usuario no puede visualizar como se ve el vuelo del cohete en movimiento.

**Solucion:**
- [ ] Nueva pestana "Animacion" o ventana emergente
- [ ] Animacion 2D lado (altitud vs distancia horizontal):
  - Cohete representado como triangulo que sigue la trayectoria
  - Orientacion del cohete segun angulo theta
  - Estela de puntos mostrando la trayectoria recorrida
  - Marcadores de eventos: MECO (amarillo), apogeo (rojo), paracaidas (azul)
  - Escala de tiempo ajustable (1x, 2x, 5x, 10x)
  - Botones play/pause/restart
- [ ] Panel lateral con datos en tiempo real:
  - Altitud, velocidad, Mach, aceleracion, fase de vuelo
  - Tiempo de simulacion actual
- [ ] Controles:
  - Slider de tiempo para ir a cualquier punto del vuelo
  - Toggle vista lateral / vista cenital
- [ ] Exportar animacion como GIF (usando `imageio` o `pillow`)

---

### PRIORIDAD 3: Features avanzados de simulacion

Estas mejoras requieren cambios en el backend pero se controlan desde la GUI.

---

#### 3.1 Pestana Monte Carlo

**Problema:** No se puede analizar incertidumbre. Un solo numero de apogeo no basta para competencias.

**Solucion:**
- [ ] Nueva pestana "Monte Carlo" en la GUI
- [ ] Interfaz de configuracion de distribuciones:
  - Por cada parametro clave, mostrar: nombre | valor base | sigma/rango | distribucion
  - Parametros configurables:
    - Cd: Normal(base, sigma)
    - Masa total: Normal(base, sigma)
    - Empuje maximo: Normal(base, sigma)
    - Viento velocidad: Uniform(min, max)
    - Viento direccion: Uniform(0, 360)
    - Angulo de riel: Normal(base, sigma)
  - Tipo de distribucion seleccionable: Normal, Uniforme, Triangular
- [ ] Numero de corridas (100, 500, 1000, 5000)
- [ ] Barra de progreso general (corrida N de M)
- [ ] Paralelizacion con `multiprocessing.Pool` (usar N-1 nucleos)
- [ ] Resultados:
  - Histograma de apogeos con media, sigma, percentiles 5% y 95%
  - Histograma de velocidades maximas
  - Elipse de dispersion de puntos de impacto sobre el mapa
  - Envolvente de trayectorias (media +/- 2 sigma)
  - Diagrama de tornado (sensibilidad: que parametro afecta mas)
  - Tabla estadistica completa
- [ ] Exportar resultados Monte Carlo a CSV y PDF

---

#### 3.2 Selector de modelo de grados de libertad

**Problema:** Cuando se implemente 6-DOF (Fase 3), la GUI necesita permitir elegir entre 3-DOF y 6-DOF.

**Solucion:**
- [ ] Dropdown en pestana "Simulacion": "Modelo: 3-DOF / 6-DOF"
- [ ] Si 6-DOF seleccionado:
  - Mostrar campos adicionales: momentos de inercia Iyy, Izz
  - Mostrar campos de condicion inicial: roll rate, yaw rate
  - Resultados adicionales: roll, yaw, quaterniones
  - Graficas adicionales: roll vs tiempo, yaw vs tiempo, estabilidad giroscopica
- [ ] Si 3-DOF: ocultar campos extra (comportamiento actual)

---

#### 3.3 Sistema de eventos configurable en la GUI

**Problema:** El usuario no puede definir eventos como despliegue de paracaidas a altitud especifica, separacion de etapas, etc.

**Solucion:**
- [ ] Nueva seccion "Eventos" en la pestana de simulacion (o sub-pestana)
- [ ] Tabla editable de eventos:
  ```
  | # | Condicion          | Accion                  | Habilitado |
  |---|-------------------|-------------------------|------------|
  | 1 | Altitud == Apogeo | Desplegar Drogue        | Si         |
  | 2 | Altitud <= 450 m  | Desplegar Main          | Si         |
  | 3 | Mach >= 0.8       | Registrar en log        | Si         |
  | 4 | Burnout motor     | Cambiar Cd a 0.5        | No         |
  ```
- [ ] Tipos de condicion: altitud (=, <, >), velocidad, Mach, tiempo, burnout, apogeo
- [ ] Tipos de accion: desplegar paracaidas, log, cambiar Cd, separar etapa
- [ ] Botones "Agregar Evento" / "Eliminar Evento"
- [ ] Los eventos se muestran en el log y en las graficas como lineas verticales

---

### PRIORIDAD 4: Calidad de experiencia de usuario

---

#### 4.1 Wizard de primera vez

**Problema:** Un usuario nuevo no sabe por donde empezar. La GUI tiene demasiados campos.

**Solucion:**
- [ ] Dialogo de bienvenida al abrir por primera vez:
  ```
  Bienvenido a Rocket-Sim UNAM

  [Cargar cohete de ejemplo (Xitle II)]
  [Crear cohete nuevo (guiado)]
  [Cargar configuracion existente...]
  ```
- [ ] Wizard "Crear cohete nuevo" en 5 pasos:
  1. Nombre y tipo de cohete
  2. Dimensiones principales (longitud total, diametro)
  3. Motor y propelente (selector o CSV)
  4. Paracaidas (drogue + main)
  5. Sitio de lanzamiento y riel
- [ ] Al finalizar el wizard, se llenan todos los campos y se dibuja el cohete
- [ ] Opcion de no mostrar el wizard de nuevo

---

#### 4.2 Temas de color configurables

**Problema:** El tema oscuro actual puede no ser comodo para todos, especialmente en presentaciones.

**Solucion:**
- [ ] Agregar menu de preferencias con selector de tema:
  - **Oscuro** (actual - ColorPalette existente)
  - **Claro** (fondo blanco, texto negro, graficas con fondo blanco)
  - **Alto contraste** (para proyectores y presentaciones)
- [ ] Refactorizar `ColorPalette` para soportar multiples temas:
  ```python
  THEMES = {
      "oscuro": ColorPalette(...),
      "claro": ColorPaletteLight(...),
      "alto_contraste": ColorPaletteHC(...),
  }
  ```
- [ ] Persistir preferencia de tema en archivo de configuracion local

---

#### 4.3 Barras de menu estandar

**Problema:** La GUI no tiene barra de menu. Todas las acciones estan en botones, lo que no es estandar para software de escritorio.

**Solucion:**
- [ ] Agregar barra de menu nativa con:
  ```
  Archivo
    ├── Nueva simulacion       Ctrl+N
    ├── Abrir configuracion    Ctrl+O
    ├── Guardar configuracion  Ctrl+S
    ├── Guardar como...        Ctrl+Shift+S
    ├── ──────────────────
    ├── Importar empuje CSV...
    ├── Importar arrastre CSV...
    ├── Importar masa CSV...
    ├── ──────────────────
    ├── Exportar resultados CSV...
    ├── Exportar resumen JSON...
    ├── Exportar graficas PNG...
    ├── Generar reporte PDF...
    ├── ──────────────────
    └── Salir                  Alt+F4

  Editar
    ├── Deshacer               Ctrl+Z
    ├── Rehacer                Ctrl+Y
    ├── ──────────────────
    ├── Resetear valores Xitle II
    └── Preferencias...

  Simulacion
    ├── Ejecutar               Ctrl+R
    ├── Cancelar
    ├── ──────────────────
    ├── Calcular CG/CP
    └── Actualizar cohete      F5

  Ver
    ├── Tema oscuro
    ├── Tema claro
    ├── ──────────────────
    ├── Mostrar log            Ctrl+L
    └── Pantalla completa      F11

  Ayuda
    ├── Manual de usuario
    ├── Acerca de...
    └── Reportar bug (GitHub)
  ```

---

#### 4.4 Internacionalizacion (i18n)

**Problema:** La GUI solo esta en espanol. Equipos internacionales no pueden usarla.

**Solucion:**
- [ ] Crear sistema de traducciones con diccionario:
  ```python
  TRANSLATIONS = {
      "es": {"run_sim": "Ejecutar Simulacion", "altitude": "Altitud", ...},
      "en": {"run_sim": "Run Simulation", "altitude": "Altitude", ...},
  }
  ```
- [ ] Selector de idioma en preferencias: Espanol / English
- [ ] Todos los textos de la GUI pasan por `t("clave")` en lugar de strings hardcodeados
- [ ] Los reportes PDF se generan en el idioma seleccionado

---

#### 4.5 Rendimiento y optimizacion

**Problema:** Con muchas graficas y datos, la GUI puede volverse lenta.

**Solucion:**
- [ ] Usar `blitting` en matplotlib para graficas en vivo (10x mas rapido)
- [ ] Limitar datos de graficas a N puntos maximo (downsampling inteligente)
- [ ] Lazy loading de pestanas: solo crear widgets al abrir la pestana por primera vez
- [ ] Cache de calculos de estabilidad (no recalcular si no cambiaron parametros)
- [ ] Profiling con `cProfile` para encontrar cuellos de botella

---

### PRIORIDAD 5: Integracion y ecosistema

---

#### 5.1 Importar/exportar formato OpenRocket (.ork)

**Problema:** Muchos equipos ya tienen cohetes definidos en OpenRocket. No pueden reutilizar esos datos.

**Solucion:**
- [ ] Parser de archivos .ork (formato XML) para extraer:
  - Componentes (nose cone, body tube, fins, etc.)
  - Dimensiones, masas, posiciones
  - Motor y curva de empuje
  - Configuracion de recuperacion
- [ ] "Importar desde OpenRocket..." en el menu Archivo
- [ ] Mapear componentes OpenRocket a nuestras clases (Cono, Cilindro, Aletas, Boattail)
- [ ] Exportar nuestro cohete a formato .ork basico (para usuarios que quieran comparar)

---

#### 5.2 Datos meteorologicos reales

**Problema:** El modelo de viento actual es una aproximacion simple. Para competencias se necesitan datos reales.

**Solucion:**
- [ ] Integracion con API de Open-Meteo (gratuita, sin API key):
  - Dado lat/lon y fecha, obtener:
    - Perfil de viento con la altitud
    - Temperatura y presion en superficie
    - Pronostico para el dia de lanzamiento
- [ ] Boton "Obtener Clima Actual" en pestana de simulacion
- [ ] Mostrar datos obtenidos:
  ```
  Sitio: 19.5N, 98W | Temp: 22C | Viento: 8 m/s NW | Presion: 1013 hPa
  ```
- [ ] Opcion de usar datos reales vs modelo simple
- [ ] Guardar datos meteorologicos en la configuracion JSON

---

#### 5.3 Exportar a formatos de competencia

**Problema:** Las competencias (IREC, Spaceport America) requieren formatos especificos de datos.

**Solucion:**
- [ ] Template para IREC Flight Card:
  - Apogeo predicho (ft y m)
  - Velocidad de descenso (fps)
  - Energia cinetica en cada seccion
  - Tiempo de vuelo
  - Drift maximo
- [ ] Exportar tabla de datos en formato compatible con requisitos SAC
- [ ] Incluir metadata del motor (designacion, impulso total, ISP)

---

## Resumen de Prioridades

| Prioridad | Mejora | Impacto | Esfuerzo |
|-----------|--------|---------|----------|
| **P1** | Graficas en vivo durante sim | Alto | Medio |
| **P1** | Zona de impacto en mapa | Alto | Bajo |
| **P1** | Reporte PDF | Alto | Medio |
| **P1** | Comparacion de simulaciones | Alto | Medio |
| **P1** | Undo/Redo | Medio | Bajo |
| **P2** | Analisis de seguridad | Alto | Medio |
| **P2** | Base de datos de motores | Alto | Medio |
| **P2** | Base de datos de materiales | Medio | Bajo |
| **P2** | Disenador visual mejorado | Alto | Alto |
| **P2** | Animacion de vuelo | Medio | Alto |
| **P3** | Pestana Monte Carlo | Alto | Alto |
| **P3** | Selector 3-DOF/6-DOF | Medio | Bajo |
| **P3** | Sistema de eventos | Alto | Alto |
| **P4** | Wizard de primera vez | Medio | Medio |
| **P4** | Temas de color | Bajo | Bajo |
| **P4** | Barras de menu | Medio | Medio |
| **P4** | Internacionalizacion | Medio | Alto |
| **P4** | Optimizacion rendimiento | Medio | Medio |
| **P5** | Import/export OpenRocket | Alto | Alto |
| **P5** | Datos meteorologicos reales | Medio | Medio |
| **P5** | Formatos de competencia | Alto | Bajo |

---

## Orden de Implementacion Sugerido

```
Sprint 1 (2-3 semanas):
  ├── P1.2 Zona de impacto en mapa (bajo esfuerzo, alto impacto)
  ├── P1.5 Undo/Redo (bajo esfuerzo)
  └── P2.3 Base de datos de materiales (bajo esfuerzo)

Sprint 2 (3-4 semanas):
  ├── P1.1 Graficas en vivo
  ├── P1.4 Comparacion de simulaciones
  └── P2.1 Analisis de seguridad

Sprint 3 (3-4 semanas):
  ├── P1.3 Reporte PDF
  ├── P2.2 Base de datos de motores
  └── P4.3 Barras de menu

Sprint 4 (4-6 semanas):
  ├── P2.4 Disenador visual mejorado
  ├── P2.5 Animacion de vuelo
  └── P4.1 Wizard de primera vez

Sprint 5 (4-6 semanas):
  ├── P3.1 Pestana Monte Carlo
  ├── P3.3 Sistema de eventos
  └── P5.2 Datos meteorologicos reales

Sprint 6 (3-4 semanas):
  ├── P3.2 Selector 3-DOF/6-DOF
  ├── P5.1 Import/export OpenRocket
  ├── P5.3 Formatos de competencia
  ├── P4.2 Temas de color
  └── P4.4 Internacionalizacion
```

---

## Notas Tecnicas

- Todas las mejoras de GUI deben mantener el patron existente: **threading para simulacion**, **self.after() para actualizacion de UI**, **ColorPalette para temas**
- Las nuevas pestanas deben seguir la misma estructura: clase que hereda de `customtkinter.CTkFrame` o `CTkScrollableFrame`
- Los datos entre pestanas se comparten via `self.winfo_toplevel()` (acceso a la instancia de App)
- El mapa usa `tkintermapview` con fallback graceful (ya implementado)
- Las graficas usan `Figure` de matplotlib con `FigureCanvasTkAgg` (ya implementado)
