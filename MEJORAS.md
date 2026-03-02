# Plan de Mejoras - Rocket-Sim UNAM

Este documento describe el plan de desarrollo y mejoras del simulador, organizado en **fases incrementales**. Cada fase se construye sobre la anterior, de modo que el simulador gana funcionalidad de forma progresiva sin romper lo que ya funciona.

---

## Estado Actual del Proyecto

| Aspecto | Estado | Observaciones |
|---|---|---|
| Fisica 3-DOF | Funcional | Solo modela pitch; falta roll y yaw |
| Integradores | Funcional | 8 metodos disponibles; los adaptativos necesitan mas pruebas |
| GUI (ModernGUI.py) | **Funcional** | Backend conectado; 6 bugs criticos corregidos; validacion completa; 5 vistas de graficas; exportacion CSV/JSON/PNG |
| Visualizacion en GUI | **Funcional** | 5 vistas de graficas (resumen, fuerzas, aerodinamica, 3D, masa/CG/CP) con tema oscuro |
| Exportacion de datos | **Funcional** | CSV (trayectoria completa), JSON (resumen), PNG (graficas 200 DPI) desde la GUI |
| Documentacion | Critica | Casi ausente; comentarios mezclados espanol/ingles |
| Tests automatizados | Inexistente | Solo casos manuales (caso1, caso2, caso3) |
| Manejo de errores | **Mejorado** | Validacion completa en GUI (80+ campos); mensajes descriptivos |
| Calidad de codigo | Mejorable | Sin type hints; numeros magicos; codigo duplicado |

### Bugs Criticos Corregidos

| Bug | Solucion |
|-----|----------|
| `run_real_simulation()` no existia | Implementada funcion completa que conecta GUI con backend |
| Modulo `Plotting` no importado | Reemplazado por metodos internos de `ResultsTab` con 5 vistas |
| `mplstyle` no importado | Import agregado correctamente |
| Typo `update_map()` | Corregido a `update_map_position()` |
| Imports del backend comentados | Imports con try/except y fallback a modo demo |
| Angulo de riel = 4984.73 | Corregido a 87 grados |

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

- [x] **Implementar `run_real_simulation()`**: Funcion completa que traduce parametros GUI a objetos backend, ejecuta la simulacion y retorna DataFrame con 20+ columnas
- [x] **Reemplazar modulo `Plotting`**: Se implementaron directamente en `ResultsTab` los metodos `_draw_summary_plots()`, `_draw_forces_plots()`, `_draw_aero_plots()`, `_draw_3d_trajectory()`, `_draw_mass_cg_plots()` con 5 vistas de graficas seleccionables
- [x] **Agregar import `matplotlib.style`**: Importado correctamente
- [x] **Corregir typo `update_map()`**: Todas las llamadas usan `update_map_position()` correctamente
- [x] **Corregir valor predeterminado del angulo de riel**: Cambiado de `4984.73` a `87` grados
- [x] **Imports del backend funcionales**: Se importan con try/except y fallback a modo demo si el backend no esta disponible

### 2.2 Conexion completa GUI ↔ Backend

Una vez corregidos los crashes, conectar cada seccion de la GUI con su modulo de backend correspondiente.

- [x] **Mapeo de campos a componentes:** `run_real_simulation()` traduce todos los campos a Cono, Cilindro, Aletas, Boattail con posiciones encadenadas automaticamente (`.bottom[2]`)
- [x] **Conectar boton "Actualizar Cohete":** Instancia componentes, redibuja cohete con marcadores CG/CP, actualiza log
- [x] **Conectar pestana "Simulacion":** Construye `atmosfera()`, `Viento(vel_base, vel_mean, vel_var, ang_base, var_ang)`, `Torrelanzamiento(longitud, angulo)`, selecciona integrador del dropdown
- [x] **Conectar carga de archivos CSV:** Archivos de empuje, arrastre y masa se pasan al constructor de `Cohete` desde `data_tables_tab.filepaths`
- [x] **Conectar pestana "Estabilidad":** Calcula CG, CP, CN por componente usando formulas Barrowman, muestra tabla completa y semaforo de estabilidad

### 2.3 Validacion robusta de entradas

La GUI tiene 80+ campos de entrada y actualmente solo valida 4. Agregar validacion completa para prevenir errores y guiar al usuario.

