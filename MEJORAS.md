# Plan de Mejoras - Rocket-Sim UNAM

Este documento describe el plan de desarrollo y mejoras del simulador, organizado en **fases incrementales**. Cada fase se construye sobre la anterior, de modo que el simulador gana funcionalidad de forma progresiva sin romper lo que ya funciona.

---

## Estado Actual del Proyecto

| Aspecto | Estado | Observaciones |
|---|---|---|
| Fisica 3-DOF | Funcional | Solo modela pitch; falta roll y yaw |
| Integradores | Funcional | 8 metodos disponibles; los adaptativos necesitan mas pruebas |
| GUI | Parcial | Diseno moderno, pero el backend no esta completamente conectado |
| Visualizacion | Funcional | Buenas graficas; rutas hardcodeadas; alto consumo de memoria |
| Documentacion | Critica | Casi ausente; comentarios mezclados espanol/ingles |
| Tests automatizados | Inexistente | Solo casos manuales (caso1, caso2, caso3) |
| Manejo de errores | Minimo | Muchos fallos silenciosos; sin validacion de entradas |
| Calidad de codigo | Mejorable | Sin type hints; numeros magicos; codigo duplicado |

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

## Fase 2: Conexion GUI-Backend y Experiencia de Usuario

**Objetivo:** Conectar completamente la interfaz grafica con el motor de simulacion y mejorar la experiencia del usuario.

**Duracion estimada:** 4-6 semanas

### 2.1 Integracion GUI con motor de simulacion

- [ ] Conectar los campos de entrada de la GUI con la clase `Cohete`
- [ ] Implementar la creacion de componentes (Cono, Cilindro, Aletas, Boattail) desde la GUI
- [ ] Conectar el boton "Actualizar Cohete" con `cohete.calc_CG()`, `cohete.calc_CP()`, `cohete.calc_Ix()`
- [ ] Conectar el boton "Ejecutar Simulacion" con `vuelo.simular_vuelo()`
- [ ] Eliminar `placeholder_run_simulation()` y reemplazar con llamadas reales al backend
- [ ] Implementar carga de archivos CSV de empuje desde la GUI (file dialog)
- [ ] Implementar carga de archivos CSV de coeficiente de arrastre desde la GUI

### 2.2 Visualizacion de resultados en la GUI

- [ ] Integrar graficas de matplotlib dentro de la interfaz (usando `FigureCanvasTkAgg`)
- [ ] Mostrar resumen numerico de resultados (apogeo, velocidad maxima, tiempo de vuelo)
- [ ] Mostrar pestana de estabilidad con diagrama CG/CP en tiempo real
- [ ] Integrar animacion 3D dentro de la GUI (o como ventana externa)
- [ ] Mostrar mapa interactivo con punto de lanzamiento e impacto

### 2.3 Guardado y carga de configuraciones

- [ ] Implementar guardado de configuracion del cohete a JSON
- [ ] Implementar carga de configuracion desde JSON
- [ ] Incluir configuracion predeterminada del cohete Xitle II como ejemplo
- [ ] Exportacion de resultados a CSV/JSON desde la GUI

### 2.4 Mejoras de usabilidad

- [ ] Agregar tooltips explicativos en los campos de entrada
- [ ] Agregar barra de progreso durante la simulacion
- [ ] Implementar sistema de logs visible en la GUI (panel de consola)
- [ ] Agregar undo/redo para cambios en parametros del cohete

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

### 4.3 Visualizacion de Monte Carlo

- [ ] Grafica de envolvente de trayectorias (media +/- 2 sigma)
- [ ] Mapa de calor de puntos de impacto
- [ ] Histograma de apogeos con intervalos de confianza
- [ ] Diagrama de tornado (sensibilidad de parametros)
- [ ] Integrar resultados de Monte Carlo en la GUI

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

### 7.3 Exportacion de reportes

- [ ] Generacion de reportes en PDF con:
  - Configuracion del cohete
  - Parametros de simulacion
  - Graficas de resultados
  - Tabla resumen del vuelo
  - Analisis de estabilidad
- [ ] Exportacion a formatos estandar (CSV, JSON, HDF5)
- [ ] Plantilla de reporte personalizable

### 7.4 CI/CD y releases

- [ ] Configurar GitHub Actions para tests automaticos en cada PR
- [ ] Linting automatico con `ruff` o `flake8`
- [ ] Releases automaticos con versionado semantico
- [ ] Publicar en PyPI: `pip install rocketsim-unam`

---

## Resumen de Fases

| Fase | Nombre | Duracion | Prioridad | Dependencias |
|------|--------|----------|-----------|--------------|
| 1 | Consolidacion y Calidad | 4-6 sem | Critica | Ninguna |
| 2 | Conexion GUI-Backend | 4-6 sem | Alta | Fase 1 |
| 3 | Modelo 6-DOF | 6-8 sem | Alta | Fase 1 |
| 4 | Monte Carlo | 4-6 sem | Media | Fase 1 |
| 5 | Multietapa y Recuperacion | 6-8 sem | Media | Fases 1, 3 |
| 6 | Modelos Avanzados | 8-10 sem | Baja | Fases 1, 3 |
| 7 | Empaquetado y Distribucion | 3-4 sem | Baja | Fases 1, 2 |

> **Nota:** Las Fases 2, 3 y 4 pueden desarrollarse en paralelo despues de completar la Fase 1. Las fases posteriores dependen de las anteriores como se indica.

```
Fase 1 (Consolidacion)
  ├── Fase 2 (GUI)  ──────────────────────────┐
  ├── Fase 3 (6-DOF) ── Fase 5 (Multietapa)   ├── Fase 7 (Empaquetado)
  │                  └── Fase 6 (Modelos)      │
  └── Fase 4 (Monte Carlo) ───────────────────┘
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
