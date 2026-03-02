# Plan de Mejoras - Rocket-Sim UNAM

Este documento describe el plan de desarrollo y mejoras del simulador, organizado en **fases incrementales**. Cada fase se construye sobre la anterior, de modo que el simulador gana funcionalidad de forma progresiva sin romper lo que ya funciona.

---

## Estado Actual del Proyecto

| Aspecto | Estado | Observaciones |
|---|---|---|
| Fisica 3-DOF | Funcional | Solo modela pitch; falta roll y yaw |
| Integradores | Funcional | 8 metodos disponibles; los adaptativos necesitan mas pruebas |
| GUI (ModernGUI.py) | **Critico** | Backend desconectado; funciones faltantes causan crashes; validacion minima |
| Visualizacion | Parcial | Buenas graficas en scripts standalone; no integradas en la GUI |
| Exportacion de datos | Basica | Solo CSV/JSON desde scripts; sin exportacion desde la GUI |
| Documentacion | Critica | Casi ausente; comentarios mezclados espanol/ingles |
| Tests automatizados | Inexistente | Solo casos manuales (caso1, caso2, caso3) |
| Manejo de errores | Minimo | Muchos fallos silenciosos; sin validacion de entradas |
| Calidad de codigo | Mejorable | Sin type hints; numeros magicos; codigo duplicado |

### Bugs Criticos Conocidos en la GUI

| Bug | Ubicacion | Impacto |
|-----|-----------|---------|
| `run_real_simulation()` no existe | `ModernGUI.py:878` | Crash al ejecutar simulacion |
| Modulo `Plotting` no importado | `ModernGUI.py:760-765` | Crash al mostrar resultados |
| `mplstyle` no importado | `ModernGUI.py:756` | Crash al abrir pestana de resultados |
| Typo `update_map()` vs `update_map_position()` | `ModernGUI.py:941` | Crash al cargar configuracion |
| Imports del backend comentados | `ModernGUI.py:22-35` | No hay conexion con el motor de simulacion |
| Angulo de riel = 4984.73° | `ModernGUI.py:593` | Valor predeterminado incorrecto (deberia ser ~5°) |

---

## Fase 1: Consolidacion y Calidad (Fundamentos)

**Objetivo:** Estabilizar el codigo existente, agregar pruebas y documentacion minima para que el proyecto sea mantenible y confiable.

**Duracion estimada:** 4-6 semanas

### 1.1 Tests unitarios y de regresion

- [ ] Configurar `pytest` como framework de pruebas
- [ ] Crear `tests/` con estructura espejo del proyecto:
  ```
  tests/
  ├── test_atmosfera.py
  ├── test_cohete.py
  ├── test_componentes.py
  ├── test_integradores.py
  ├── test_viento.py
  └── test_vuelo.py
  ```
- [ ] Tests para `atmosfera.py`: verificar T, P, rho contra tablas ISA estandar
- [ ] Tests para `componentes.py`: verificar CG, CP, CN contra valores analiticos conocidos
- [ ] Tests para `integradores.py`: comparar con soluciones analiticas (caso1, caso2)
- [ ] Tests para `cohete.py`: verificar calculo de masa, CG, CP, area de referencia
- [ ] Tests para `vuelo.py`: simular caso simple y verificar apogeo contra solucion conocida
- [ ] Configurar ejecucion automatica con `pytest` en CI (GitHub Actions)

### 1.2 Manejo de errores y validacion

- [ ] Agregar validacion de entradas en `Cohete`: masa > 0, longitud > 0, diametro > 0
- [ ] Agregar validacion en `Vuelo`: dt > 0, tiempo total > 0, estado inicial coherente
- [ ] Verificar que el archivo CSV de empuje exista y tenga el formato correcto antes de simular
- [ ] Agregar mensajes de error descriptivos en lugar de fallos silenciosos
- [ ] Validar margen de estabilidad antes de iniciar la simulacion (advertencia si CG > CP)

### 1.3 Limpieza de codigo

