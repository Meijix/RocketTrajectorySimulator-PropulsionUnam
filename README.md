# 🚀 Rocket-Sim UNAM: Simulador de Vuelo de Cohetes 3-DOF 🚀

![Logo Propulsión UNAM](https://www.propulsion-unam.com/images/logo-propulsion-blanco.png)

**Rocket-Sim UNAM** es un simulador numérico avanzado para la dinámica de vuelo de cohetes suborbitales, con un motor de 3 Grados de Libertad (3-DOF) y una interfaz gráfica de usuario moderna. Este proyecto nació como parte de la tesis de licenciatura en Matemáticas y fue desarrollado en colaboración con el equipo **Propulsión UNAM** de la Facultad de Ingeniería de la UNAM.

---

## 📄 Descripción General del Proyecto

El objetivo principal de este simulador es proporcionar una herramienta robusta y de código abierto para el **diseño, análisis y validación de trayectorias de cohetes experimentales**. Está diseñado para ser utilizado por equipos estudiantiles de cohetería, investigadores, y como recurso educativo en cursos de ingeniería aeroespacial y dinámica de vuelo.

Este software traduce los complejos modelos matemáticos de la mecánica de vuelo a una plataforma interactiva y accesible, permitiendo a los usuarios:
-   **Evaluar la estabilidad** de un diseño antes de su manufactura.
-   **Predecir con precisión** el apogeo, la zona de impacto y otros parámetros críticos del vuelo.
-   **Optimizar el rendimiento** del vehículo a través de la simulación de múltiples escenarios.
-   **Incrementar la seguridad** en los lanzamientos experimentales.

El desarrollo y la validación de este simulador constituyen el núcleo de la tesis de licenciatura **"Simulación Numérica de la Dinámica de un Cohete Híbrido"**.

➡️ **[Consulta la tesis completa aquí (PDF)](./Tesis_UNAM_NataliaMejBau_COMPLETAFINAL.pdf)**

---

## ✨ Características Principales

-   **Motor de Simulación 3-DOF:** Modela con precisión la traslación (x, y, z) y la rotación pitch del cohete, considerándolo como un cuerpo rígido.
-   **Interfaz Gráfica Intuitiva:** Desarrollada con `CustomTkinter`, permite definir todos los aspectos del cohete y la simulación sin necesidad de escribir código.
-   **Definición Modular de Cohetes:** Permite construir un cohete a partir de componentes detallados (ojiva, cuerpo, aletas, motor, tanques, sistemas internos, etc.), especificando sus masas, dimensiones y posiciones.
-   **Métodos Numéricos Avanzados:** Incluye una suite de integradores de Ecuaciones Diferenciales Ordinarias (EDOs) de alto orden y con control de paso adaptativo, como **DOP853 (Dormand-Prince)**, RK45, BDF y LSODA.
-   **Análisis de Estabilidad Estática:** Calcula automáticamente el Centro de Gravedad (CG) y el Centro de Presión (CP) en tiempo real, mostrando el margen estático para evaluar la estabilidad del vehículo.
-   **Visualización de Datos Completa:** Genera gráficas detalladas y animaciones 3D de la trayectoria, orientación, velocidades y fuerzas aerodinámicas.
-   **Importación de Datos Externos:** Permite cargar curvas de empuje y coeficientes de arrastre desde archivos CSV para simular motores y aerodinámicas específicas.
-   **Mapa Interactivo:** Visualiza el sitio de lanzamiento y la trayectoria proyectada en un mapa, gracias a la integración con `tkintermapview`.

---

## 📸 Capturas de Pantalla de la GUI

<table>
  <tr>
    <td><img src="https://i.imgur.com/r0V5VfN.png" alt="Pestaña de Definición del Cohete" width="400"/></td>
    <td><img src="https://i.imgur.com/yB2f9Lq.png" alt="Análisis de Estabilidad" width="400"/></td>
  </tr>
  <tr>
    <td align="center"><em>Definición modular y detallada del cohete.</em></td>
    <td align="center"><em>Cálculo en tiempo real de CG, CP y margen estático.</em></td>
  </tr>
  <tr>
    <td><img src="https://i.imgur.com/o7b8sJj.png" alt="Resultados de la Simulación" width="400"/></td>
    <td><img src="https://i.imgur.com/gK9x2cE.png" alt="Animación de Vuelo" width="400"/></td>
  </tr>
  <tr>
    <td align="center"><em>Gráficas completas de los resultados del vuelo.</em></td>
    <td align="center"><em>Animación 3D de la trayectoria y orientación.</em></td>
  </tr>
</table>

---

## ⚙️ Instalación y Ejecución

Para poner en marcha el simulador, sigue estos pasos:

### Requisitos Previos
-   Python 3.9 o superior.
-   Git para clonar el repositorio.

### Pasos
1.  **Clona el repositorio de GitHub:**
    ```bash
    git clone [https://github.com/Meijix/RocketTrajectorySimulator-PropulsionUnam.git](https://github.com/Meijix/RocketTrajectorySimulator-PropulsionUnam.git)
    cd RocketTrajectorySimulator-PropulsionUnam
    ```

2.  **Crea y activa un entorno virtual (recomendado):**
    ```bash
    python -m venv venv
    # En macOS/Linux:
    source venv/bin/activate
    # En Windows:
    .\venv\Scripts\activate
    ```

3.  **Instala las dependencias:**
    El archivo `requirements.txt` contiene todas las librerías necesarias.
    ```bash
    pip install -r requirements.txt
    ```
---

## ▶️ Uso Básico

1.  **Iniciar el Simulador:**
    Ejecuta el siguiente comando desde la **carpeta raíz** del proyecto:
    ```bash
    python -m Simulador.GUI.ModernGUI
    ```

2.  **Definir un Cohete:**
    -   Ve a la pestaña **"🚀 Cohete"**.
    -   Introduce las dimensiones, masas y posiciones de cada componente.
    -   Carga el archivo de la curva de empuje del motor.

3.  **Actualizar y Validar:**
    -   Haz clic en el botón **"🔄 Actualizar Cohete"**.
    -   Ve a la pestaña **"⚖️ Estabilidad"** para verificar que el margen estático sea positivo (idealmente entre 1 y 2 calibres).

4.  **Correr la Simulación:**
    -   Ve a la pestaña **"⚙️ Simulación"** y configura los parámetros del entorno y el integrador numérico.
    -   Haz clic en **"✅ Ejecutar Simulación"**.

5.  **Interpretar los Resultados:**
    -   La aplicación te llevará automáticamente a la pestaña **"📊 Resultados"**, donde verás las gráficas del vuelo.
    -   En la pestaña **"🎬 Animaciones"** podrás visualizar la trayectoria en 3D.

---

## 📁 Estructura del Proyecto

El código está organizado de forma modular para facilitar su mantenimiento y extensión:

-   **/Simulador/GUI/ModernGUI.py**: Archivo principal que contiene la interfaz gráfica de usuario.
-   **/Simulador/src/**: Contiene la lógica principal que orquesta la simulación (`VueloLibre.py`).
-   **/Simulador/Visualizacion/**: Módulos para generar las `Graficas` y `Animaciones`.
-   **/Paquetes/PaqueteFisica/**: Clases que definen el `Cohete`, sus `Componentes`, el `Motor`, la `Atmosfera`, etc.
-   **/Paquetes/PaqueteEDOs/**: Implementación de los integradores numéricos.
-   **/Archivos/**: Contiene datos de entrada, como curvas de empuje (`.csv`) y datos de vuelos reales.
-   **Tesis_UNAM_NataliaMejBau_COMPLETAFINAL.pdf**: El documento de tesis que fundamenta todo el proyecto.

---

## ✅ Validación

Los resultados del simulador han sido rigurosamente validados mediante la comparación con:
1.  **Soluciones Analíticas:** Para casos simplificados (tiro parabólico con arrastre lineal y cuadrático), demostrando la precisión del motor numérico.
2.  **Datos Experimentales:** Se compararon los resultados con los datos de telemetría del vuelo real del cohete **Xitle II** de Propulsión UNAM, obteniendo una correlación excelente (error < 1% en apogeo).
3.  **Software Comercial:** Se contrastaron los resultados con simuladores estándar de la industria como OpenRocket, demostrando una mayor precisión en la predicción de la trayectoria bajo condiciones de viento.

(Ver Capítulo 5 de la [tesis](./Tesis_UNAM_NataliaMejBau_COMPLETAFINAL.pdf) para un análisis detallado de la validación).

---

## ✒️ Créditos y Autoría

Este proyecto es el resultado de mi trabajo de tesis para obtener el título de Matemática por la Facultad de Ciencias de la UNAM.

-   **Autora Principal:** Natalia Edith Mejia Bautista
-   **Asesores de Tesis:** Dra. Ursula X. Iturrarán Viveros, Dr. Juan Claudio Toledo Roy


Un colaboración con el equipo **Propulsión UNAM** por proporcionar los datos experimentales y por ser la principal fuente de inspiración y validación para este proyecto.

---

## 📄 Licencia

Este proyecto se distribuye bajo la **Licencia MIT**. Eres libre de usar, modificar y distribuir este software, siempre y cuando se incluya el aviso de copyright original.

---

## 📈 Posibles Mejoras (Roadmap)

-   [ ] Añadir soporte para cohetes multietapa.
-   [ ] Integrar un módulo de simulación de Monte Carlo para análisis de dispersión.
-   [ ] Desarrollar modelos aerodinámicos más avanzados para motores sólidos y sistemas de control activo (TVC).
-   [ ] Empaquetar el simulador como una aplicación ejecutable independiente.