- [x] **Validacion en tiempo real:** `_validate_field()` verifica al salir del campo, resalta en rojo/amarillo, con tooltips de rango
- [x] **Validaciones fisicas:** `validate_params()` en RocketTab verifica masas > 0, longitudes > 0, diam_int < diam_ext (7 pares), aletas >= 3, propelentes > 0
- [x] **Validaciones antes de simular:** `validate_params()` en SimulationEnvironmentTab verifica lat/lon, angulo riel 0-90, dt 0.0001-1.0, t_max > 0, CSVs cargados
- [x] **Mensajes de error claros:** `messagebox.showerror()` con lista detallada de errores, cada mensaje indica el campo y valor esperado

### 2.4 Visualizacion de resultados en tiempo real

Actualmente no hay forma de ver los resultados durante la simulacion. Agregar graficas que se actualicen en vivo.

- [x] **Barra de progreso en vivo:** Callback `progress_callback` actualiza `CTkProgressBar` durante la simulacion via `self.after()` (thread-safe)
- [ ] **Graficas en vivo (mejora futura):** Crear `LivePlotFrame` que se actualice cada N pasos de integracion mostrando altitud y velocidad en tiempo real
- [x] **Pestana de resultados completa (5 vistas seleccionables por dropdown):**
  - **Resumen (6 graficas):** Altitud, Velocidad, Aceleracion, Mach, Alpha, Trayectoria X-Z con marcadores de apogeo
  - **Fuerzas:** Empuje, Arrastre, Normal, y las 3 superpuestas
  - **Aerodinamica:** Cd, Mach, Alpha, Gamma
  - **Trayectoria 3D:** Grafica 3D con marcadores de lanzamiento y apogeo
  - **Masa y CG/CP:** Masa vs tiempo, CG/CP vs tiempo, theta, omega
- [x] **Resumen numerico del vuelo:** Apogeo, Vel. Max, Mach Max, Tiempo de vuelo, Distancia de impacto

### 2.5 Exportacion de datos y resultados

Permitir al usuario guardar y compartir los resultados de sus simulaciones.

- [x] **Exportar datos crudos CSV:** Boton "Exportar CSV" guarda toda la trayectoria (20+ columnas) con nombre predeterminado `simulacion_YYYY-MM-DD_HH-MM.csv`
- [x] **Exportar resumen JSON:** Boton "Exportar JSON" guarda metricas clave (apogeo, vel. max, mach max, accel max, distancia impacto, masas)
- [x] **Exportar graficas:** Boton "Guardar Graficas" exporta las 5 vistas como PNG a 200 DPI en carpeta seleccionada
- [x] **Exportar configuracion del cohete:** Guardar/cargar JSON con todos los parametros + rutas CSV referenciadas. Bug `update_map()` corregido
- [ ] **Exportar reporte PDF:** Usar `fpdf2` para generar reporte completo con configuracion + graficas + resumen (pendiente)
- [ ] **Historial de simulaciones:** Guardar resumen automatico y permitir comparar simulaciones lado a lado (pendiente)

### 2.6 Mejoras de usabilidad y experiencia de usuario

- [x] **Sistema de tooltips funcional:** Clase `ToolTip` con ventana flotante. 15+ tooltips en campos de aletas, paracaidas, propelentes y botones
- [x] **Implementar `reset_to_defaults()`:** Boton "Resetear Defaults" con confirmacion, restaura 40+ valores del Xitle II definidos en `DEFAULTS`
- [x] **Dibujo del cohete con marcadores CG/CP:** Dibujo 2D con colores por componente, lineas de CG (verde) y CP (rojo) con etiquetas
- [x] **Mapa interactivo funcional:** Mapa se actualiza en tiempo real al cambiar lat/lon via `on_coordinate_change`. Fallback graceful si `tkintermapview` no esta instalado
- [x] **Panel de consola/logs:** Pestana "Log" con `CTkTextbox` monoespacio, timestamps, niveles [INFO/WARN/ERROR/OK/SIM], botones Limpiar y Copiar al Portapapeles
- [x] **Indicadores visuales de estado:** Semaforo de estabilidad (verde/amarillo/rojo), indicadores de archivos CSV cargados (verde/rojo), indicador de backend (conectado/demo)
- [x] **Atajos de teclado:** `Ctrl+R` ejecutar, `Ctrl+S` guardar, `Ctrl+O` cargar, `F5` actualizar cohete
- [ ] **Pestana de comparacion de simulaciones:** Cargar 2+ simulaciones y mostrar graficas superpuestas (pendiente)

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