- [ ] Eliminar rutas absolutas hardcodeadas (ej: `C:\Users\Natalia\...` en `Graficas.py`)
- [ ] Reemplazar numeros magicos por constantes con nombre (ej: factores 0.9, 1.1 en `vuelo.py`)
- [ ] Agregar type hints a las funciones publicas de los modulos principales
- [ ] Eliminar imports comentados y codigo muerto
- [ ] Unificar idioma en nombres de variables/funciones (preferir espanol por consistencia)
- [ ] Agregar docstrings minimos a clases y funciones publicas

### 1.4 Mejoras al sistema de dependencias

- [ ] Agregar `seaborn` a `requirements.txt` (se usa en los casos de estudio pero no esta listado)
- [ ] Fijar versiones de dependencias: `numpy>=1.21`, `scipy>=1.7`, etc.
- [ ] Agregar `pytest` como dependencia de desarrollo
- [ ] Crear `pyproject.toml` o `setup.py` para instalacion formal del paquete

---

## Fase 2: GUI Completa, Usable y Sin Errores

**Objetivo:** Transformar la GUI de un prototipo con bugs criticos a una interfaz funcional, conectada al backend, con resultados en tiempo real y capacidad de exportar datos.

**Duracion estimada:** 8-10 semanas

**Prioridad:** Critica

Esta es la fase mas extensa porque la GUI es la cara del simulador y actualmente tiene errores que impiden su uso basico. Se divide en 6 subfases que van desde corregir crashes hasta agregar visualizacion en tiempo real.

### 2.1 Correccion de bugs criticos (bloqueantes)

Estos bugs impiden que la GUI funcione. Deben corregirse antes de cualquier otra mejora.

- [ ] **Implementar `run_real_simulation()`** (`ModernGUI.py:878`):
  - Funcion que traduzca los parametros de la GUI a objetos `Cohete`, `Vuelo`, `Atmosfera`, `Viento`, `Riel`
  - Ejecute `vuelo.simular_vuelo()` con los integradores seleccionados
  - Retorne un DataFrame con las columnas esperadas por `ResultsTab`
  - Use callbacks para reportar progreso y estado al hilo principal
- [ ] **Crear modulo `Plotting`** o reemplazar las llamadas en `ResultsTab` (`ModernGUI.py:760-765`):
  - Implementar `plot_altitude(ax, df)`, `plot_velocity(ax, df)`, `plot_acceleration(ax, df)`
  - Implementar `plot_mach(ax, df)`, `plot_alpha(ax, df)`, `plot_trajectory_3d(fig, df)`
  - Integrar con el canvas de matplotlib que ya existe en `ResultsTab`
- [ ] **Agregar import faltante** `import matplotlib.style as mplstyle` (`ModernGUI.py:756`)
- [ ] **Corregir typo** `update_map()` → `update_map_position()` en `load_configuration()` (`ModernGUI.py:941`)
- [ ] **Corregir valor predeterminado** del angulo de riel: cambiar `4984.73...` a `5.0` grados (`ModernGUI.py:593`)
- [ ] **Descomentar imports del backend** y verificar que los modulos existan (`ModernGUI.py:22-35`):
  ```python
  from Paquetes.PaqueteFisica.cohete import Cohete
  from Paquetes.PaqueteFisica.vuelo import Vuelo
  from Paquetes.PaqueteFisica.atmosfera import Atmosfera
  from Paquetes.PaqueteFisica.viento import Viento
  from Paquetes.PaqueteFisica.riel import Torrelanzamiento
  ```

### 2.2 Conexion completa GUI ↔ Backend

Una vez corregidos los crashes, conectar cada seccion de la GUI con su modulo de backend correspondiente.

- [ ] **Mapeo de campos a componentes:** Crear funcion que traduzca los 58 campos de `RocketTab` a objetos del backend:
  - Campos de nariz → `Cono(longitud, diametro, masa, pos_z, tipo_geometria)`
  - Campos de cuerpo (coples, tubo, tanque, etc.) → `Cilindro(longitud, diametro_ext, diametro_int, masa, pos_z)`
  - Campos de aletas → `Aletas(numero, masa_total, envergadura, cuerda_raiz, cuerda_punta, angulo_barrido, pos_z)`
  - Campos de boattail → `Boattail(longitud, diametro_frente, diametro_trasero, masa, pos_z)`
