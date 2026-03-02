# Investigación: Conversión a 6-DOF con Cuaterniones

## Simulador de Trayectoria de Cohetes — Propulsión UNAM

**Fecha:** 2026-03-02
**Objetivo:** Documentar toda la teoría, ecuaciones y plan de implementación para convertir el simulador actual de 3-DOF a 6-DOF completo usando cuaterniones.

---

## Índice

1. [Estado actual del simulador (3-DOF)](#1-estado-actual-del-simulador-3-dof)
2. [Teoría de cuaterniones](#2-teoría-de-cuaterniones)
3. [Ecuaciones de movimiento 6-DOF](#3-ecuaciones-de-movimiento-6-dof)
4. [Tensor de inercia 3×3](#4-tensor-de-inercia-3×3)
5. [Aerodinámica en 6-DOF](#5-aerodinámica-en-6-dof)
6. [Coeficientes de amortiguamiento](#6-coeficientes-de-amortiguamiento)
7. [Marcos de referencia y convenciones](#7-marcos-de-referencia-y-convenciones)
8. [Fenómenos físicos adicionales en 6-DOF](#8-fenómenos-físicos-adicionales-en-6-dof)
9. [Integración numérica con cuaterniones](#9-integración-numérica-con-cuaterniones)
10. [Mapeo detallado: cambios por archivo](#10-mapeo-detallado-cambios-por-archivo)
11. [Plan de implementación](#11-plan-de-implementación)
12. [Validación y pruebas](#12-validación-y-pruebas)
13. [Referencias](#13-referencias)

---

## 1. Estado actual del simulador (3-DOF)

### 1.1 Vector de estado actual (8 variables)

```
state = [x, y, z, vx, vy, vz, θ, ω]
```

| Índice | Variable | Descripción | Unidades |
|--------|----------|-------------|----------|
| 0-2 | x, y, z | Posición en marco terrestre | m |
| 3-5 | vx, vy, vz | Velocidad en marco terrestre | m/s |
| 6 | θ (theta) | Ángulo de cabeceo (pitch) | rad |
| 7 | ω (omega) | Velocidad angular de cabeceo | rad/s |

### 1.2 Ecuaciones actuales (vuelo.py)

**Traslación** (marco terrestre):
```
dx/dt = vx
dy/dt = vy
dz/dt = vz

dvx/dt = (Tx + Dx + Nx) / m
dvy/dt = (Ty + Dy + Ny) / m
dvz/dt = (Tz + Dz + Nz) / m - g(z)
```

**Rotación** (solo cabeceo):
```
dθ/dt = ω
dω/dt = τ_y / I_x
```

Donde `τ_y = -(palanca × D + palanca × N)_y` con `palanca = R(θ) · (CP - CG)`

### 1.3 Limitaciones del modelo actual

| Aspecto | Estado actual | Necesario para 6-DOF |
|---------|--------------|---------------------|
| Rotación | Solo pitch (θ) | Pitch, yaw, roll (3 ejes) |
| Momento de inercia | Escalar I_x | Tensor 3×3 [Ixx, Iyy, Izz] |
| Representación orientación | Ángulo θ | Cuaternión q = [q0, q1, q2, q3] |
| Fuerza normal | 1 componente (plano xz) | 2 componentes (pitch + yaw) |
| Momentos | Solo cabeceo τ_y | Cabeceo, guiñada, alabeo |
| Ángulo de ataque | α = θ - γ (2D) | α total en 3D + sideslip β |
| Amortiguamiento | Ninguno | Cmq, Cnr, Clp |
| Efecto Magnus | No | Sí (para cohetes con spin) |
| Empuje | Alineado con θ | Alineado con eje del cuerpo vía q |

---

## 2. Teoría de cuaterniones

### 2.1 Definición

Un cuaternión unitario q representa una rotación del marco del cuerpo respecto al marco terrestre:

```
q = q0 + q1·i + q2·j + q3·k = [q0, q1, q2, q3]
```

Donde:
- `q0` = parte escalar (coseno del medio ángulo)
- `q1, q2, q3` = parte vectorial (eje de rotación × seno del medio ángulo)
- **Restricción:** `|q|² = q0² + q1² + q2² + q3² = 1`

**Convención adoptada:** Hamilton (usada por RocketPy, SciPy, NASA)
- `q = [q0, q1, q2, q3]` donde q0 es escalar
- Rotación activa: transforma vectores del marco cuerpo al marco terrestre

### 2.2 ¿Por qué cuaterniones y no ángulos de Euler?

| Propiedad | Ángulos de Euler | Cuaterniones |
|-----------|-----------------|--------------|
| Variables | 3 (φ, θ, ψ) | 4 (q0, q1, q2, q3) |
| Gimbal lock | Sí (θ = ±90°) | No |
| Singularidades | Sí | No |
| Costo computacional ODE | Mayor (funciones trigonométricas) | Menor (productos bilineales) |
| Estabilidad numérica | Pobre para rotaciones grandes | Excelente |
| Normalización | Implícita | Explícita (simple: q/|q|) |
| Interpolación | No trivial | SLERP natural |

**Para cohetes suborbitales es crítico:** El ángulo de pitch θ pasa por ~87° durante el vuelo (lanzamiento casi vertical), peligrosamente cerca del gimbal lock en Euler.

### 2.3 Cuaternión a Matriz de Rotación (DCM)

La matriz de cosenos directores R(q) que transforma vectores del **marco cuerpo al marco terrestre**:

```
        ⎡ 1-2(q2²+q3²)    2(q1q2-q0q3)    2(q1q3+q0q2) ⎤
R(q) =  ⎢ 2(q1q2+q0q3)    1-2(q1²+q3²)    2(q2q3-q0q1) ⎥
        ⎣ 2(q1q3-q0q2)    2(q2q3+q0q1)    1-2(q1²+q2²) ⎦
```

En código Python:
```python
def quaternion_to_dcm(q):
    q0, q1, q2, q3 = q
    return np.array([
        [1 - 2*(q2**2 + q3**2),  2*(q1*q2 - q0*q3),      2*(q1*q3 + q0*q2)],
        [2*(q1*q2 + q0*q3),      1 - 2*(q1**2 + q3**2),   2*(q2*q3 - q0*q1)],
        [2*(q1*q3 - q0*q2),      2*(q2*q3 + q0*q1),       1 - 2*(q1**2 + q2**2)]
    ])
```

**Transformación inversa** (terrestre → cuerpo): `R(q)^T = R(q)^(-1)` (ortogonal)

### 2.4 Ecuación diferencial del cuaternión

La cinemática del cuaternión se describe por:

```
dq/dt = ½ · Ω(ω) · q
```

Donde ω = [p, q, r] es el vector de velocidad angular en **coordenadas del cuerpo** y Ω es la matriz antisimétrica:

```
         ⎡  0   -p   -q   -r ⎤   ⎡ q0 ⎤
dq/dt =  ⎢  p    0    r   -q ⎥ · ⎢ q1 ⎥  ·  ½
         ⎢  q   -r    0    p ⎥   ⎢ q2 ⎥
         ⎣  r    q   -p    0 ⎦   ⎣ q3 ⎦
```

Expandido:
```
dq0/dt = -½ (p·q1 + q·q2 + r·q3)
dq1/dt =  ½ (p·q0 + r·q2 - q·q3)
dq2/dt =  ½ (q·q0 - r·q1 + p·q3)
dq3/dt =  ½ (r·q0 + q·q1 - p·q2)
```

En código Python:
```python
def quaternion_derivative(q, omega):
    q0, q1, q2, q3 = q
    p, qw, r = omega  # nota: qw para evitar conflicto con q del cuaternión

    dq0 = 0.5 * (-p*q1 - qw*q2 - r*q3)
    dq1 = 0.5 * ( p*q0 + r*q2 - qw*q3)
    dq2 = 0.5 * ( qw*q0 - r*q1 + p*q3)
    dq3 = 0.5 * ( r*q0 + qw*q1 - p*q2)

    return np.array([dq0, dq1, dq2, dq3])
```

### 2.5 Ángulos de Euler desde cuaternión (para visualización)

Secuencia ZYX (yaw → pitch → roll):
```
φ (roll)  = atan2(2(q0q1 + q2q3), 1 - 2(q1² + q2²))
θ (pitch) = arcsin(2(q0q2 - q3q1))
ψ (yaw)   = atan2(2(q0q3 + q1q2), 1 - 2(q2² + q3²))
```

### 2.6 Cuaternión desde ángulos de Euler (para inicialización)

```python
def euler_to_quaternion(phi, theta, psi):
    """Convierte ángulos de Euler (roll, pitch, yaw) a cuaternión."""
    cp, sp = np.cos(phi/2), np.sin(phi/2)
    ct, st = np.cos(theta/2), np.sin(theta/2)
    cy, sy = np.cos(psi/2), np.sin(psi/2)

    q0 = cp*ct*cy + sp*st*sy
    q1 = sp*ct*cy - cp*st*sy
    q2 = cp*st*cy + sp*ct*sy
    q3 = cp*ct*sy - sp*st*cy

    return np.array([q0, q1, q2, q3])
```

---

## 3. Ecuaciones de movimiento 6-DOF

### 3.1 Vector de estado completo (13 variables)

```
state = [x, y, z, vx, vy, vz, q0, q1, q2, q3, p, q, r]
         ─────────  ────────────  ──────────────  ────────
         posición   velocidad     cuaternión      vel. angular
         (tierra)   (tierra)      (tierra→cuerpo) (cuerpo)
```

| Índice | Variable | Descripción | Unidades |
|--------|----------|-------------|----------|
| 0-2 | x, y, z | Posición en marco terrestre (ENU) | m |
| 3-5 | vx, vy, vz | Velocidad en marco terrestre | m/s |
| 6-9 | q0, q1, q2, q3 | Cuaternión de orientación | adimensional |
| 10-12 | p, q, r | Velocidad angular en cuerpo (roll, pitch, yaw) | rad/s |

**Total: 13 estados** (vs. 8 en 3-DOF)

### 3.2 Ecuaciones traslacionales (marco terrestre)

```
dx/dt = vx
dy/dt = vy
dz/dt = vz

⎡ dvx/dt ⎤         ⎡ F_xb ⎤   ⎡  0 ⎤
⎢ dvy/dt ⎥ = R(q)· ⎢ F_yb ⎥ + ⎢  0 ⎥
⎣ dvz/dt ⎦    ___  ⎣ F_zb ⎦   ⎣ -g ⎦
               m
```

Donde:
- `R(q)` = DCM del cuaternión (cuerpo → tierra)
- `F_xb, F_yb, F_zb` = fuerzas totales en marco del cuerpo (empuje + aerodinámicas)
- `g` = gravedad dependiente de altitud
- `m` = masa total (variable con el tiempo)

**En código:**
```python
# Fuerzas en marco cuerpo
F_body = F_thrust_body + F_aero_body  # [Fx_b, Fy_b, Fz_b]

# Transformar a marco terrestre
R = quaternion_to_dcm(q)
F_earth = R @ F_body

# Aceleración en marco terrestre
a_earth = F_earth / m + np.array([0, 0, -g])
```

### 3.3 Ecuaciones rotacionales (Ecuaciones de Euler — marco del cuerpo)

```
I · dω/dt = M - ω × (I · ω)
```

Expandido para cohete axialmente simétrico (Ixx = Iyy ≠ Izz):

```
Ixx · dp/dt = M_x - (Izz - Iyy) · q · r  =  M_x + (Iyy - Izz) · q · r
Iyy · dq/dt = M_y - (Ixx - Izz) · r · p  =  M_y + (Izz - Ixx) · r · p
Izz · dr/dt = M_z - (Iyy - Ixx) · p · q  =  M_z + (Ixx - Iyy) · p · q
```

Para cohete cilíndrico simétrico donde `Ixx = Iyy`:

```
dp/dt = [M_x + (Ixx - Izz) · q · r] / Ixx
dq/dt = [M_y + (Izz - Ixx) · r · p] / Iyy     (= Ixx)
dr/dt = M_z / Izz                                (porque Ixx = Iyy, término cruzado = 0)
```

Donde:
- `p` = velocidad angular de alabeo (roll, en torno al eje x del cuerpo = eje longitudinal)
- `q` = velocidad angular de cabeceo (pitch, en torno al eje y del cuerpo)
- `r` = velocidad angular de guiñada (yaw, en torno al eje z del cuerpo)
- `M_x, M_y, M_z` = momentos totales en marco del cuerpo
- `Ixx, Iyy, Izz` = momentos principales de inercia

**Nota importante:** Los términos `ω × (I·ω)` son los **términos giroscópicos** que acoplan las rotaciones entre ejes. Son cero solo si el cohete no rota.

### 3.4 Ecuaciones cinemáticas del cuaternión

```
dq0/dt = -½ (p·q1 + q·q2 + r·q3)
dq1/dt =  ½ (p·q0 + r·q2 - q·q3)
dq2/dt =  ½ (q·q0 - r·q1 + p·q3)
dq3/dt =  ½ (r·q0 + q·q1 - p·q2)
```

### 3.5 Sistema completo de ODEs (13 ecuaciones)

```python
def fun_derivs_6dof(t, state):
    # Desempaquetar estado
    pos = state[0:3]    # [x, y, z] en tierra
    vel = state[3:6]    # [vx, vy, vz] en tierra
    q = state[6:10]     # [q0, q1, q2, q3] cuaternión
    omega = state[10:13] # [p, q, r] en cuerpo

    p, qw, r = omega

    # 1. Normalizar cuaternión (protección numérica)
    q = q / np.linalg.norm(q)

    # 2. Matrices de rotación
    R_body_to_earth = quaternion_to_dcm(q)
    R_earth_to_body = R_body_to_earth.T

    # 3. Velocidad relativa al viento en marco cuerpo
    v_wind_earth = viento.vector
    v_rel_earth = vel - v_wind_earth
    v_rel_body = R_earth_to_body @ v_rel_earth

    # 4. Ángulos aerodinámicos
    u, v, w = v_rel_body  # componentes en cuerpo
    V = np.linalg.norm(v_rel_body)
    alpha = np.arctan2(w, u)         # ángulo de ataque
    beta = np.arctan2(v, np.sqrt(u**2 + w**2))  # sideslip

    # 5. Fuerzas aerodinámicas en marco cuerpo
    F_aero_body = calc_fuerzas_aero_6dof(pos, v_rel_body, alpha, beta, V)

    # 6. Momentos aerodinámicos en marco cuerpo
    M_aero_body = calc_momentos_aero_6dof(v_rel_body, alpha, beta, V, omega)

    # 7. Empuje en marco cuerpo (a lo largo del eje x del cuerpo)
    T_mag = vehiculo.calc_empuje_magn(t)
    F_thrust_body = np.array([T_mag, 0, 0])

    # 8. Fuerza total en cuerpo
    F_body = F_aero_body + F_thrust_body

    # 9. Traslación (en tierra)
    g = calc_gravedad(pos[2])
    a_earth = R_body_to_earth @ F_body / m + np.array([0, 0, -g])

    # 10. Rotación (ecuaciones de Euler, en cuerpo)
    I = vehiculo.inertia_tensor  # [Ixx, Iyy, Izz]
    Ixx, Iyy, Izz = I
    M_total = M_aero_body  # + otros momentos

    dp_dt = (M_total[0] - (Izz - Iyy) * qw * r) / Ixx
    dq_dt = (M_total[1] - (Ixx - Izz) * r * p) / Iyy
    dr_dt = (M_total[2] - (Iyy - Ixx) * p * qw) / Izz

    # 11. Cinemática del cuaternión
    dq_quat = quaternion_derivative(q, omega)

    # 12. Ensamblar derivadas
    derivs = np.concatenate([
        vel,          # dx/dt = v (3)
        a_earth,      # dv/dt = a (3)
        dq_quat,      # dq/dt (4)
        [dp_dt, dq_dt, dr_dt]  # dω/dt (3)
    ])

    return derivs  # 13 derivadas
```

---

## 4. Tensor de inercia 3×3

### 4.1 Definición general

```
        ⎡ Ixx  -Ixy  -Ixz ⎤
I   =   ⎢-Ixy   Iyy  -Iyz ⎥
        ⎣-Ixz  -Iyz   Izz ⎦
```

### 4.2 Simplificación para cohete axialmente simétrico

Para un cohete con simetría axial (cuerpo de revolución), con el eje x apuntando hacia la nariz:

```
        ⎡ Izz_long   0         0      ⎤
I   =   ⎢ 0          Ixx_lat   0      ⎥
        ⎣ 0          0         Ixx_lat ⎦
```

Donde:
- **I_longitudinal (Izz del cuerpo)** = momento de inercia en torno al eje del cohete (el menor)
- **I_lateral (Ixx = Iyy del cuerpo)** = momento de inercia en torno a un eje perpendicular (el mayor)

**IMPORTANTE — Convención de ejes:**

En nuestro código actual, el eje **z apunta hacia la cola** y el `Ix` que calculamos es realmente el momento lateral. Para 6-DOF con la convención estándar de **x hacia la nariz**:

| Actual (3-DOF) | 6-DOF (x → nariz) | Descripción |
|-----------------|-------------------|-------------|
| `cohete.Ix` | `Iyy = Izz` | Momento lateral (pitch/yaw) |
| No calculado | `Ixx` | Momento longitudinal (roll) |

### 4.3 Cálculo del momento de inercia longitudinal (roll)

Para cada componente, necesitamos calcular `Ixx_roll` (momento en torno al eje longitudinal).

**Cono (nariz):**
```
Ixx_roll = (3/10) · m · r²
```

**Cilindro hueco:**
```
Ixx_roll = ½ · m · (r_ext² + r_int²)
```

**Aletas (4 aletas planas uniformes):**
```
Ixx_roll_una = (1/12) · m_una · span²  +  m_una · (r_fus + span/2)²
Ixx_roll_total = n_fins · Ixx_roll_una
```

Donde se usa el teorema de ejes paralelos para trasladar desde el CG de la aleta al eje del cohete.

**Boattail (cono truncado):**
```
Ixx_roll = (3/10) · m · (rF⁵ - rR⁵) / (rF³ - rR³)
```

### 4.4 Cálculo para componentes combinados (teorema de ejes paralelos 3D)

Para cada componente con inercia local `I_comp` centrada en su CG local, y cuyo CG está a distancia `d` del CG total del cohete:

```
I_total = Σ [I_comp_CG + m_comp · (|d|²·E - d⊗d)]
```

Donde `E` es la matriz identidad 3×3 y `d⊗d` es el producto exterior.

Para **eje axial** (roll), la distancia relevante es la distancia **radial** del CG del componente al eje del cohete (que para componentes centrados es 0):

```
Ixx_total = Σ Ixx_comp_i
```

Para **ejes laterales** (pitch/yaw), la distancia relevante es a lo largo del eje longitudinal:

```
Iyy_total = Σ [Iyy_comp_i + m_i · (z_CG_i - z_CG_total)²]
Izz_total = Iyy_total  (por simetría axial)
```

### 4.5 Variación temporal

El tensor de inercia cambia con el tiempo debido al consumo de propulsante:

```python
def actualizar_inercia(self, t):
    self.actualizar_masas_motor(t)
    self.calc_masa()
    self.calc_CG()
    self.calc_inertia_tensor()  # NUEVO: calcula Ixx, Iyy, Izz
```

---

## 5. Aerodinámica en 6-DOF

### 5.1 Velocidad relativa al viento en marco cuerpo

```python
v_rel_earth = v_rocket_earth - v_wind_earth
v_rel_body = R^T(q) · v_rel_earth
u, v, w = v_rel_body  # [axial, lateral_y, lateral_z]
```

### 5.2 Ángulos aerodinámicos en 3D

**Ángulo de ataque (pitch plane):**
```
α = atan2(w, u)
```

**Ángulo de deslizamiento lateral (sideslip):**
```
β = atan2(v, √(u² + w²))
```

**Ángulo de ataque total:**
```
α_total = arccos(u / V)  =  arctan(√(v² + w²) / u)
```

Donde `V = |v_rel_body| = √(u² + v² + w²)`

**Comparación con el modelo actual:**
```
ACTUAL:  α = θ - atan2(v_rel_z, v_rel_x)  → solo en plano XZ
6-DOF:   α y β independientes en 3D
```

### 5.3 Fuerzas aerodinámicas en marco cuerpo

**Fuerza axial (drag):**
```
F_A = -½ · ρ · V² · A_ref · C_A · x̂_body
```

Donde `C_A ≈ C_D` (coeficiente de arrastre axial, función del Mach)

**Fuerza normal (en plano de α):**
```
F_N_α = -½ · ρ · V² · A_ref · C_Nα · α
```

**Fuerza lateral (en plano de β):**
```
F_Y_β = -½ · ρ · V² · A_ref · C_Nα · β
```

**Nota:** Para un cuerpo axialmente simétrico, `C_Yβ = C_Nα` (el mismo coeficiente de fuerza normal aplica en cualquier plano que contenga el eje).

**Vector de fuerza aerodinámica total en cuerpo:**
```python
def calc_fuerzas_aero_6dof(pos, v_rel_body, alpha, beta, V):
    u, v, w = v_rel_body
    rho = atmosfera.calc_propiedades(pos[2])[1]
    mach = V / atmosfera.calc_propiedades(pos[2])[3]

    q_dyn = 0.5 * rho * V**2  # presión dinámica
    CA = vehiculo.calc_Cd(mach)  # coef. de arrastre axial
    CNa = vehiculo.CN           # coef. de fuerza normal (por radián)
    A = vehiculo.A              # área de referencia

    # Fuerza axial (opuesta a la dirección de vuelo en cuerpo)
    F_axial = -q_dyn * A * CA

    # Fuerza normal (plano pitch, proporcional a α)
    F_normal_z = -q_dyn * A * CNa * alpha

    # Fuerza lateral (plano yaw, proporcional a β)
    F_lateral_y = -q_dyn * A * CNa * beta

    return np.array([F_axial, F_lateral_y, F_normal_z])
```

### 5.4 Momentos aerodinámicos en marco cuerpo

Los momentos se calculan respecto al CG del cohete:

**Momento de cabeceo (pitch, en torno a eje y del cuerpo):**
```
M_y = q_dyn · A · d_ref · [C_mα · α + C_mq · (q · d_ref)/(2V)]
```

**Momento de guiñada (yaw, en torno a eje z del cuerpo):**
```
M_z = q_dyn · A · d_ref · [C_nβ · β + C_nr · (r · d_ref)/(2V)]
```

**Momento de alabeo (roll, en torno a eje x del cuerpo):**
```
M_x = q_dyn · A · d_ref · [C_lδ + C_lp · (p · d_ref)/(2V)]
```

Donde:
- `d_ref` = diámetro de referencia (o longitud de referencia L_ref)
- `C_mα` = derivada del momento de cabeceo respecto a α (estática)
- `C_mq` = derivada de amortiguamiento de cabeceo
- `C_nβ` = derivada del momento de guiñada respecto a β
- `C_nr` = derivada de amortiguamiento de guiñada
- `C_lp` = derivada de amortiguamiento de alabeo
- `C_lδ` = momento de alabeo por desalineación de aletas (normalmente ≈ 0)

**Para cohete axialmente simétrico:** `C_nβ = -C_mα` y `C_nr = C_mq`

### 5.5 Derivada estática de estabilidad C_mα

```
C_mα = C_Nα · (x_CP - x_CG) / d_ref
```

Donde `(x_CP - x_CG)` es el **margen estático** (positivo = estable, CP detrás de CG).

**Esto es equivalente** a lo que hace el código actual con el brazo de palanca `palanca = CP - CG`, pero ahora expresado como un coeficiente adimensional.

```python
def calc_Cma(self):
    """Calcula la derivada estática de estabilidad."""
    # margen_estatico > 0 → estable
    margen_estatico = self.CP[2] - self.CG[2]  # en metros (eje z del cuerpo)
    self.Cma = self.CN * margen_estatico / self.d_ref
```

---

## 6. Coeficientes de amortiguamiento

### 6.1 Amortiguamiento de cabeceo C_mq

El coeficiente de amortiguamiento de cabeceo es crucial para la estabilidad dinámica. Para un cohete, contribuyen:

**Contribución de las aletas (Barrowman extendido):**
```
C_mq_fins = -2 · C_Nα_fins · [(x_fins - x_CG) / d_ref]²
```

**Contribución del cuerpo:**
```
C_mq_body = -2 · C_Nα_body · [(x_CP_body - x_CG) / d_ref]²
```

**Total:**
```
C_mq = C_mq_fins + C_mq_body
```

**Regla empírica** (si no se tienen datos precisos):
```
C_mq ≈ -2 · C_Nα · (margen_estático / d_ref)²
```

Típicamente `C_mq` es negativo (amortiguación estabilizadora) con valores entre -10 y -100 para cohetes bien diseñados.

### 6.2 Amortiguamiento de alabeo C_lp

```
C_lp = -(C_Nα_fin / n_fins) · n_fins · (r_fus + ⅔·span)² · 4 / (A_ref · d_ref)
```

Aproximación simplificada:
```
C_lp ≈ -C_Nα_fins · (2/3 · span + r_fus)² / (A_ref · d_ref / 4)
```

`C_lp` es siempre negativo (amortigua el spin).

### 6.3 Amortiguamiento de guiñada C_nr

Para cohete axialmente simétrico:
```
C_nr = C_mq  (idéntico al amortiguamiento de cabeceo)
```

### 6.4 Jet damping (amortiguamiento por chorro de motor)

Cuando el motor está activo, el chorro de gases produce un efecto estabilizador adicional:

```
M_jet = -ṁ · (x_nozzle - x_CG)² · ω_lateral
```

Donde:
- `ṁ` = tasa de gasto másico (derivada negativa de la masa)
- `x_nozzle` = posición de la tobera
- `ω_lateral` = componente lateral de la velocidad angular

Este efecto es significativo durante la fase de motor encendido y se puede incluir como un amortiguamiento adicional.

---

## 7. Marcos de referencia y convenciones

### 7.1 Marco terrestre (ENU — East-North-Up)

Adoptamos ENU para consistencia con el código actual:

```
x → Este
y → Norte
z → Arriba (Up)
```

**Origen:** Punto de lanzamiento.

### 7.2 Marco del cuerpo (convención estándar de cohetes)

```
x_body → Hacia la nariz (eje longitudinal del cohete)
y_body → A estribor (starboard)
z_body → "Abajo" respecto al cohete (completa mano derecha)
```

**CAMBIO RESPECTO AL CÓDIGO ACTUAL:**

En el código actual, el eje z del cuerpo apunta desde la nariz hacia la cola. En la convención estándar 6-DOF, el eje x del cuerpo apunta hacia la nariz. Esto requiere un remapeo:

```
ACTUAL:           6-DOF:
z_body → cola     x_body → nariz (eje longitudinal, invertido)
x_body → lateral  y_body → lateral
y_body → lateral  z_body → lateral
```

### 7.3 Conversión de velocidades entre marcos

```python
# Tierra → Cuerpo
v_body = R(q)^T · v_earth

# Cuerpo → Tierra
v_earth = R(q) · v_body
```

### 7.4 Comparación de convenciones entre simuladores

| Aspecto | Nuestro simulador | RocketPy | OpenRocket | Cambridge |
|---------|-------------------|----------|------------|-----------|
| Marco tierra | ENU | Inercial (A) | NED | NED |
| Eje cuerpo longitudinal | z → cola | b3 → nariz | x → nariz | z → nariz |
| Vector estado | [pos, vel, θ, ω] | [pos, vel, quat, ω] | [pos, vel, euler, ω] | [pos, quat, P, L] |
| Rotaciones | Solo pitch | quat (Hamilton) | Euler | quat |
| Masa variable | Sí (interpol.) | Sí (Kane/Reynolds) | Sí | Sí (momento) |
| Aerodinámica | Bulk CN | Por superficie | Bulk CN | Bulk CN |
| Integrador | RK4/solve_ivp | LSODA (default) | RK4 fijo | RKF45 |

**Decisión de diseño para nuestro simulador:**
- Mantenemos **ENU** (compatible con el código actual)
- Cambiamos eje longitudinal a **x → nariz** (estándar aerodinámico)
- Usamos **cuaterniones Hamilton** [q0, q1, q2, q3]
- Mantenemos aerodinámica **bulk** con coeficientes de amortiguamiento

### 7.5 Estado inicial para lanzamiento

Para un cohete en el riel con ángulo `θ_riel` desde la vertical:

```python
# Orientación inicial: cohete inclinado θ_riel grados desde vertical
# En ENU: el eje x del cuerpo apunta hacia arriba/al horizonte
phi_0 = 0                          # sin roll
theta_0 = np.deg2rad(angulo_riel)  # pitch = ángulo del riel
psi_0 = np.deg2rad(azimut_riel)    # yaw = dirección del riel

q_init = euler_to_quaternion(phi_0, theta_0, psi_0)

# Estado inicial completo
state_0 = np.array([
    0, 0, 0,           # posición [x,y,z]
    0, 0, 0,           # velocidad [vx,vy,vz]
    *q_init,           # cuaternión [q0,q1,q2,q3]
    0, 0, 0            # vel. angular [p,q,r]
])
```

---

## 8. Fenómenos físicos adicionales en 6-DOF

### 8.1 Weathercocking (efecto veleta)

Es el fenómeno donde el viento lateral causa un momento restaurador que alinea el cohete con la dirección del viento relativo. Ya está **implícito** en las ecuaciones de momento cuando se usa la velocidad relativa al viento para calcular α y β.

### 8.2 Roll coupling (acoplamiento de alabeo)

Cuando un cohete con spin tiene algún ángulo de ataque, el spin causa un acoplamiento entre los planos de cabeceo y guiñada. Esto aparece naturalmente en los **términos cruzados** de las ecuaciones de Euler:

```
dp/dt incluye término (Iyy - Izz)·q·r
dq/dt incluye término (Izz - Ixx)·r·p  ← este es el acoplamiento roll-pitch
dr/dt incluye término (Ixx - Iyy)·p·q  ← y este roll-yaw
```

Para cohetes con alta tasa de spin y bajo margen estático, esto puede causar **inestabilidad dinámica** — un fenómeno que el simulador 3-DOF no puede capturar.

### 8.3 Desalineación de empuje

Si el vector de empuje no pasa exactamente por el CG:

```python
# Offset del empuje respecto al eje
thrust_offset = np.array([0, dy_thrust, dz_thrust])  # en cuerpo

# Momento por desalineación
M_thrust = np.cross(thrust_offset, F_thrust_body)
```

Para simulaciones normales se asume `offset = 0`, pero se puede parametrizar.

### 8.4 Efecto Magnus

Para cohetes con spin, el flujo cruzado genera una fuerza lateral (efecto Magnus):

```
C_Y_Magnus = C_Nα_Magnus · p · d_ref / (2V) · β
F_Magnus = q_dyn · A · C_Y_Magnus
```

Este efecto es generalmente pequeño para cohetes suborbitales con bajo spin, pero se puede incluir como mejora futura.

### 8.5 Efectos de Coriolis y centrípetos

Para vuelos que alcanzan altitudes > 10 km o distancias laterales > 5 km, se debe considerar la rotación terrestre:

```
a_Coriolis = -2 · Ω_tierra × v
a_centripeta = -Ω_tierra × (Ω_tierra × r)
```

Donde `Ω_tierra = [0, Ω·cos(lat), Ω·sin(lat)]` en marco NED con Ω = 7.2921×10⁻⁵ rad/s.

**Para el Xitle II (~5-15 km altitud):** Estos efectos son del orden de 0.1% y pueden ignorarse en primera aproximación, pero es fácil incluirlos.

### 8.6 Enfoque de RocketPy: ángulo de ataque local por superficie

RocketPy calcula las fuerzas aerodinámicas **por superficie** en lugar de usar coeficientes bulk. Cada superficie experimenta su propia velocidad local que incluye el efecto de la rotación:

```
v_i = v_freestream + ω × r_i
```

Donde `r_i` es el vector del CG a la i-ésima superficie. Esto produce **amortiguamiento natural**: superficies lejanas al CG (aletas) ven una mayor perturbación en α local debido a ω, generando momentos restauradores automáticos.

**Ventaja:** Es más preciso que aplicar un coeficiente de amortiguamiento bulk (C_mq).

**Para nuestra implementación:** Como primera versión, usaremos coeficientes bulk (C_mq, C_lp, C_nr) que son más simples. La mejora a ángulo de ataque local por superficie se puede implementar como refinamiento futuro.

### 8.7 Amortiguamiento de cabeceo de OpenRocket

**Contribución del cuerpo:**
```
C_damp_body = 0.55 · (l⁴ · r_t) / (A_ref · d) · (ω² / V²)
```

**Contribución de aletas:**
```
C_damp_fin = 0.6 · N · A_fin · ξ³ / (A_ref · d) · (ω² / V²)
```

Donde `ξ` es la distancia del CG a las aletas, N = número de aletas (máx. 4 para cálculo).

### 8.8 Momento de roll por aletas inclinadas (canted fins)

De Barrowman ecuación (3-31):
```
M_roll = N · (Y_MA + r_t) · C_Nα_1fin · δ · q_dyn · A_ref
```

Donde `δ` = ángulo de cant de las aletas (normalmente 0° para cohetes sin spin inducido).

**Amortiguamiento de roll para aletas trapezoidales:**
```
C_lp = (2·N·C_Nα_1fin) / (A_ref · L_ref²) · cos(δ) · ∫c(ξ)·ξ²·dξ
```

Con la integral evaluada para geometría trapezoidal:
```
∫ = (s/12) · [(C_r + 3C_t)s² + 4(C_r + 2C_t)s·r_t + 6(C_r + C_t)r_t²]
```

---

## 9. Integración numérica con cuaterniones

### 9.1 Normalización del cuaternión

Después de cada paso de integración, el cuaternión debe renormalizarse:

```python
q = q / np.linalg.norm(q)
```

**¿Por qué?** Los errores de truncamiento numérico hacen que `|q|` se desvíe lentamente de 1. Si no se normaliza, la DCM pierde ortogonalidad y la simulación diverge.

**¿Con qué frecuencia?** Después de **cada paso** del integrador.

### 9.2 Método de normalización dentro del integrador

**Opción A — Post-step normalización (recomendada por simplicidad):**
```python
state_new = integrator.step(t, state, dt)
state_new[6:10] /= np.linalg.norm(state_new[6:10])
```

**Opción B — Baumgarte stabilization (más elegante):**

Agregar un término de penalización a las derivadas del cuaternión:

```
dq/dt = ½ · Ω · q + λ · (1 - |q|²) · q
```

Con λ ≈ 1/dt. Esto fuerza al cuaternión hacia la esfera unitaria sin normalización explícita.

**Recomendación:** Usar Opción A por ser más simple y robusta.

### 9.3 Integradores recomendados

| Integrador | Orden | Adaptativo | Recomendación |
|------------|-------|-----------|---------------|
| RK4 | 4 | No | Bueno para inicio, dt = 0.001-0.01 |
| RK45 (Dormand-Prince) | 4/5 | Sí | **Mejor opción general** |
| DOP853 | 8 | Sí | Excelente precisión, más lento |
| LSODA | Variable | Sí | Bueno para sistemas stiff |

**Para 6-DOF de cohetes:** RK45 adaptativo con tolerancia 1e-8 a 1e-10 es lo estándar.

**Paso de tiempo típico:** 0.001 - 0.01 s durante el vuelo con motor; 0.01 - 0.1 s en fase balística.

### 9.4 Consideración de rigidez (stiffness)

Las ecuaciones 6-DOF de cohetes **no son típicamente stiff** para vuelo libre. Sin embargo, pueden volverse stiff cuando:
- El cohete está en el riel (constraint)
- La fase de paracaídas con despliegue abrupto
- Momentos de amortiguamiento muy grandes

En estos casos, LSODA (que alterna entre stiff y non-stiff) es una buena opción.

---

## 10. Mapeo detallado: cambios por archivo

### 10.1 `vuelo.py` — CAMBIOS MAYORES

| Sección | Cambio | Prioridad |
|---------|--------|-----------|
| `__init__` | Agregar modo `'6dof'` vs `'3dof'` | Alta |
| `fun_derivs` | Nuevo `fun_derivs_6dof()` con 13 estados | **Crítica** |
| `calc_empuje` | Empuje en marco cuerpo via cuaternión | Alta |
| `calc_aero` | Nuevo `calc_fuerzas_aero_6dof()` con α, β en 3D | **Crítica** |
| `calc_arrastre_normal` | Refactorizar para fuerzas en cuerpo | Alta |
| `accangular` | Reemplazar con `calc_momentos_6dof()` | **Crítica** |
| `calc_alpha` | Nuevo `calc_aero_angles()` con α, β, α_total | Alta |
| `simular_vuelo` | Normalización de q post-step, 13 estados | Alta |
| Output | Agregar roll, yaw, q-rates a salida | Media |

**Líneas afectadas estimadas:** ~70% del archivo (300+ líneas de 430)

### 10.2 `cohete.py` — CAMBIOS MODERADOS

| Sección | Cambio | Prioridad |
|---------|--------|-----------|
| `__init__` | Agregar `Ixx_roll`, `Iyy`, `Izz`, `d_ref` | Alta |
| `calc_mom_inercia_total` | Calcular tensor completo [Ixx, Iyy, Izz] | **Crítica** |
| Nuevo | `calc_Cma()` derivada de estabilidad | Alta |
| Nuevo | `calc_Cmq()` amortiguamiento de cabeceo | Alta |
| Nuevo | `calc_Clp()` amortiguamiento de roll | Media |
| `actualizar_masa` | También actualizar tensor de inercia | Alta |
| `calc_A` | Calcular `d_ref` además de `A` | Media |

**Líneas nuevas estimadas:** ~80 líneas

### 10.3 `componentes.py` — CAMBIOS MENORES-MODERADOS

| Sección | Cambio | Prioridad |
|---------|--------|-----------|
| `Componente` base | Agregar `Ix_roll` (momento de inercia axial) | Alta |
| `Cono.calc_Ix` | Agregar `calc_Ix_roll()` = 3/10 · m · r² | Alta |
| `Cilindro.calc_Ix` | Agregar `calc_Ix_roll()` = ½·m·(re²+ri²) | Alta |
| `Aletas.calc_Ix` | Agregar `calc_Ix_roll()` con ejes paralelos | Alta |
| `Boattail.calc_Ix` | Agregar `calc_Ix_roll()` para cono truncado | Alta |
| `Aletas` | Agregar `calc_Clp_contribution()` | Media |

**Líneas nuevas estimadas:** ~40 líneas

### 10.4 `condiciones_init.py` — CAMBIOS MENORES

| Sección | Cambio | Prioridad |
|---------|--------|-----------|
| Estado inicial | 13 estados con cuaternión inicial | Alta |
| Nuevo | Azimut del riel como parámetro | Media |
| Nuevo | Flag `modo_6dof = True/False` | Media |

### 10.5 `integradores.py` — CAMBIOS MENORES

| Sección | Cambio | Prioridad |
|---------|--------|-----------|
| Post-step | Agregar normalización de cuaternión | Alta |
| RK4, RKF45 | Callback post-step para normalización | Alta |

### 10.6 `funciones.py` — CAMBIOS MENORES

| Sección | Cambio | Prioridad |
|---------|--------|-----------|
| Nuevo | `quaternion_to_dcm(q)` | Alta |
| Nuevo | `quaternion_derivative(q, omega)` | Alta |
| Nuevo | `euler_to_quaternion(phi, theta, psi)` | Alta |
| Nuevo | `quaternion_to_euler(q)` | Media |
| `guardar_datos_csv` | Agregar columnas 6-DOF | Media |

### 10.7 `ModernGUI.py` — CAMBIOS PARA INTERFAZ

| Sección | Cambio | Prioridad |
|---------|--------|-----------|
| SimulationTab | Selector 3-DOF / 6-DOF | Media |
| ResultsTab | Gráficas de roll/yaw/pitch angles | Media |
| ResultsTab | Gráfica de cuaternión (debug) | Baja |
| StabilityTab | Amortiguamiento dinámico | Baja |

---

## 11. Plan de implementación

### Fase 1: Infraestructura matemática (funciones.py)

**Archivos:** `Paquetes/utils/funciones.py`

Agregar funciones de cuaterniones:

```python
# ========== FUNCIONES DE CUATERNIONES ==========

def quaternion_to_dcm(q):
    """Convierte cuaternión [q0,q1,q2,q3] a DCM (cuerpo→tierra)."""
    q0, q1, q2, q3 = q
    return np.array([
        [1-2*(q2**2+q3**2), 2*(q1*q2-q0*q3), 2*(q1*q3+q0*q2)],
        [2*(q1*q2+q0*q3), 1-2*(q1**2+q3**2), 2*(q2*q3-q0*q1)],
        [2*(q1*q3-q0*q2), 2*(q2*q3+q0*q1), 1-2*(q1**2+q2**2)]
    ])

def quaternion_derivative(q, omega):
    """Calcula dq/dt dado cuaternión q y vel. angular omega=[p,q,r]."""
    q0, q1, q2, q3 = q
    p, qw, r = omega
    return 0.5 * np.array([
        -p*q1 - qw*q2 - r*q3,
         p*q0 + r*q2 - qw*q3,
         qw*q0 - r*q1 + p*q3,
         r*q0 + qw*q1 - p*q2
    ])

def quaternion_normalize(q):
    """Normaliza cuaternión a norma unitaria."""
    return q / np.linalg.norm(q)

def euler_to_quaternion(phi, theta, psi):
    """Euler (roll, pitch, yaw) en radianes → cuaternión."""
    cp, sp = np.cos(phi/2), np.sin(phi/2)
    ct, st = np.cos(theta/2), np.sin(theta/2)
    cy, sy = np.cos(psi/2), np.sin(psi/2)
    return np.array([
        cp*ct*cy + sp*st*sy,
        sp*ct*cy - cp*st*sy,
        cp*st*cy + sp*ct*sy,
        cp*ct*sy - sp*st*cy
    ])

def quaternion_to_euler(q):
    """Cuaternión → Euler (roll, pitch, yaw) en radianes."""
    q0, q1, q2, q3 = q
    phi = np.arctan2(2*(q0*q1 + q2*q3), 1 - 2*(q1**2 + q2**2))
    theta = np.arcsin(np.clip(2*(q0*q2 - q3*q1), -1, 1))
    psi = np.arctan2(2*(q0*q3 + q1*q2), 1 - 2*(q2**2 + q3**2))
    return phi, theta, psi

def quaternion_rotate_vector(q, v):
    """Rota vector v del marco cuerpo al marco tierra usando cuaternión q."""
    return quaternion_to_dcm(q) @ v
```

### Fase 2: Tensor de inercia (componentes.py + cohete.py)

**Agregar a cada componente** un método `calc_Ix_roll()`:

```python
# En Cono:
def calc_Ix_roll(self):
    self.Ix_roll = (3/10) * self.masa * self.rad**2

# En Cilindro:
def calc_Ix_roll(self):
    self.Ix_roll = 0.5 * self.masa * (self.rad_ext**2 + self.rad_int**2)

# En Aletas:
def calc_Ix_roll(self):
    # Momento de inercia de una aleta respecto al eje del cohete
    # usando teorema de ejes paralelos
    r_cg_fin = self.rad_fus + self.semispan / 3  # distancia CG aleta al eje
    I_one_fin = (1/12) * (self.masa/self.numf) * self.semispan**2
    self.Ix_roll = self.numf * (I_one_fin + (self.masa/self.numf) * r_cg_fin**2)

# En Boattail:
def calc_Ix_roll(self):
    if self.radF != self.radR:
        self.Ix_roll = (3/10) * self.masa * (self.radF**5 - self.radR**5) / (self.radF**3 - self.radR**3)
    else:
        self.Ix_roll = 0.5 * self.masa * self.radF**2
```

**En Cohete:**

```python
def calc_inertia_tensor(self):
    """Calcula tensor de inercia diagonal [Ixx, Iyy, Izz]."""
    if self.CG is None:
        self.calc_CG()

    Ixx_roll = 0.0   # Momento axial (roll)
    Iyy_pitch = 0.0  # Momento lateral (pitch)

    for comp in self.componentes.values():
        # Roll: momento axial de cada componente
        Ixx_roll += comp.Ix_roll

        # Pitch/Yaw: momento lateral con ejes paralelos
        d_axial = np.linalg.norm((comp.posicion + comp.CG) - self.CG)
        Iyy_pitch += comp.Ix + comp.masa * d_axial**2

    self.Ixx = Ixx_roll      # Roll
    self.Iyy = Iyy_pitch     # Pitch (= actual self.Ix)
    self.Izz = Iyy_pitch     # Yaw (= Pitch por simetría)
```

### Fase 3: Motor de vuelo 6-DOF (vuelo.py)

Crear nueva clase `Vuelo6DOF` que herede de `Vuelo`:

```python
class Vuelo6DOF(Vuelo):
    """Simulador de vuelo 6-DOF con cuaterniones."""

    def calc_aero_angles(self, v_rel_body):
        """Calcula ángulos aerodinámicos en 3D."""
        u, v, w = v_rel_body
        V = np.linalg.norm(v_rel_body)
        if V < 1e-6:
            return 0.0, 0.0, 0.0, V
        alpha = np.arctan2(w, u)
        beta = np.arctan2(v, np.sqrt(u**2 + w**2))
        alpha_total = np.arctan2(np.sqrt(v**2 + w**2), u)
        return alpha, beta, alpha_total, V

    def calc_fuerzas_aero_body(self, pos, v_rel_body, alpha, beta, V):
        """Calcula fuerzas aerodinámicas en marco cuerpo."""
        if V < 1e-6 or pos[2] > self.atmosfera.h_max:
            return np.zeros(3)

        _, rho, _, cs = self.atmosfera.calc_propiedades(pos[2])
        mach = V / cs
        q_dyn = 0.5 * rho * V**2
        CA = self.vehiculo.calc_Cd(mach)
        CNa = self.vehiculo.CN
        A = self.vehiculo.A

        Fx = -q_dyn * A * CA           # Fuerza axial (drag)
        Fy = -q_dyn * A * CNa * beta   # Fuerza lateral
        Fz = -q_dyn * A * CNa * alpha  # Fuerza normal

        return np.array([Fx, Fy, Fz])

    def calc_momentos_body(self, v_rel_body, alpha, beta, V, omega):
        """Calcula momentos aerodinámicos en marco cuerpo."""
        if V < 1e-6:
            return np.zeros(3)

        _, rho, _, cs = self.atmosfera.calc_propiedades(...)
        q_dyn = 0.5 * rho * V**2
        A = self.vehiculo.A
        d = self.vehiculo.d_ref
        p, qw, r = omega

        # Derivadas de estabilidad
        Cma = self.vehiculo.Cma    # estática pitch
        Cmq = self.vehiculo.Cmq    # damping pitch
        Clp = self.vehiculo.Clp    # damping roll

        # Momentos
        Mx = q_dyn * A * d * (Clp * p * d / (2*V))      # Roll
        My = q_dyn * A * d * (Cma * alpha + Cmq * qw * d / (2*V))  # Pitch
        Mz = q_dyn * A * d * (-Cma * beta + Cmq * r * d / (2*V))   # Yaw

        return np.array([Mx, My, Mz])

    def fun_derivs_6dof(self, t, state):
        """Sistema de 13 ODEs para 6-DOF con cuaterniones."""
        pos = state[0:3]
        vel = state[3:6]
        q = state[6:10]
        omega = state[10:13]
        p, qw, r = omega

        # Normalizar cuaternión
        q = quaternion_normalize(q)

        # Matrices de rotación
        R_b2e = quaternion_to_dcm(q)
        R_e2b = R_b2e.T

        # Velocidad relativa en cuerpo
        v_wind = self.viento.vector
        v_rel_earth = vel - v_wind
        v_rel_body = R_e2b @ v_rel_earth

        # Ángulos aerodinámicos
        alpha, beta, alpha_total, V = self.calc_aero_angles(v_rel_body)

        # Fuerzas en cuerpo
        F_aero = self.calc_fuerzas_aero_body(pos, v_rel_body, alpha, beta, V)
        T_mag = self.vehiculo.calc_empuje_magn(t)
        F_thrust = np.array([T_mag, 0, 0])
        F_body = F_aero + F_thrust

        # Momentos en cuerpo
        M_body = self.calc_momentos_body(v_rel_body, alpha, beta, V, omega)

        # === TRASLACIÓN (marco tierra) ===
        m = self.vehiculo.masa
        g = calc_gravedad(pos[2])
        a_earth = R_b2e @ F_body / m + np.array([0, 0, -g])

        # === ROTACIÓN (ecuaciones de Euler, marco cuerpo) ===
        Ixx = self.vehiculo.Ixx
        Iyy = self.vehiculo.Iyy
        Izz = self.vehiculo.Izz

        # Restricción en riel
        dist = np.linalg.norm(pos)
        if dist <= self.vehiculo.riel.longitud:
            omega = np.zeros(3)
            domega = np.zeros(3)
            dq_quat = np.zeros(4)
        else:
            dp = (M_body[0] - (Izz - Iyy) * qw * r) / Ixx
            dqw = (M_body[1] - (Ixx - Izz) * r * p) / Iyy
            dr = (M_body[2] - (Iyy - Ixx) * p * qw) / Izz
            domega = np.array([dp, dqw, dr])
            dq_quat = quaternion_derivative(q, omega)

        # Ensamblar
        return np.concatenate([vel, a_earth, dq_quat, domega])
```

### Fase 4: Condiciones iniciales y post-procesamiento

**condiciones_init.py:**
```python
# Modo de simulación
modo_6dof = True

# Ángulos del riel
angulo_riel = 87     # grados desde horizontal
azimut_riel = 0      # grados desde Norte (0=N, 90=E, 180=S, 270=W)

# Estado inicial 6-DOF
if modo_6dof:
    q_init = euler_to_quaternion(0, np.deg2rad(angulo_riel), np.deg2rad(azimut_riel))
    estado = np.array([
        x0, y0, z0,      # posición
        vx0, vy0, vz0,    # velocidad
        *q_init,           # cuaternión
        0, 0, 0            # velocidades angulares
    ])
else:
    # Estado 3-DOF (compatible con código actual)
    estado = np.array([x0, y0, z0, vx0, vy0, vz0, theta0, omega0])
```

### Fase 5: Integración numérica (integradores.py)

Agregar normalización post-step:

```python
class RungeKutta4_Quat(RungeKutta4):
    """RK4 con normalización de cuaternión."""

    def step(self, t, state, dt):
        new_state, dt = super().step(t, state, dt)
        # Normalizar cuaternión (índices 6-9)
        q_norm = np.linalg.norm(new_state[6:10])
        if q_norm > 0:
            new_state[6:10] /= q_norm
        return new_state, dt
```

---

## 12. Validación y pruebas

### 12.1 Prueba unitaria: cuaterniones

```python
def test_quaternion_identity():
    """Cuaternión identidad no rota."""
    q = [1, 0, 0, 0]
    R = quaternion_to_dcm(q)
    assert np.allclose(R, np.eye(3))

def test_quaternion_90_pitch():
    """Rotación 90° en pitch."""
    q = euler_to_quaternion(0, np.pi/2, 0)
    v_body = np.array([1, 0, 0])  # vector hacia nariz
    v_earth = quaternion_to_dcm(q) @ v_body
    assert np.allclose(v_earth, [0, 0, 1], atol=1e-10)  # apunta arriba

def test_quaternion_roundtrip():
    """Euler → quaternion → Euler preserva ángulos."""
    phi, theta, psi = 0.3, 1.2, -0.5
    q = euler_to_quaternion(phi, theta, psi)
    phi2, theta2, psi2 = quaternion_to_euler(q)
    assert np.allclose([phi, theta, psi], [phi2, theta2, psi2])
```

### 12.2 Prueba de regresión: 3-DOF vs 6-DOF sin roll/yaw

Ejecutar simulación 6-DOF con condiciones que deberían reproducir el 3-DOF:
- `beta_0 = 0` (sin sideslip)
- `p_0 = 0` (sin roll)
- `r_0 = 0` (sin yaw rate)
- Viento solo en plano XZ

El resultado debería coincidir con la simulación 3-DOF dentro de ~1%.

### 12.3 Prueba de conservación

Sin fuerzas externas ni gravedad, la energía cinética rotacional debe conservarse:

```
E_rot = ½(Ixx·p² + Iyy·q² + Izz·r²) = constante
```

### 12.4 Prueba de estabilidad estática

Un cohete con CP detrás de CG (estable), al perturbarlo con un ángulo de ataque pequeño, debe oscilar y regresar a α = 0 si hay amortiguamiento.

### 12.5 Comparación con OpenRocket / RocketPy

Simular el Xitle II en OpenRocket o RocketPy y comparar:
- Apogeo
- Tiempo de vuelo
- Velocidad máxima
- Rango lateral (drift)

---

## 13. Referencias

### Libros y tesis
1. **Niskanen, S.** "OpenRocket — Development of an Open Source Model Rocket Simulator" (Tesis de maestría, 2013). Base teórica para Barrowman extendido y amortiguamiento. [PDF](https://openrocket.sourceforge.net/thesis.pdf)
2. **Box, S. et al.** "Stochastic Six-Degree-of-Freedom Flight Simulator for Passively Controlled High Power Rockets" (2011). Ecuaciones 6-DOF completas. [PDF](https://pages.hmc.edu/spjut/AdvRoc/PDF/CambridgeRocketSimPaper.pdf)
3. **Zipfel, P.** "Modeling and Simulation of Aerospace Vehicle Dynamics" (AIAA, 2007). Referencia estándar para cuaterniones.

### Software de referencia
4. **RocketPy** — https://github.com/RocketPy-Team/RocketPy — Simulador 6-DOF en Python con cuaterniones. Usa ecuaciones de Kane con Reynolds Transport Theorem para masa variable.
5. **OpenRocket** — https://openrocket.info/ — [Documentación técnica](https://openrocket.sourceforge.net/techdoc.pdf)
6. **Cambridge Rocketry Simulator** — Formulación basada en momento (P, L) en lugar de (v, ω).

### Papers técnicos y documentación en línea
7. **RocketPy Equations of Motion v1** — https://docs.rocketpy.org/en/latest/technical/equations_of_motion_v1.html — Derivación detallada con SymPy.
8. **RocketPy Roll Equations** — https://docs.rocketpy.org/en/latest/technical/aerodynamics/roll_equations.html
9. **MATLAB 6DOF Quaternion Block** — https://www.mathworks.com/help/aeroblks/6dofquaternion.html — Implementación de referencia.
10. **Quaternion Dynamics (arXiv)** — Basile Graf, https://arxiv.org/pdf/0811.2889 — Derivación completa.

### Recursos matemáticos
11. **Barrowman, J.S.** "The Practical Calculation of the Aerodynamic Characteristics of Slender Finned Vehicles" (1967).
12. **VectorNav** — Attitude Transformations: https://www.vectornav.com/resources/inertial-navigation-primer/math-fundamentals/math-attitudetran

---

## Resumen ejecutivo

### Cambio clave: de 8 a 13 estados
```
3-DOF: [x, y, z, vx, vy, vz, θ, ω]           → 8 variables
6-DOF: [x, y, z, vx, vy, vz, q0,q1,q2,q3, p,q,r] → 13 variables
```

### Esfuerzo estimado por módulo

| Módulo | Complejidad | Líneas nuevas/modificadas |
|--------|------------|--------------------------|
| funciones.py (cuaterniones) | Baja | ~60 nuevas |
| componentes.py (Ix_roll) | Baja | ~30 nuevas |
| cohete.py (tensor + derivadas) | Media | ~80 nuevas |
| vuelo.py (motor 6-DOF) | **Alta** | ~250 nuevas |
| condiciones_init.py | Baja | ~15 modificadas |
| integradores.py | Baja | ~20 modificadas |
| GUI (visualización) | Media | ~100 modificadas |
| Tests de validación | Media | ~150 nuevas |
| **TOTAL** | | **~705 líneas** |

### Orden de implementación recomendado

```
1. funciones.py      → Utilidades de cuaterniones (sin dependencias)
2. componentes.py    → Ix_roll por componente (depende de 1)
3. cohete.py         → Tensor de inercia + coeficientes (depende de 2)
4. vuelo.py          → Motor 6-DOF (depende de 1, 3)
5. condiciones_init  → Estado inicial 6-DOF (depende de 1)
6. integradores.py   → Normalización post-step (depende de 4)
7. Validación        → Tests unitarios y de regresión (depende de todo)
8. GUI               → Selector y gráficas (depende de 4)
```

### Compatibilidad con 3-DOF

El simulador debe **mantener ambos modos** (3-DOF y 6-DOF) mediante un flag de configuración. Esto permite:
- Comparar resultados para validación
- Simulaciones rápidas con 3-DOF cuando no se necesita la complejidad completa
- Regresión contra el código existente probado