- [ ] **Conectar boton "Actualizar Cohete":**
  - Instanciar componentes con los valores de la GUI
  - Llamar a `cohete.calc_masa()`, `cohete.calc_CG()`, `cohete.calc_CP()`, `cohete.calc_Ix()`
  - Actualizar el dibujo 2D del cohete automaticamente
  - Mostrar masa total, CG, CP y margen estatico en la barra de estado
- [ ] **Conectar pestana "Simulacion":**
  - Construir objeto `Atmosfera` con altitud del sitio de lanzamiento
  - Construir objeto `Viento` con los 4 parametros del modelo de viento
  - Construir objeto `Torrelanzamiento` con longitud y angulo del riel
  - Seleccionar integrador numerico segun la opcion elegida en el dropdown
- [ ] **Conectar carga de archivos CSV:**
  - Enlazar archivo de empuje con `cohete.agregar_empuje(filepath)`
  - Enlazar archivo de Cd vs Mach con la funcion de interpolacion del arrastre
  - Enlazar archivo de masa vs tiempo con `cohete.actualizar_masa(filepath)`
- [ ] **Conectar pestana "Estabilidad":**
  - Reemplazar calculo placeholder por llamadas reales a `cohete.calc_CG()`, `cohete.calc_CP()`
  - Calcular margen estatico real: `(CP - CG) / diametro_referencia`
  - Mostrar tabla con CG, CP, CN y masa de cada componente individual

### 2.3 Validacion robusta de entradas

La GUI tiene 80+ campos de entrada y actualmente solo valida 4. Agregar validacion completa para prevenir errores y guiar al usuario.

- [ ] **Validacion en tiempo real** (al escribir en cada campo):
  - Verificar que los valores sean numericos
  - Resaltar campo en rojo si el valor es invalido
  - Mostrar tooltip con el rango valido
- [ ] **Validaciones fisicas al dar "Actualizar Cohete":**
  - Masa de cada componente > 0
  - Longitudes y diametros > 0
  - Diametro interno < diametro externo en cilindros
  - Numero de aletas >= 3 (entero)
  - Cuerda de punta <= cuerda de raiz en aletas
  - Posiciones z coherentes (componentes no se solapan)
  - Masa del propelente > 0 si se va a simular con motor
- [ ] **Validaciones antes de simular:**
  - Archivos de empuje y arrastre cargados
  - Tiempo de simulacion > 0
  - Paso de tiempo razonable (0.0001 < dt < 1.0)
  - Margen de estabilidad positivo (advertencia si < 1.0 calibres, error si < 0)
  - Latitud entre -90° y 90°, longitud entre -180° y 180°
  - Angulo del riel entre 0° y 90°
- [ ] **Mensajes de error claros:**
  - Usar `messagebox.showwarning()` para advertencias (cohete marginalmente estable)
  - Usar `messagebox.showerror()` para errores bloqueantes (falta archivo de empuje)
  - Mostrar exactamente que campo tiene el problema y cual es el valor esperado

### 2.4 Visualizacion de resultados en tiempo real

Actualmente no hay forma de ver los resultados durante la simulacion. Agregar graficas que se actualicen en vivo.

- [ ] **Panel de resultados en vivo durante la simulacion:**
  - Crear un `LivePlotFrame` que se actualice cada N pasos de integracion
  - Grafica de altitud vs tiempo (se dibuja conforme avanza la simulacion)
  - Grafica de velocidad vs tiempo (actualizada en vivo)
  - Indicadores numericos en vivo: altitud actual, velocidad actual, Mach actual
  - Deteccion y marcado automatico de eventos (MECO, apogeo, despliegue de paracaidas)
- [ ] **Callback de progreso desde el integrador:**
  - Modificar `vuelo.simular_vuelo()` para aceptar un callback `on_step(t, state)`
  - Llamar al callback cada N pasos (configurable, ej: cada 50 pasos)
  - Desde el callback, actualizar graficas via `self.after()` (thread-safe)
  - Actualizar barra de progreso con `t / t_max`
- [ ] **Indicador de fase de vuelo:**
  - Mostrar fase actual: "En riel", "Vuelo propulsado", "Coasting", "Descenso con paracaidas"
  - Cambiar color del indicador segun la fase
  - Mostrar tiempo transcurrido de simulacion
- [ ] **Pestana de resultados completa (post-simulacion):**
  - **6 graficas principales en grid 2x3:**
    1. Altitud vs Tiempo (con marcadores de MECO, apogeo, impacto)
    2. Velocidad total vs Tiempo
    3. Aceleracion vs Tiempo
    4. Numero de Mach vs Tiempo
    5. Angulo de ataque (alpha) vs Tiempo
    6. Trayectoria 3D (x, y, z)
  - **Graficas adicionales accesibles por dropdown o tabs:**
    - Componentes de velocidad (vx, vy, vz)
    - Fuerzas: empuje, arrastre, fuerza normal
    - Posiciones CG y CP vs tiempo
    - Angulos: pitch (theta), gamma (angulo de trayectoria)
    - Magnitud y direccion del viento
    - Masa del cohete vs tiempo
    - Numero de Reynolds vs tiempo
  - **Resumen numerico del vuelo:**
    - Apogeo (m), tiempo al apogeo (s)
    - Velocidad maxima (m/s), Mach maximo
    - Aceleracion maxima (g)
    - Tiempo total de vuelo (s)
    - Distancia de impacto (m), azimut de impacto (°)
    - Velocidad de impacto (m/s)
    - Tiempo de salida del riel (s), velocidad de salida del riel (m/s)
    - Margen de estabilidad minimo durante el vuelo

### 2.5 Exportacion de datos y resultados

Permitir al usuario guardar y compartir los resultados de sus simulaciones.

- [ ] **Exportar datos crudos de la simulacion:**
  - Boton "Exportar CSV" que guarde toda la trayectoria (t, x, y, z, vx, vy, vz, theta, omega, CG, CP, Mach, alpha, fuerzas, etc.)
  - Boton "Exportar JSON" con resumen de metricas clave
  - Dialogo de seleccion de ruta con nombre predeterminado: `simulacion_YYYY-MM-DD_HH-MM.csv`
- [ ] **Exportar graficas individuales:**
  - Click derecho en cualquier grafica → "Guardar como PNG/SVG/PDF"
  - Opcion de guardar todas las graficas en una carpeta de una sola vez
  - Resolucion configurable (72, 150, 300 DPI)
- [ ] **Exportar reporte completo en PDF:**
  - Usar `matplotlib` + `reportlab` o `fpdf2` para generar el PDF
  - Contenido del reporte:
    - Titulo: "Reporte de Simulacion - [nombre del cohete]"
    - Seccion 1: Configuracion del cohete (tabla de componentes con masas, dimensiones)
    - Seccion 2: Analisis de estabilidad (CG, CP, margen estatico, diagrama)
    - Seccion 3: Parametros de simulacion (viento, riel, integrador, sitio de lanzamiento)
    - Seccion 4: Resultados del vuelo (tabla resumen + graficas principales)
    - Seccion 5: Graficas detalladas (todas las graficas disponibles)
    - Pie de pagina: fecha, version del simulador, nombre del archivo
  - Boton "Generar Reporte PDF" en la pestana de resultados
- [ ] **Exportar configuracion del cohete:**
  - Guardar/cargar toda la configuracion como JSON (ya parcialmente implementado)
  - Corregir bug en `load_configuration()` (`update_map()` → `update_map_position()`)
  - Incluir archivos CSV referenciados (empuje, arrastre, masa) como rutas relativas
  - Incluir configuracion Xitle II como archivo de ejemplo: `configs/xitle_ii.json`
- [ ] **Historial de simulaciones:**
  - Guardar automaticamente un resumen de cada simulacion ejecutada
  - Archivo `historial_simulaciones.json` con fecha, parametros clave y resultados
  - Permitir comparar dos simulaciones lado a lado (mismas graficas, datos diferentes)

### 2.6 Mejoras de usabilidad y experiencia de usuario

- [ ] **Sistema de tooltips funcional:**
  - Implementar `create_tooltip()` (actualmente es placeholder vacio)
  - Agregar tooltips a todos los campos de entrada explicando:
    - Que representa el parametro
    - Unidades esperadas
    - Rango tipico de valores
  - Ejemplo: campo "Envergadura de aletas" → "Distancia desde la raiz hasta la punta de la aleta, medida perpendicularmente al cuerpo. Valores tipicos: 0.05 - 0.3 m"
- [ ] **Implementar `reset_to_defaults()`:**
  - Boton que restaure todos los campos a los valores del cohete Xitle II
  - Pedir confirmacion antes de resetear: "¿Deseas restaurar todos los valores predeterminados?"
- [ ] **Actualizacion automatica del dibujo del cohete:**
  - Redibujar automaticamente al cambiar cualquier campo de dimension (longitud, diametro)
  - Usar evento `<FocusOut>` o timer con debounce (300ms) para no redibujar en cada tecla
  - Mostrar marcadores de CG (verde) y CP (rojo) en el dibujo
- [ ] **Mapa interactivo funcional:**
  - Actualizar el marcador del mapa al cambiar latitud/longitud (corregir `on_coordinate_change`)
  - Permitir click en el mapa para seleccionar ubicacion de lanzamiento
  - Mostrar punto de impacto estimado en el mapa despues de la simulacion
  - Mostrar elipse de dispersion si se ejecuto Monte Carlo
- [ ] **Panel de consola/logs:**
  - Agregar un panel de texto en la parte inferior de la GUI
  - Registrar todos los eventos: "Cohete actualizado", "Simulacion iniciada", "MECO detectado a t=3.2s"
  - Registrar advertencias: "Margen estatico bajo: 0.8 calibres"
  - Registrar errores: "Error: archivo de empuje no encontrado"
  - Permitir copiar texto del log al clipboard
- [ ] **Pestana de comparacion de simulaciones:**
  - Cargar dos o mas simulaciones previamente guardadas
  - Mostrar graficas superpuestas (mismos ejes, diferentes colores)
  - Tabla comparativa de metricas clave (apogeo, vel. max, tiempo de vuelo)
  - Util para evaluar el efecto de cambiar un parametro
- [ ] **Indicadores visuales de estado:**
  - Semaforo de estabilidad: verde (margen > 1.5 cal), amarillo (1.0-1.5), rojo (< 1.0)
  - Indicador de archivos cargados: checkmark verde si empuje y Cd estan cargados
  - Indicador de cohete actualizado: advertencia si se cambiaron parametros sin dar "Actualizar"
- [ ] **Atajos de teclado:**
  - `Ctrl+S`: Guardar configuracion
  - `Ctrl+O`: Cargar configuracion
  - `Ctrl+R`: Ejecutar simulacion
  - `Ctrl+E`: Exportar resultados
  - `F5`: Actualizar cohete

---

## Fase 3: Modelo de 6 Grados de Libertad (6-DOF)

**Objetivo:** Ampliar el motor de simulacion de 3-DOF a 6-DOF para modelar la dinamica rotacional completa del cohete.

**Duracion estimada:** 6-8 semanas

### 3.1 Representacion de actitud con cuaterniones

- [ ] Implementar clase `Quaternion` con operaciones basicas:
  - Multiplicacion, conjugado, norma, inverso
  - Conversion a/desde angulos de Euler
  - Conversion a/desde matriz de rotacion (DCM)
  - Interpolacion (SLERP)
- [ ] Implementar integracion de cuaterniones: `dq/dt = 0.5 * q * omega`
- [ ] Tests unitarios: rotaciones conocidas, identidades, gimbal lock
- [ ] Integrar con `Extras/NoImplementadoAun/angulos_euler.py` existente

### 3.2 Ecuaciones de movimiento 6-DOF

- [ ] Ampliar el vector de estado:
  ```
  Estado 3-DOF: [x, y, z, vx, vy, vz, theta, omega]          (8 variables)
  Estado 6-DOF: [x, y, z, vx, vy, vz, q0, q1, q2, q3, wx, wy, wz]  (13 variables)
  ```
- [ ] Implementar ecuaciones de Euler para rotacion:
  ```
  I * dw/dt = tau - w x (I * w)
  ```
  donde `I` es el tensor de inercia completo (Ixx, Iyy, Izz, Ixy, Ixz, Iyz)
- [ ] Calcular momentos aerodinamicos en 3 ejes (pitch, yaw, roll)
- [ ] Implementar amortiguamiento aerodinamico rotacional
- [ ] Transformar fuerzas del marco cuerpo al marco inercial usando cuaterniones
- [ ] Mantener compatibilidad: poder elegir entre 3-DOF y 6-DOF en la GUI

### 3.3 Tensor de inercia completo

- [ ] Extender `componentes.py` para calcular Ixx, Iyy, Izz de cada componente
- [ ] Implementar teorema de ejes paralelos en 3D (tensor de Steiner)
- [ ] Calcular tensor de inercia total del cohete (suma de componentes)
- [ ] Actualizar tensor con la perdida de masa del motor en tiempo real

### 3.4 Fuerzas y momentos en 3D

- [ ] Fuerza normal en plano de ataque (no solo pitch): `N = f(alpha, beta)`
- [ ] Momento restaurador: `M = N * (CP - CG)`
- [ ] Momento de roll por aletas (roll damping)
- [ ] Momento de amortiguamiento aerodinamico (pitch/yaw damping)
- [ ] Calculo del angulo de ataque total: `alpha_total = arccos(v_body · e_x / |v|)`

### 3.5 Validacion del 6-DOF

- [ ] Comparar caso sin viento contra 3-DOF (deben coincidir en traslacion)
- [ ] Verificar conservacion de momento angular sin fuerzas externas
- [ ] Comparar con OpenRocket o RASAero para trayectorias estandar
- [ ] Verificar estabilidad giroscopica con parametros conocidos

---

## Fase 4: Simulacion de Monte Carlo y Analisis de Incertidumbre

**Objetivo:** Permitir analisis estadistico de trayectorias considerando incertidumbres en los parametros del cohete y del entorno.

**Duracion estimada:** 4-6 semanas

### 4.1 Framework de Monte Carlo

- [ ] Definir parametros con distribucion de probabilidad:
  ```python
  parametros = {
      "masa_total": Normal(media=12.5, sigma=0.3),      # kg
      "Cd":         Normal(media=0.45, sigma=0.05),
      "empuje_max": Normal(media=1200, sigma=50),        # N
      "viento_vel": Uniform(min=0, max=15),              # m/s
      "viento_dir": Uniform(min=0, max=360),             # grados
      "angulo_riel": Normal(media=85, sigma=1),          # grados
  }
  ```
- [ ] Implementar muestreo (Latin Hypercube Sampling recomendado para eficiencia)
- [ ] Ejecutar N simulaciones con parametros muestreados
- [ ] Paralelizar con `multiprocessing` o `joblib`
- [ ] Almacenar resultados resumidos de cada corrida

### 4.2 Analisis estadistico de resultados

- [ ] Calcular estadisticas: media, desviacion estandar, percentiles (5%, 95%) de:
  - Apogeo
  - Velocidad maxima
  - Numero de Mach maximo
  - Punto de impacto (distancia y azimut)
  - Tiempo de vuelo
- [ ] Generar histogramas de distribucion de apogeo y punto de impacto
- [ ] Generar elipse de dispersion de puntos de impacto (2D, sobre mapa)
- [ ] Analisis de sensibilidad: identificar que parametros afectan mas al resultado

### 4.3 Visualizacion e integracion con GUI

- [ ] Grafica de envolvente de trayectorias (media +/- 2 sigma)
- [ ] Mapa de calor de puntos de impacto
- [ ] Histograma de apogeos con intervalos de confianza
- [ ] Diagrama de tornado (sensibilidad de parametros)
- [ ] Nueva pestana "Monte Carlo" en la GUI con:
  - Configuracion de distribuciones por parametro
  - Numero de corridas
  - Barra de progreso general
  - Resultados estadisticos y graficas

---

## Fase 5: Cohetes Multietapa y Sistemas de Recuperacion

**Objetivo:** Soportar cohetes con multiples etapas y modelar la fase de recuperacion con paracaidas de forma realista.

**Duracion estimada:** 6-8 semanas

### 5.1 Soporte para cohetes multietapa

- [ ] Disenar estructura de datos para multiples etapas:
  ```python
  cohete = CoheteMultietapa(
      etapas=[etapa1, etapa2, etapa3],
      tiempos_separacion=[t1, t2],      # o por evento (burnout)
      retardos_ignicion=[dt1, dt2],      # retardo entre separacion e ignicion
  )
  ```
- [ ] Implementar logica de separacion de etapas:
  - Deteccion de fin de empuje (burnout)
  - Retardo configurable antes de ignicion de siguiente etapa
  - Recalculo de masa, CG, CP, Ix al separar
- [ ] Modelar la caida de etapas gastadas (simulacion paralela opcional)
- [ ] Soporte de interstage: aerodinamica de la seccion entre etapas
- [ ] Actualizar GUI para definir multiples etapas

### 5.2 Sistema de recuperacion realista

- [ ] Modelar despliegue de paracaidas con dinamica de apertura:
  ```
  Cd_paracaidas(t) = Cd_final * (1 - exp(-t / tau_apertura))
  ```
- [ ] Soporte para recuperacion dual (drogue + main):
  - Drogue desplegado en apogeo
  - Main desplegado a altitud configurable
- [ ] Calcular velocidad de descenso y fuerza de apertura (shock load)
- [ ] Modelar oscilacion pendular durante descenso
- [ ] Integrar con mapa: zona de aterrizaje con viento

### 5.3 Eventos configurables

- [ ] Disenar sistema general de eventos:
  ```python
  eventos = [
      Evento(condicion="altitud == apogeo", accion="desplegar_drogue"),
      Evento(condicion="altitud <= 500 m",  accion="desplegar_main"),
      Evento(condicion="burnout_etapa_1",   accion="separar_etapa"),
  ]
  ```
- [ ] Deteccion de eventos por cruce de cero (zero-crossing) durante integracion
- [ ] Soporte para eventos por temporizador, altitud, velocidad o Mach
- [ ] Log de eventos durante la simulacion

---

## Fase 6: Modelos Avanzados (Aerodinamica, Atmosfera, Viento)

**Objetivo:** Mejorar la fidelidad de los modelos fisicos para simulaciones mas precisas.

**Duracion estimada:** 8-10 semanas

### 6.1 Aerodinamica avanzada

- [ ] Coeficiente de arrastre dependiente de alpha y Mach: `Cd = f(M, alpha)`
- [ ] Correcciones de compresibilidad (Prandtl-Glauert para M < 0.8)
- [ ] Efectos transonicos (0.8 < M < 1.2): interpolacion con datos experimentales
- [ ] Arrastre de base (base drag) y efecto de boattail
- [ ] Arrastre por rugosidad superficial
- [ ] Efectos de numero de Reynolds en CN y Cd
- [ ] Interferencia entre componentes (aletas-cuerpo, boattail-aletas)
- [ ] Soporte para importar datos aerodinamicos de OpenRocket (.ork)

### 6.2 Modelo atmosferico mejorado

- [ ] Soporte para datos atmosfericos reales (radiosondeos)
- [ ] Modelo de humedad y su efecto en la densidad del aire
- [ ] Capas de inversion termica configurables
- [ ] Variacion de la gravedad con la altitud (ya existe `calc_gravedad()` pero no se usa consistentemente)

### 6.3 Modelo de viento realista

- [ ] Perfil de viento con la altitud (power law o logaritmico):
  ```
  v(h) = v_ref * (h / h_ref)^alpha_wind
  ```
- [ ] Modelos de turbulencia: Dryden o von Karman (espectrales)
- [ ] Rafagas con coherencia temporal (no aleatorias en cada paso)
- [ ] Soporte para importar datos de viento reales (estacion meteorologica)
- [ ] Modelos de rafaga estandar (MIL-STD-1797, FAR 25)

### 6.4 Modelo de propulsion mejorado

- [ ] Incertidumbre en la curva de empuje (variacion run-to-run)
- [ ] Retardo de ignicion configurable
- [ ] Modelo de tailoff (caida gradual del empuje al final)
- [ ] Variacion del empuje con la presion ambiente (motores hibridos)

---

## Fase 7: Empaquetado y Distribucion

**Objetivo:** Hacer el simulador facil de instalar, distribuir y usar por cualquier persona.

**Duracion estimada:** 3-4 semanas

### 7.1 Empaquetado como aplicacion

- [ ] Crear ejecutable independiente con PyInstaller o cx_Freeze
- [ ] Generar instaladores para Windows, macOS y Linux
- [ ] Incluir datos de ejemplo (curvas de empuje, configuracion Xitle II)
- [ ] Crear icono y branding de la aplicacion

### 7.2 Documentacion completa

- [ ] Manual de usuario: como definir un cohete, ejecutar simulaciones, interpretar resultados
- [ ] Manual tecnico: ecuaciones de movimiento, aproximaciones, limitaciones
- [ ] Guia de API con Sphinx (documentacion auto-generada del codigo)
- [ ] Tutoriales paso a paso para casos de uso comunes
- [ ] Video demostrativo

### 7.3 CI/CD y releases

- [ ] Configurar GitHub Actions para tests automaticos en cada PR
- [ ] Linting automatico con `ruff` o `flake8`
- [ ] Releases automaticos con versionado semantico
- [ ] Publicar en PyPI: `pip install rocketsim-unam`

---

## Resumen de Fases

| Fase | Nombre | Duracion | Prioridad | Dependencias |
|------|--------|----------|-----------|--------------|
| 1 | Consolidacion y Calidad | 4-6 sem | Critica | Ninguna |
| 2 | GUI Completa, Usable y Sin Errores | 8-10 sem | **Critica** | Fase 1 |
| 3 | Modelo 6-DOF | 6-8 sem | Alta | Fase 1 |
| 4 | Monte Carlo | 4-6 sem | Media | Fases 1, 2 |
| 5 | Multietapa y Recuperacion | 6-8 sem | Media | Fases 1, 3 |
| 6 | Modelos Avanzados | 8-10 sem | Baja | Fases 1, 3 |
| 7 | Empaquetado y Distribucion | 3-4 sem | Baja | Fases 1, 2 |

> **Nota:** La Fase 2 (GUI) y la Fase 3 (6-DOF) pueden desarrollarse en paralelo. La Fase 4 (Monte Carlo) necesita la Fase 2 para la interfaz de configuracion y visualizacion. Las fases 5, 6 y 7 dependen de las anteriores como se indica.

```
Fase 1 (Consolidacion)
  ├── Fase 2 (GUI) ─────── Fase 4 (Monte Carlo) ──┐
  │                    └── Fase 7 (Empaquetado)    │
  ├── Fase 3 (6-DOF) ── Fase 5 (Multietapa)       │
  │                  └── Fase 6 (Modelos)          │
  └────────────────────────────────────────────────┘
```

---

## Como Contribuir a una Fase

1. Elige una fase y una tarea especifica (checkbox).
2. Crea una rama: `git checkout -b fase-N/nombre-tarea`
3. Implementa la mejora con tests.
4. Abre un Pull Request referenciando este documento.
5. Marca la tarea como completada en este archivo.

---

## Referencias Tecnicas

- **6-DOF Rocket Dynamics:** Zipfel, P. *Modeling and Simulation of Aerospace Vehicle Dynamics*. AIAA, 2007.
- **Quaternion Attitude:** Diebel, J. *Representing Attitude: Euler Angles, Unit Quaternions, and Rotation Vectors*. Stanford, 2006.
- **Monte Carlo for Rockets:** Box, S. et al. *Stochastic Six-Degree-of-Freedom Flight Simulator for Passively Controlled High Power Rockets*. Journal of Aerospace Engineering, 2011.
- **Atmospheric Models:** U.S. Standard Atmosphere, 1976. NOAA/NASA.
- **Wind Turbulence:** MIL-STD-1797A, *Flying Qualities of Piloted Aircraft*.
- **OpenRocket:** Niskanen, S. *Development of an Open Source model rocket simulation software*. Helsinki, 2009.
- **GUI Design for Scientific Software:** Nielsen, J. *Usability Engineering*. Morgan Kaufmann, 1994.
