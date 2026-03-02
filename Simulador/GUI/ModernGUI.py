import customtkinter
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import os
import json
import threading
import time
import datetime
import csv
import pandas as pd
import numpy as np
import sys
import math

# --- Matplotlib Integration ---
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.patches as patches
import matplotlib.style as mplstyle

# --- Map Integration ---
try:
    from tkintermapview import TkinterMapView
    MAP_AVAILABLE = True
except ImportError:
    MAP_AVAILABLE = False

# --- Backend Integration ---
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

BACKEND_AVAILABLE = False
try:
    from Paquetes.PaqueteFisica.componentes import Cono, Cilindro, Aletas, Boattail
    from Paquetes.PaqueteFisica.cohete import Cohete, Parachute
    from Paquetes.PaqueteFisica.vuelo import Vuelo
    from Paquetes.PaqueteFisica.atmosfera import atmosfera
    from Paquetes.PaqueteFisica.viento import Viento
    from Paquetes.PaqueteFisica.riel import Torrelanzamiento
    from Paquetes.utils.funciones import guardar_datos_csv, guardar_datos_json
    BACKEND_AVAILABLE = True
except ImportError as e:
    print(f"[WARN] Backend no disponible: {e}")
    print("La GUI funcionara en modo demo con datos simulados.")


# =============================================================================
# Paleta de colores
# =============================================================================
class ColorPalette:
    BG_MAIN = "#050253"
    BG_FRAME = "#233969"
    BG_ENTRY = "#E2EAF4"
    BUTTON_RED = "#ef4444"
    BUTTON_GREEN = "#00792C"
    ACCENT_CYAN = "#15D0FF"
    ACCENT_BLUE = "#0211B7"
    ACCENT_VIOLET = "#5A00C0"
    ACCENT_Orange = "#C66907"
    TEXT_PRIMARY = "#FFFFFF"
    TEXT_SECONDARY = "#E2EAF4"
    TEXT_ENTRY = "#050253"
    # Semaforo de estabilidad
    STABILITY_OK = "#22c55e"
    STABILITY_WARN = "#eab308"
    STABILITY_DANGER = "#ef4444"


# =============================================================================
# Tooltip
# =============================================================================
class ToolTip:
    """Tooltip flotante para widgets."""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        widget.bind("<Enter>", self.show)
        widget.bind("<Leave>", self.hide)

    def show(self, event=None):
        if self.tip_window:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify="left",
                         background="#fffde7", foreground="#333",
                         relief="solid", borderwidth=1,
                         font=("Segoe UI", 10), wraplength=300, padx=6, pady=4)
        label.pack()

    def hide(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None


# =============================================================================
# Funciones de simulacion (real y placeholder)
# =============================================================================
def placeholder_run_simulation(params, progress_callback, status_callback):
    """Simulacion de prueba cuando el backend no esta disponible."""
    status_callback("Ejecutando simulacion de prueba (sin backend)...")
    t = np.linspace(0, 60, 600)
    dt_step = t[1] - t[0]
    g = 9.81
    thrust_time = 5.0
    thrust = 3000.0
    mass_init = 25.0
    mass_prop = 12.0
    cd = 0.45
    A = 0.018
    rho = 1.225

    x = np.zeros_like(t)
    y = np.zeros_like(t)
    z = np.zeros_like(t)
    vx = np.zeros_like(t)
    vy = np.zeros_like(t)
    vz = np.zeros_like(t)
    theta = np.full_like(t, np.deg2rad(87))
    omega = np.zeros_like(t)

    for i in range(1, len(t)):
        progress_callback(i / len(t))
        m = mass_init - mass_prop * min(t[i] / thrust_time, 1.0)
        T = thrust if t[i] < thrust_time else 0.0
        vel = np.sqrt(vx[i-1]**2 + vy[i-1]**2 + vz[i-1]**2)
        drag = 0.5 * rho * cd * A * vel**2 if vel > 0 else 0.0
        az = (T * np.sin(theta[i-1]) - drag * (vz[i-1]/(vel+1e-9)) - m * g) / m
        ax_val = (T * np.cos(theta[i-1]) * 0.05 - drag * (vx[i-1]/(vel+1e-9))) / m
        vz[i] = vz[i-1] + az * dt_step
        vx[i] = vx[i-1] + ax_val * dt_step
        z[i] = max(0, z[i-1] + vz[i] * dt_step)
        x[i] = x[i-1] + vx[i] * dt_step
        if z[i] == 0 and i > 10:
            x[i:] = x[i]; y[i:] = y[i]; z[i:] = 0
            vx[i:] = 0; vy[i:] = 0; vz[i:] = 0
            break
        time.sleep(0.001)

    progress_callback(1.0)
    status_callback("Simulacion de prueba completada.")

    cs = 343.0
    df = pd.DataFrame({
        't': t, 'x': x, 'y': y, 'z': z,
        'vx': vx, 'vy': vy, 'vz': vz,
        'thetas': theta, 'omegas': omega,
        'CPs': np.full_like(t, 2.5), 'CGs': np.full_like(t, 2.8),
        'masavuelo': mass_init - mass_prop * np.minimum(t / thrust_time, 1.0),
        'Tmags': np.where(t < thrust_time, thrust, 0),
        'Dmags': 0.5 * rho * cd * A * (vx**2 + vy**2 + vz**2),
        'Nmags': np.zeros_like(t),
        'Gammas': np.arctan2(vz, np.sqrt(vx**2 + vy**2) + 1e-9),
        'Alphas': np.zeros_like(t),
        'Cds': np.full_like(t, cd),
        'Machs': np.sqrt(vx**2 + vy**2 + vz**2) / cs,
        'accels': np.gradient(np.sqrt(vx**2 + vy**2 + vz**2), t),
    })
    return df


def run_real_simulation(params, data_tables, progress_callback, status_callback):
    """Ejecutar simulacion real conectando con el backend."""
    if not BACKEND_AVAILABLE:
        return placeholder_run_simulation(params, progress_callback, status_callback)

    status_callback("Construyendo componentes del cohete...")
    progress_callback(0.05)

    diam_ext = params.get('nose_diam', 0.152)
    espesor = 0.003

    # --- Construir componentes (posicion es np.array([0,0,z])) ---
    nariz = Cono("Nariz", params.get('nose_mass', 0.81),
                 np.array([0.0, 0.0, 0.0]),
                 params.get('nose_len', 0.81), diam_ext,
                 params.get('nose_shape', 'ogiva'))

    coples = Cilindro("Coples", params.get('coples_mass', 0.176),
                      np.array([0.0, 0.0, nariz.bottom[2]]),
                      params.get('coples_len', 0.15),
                      params.get('coples_diam_ext', diam_ext),
                      params.get('coples_diam_int', diam_ext - espesor))

    tubo_recup = Cilindro("Tubo recuperacion", params.get('tubo_recup_mass', 0.92),
                          np.array([0.0, 0.0, coples.bottom[2]]),
                          params.get('tubo_recup_len', 0.3),
                          params.get('tubo_recup_diam_ext', diam_ext),
                          params.get('tubo_recup_diam_int', diam_ext - espesor))

    transfer = Cilindro("Transferidor", params.get('transfer_mass', 0.25),
                        np.array([0.0, 0.0, tubo_recup.bottom[2]]),
                        params.get('transfer_len', 0.10),
                        params.get('transfer_diam_ext', diam_ext),
                        params.get('transfer_diam_int', diam_ext - espesor))

    tanquevacio = Cilindro("Tanquevacio", params.get('tanque_vacio_mass', 1.25),
                           np.array([0.0, 0.0, transfer.bottom[2]]),
                           params.get('tanque_vacio_len', 0.87),
                           params.get('tanque_vacio_diam_ext', diam_ext),
                           params.get('tanque_vacio_diam_int', diam_ext - espesor))

    valvulas = Cilindro("Valvulas", params.get('valvulas_mass', 0.167),
                        np.array([0.0, 0.0, tanquevacio.bottom[2]]),
                        params.get('valvulas_len', 0.24),
                        params.get('valvulas_diam_ext', diam_ext),
                        params.get('valvulas_diam_int', diam_ext - espesor))

    CC = Cilindro("Camara de Combustion", params.get('cc_mass', 0.573),
                  np.array([0.0, 0.0, valvulas.bottom[2]]),
                  params.get('cc_len', 0.43),
                  params.get('cc_diam_ext', diam_ext),
                  params.get('cc_diam_int', params.get('cc_diam_int', 0.102)))

    boattail = Boattail("Boattail", params.get('bt_mass', 0.251),
                        np.array([0.0, 0.0, CC.bottom[2]]),
                        params.get('bt_len', 0.12),
                        params.get('bt_diam_front', diam_ext),
                        params.get('bt_diam_rear', 0.132),
                        params.get('bt_espesor', espesor))

    avionica = Cilindro("Avionica", params.get('avionics_mass', 0.21),
                        np.array([0.0, 0.0, 0.20]), 0.21, 0.14, 0)

    CU = Cilindro("CU", params.get('cu_mass', 0.3),
                  np.array([0.0, 0.0, 0.50]), 0.3, 0.14, 0)

    drogue_comp = Cilindro("Drogue", params.get('drogue_mass', 0.17),
                           np.array([0.0, 0.0, 1.0]), 0.17, 0.14, 0)

    main_comp = Cilindro("Main", params.get('main_mass', 0.30),
                         np.array([0.0, 0.0, 1.4]), 0.30, 0.14, 0)

    fin_sweep_rad = np.deg2rad(params.get('fin_sweep', 25))
    aletas = Aletas("Aletas", params.get('fin_mass', 1.1),
                    np.array([0.0, 0.0, CC.bottom[2]]),
                    diam_ext,
                    int(params.get('fin_num', 4)),
                    params.get('fin_span', 0.10),
                    params.get('fin_root_chord', 0.2),
                    params.get('fin_tip_chord', 0.1),
                    0.2, fin_sweep_rad)

    oxidante = Cilindro("Oxidante", params.get('oxidante_mass', 12.0),
                        np.array([0.0, 0.0, transfer.bottom[2]]),
                        1.33, 0.1461, 0)

    grano = Cilindro("Grano", params.get('grano_mass', 4.88),
                     np.array([0.0, 0.0, valvulas.bottom[2]]),
                     params.get('grano_length', 0.505),
                     params.get('grano_outer_diam', 0.158),
                     params.get('grano_inner_diam', 0.030))

    status_callback("Ensamblando cohete...")
    progress_callback(0.10)

    componentes = {
        'Nariz': nariz, 'coples': coples, 'Tubo recuperacion': tubo_recup,
        'Transferidor de carga': transfer, 'Avionica': avionica,
        'Carga Util': CU, 'drogue': drogue_comp, 'main': main_comp,
        'tanquevacio': tanquevacio, 'oxidante': oxidante,
        'valvulas': valvulas, 'grano': grano,
        'Camara Combustion': CC, 'Aletas': aletas, 'Boattail': boattail
    }
    componentes_externos = {
        'Nariz': nariz, 'coples': coples, 'Tubo recuperacion': tubo_recup,
        'Transferidor de carga': transfer, 'tanquevacio': tanquevacio,
        'valvulas': valvulas, 'Camara Combustion': CC, 'Boattail': boattail
    }

    # Tablas CSV
    thrust_path = data_tables.get('thrust', '')
    drag_path = data_tables.get('drag', '')
    mass_path = data_tables.get('mass', '')

    rail_len = float(params.get('rail_len', 10))
    rail_angle = float(params.get('rail_angle', 87))
    riel = Torrelanzamiento(rail_len, rail_angle)

    cohete = Cohete("Cohete_GUI", "hibrido", componentes, componentes_externos,
                    drag_path, thrust_path, mass_path, riel)
    cohete.d_ext = diam_ext

    # Paracaidas
    drogue_cd = float(params.get('drogue_cd', 0.7))
    drogue_diam = float(params.get('drogue_chute_diam', 0.8))
    drogue_area = math.pi * (drogue_diam / 2) ** 2
    parachute = Parachute(drogue_cd, drogue_area)
    cohete.agregar_paracaidas(parachute)

    status_callback("Configurando atmosfera y viento...")
    progress_callback(0.15)

    atm = atmosfera()
    viento_obj = Viento(
        vel_base=float(params.get('wind_base_speed', 5)),
        vel_mean=float(params.get('wind_mean_speed', 3)),
        vel_var=float(params.get('wind_speed_var', 2)),
        ang_base=230,
        var_ang=float(params.get('wind_angle_var', 10))
    )
    viento_obj.actualizar_viento3D()

    status_callback("Ejecutando simulacion...")
    progress_callback(0.20)

    vuelo = Vuelo(cohete, atm, viento_obj)

    theta0 = np.deg2rad(rail_angle)
    estado = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, theta0, 0.0])

    t_max = float(params.get('sim_max_time', 400))
    dt = float(params.get('sim_time_step', 0.01))
    dt_out = 0.01
    integrador = params.get('integrator', 'DOP853')

    result = vuelo.simular_vuelo(estado, t_max, dt, dt_out, integrador)
    (tiempos, sim, CPs, CGs, masavuelo, viento_mags, viento_dirs,
     viento_vecs, Tvecs, Dvecs, Nvecs, accels, palancas, accangs,
     Gammas, Alphas, torcas, Cds, Machs) = result

    status_callback("Procesando resultados...")
    progress_callback(0.90)

    n = len(tiempos)
    xs = [sim[i][0] for i in range(n)]
    ys = [sim[i][1] for i in range(n)]
    zs = [sim[i][2] for i in range(n)]
    vxs = [sim[i][3] for i in range(n)]
    vys = [sim[i][4] for i in range(n)]
    vzs = [sim[i][5] for i in range(n)]
    thetas = [sim[i][6] for i in range(n)]
    omegas = [sim[i][7] for i in range(n)]

    Tmags = [np.linalg.norm(Tvecs[i]) for i in range(n)]
    Dmags = [np.linalg.norm(Dvecs[i]) for i in range(n)]
    Nmags = [np.linalg.norm(Nvecs[i]) for i in range(n)]
    accel_mags = [np.linalg.norm(accels[i]) for i in range(n)]

    df = pd.DataFrame({
        't': tiempos, 'x': xs, 'y': ys, 'z': zs,
        'vx': vxs, 'vy': vys, 'vz': vzs,
        'thetas': thetas, 'omegas': omegas,
        'CPs': CPs, 'CGs': CGs, 'masavuelo': masavuelo,
        'Tmags': Tmags, 'Dmags': Dmags, 'Nmags': Nmags,
        'Gammas': Gammas, 'Alphas': Alphas,
        'Cds': Cds, 'Machs': Machs, 'accels': accel_mags,
    })

    # Guardar metadatos del vuelo
    df.attrs['tiempo_salida_riel'] = getattr(vuelo, 'tiempo_salida_riel', None)
    df.attrs['tiempo_apogeo'] = getattr(vuelo, 'tiempo_apogeo', None)
    df.attrs['apogeo'] = getattr(vuelo, 'apogeo', None)
    df.attrs['tiempo_impacto'] = getattr(vuelo, 'tiempo_impacto', None)

    progress_callback(1.0)
    status_callback("Simulacion completada.")
    return df



# =============================================================================
# Pestana: Cohete (RocketTab)
# =============================================================================
class RocketTab(customtkinter.CTkScrollableFrame):
    """Tab para definir todos los componentes fisicos del cohete."""

    # Valores por defecto del Xitle II
    DEFAULTS = {
        'nose_len': 0.81, 'nose_mass': 0.81, 'nose_pos_z': 0.0,
        'nose_diam': 0.152, 'nose_shape': 'ogiva',
        'coples_len': 0.15, 'coples_mass': 0.176, 'coples_diam_ext': 0.152,
        'coples_diam_int': 0.149,
        'tubo_recup_len': 0.3, 'tubo_recup_mass': 0.92,
        'tubo_recup_diam_ext': 0.152, 'tubo_recup_diam_int': 0.149,
        'transfer_len': 0.10, 'transfer_mass': 0.25,
        'transfer_diam_ext': 0.152, 'transfer_diam_int': 0.149,
        'tanque_vacio_len': 0.87, 'tanque_vacio_mass': 1.25,
        'tanque_vacio_diam_ext': 0.152, 'tanque_vacio_diam_int': 0.149,
        'valvulas_len': 0.24, 'valvulas_mass': 0.167,
        'valvulas_diam_ext': 0.152, 'valvulas_diam_int': 0.149,
        'cc_len': 0.43, 'cc_mass': 0.573,
        'cc_diam_ext': 0.152, 'cc_diam_int': 0.102,
        'bt_len': 0.12, 'bt_mass': 0.251,
        'bt_diam_front': 0.152, 'bt_diam_rear': 0.132, 'bt_espesor': 0.003,
        'fin_num': 4, 'fin_mass': 1.1, 'fin_span': 0.11,
        'fin_root_chord': 0.3, 'fin_tip_chord': 0.1, 'fin_sweep': 25,
        'avionics_mass': 0.21, 'avionics_pos_z': 0.20,
        'cu_mass': 0.3, 'cu_pos_z': 0.50,
        'motor_mass_inert': 3.2, 'motor_pos_z': 0.45,
        'drogue_mass': 0.17, 'drogue_pos_z': 1.0,
        'drogue_chute_diam': 0.8, 'drogue_cd': 0.7, 'drogue_deploy_alt': 100,
        'main_mass': 0.30, 'main_pos_z': 1.4,
        'main_chute_diam': 2.0, 'main_cd': 1.8, 'main_deploy_alt': 450,
        'oxidante_mass': 12.0, 'oxidante_density': 1220, 'oxidante_temp': 20,
        'grano_mass': 4.88, 'grano_length': 0.35,
        'grano_outer_diam': 0.098, 'grano_inner_diam': 0.030, 'grano_config': 'BATES',
    }

    # Tooltips para cada campo
    TOOLTIPS = {
        'nose_len': 'Longitud de la nariz. Valores tipicos: 0.3 - 1.5 m',
        'nose_mass': 'Masa de la nariz. Valores tipicos: 0.3 - 2.0 kg',
        'nose_diam': 'Diametro de la base de la nariz = diametro del fuselaje',
        'nose_shape': 'Geometria de la nariz. Ogiva es la mas comun para cohetes',
        'fin_num': 'Numero de aletas. Minimo 3 para estabilidad',
        'fin_span': 'Distancia desde la raiz hasta la punta, perpendicular al cuerpo. Tipico: 0.05 - 0.3 m',
        'fin_root_chord': 'Largo de la aleta en la base (pegada al cuerpo). Tipico: 0.1 - 0.4 m',
        'fin_tip_chord': 'Largo de la aleta en la punta. Debe ser menor que la cuerda raiz',
        'fin_sweep': 'Angulo de barrido de las aletas en grados',
        'drogue_chute_diam': 'Diametro del paracaidas drogue. Se despliega en el apogeo',
        'drogue_cd': 'Coeficiente de arrastre del drogue. Tipico: 0.5 - 1.0',
        'main_chute_diam': 'Diametro del paracaidas principal. Se despliega a baja altitud',
        'main_cd': 'Coeficiente de arrastre del main. Tipico: 1.5 - 2.5',
        'oxidante_mass': 'Masa total de oxidante (N2O). Tipico: 5 - 20 kg',
        'grano_mass': 'Masa del grano de combustible solido',
        'grano_config': 'Configuracion del grano: BATES, Estrella, Finocyl, Moonburner',
    }

    def __init__(self, master):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        self.widgets = {}
        self._validation_labels = {}

        # --- Secciones principales ---
        self.external_components_frame = self.create_main_section_frame("Componentes Externos", 0)
        self.internal_components_frame = self.create_main_section_frame("Componentes Internos", 1)
        self.combustible_frame = self.create_main_section_frame("Propelentes", 2)

        self.external_components_frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="col_ext")
        self.internal_components_frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="col_int")
        self.combustible_frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="col_comb")

        # --- Componentes Externos ---
        self.create_nariz_frame(self.external_components_frame, row=1, column=0)
        self.create_coples_frame(self.external_components_frame, row=1, column=1)
        self.create_tubo_recuperacion_frame(self.external_components_frame, row=1, column=2)
        self.create_transferidor_frame(self.external_components_frame, row=2, column=0)
        self.create_tanque_vacio_frame(self.external_components_frame, row=2, column=1)
        self.create_valvulas_frame(self.external_components_frame, row=2, column=2)
        self.create_camara_combustion_frame(self.external_components_frame, row=3, column=0)
        self.create_boattail_frame(self.external_components_frame, row=3, column=1)
        self.create_aletas_frame(self.external_components_frame, row=3, column=2)

        # --- Componentes Internos ---
        self.create_avionica_frame(self.internal_components_frame, row=1, column=0)
        self.create_carga_util_frame(self.internal_components_frame, row=1, column=1)
        self.create_motor_frame(self.internal_components_frame, row=1, column=2)
        self.create_drogue_frame(self.internal_components_frame, row=2, column=0)
        self.create_main_chute_frame(self.internal_components_frame, row=2, column=1)

        # --- Propelentes ---
        self.create_oxidante_frame(self.combustible_frame, row=1, column=0)
        self.create_grano_frame(self.combustible_frame, row=1, column=1)

    def create_labeled_widget(self, master, w_type, name, label_text, default_value, row,
                              values=None, unit="", tooltip=None):
        container = customtkinter.CTkFrame(master, fg_color="transparent")
        container.grid(row=row, column=0, columnspan=2, padx=8, pady=3, sticky="ew")
        container.grid_columnconfigure(1, weight=1)

        label_full = f"{label_text} {unit}:" if unit else f"{label_text}:"
        label = customtkinter.CTkLabel(
            container, text=label_full, text_color=ColorPalette.TEXT_PRIMARY,
            font=customtkinter.CTkFont(size=12), anchor="w", width=140)
        label.grid(row=0, column=0, padx=(5, 5), sticky="w")

        if w_type == "entry":
            widget = customtkinter.CTkEntry(
                container, fg_color=ColorPalette.BG_ENTRY,
                text_color=ColorPalette.TEXT_ENTRY, border_width=0,
                corner_radius=6, height=28, font=customtkinter.CTkFont(size=12))
            widget.insert(0, str(default_value))
            # Validacion en tiempo real
            widget.bind('<FocusOut>', lambda e, n=name, w=widget: self._validate_field(n, w))
        elif w_type == "option":
            widget = customtkinter.CTkOptionMenu(
                container, values=values, fg_color=ColorPalette.BG_ENTRY,
                text_color=ColorPalette.TEXT_ENTRY, button_color=ColorPalette.BG_ENTRY,
                button_hover_color=ColorPalette.TEXT_SECONDARY,
                dropdown_fg_color=ColorPalette.BG_ENTRY,
                dropdown_text_color=ColorPalette.TEXT_ENTRY,
                dropdown_hover_color=ColorPalette.TEXT_SECONDARY,
                corner_radius=6, height=28, font=customtkinter.CTkFont(size=12))
            widget.set(default_value)

        widget.grid(row=0, column=1, padx=(0, 5), sticky="ew")
        self.widgets[name] = widget

        # Tooltip
        tip_text = tooltip or self.TOOLTIPS.get(name, None)
        if tip_text:
            ToolTip(widget, tip_text)

        return widget

    def _validate_field(self, name, widget):
        """Validar campo numerico en tiempo real."""
        val = widget.get()
        try:
            v = float(val)
            # Validaciones especificas
            if '_mass' in name and v < 0:
                widget.configure(border_width=2, border_color=ColorPalette.STABILITY_DANGER)
                return
            if '_len' in name and v <= 0:
                widget.configure(border_width=2, border_color=ColorPalette.STABILITY_DANGER)
                return
            if '_diam' in name and v <= 0:
                widget.configure(border_width=2, border_color=ColorPalette.STABILITY_DANGER)
                return
            if name == 'fin_num' and v < 3:
                widget.configure(border_width=2, border_color=ColorPalette.STABILITY_WARN)
                return
            # Campo valido
            widget.configure(border_width=0)
        except ValueError:
            if name not in ('nose_shape', 'grano_config'):
                widget.configure(border_width=2, border_color=ColorPalette.STABILITY_DANGER)

    def create_main_section_frame(self, title, section_row):
        frame = customtkinter.CTkFrame(self, fg_color=ColorPalette.BG_FRAME,
                                       corner_radius=10, border_width=0)
        frame.grid(row=section_row, column=0, padx=15, pady=10, sticky="ew")
        title_color = ColorPalette.ACCENT_CYAN
        frame_title = customtkinter.CTkLabel(
            frame, text=f"  {title}",
            font=customtkinter.CTkFont(size=18, weight="bold"),
            text_color=title_color)
        frame_title.grid(row=0, column=0, columnspan=3, pady=(15, 10), padx=20, sticky="w")
        return frame

    def create_sub_frame(self, master, title, row, column):
        frame = customtkinter.CTkFrame(master, fg_color=ColorPalette.BG_MAIN, corner_radius=8)
        frame.grid(row=row, column=column, padx=8, pady=8, sticky="nsew")
        frame.grid_columnconfigure(0, weight=1)
        frame_title = customtkinter.CTkLabel(
            frame, text=title, font=customtkinter.CTkFont(size=14, weight="bold"),
            text_color=ColorPalette.TEXT_PRIMARY)
        frame_title.grid(row=0, column=0, columnspan=2, pady=(10, 5), padx=10, sticky="w")
        return frame

    # ---------- Componentes Externos ----------
    def create_nariz_frame(self, master, row, column):
        frame = self.create_sub_frame(master, "Nariz (Cono)", row, column)
        self.create_labeled_widget(frame, "entry", "nose_len", "Longitud", 0.81, 1, unit="m")
        self.create_labeled_widget(frame, "entry", "nose_mass", "Masa", 0.81, 2, unit="kg")
        self.create_labeled_widget(frame, "entry", "nose_diam", "Diametro", 0.152, 4, unit="m")
        self.create_labeled_widget(frame, "option", "nose_shape", "Geometria", "ogiva", 5,
                                   values=["ogiva", "conica", "eliptica", "parabolica"])

    def create_coples_frame(self, master, row, column):
        frame = self.create_sub_frame(master, "Coples", row, column)
        self.create_labeled_widget(frame, "entry", "coples_len", "Longitud", 0.15, 1, unit="m")
        self.create_labeled_widget(frame, "entry", "coples_mass", "Masa", 0.176, 2, unit="kg")
        self.create_labeled_widget(frame, "entry", "coples_diam_ext", "Diam. Ext", 0.152, 4, unit="m")
        self.create_labeled_widget(frame, "entry", "coples_diam_int", "Diam. Int", 0.149, 5, unit="m")

    def create_tubo_recuperacion_frame(self, master, row, column):
        frame = self.create_sub_frame(master, "Tubo Recuperacion", row, column)
        self.create_labeled_widget(frame, "entry", "tubo_recup_len", "Longitud", 0.3, 1, unit="m")
        self.create_labeled_widget(frame, "entry", "tubo_recup_mass", "Masa", 0.92, 2, unit="kg")
        self.create_labeled_widget(frame, "entry", "tubo_recup_diam_ext", "Diam. Ext", 0.152, 4, unit="m")
        self.create_labeled_widget(frame, "entry", "tubo_recup_diam_int", "Diam. Int", 0.149, 5, unit="m")

    def create_transferidor_frame(self, master, row, column):
        frame = self.create_sub_frame(master, "Transferidor", row, column)
        self.create_labeled_widget(frame, "entry", "transfer_len", "Longitud", 0.10, 1, unit="m")
        self.create_labeled_widget(frame, "entry", "transfer_mass", "Masa", 0.25, 2, unit="kg")
        self.create_labeled_widget(frame, "entry", "transfer_diam_ext", "Diam. Ext", 0.152, 4, unit="m")
        self.create_labeled_widget(frame, "entry", "transfer_diam_int", "Diam. Int", 0.149, 5, unit="m")

    def create_tanque_vacio_frame(self, master, row, column):
        frame = self.create_sub_frame(master, "Tanque Oxidante", row, column)
        self.create_labeled_widget(frame, "entry", "tanque_vacio_len", "Longitud", 0.87, 1, unit="m")
        self.create_labeled_widget(frame, "entry", "tanque_vacio_mass", "Masa", 1.25, 2, unit="kg")
        self.create_labeled_widget(frame, "entry", "tanque_vacio_diam_ext", "Diam. Ext", 0.152, 4, unit="m")
        self.create_labeled_widget(frame, "entry", "tanque_vacio_diam_int", "Diam. Int", 0.149, 5, unit="m")

    def create_valvulas_frame(self, master, row, column):
        frame = self.create_sub_frame(master, "Valvulas", row, column)
        self.create_labeled_widget(frame, "entry", "valvulas_len", "Longitud", 0.24, 1, unit="m")
        self.create_labeled_widget(frame, "entry", "valvulas_mass", "Masa", 0.167, 2, unit="kg")
        self.create_labeled_widget(frame, "entry", "valvulas_diam_ext", "Diam. Ext", 0.152, 4, unit="m")
        self.create_labeled_widget(frame, "entry", "valvulas_diam_int", "Diam. Int", 0.149, 5, unit="m")

    def create_camara_combustion_frame(self, master, row, column):
        frame = self.create_sub_frame(master, "Camara Combustion", row, column)
        self.create_labeled_widget(frame, "entry", "cc_len", "Longitud", 0.43, 1, unit="m")
        self.create_labeled_widget(frame, "entry", "cc_mass", "Masa", 0.573, 2, unit="kg")
        self.create_labeled_widget(frame, "entry", "cc_diam_ext", "Diam. Ext", 0.152, 4, unit="m")
        self.create_labeled_widget(frame, "entry", "cc_diam_int", "Diam. Int", 0.102, 5, unit="m")

    def create_boattail_frame(self, master, row, column):
        frame = self.create_sub_frame(master, "Boattail/Tobera", row, column)
        self.create_labeled_widget(frame, "entry", "bt_len", "Longitud", 0.12, 1, unit="m")
        self.create_labeled_widget(frame, "entry", "bt_mass", "Masa", 0.251, 2, unit="kg")
        self.create_labeled_widget(frame, "entry", "bt_diam_front", "Diam. Frontal", 0.152, 4, unit="m")
        self.create_labeled_widget(frame, "entry", "bt_diam_rear", "Diam. Trasero", 0.132, 5, unit="m")
        self.create_labeled_widget(frame, "entry", "bt_espesor", "Espesor", 0.003, 6, unit="m")

    def create_aletas_frame(self, master, row, column):
        frame = self.create_sub_frame(master, "Aletas", row, column)
        self.create_labeled_widget(frame, "entry", "fin_num", "Numero", 4, 1, unit="")
        self.create_labeled_widget(frame, "entry", "fin_mass", "Masa Total", 1.1, 2, unit="kg")
        self.create_labeled_widget(frame, "entry", "fin_span", "Envergadura", 0.11, 4, unit="m")
        self.create_labeled_widget(frame, "entry", "fin_root_chord", "Cuerda Raiz", 0.3, 5, unit="m")
        self.create_labeled_widget(frame, "entry", "fin_tip_chord", "Cuerda Punta", 0.1, 6, unit="m")
        self.create_labeled_widget(frame, "entry", "fin_sweep", "Angulo barrido", 25, 7, unit="deg")

    # ---------- Componentes Internos ----------
    def create_avionica_frame(self, master, row, column):
        frame = self.create_sub_frame(master, "Avionica", row, column)
        self.create_labeled_widget(frame, "entry", "avionics_mass", "Masa", 0.21, 1, unit="kg")
        self.create_labeled_widget(frame, "entry", "avionics_pos_z", "Posicion Z", 0.20, 2, unit="m")

    def create_carga_util_frame(self, master, row, column):
        frame = self.create_sub_frame(master, "Carga Util", row, column)
        self.create_labeled_widget(frame, "entry", "cu_mass", "Masa", 0.3, 1, unit="kg")
        self.create_labeled_widget(frame, "entry", "cu_pos_z", "Posicion Z", 0.50, 2, unit="m")

    def create_motor_frame(self, master, row, column):
        frame = self.create_sub_frame(master, "Motor", row, column)
        self.create_labeled_widget(frame, "entry", "motor_mass_inert", "Masa Inerte", 3.2, 1, unit="kg")
        self.create_labeled_widget(frame, "entry", "motor_pos_z", "Posicion Z", 0.45, 2, unit="m")

    def create_drogue_frame(self, master, row, column):
        frame = self.create_sub_frame(master, "Drogue", row, column)
        self.create_labeled_widget(frame, "entry", "drogue_mass", "Masa", 0.17, 1, unit="kg")
        self.create_labeled_widget(frame, "entry", "drogue_pos_z", "Posicion Z", 1.0, 2, unit="m")
        self.create_labeled_widget(frame, "entry", "drogue_chute_diam", "Diam. Paracaidas", 0.8, 3, unit="m")
        self.create_labeled_widget(frame, "entry", "drogue_cd", "Coef. Arrastre", 0.7, 4, unit="")
        self.create_labeled_widget(frame, "entry", "drogue_deploy_alt", "Alt. Despliegue", 100, 5, unit="m")

    def create_main_chute_frame(self, master, row, column):
        frame = self.create_sub_frame(master, "Main (Principal)", row, column)
        self.create_labeled_widget(frame, "entry", "main_mass", "Masa", 0.30, 1, unit="kg")
        self.create_labeled_widget(frame, "entry", "main_pos_z", "Posicion Z", 1.4, 2, unit="m")
        self.create_labeled_widget(frame, "entry", "main_chute_diam", "Diam. Paracaidas", 2.0, 3, unit="m")
        self.create_labeled_widget(frame, "entry", "main_cd", "Coef. Arrastre", 1.8, 4, unit="")
        self.create_labeled_widget(frame, "entry", "main_deploy_alt", "Alt. Despliegue", 450, 5, unit="m")

    # ---------- Propelentes ----------
    def create_oxidante_frame(self, master, row, column):
        frame = self.create_sub_frame(master, "Oxidante (N2O)", row, column)
        self.create_labeled_widget(frame, "entry", "oxidante_mass", "Masa", 12.0, 1, unit="kg")
        self.create_labeled_widget(frame, "entry", "oxidante_density", "Densidad", 1220, 2, unit="kg/m3")
        self.create_labeled_widget(frame, "entry", "oxidante_temp", "Temperatura", 20, 3, unit="C")

    def create_grano_frame(self, master, row, column):
        frame = self.create_sub_frame(master, "Grano (Combustible)", row, column)
        self.create_labeled_widget(frame, "entry", "grano_mass", "Masa", 4.88, 1, unit="kg")
        self.create_labeled_widget(frame, "entry", "grano_length", "Longitud", 0.35, 2, unit="m")
        self.create_labeled_widget(frame, "entry", "grano_outer_diam", "Diam. Exterior", 0.098, 3, unit="m")
        self.create_labeled_widget(frame, "entry", "grano_inner_diam", "Diam. Interior", 0.030, 4, unit="m")
        self.create_labeled_widget(frame, "option", "grano_config", "Configuracion", "BATES", 5,
                                   values=["BATES", "Estrella", "Finocyl", "Moonburner"])

    # ---------- Metodos de datos ----------
    def get_params(self):
        params = {}
        try:
            for name, widget in self.widgets.items():
                val = widget.get()
                try:
                    params[name] = float(val) if '.' in val or 'e' in val.lower() else int(val)
                except (ValueError, TypeError):
                    params[name] = val
            return params
        except Exception as e:
            print(f"Error al obtener parametros: {e}")
            return None

    def validate_params(self):
        """Validar que los parametros sean coherentes. Retorna (ok, mensajes)."""
        params = self.get_params()
        if not params:
            return False, ["Error al obtener parametros"]
        errors = []
        warnings = []

        # Masas > 0
        for key in [k for k in params if '_mass' in k]:
            if isinstance(params[key], (int, float)) and params[key] < 0:
                errors.append(f"{key}: la masa no puede ser negativa ({params[key]})")

        # Longitudes > 0
        for key in [k for k in params if '_len' in k]:
            if isinstance(params[key], (int, float)) and params[key] <= 0:
                errors.append(f"{key}: la longitud debe ser mayor a 0")

        # Diametros > 0
        for key in [k for k in params if '_diam' in k and key != 'grano_inner_diam']:
            if isinstance(params[key], (int, float)) and params[key] <= 0:
                errors.append(f"{key}: el diametro debe ser mayor a 0")

        # Diam int < Diam ext
        diam_pairs = [
            ('coples_diam_int', 'coples_diam_ext'),
            ('tubo_recup_diam_int', 'tubo_recup_diam_ext'),
            ('transfer_diam_int', 'transfer_diam_ext'),
            ('tanque_vacio_diam_int', 'tanque_vacio_diam_ext'),
            ('valvulas_diam_int', 'valvulas_diam_ext'),
            ('cc_diam_int', 'cc_diam_ext'),
            ('grano_inner_diam', 'grano_outer_diam'),
        ]
        for d_int, d_ext in diam_pairs:
            vi = params.get(d_int, 0)
            ve = params.get(d_ext, 1)
            if isinstance(vi, (int, float)) and isinstance(ve, (int, float)) and vi >= ve:
                errors.append(f"Diam. interior ({d_int}={vi}) >= exterior ({d_ext}={ve})")

        # Aletas
        if params.get('fin_num', 0) < 3:
            errors.append("El numero de aletas debe ser al menos 3")
        if params.get('fin_tip_chord', 0) > params.get('fin_root_chord', 0):
            warnings.append("La cuerda de punta es mayor que la de raiz")

        # Propelentes
        if params.get('oxidante_mass', 0) <= 0:
            errors.append("La masa de oxidante debe ser mayor a 0")
        if params.get('grano_mass', 0) <= 0:
            errors.append("La masa de combustible debe ser mayor a 0")

        if errors:
            return False, errors
        if warnings:
            return True, warnings
        return True, ["Parametros validos"]

    def reset_to_defaults(self):
        """Resetear todos los valores a los defaults del Xitle II."""
        for name, widget in self.widgets.items():
            default = self.DEFAULTS.get(name)
            if default is not None:
                if isinstance(widget, customtkinter.CTkEntry):
                    widget.delete(0, "end")
                    widget.insert(0, str(default))
                    widget.configure(border_width=0)
                elif isinstance(widget, customtkinter.CTkOptionMenu):
                    widget.set(str(default))



# =============================================================================
# Pestana: Simulacion/Entorno
# =============================================================================
class SimulationEnvironmentTab(customtkinter.CTkScrollableFrame):
    def __init__(self, master):
        super().__init__(master)
        self.configure(fg_color=ColorPalette.BG_FRAME)
        self.grid_columnconfigure(0, weight=1, uniform="col")
        self.grid_columnconfigure(1, weight=1, uniform="col")
        self.grid_columnconfigure(2, weight=1)
        self.widgets = {}

        self.create_launch_site_frame(row=0, column=0)
        self.create_wind_frame(row=0, column=1)
        self.create_rail_frame(row=1, column=0)
        self.create_simulation_frame(row=1, column=1)
        if MAP_AVAILABLE:
            self.create_map_frame(row=0, column=2, rowspan=2)

    def create_map_frame(self, row, column, rowspan):
        frame = self.create_frame("Mapa: Sitio de lanzamiento", row, column, rowspan)
        map_container = customtkinter.CTkFrame(frame, fg_color=ColorPalette.BG_FRAME, corner_radius=10)
        map_container.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        self.map_widget = TkinterMapView(map_container, width=400, height=350, corner_radius=10)
        self.map_widget.pack(fill="both", expand=True, padx=5, pady=5)
        self.update_map_position()

    def update_map_position(self):
        if not MAP_AVAILABLE or not hasattr(self, 'map_widget'):
            return
        try:
            lat = float(self.widgets['launch_lat'].get()) if 'launch_lat' in self.widgets else 19.5
            lon = float(self.widgets['launch_lon'].get()) if 'launch_lon' in self.widgets else -98
            self.map_widget.set_position(lat, lon)
            self.map_widget.delete_all_marker()
            self.map_widget.set_marker(lat, lon, text="Sitio de Lanzamiento")
            self.map_widget.set_zoom(12)
        except (ValueError, KeyError):
            pass

    def create_labeled_widget(self, master, w_type, name, label_text, default_value, row,
                              values=None, width=150, label_width=150):
        container = customtkinter.CTkFrame(master, fg_color="transparent")
        container.grid(row=row, column=0, columnspan=2, padx=5, pady=3, sticky="ew")
        container.grid_columnconfigure(1, weight=1)

        label = customtkinter.CTkLabel(container, text=label_text, width=label_width,
                                       anchor="w", text_color="white")
        label.grid(row=0, column=0, padx=(10, 5), sticky="w")

        if w_type == "entry":
            widget = customtkinter.CTkEntry(container, width=width, fg_color="white",
                                            text_color="black", border_width=1)
            widget.insert(0, str(default_value))
            if name in ['launch_lat', 'launch_lon']:
                widget.bind('<KeyRelease>', lambda e: self.on_coordinate_change())
        elif w_type == "option":
            widget = customtkinter.CTkOptionMenu(container, values=values, width=width,
                                                  fg_color="white", text_color="black",
                                                  button_color="white", button_hover_color="#e0e0e0")
            widget.set(default_value)
        elif w_type == "switch":
            widget = customtkinter.CTkSwitch(container, text="", fg_color="gray",
                                             progress_color=ColorPalette.ACCENT_CYAN)
            if default_value:
                widget.select()

        widget.grid(row=0, column=1, padx=(0, 10), sticky="w")
        self.widgets[name] = widget
        return widget

    def on_coordinate_change(self):
        if hasattr(self, 'map_widget'):
            self.update_map_position()

    def create_frame(self, title, row, column, rowspan=1, colspan=1):
        frame = customtkinter.CTkFrame(self, fg_color=ColorPalette.BG_MAIN,
                                       corner_radius=10, border_width=0)
        frame.grid(row=row, column=column, rowspan=rowspan, columnspan=colspan,
                   padx=10, pady=10, sticky="nsew")
        title_label = customtkinter.CTkLabel(frame, text=title,
                                             font=customtkinter.CTkFont(size=20, weight="bold"),
                                             text_color=ColorPalette.ACCENT_CYAN)
        title_label.grid(row=0, column=0, columnspan=2, pady=(10, 10), padx=10, sticky="w")
        return frame

    def create_launch_site_frame(self, row, column):
        frame = self.create_frame("Sitio de Lanzamiento:", row, column)
        self.create_labeled_widget(frame, "entry", "launch_lat", "Latitud (deg):", "19.5", 1)
        self.create_labeled_widget(frame, "entry", "launch_lon", "Longitud (deg):", "-98", 2)
        self.create_labeled_widget(frame, "entry", "launch_alt", "Altitud (m):", "20", 3)
        self.create_labeled_widget(frame, "entry", "launch_date", "Fecha (YYYY-MM-DD):", "2024-11-06", 4)

    def create_wind_frame(self, row, column):
        frame = self.create_frame("Viento (Modelo Simple):", row, column)
        self.create_labeled_widget(frame, "entry", "wind_base_speed", "Velocidad Base (m/s):", "5", 1)
        self.create_labeled_widget(frame, "entry", "wind_mean_speed", "Velocidad Media (m/s):", "3", 2)
        self.create_labeled_widget(frame, "entry", "wind_speed_var", "Variacion Velocidad:", "2", 3)
        self.create_labeled_widget(frame, "entry", "wind_angle_var", "Variacion Angulo (deg):", "10.0", 4)

    def create_rail_frame(self, row, column):
        frame = self.create_frame("Riel de Lanzamiento:", row, column)
        self.create_labeled_widget(frame, "entry", "rail_len", "Longitud (m):", "10", 1)
        self.create_labeled_widget(frame, "entry", "rail_angle", "Angulo Elevacion (deg):", "87", 2)

    def create_simulation_frame(self, row, column):
        frame = self.create_frame("Simulacion:", row, column)
        self.create_labeled_widget(frame, "entry", "sim_max_time", "Tiempo Maximo (s):", "400", 1)
        self.create_labeled_widget(frame, "entry", "sim_time_step", "Paso de Tiempo (s):", "0.01", 2)
        self.create_labeled_widget(frame, "option", "integrator", "Metodo Integracion:", "DOP853", 3,
                                   ["DOP853", "RK45", "RK23", "RungeKutta4", "Euler"])

    def get_params(self):
        params = {}
        try:
            for name, widget in self.widgets.items():
                val = widget.get()
                try:
                    params[name] = float(val) if '.' in val or 'e' in val.lower() else int(val)
                except (ValueError, TypeError):
                    params[name] = val
            return params
        except Exception:
            return None

    def validate_params(self):
        """Validar parametros de simulacion."""
        params = self.get_params()
        if not params:
            return False, ["Error al obtener parametros de simulacion"]
        errors = []

        # Coordenadas
        try:
            lat = float(params.get('launch_lat', 0))
            if not -90 <= lat <= 90:
                errors.append(f"Latitud fuera de rango: {lat} (debe ser -90 a 90)")
        except (ValueError, TypeError):
            errors.append("Latitud no es un numero valido")

        try:
            lon = float(params.get('launch_lon', 0))
            if not -180 <= lon <= 180:
                errors.append(f"Longitud fuera de rango: {lon} (debe ser -180 a 180)")
        except (ValueError, TypeError):
            errors.append("Longitud no es un numero valido")

        # Riel
        try:
            angle = float(params.get('rail_angle', 0))
            if not 0 < angle <= 90:
                errors.append(f"Angulo de riel fuera de rango: {angle} (debe ser 0-90 grados)")
        except (ValueError, TypeError):
            errors.append("Angulo de riel no es un numero valido")

        try:
            rail_len = float(params.get('rail_len', 0))
            if rail_len <= 0:
                errors.append("Longitud del riel debe ser mayor a 0")
        except (ValueError, TypeError):
            errors.append("Longitud del riel no es un numero valido")

        # Simulacion
        try:
            dt = float(params.get('sim_time_step', 0))
            if not 0.0001 <= dt <= 1.0:
                errors.append(f"Paso de tiempo fuera de rango: {dt} (debe ser 0.0001 a 1.0)")
        except (ValueError, TypeError):
            errors.append("Paso de tiempo no es un numero valido")

        try:
            t_max = float(params.get('sim_max_time', 0))
            if t_max <= 0:
                errors.append("Tiempo maximo debe ser mayor a 0")
        except (ValueError, TypeError):
            errors.append("Tiempo maximo no es un numero valido")

        if errors:
            return False, errors
        return True, ["Parametros de simulacion validos"]



# =============================================================================
# Pestana: Tablas de Datos (CSV import)
# =============================================================================
class DataTablesTab(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.configure(fg_color=ColorPalette.BG_FRAME)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.dataframes = {"thrust": None, "drag": None, "mass": None}
        self.filepaths = {"thrust": "", "drag": "", "mass": ""}
        self.canvas = None

        # Frames superiores
        self.top_frame = customtkinter.CTkFrame(self)
        self.top_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        self.top_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.mid_frame = customtkinter.CTkFrame(self)
        self.mid_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))
        self.mid_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.plot_frame = customtkinter.CTkFrame(self, fg_color="#E5E5E5")
        self.plot_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
        self.plot_frame.grid_columnconfigure(0, weight=1)
        self.plot_frame.grid_rowconfigure(0, weight=1)

        self.create_importers()
        self.show_placeholder_message()

    def create_importers(self):
        # Empuje
        btn1 = customtkinter.CTkButton(self.top_frame, text="Importar Empuje (T vs t)",
                                       command=lambda: self.load_csv("thrust"),
                                       fg_color=ColorPalette.ACCENT_Orange)
        self.lbl1 = customtkinter.CTkLabel(self.mid_frame, text="Empuje: No cargado")
        btn2 = customtkinter.CTkButton(self.mid_frame, text="Visualizar Empuje",
                                       command=lambda: self.visualize_data("thrust"),
                                       fg_color=ColorPalette.ACCENT_BLUE)
        btn1.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.lbl1.grid(row=0, column=0, padx=5, pady=5)
        btn2.grid(row=1, column=0, padx=5, pady=5)

        # Arrastre
        btn3 = customtkinter.CTkButton(self.top_frame, text="Importar Arrastre (Cd vs Mach)",
                                       command=lambda: self.load_csv("drag"),
                                       fg_color=ColorPalette.ACCENT_Orange)
        self.lbl2 = customtkinter.CTkLabel(self.mid_frame, text="Cd_vs_mach: No cargado")
        btn4 = customtkinter.CTkButton(self.mid_frame, text="Visualizar Arrastre",
                                       command=lambda: self.visualize_data("drag"),
                                       fg_color=ColorPalette.ACCENT_BLUE)
        btn3.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.lbl2.grid(row=0, column=1, padx=5, pady=5)
        btn4.grid(row=1, column=1, padx=5, pady=5)

        # Masa
        btn5 = customtkinter.CTkButton(self.top_frame, text="Importar Masa (M vs t)",
                                       command=lambda: self.load_csv("mass"),
                                       fg_color=ColorPalette.ACCENT_Orange)
        self.lbl3 = customtkinter.CTkLabel(self.mid_frame, text="Masa: No cargado")
        btn6 = customtkinter.CTkButton(self.mid_frame, text="Visualizar Masa",
                                       command=lambda: self.visualize_data("mass"),
                                       fg_color=ColorPalette.ACCENT_BLUE)
        btn5.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        self.lbl3.grid(row=0, column=2, padx=5, pady=5)
        btn6.grid(row=1, column=2, padx=5, pady=5)

        # Indicadores de estado (checkmarks)
        self.status_labels = {}
        for i, dtype in enumerate(['thrust', 'drag', 'mass']):
            lbl = customtkinter.CTkLabel(self.top_frame, text="", font=customtkinter.CTkFont(size=14))
            lbl.grid(row=1, column=i, padx=5, pady=2)
            self.status_labels[dtype] = lbl

    def _update_status_indicator(self, data_type):
        if data_type in self.status_labels:
            if self.dataframes.get(data_type) is not None:
                self.status_labels[data_type].configure(
                    text="Cargado", text_color=ColorPalette.STABILITY_OK)
            else:
                self.status_labels[data_type].configure(
                    text="No cargado", text_color=ColorPalette.STABILITY_DANGER)

    def load_csv(self, data_type, filepath=None):
        if filepath is None:
            filepath = filedialog.askopenfilename(
                filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
                title=f"Importar {data_type}")
        if not filepath:
            return
        try:
            df = pd.read_csv(filepath, header=None, names=['x', 'y'],
                             comment='#', skip_blank_lines=True,
                             on_bad_lines='skip').apply(pd.to_numeric, errors='coerce').dropna()
            if df.empty:
                messagebox.showwarning("Archivo Vacio",
                                       f"El archivo no contiene datos numericos validos.")
                return
            self.dataframes[data_type] = df
            self.filepaths[data_type] = filepath
            labels = {'thrust': self.lbl1, 'drag': self.lbl2, 'mass': self.lbl3}
            names = {'thrust': 'Empuje', 'drag': 'Cd_vs_mach', 'mass': 'Masa'}
            labels[data_type].configure(text=f"{names[data_type]}: {os.path.basename(filepath)}")
            self._update_status_indicator(data_type)
            self.visualize_data(data_type)
        except Exception as e:
            messagebox.showerror("Error al Cargar CSV",
                                 f"No se pudo leer el archivo.\nError: {e}")

    def show_placeholder_message(self):
        for w in self.plot_frame.winfo_children():
            w.destroy()
        customtkinter.CTkLabel(self.plot_frame,
                               text="Seleccione un tipo de dato para visualizar la grafica.",
                               font=customtkinter.CTkFont(size=16)).pack(expand=True)
        self.canvas = None
        for dtype in ['thrust', 'drag', 'mass']:
            self._update_status_indicator(dtype)

    def visualize_data(self, data_type):
        df = self.dataframes.get(data_type)
        if df is None:
            messagebox.showwarning("Sin Datos", f"Cargue un archivo para '{data_type}'.")
            return
        for w in self.plot_frame.winfo_children():
            w.destroy()
        fig = Figure(figsize=(8, 6), dpi=100, facecolor="#FFFFFF")
        ax = fig.add_subplot(111)
        titles = {"thrust": "Curva de Empuje", "drag": "Curva de Arrastre", "mass": "Curva de Masa"}
        x_labels = {"thrust": "Tiempo (s)", "drag": "Mach", "mass": "Tiempo (s)"}
        y_labels = {"thrust": "Empuje (N)", "drag": "Cd", "mass": "Masa (kg)"}
        ax.plot(df['x'], df['y'], marker='.', linestyle='-', markersize=3, color='#0078D7')
        ax.set_title(titles[data_type])
        ax.set_xlabel(x_labels[data_type])
        ax.set_ylabel(y_labels[data_type])
        ax.grid(True, linestyle='--', alpha=0.6)
        fig.tight_layout()
        self.canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)



# =============================================================================
# Pestana: Resultados (con graficas completas y exportacion)
# =============================================================================
class ResultsTab(customtkinter.CTkFrame):
    """Pestana para mostrar resultados de la simulacion con graficas y exportacion."""

    def __init__(self, parent):
        super().__init__(parent)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.simulation_df = None

        # --- Barra de herramientas de exportacion ---
        self.export_frame = customtkinter.CTkFrame(self, height=40)
        self.export_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))
        self.export_frame.grid_columnconfigure(5, weight=1)

        customtkinter.CTkButton(self.export_frame, text="Exportar CSV",
                                command=self.export_csv, fg_color=ColorPalette.ACCENT_Orange,
                                width=120).grid(row=0, column=0, padx=5, pady=5)
        customtkinter.CTkButton(self.export_frame, text="Exportar JSON",
                                command=self.export_json, fg_color=ColorPalette.ACCENT_Orange,
                                width=120).grid(row=0, column=1, padx=5, pady=5)
        customtkinter.CTkButton(self.export_frame, text="Guardar Graficas",
                                command=self.export_plots, fg_color=ColorPalette.ACCENT_BLUE,
                                width=130).grid(row=0, column=2, padx=5, pady=5)

        # Selector de tipo de grafica
        self.plot_selector = customtkinter.CTkOptionMenu(
            self.export_frame,
            values=["Resumen (6 graficas)", "Fuerzas", "Aerodinamica",
                    "Trayectoria 3D", "Masa y CG/CP"],
            command=self._on_plot_type_change,
            fg_color="white", text_color="black", button_color="white",
            width=180)
        self.plot_selector.grid(row=0, column=3, padx=10, pady=5)
        self.plot_selector.set("Resumen (6 graficas)")

        # --- Area de graficas ---
        self.plot_frame = customtkinter.CTkFrame(self)
        self.plot_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        self.plot_frame.grid_columnconfigure(0, weight=1)
        self.plot_frame.grid_rowconfigure(0, weight=1)

        # --- Resumen numerico ---
        self.summary_frame = customtkinter.CTkFrame(self, height=80)
        self.summary_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))
        self.summary_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        self.canvas = None
        self.toolbar = None
        self.create_summary_widgets()
        self.show_placeholder_message()

    def create_summary_widgets(self):
        font_style = customtkinter.CTkFont(size=13, weight="bold")
        self.summary_labels = {}
        labels_def = [
            ("apogee", "Apogeo: -- m", 0),
            ("max_vel", "Vel. Max: -- m/s", 1),
            ("max_mach", "Mach Max: --", 2),
            ("flight_time", "T. Vuelo: -- s", 3),
            ("landing_dist", "Dist. Impacto: -- m", 4),
        ]
        for key, text, col in labels_def:
            lbl = customtkinter.CTkLabel(self.summary_frame, text=text, font=font_style)
            lbl.grid(row=0, column=col, pady=8, padx=5)
            self.summary_labels[key] = lbl

    def show_placeholder_message(self):
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
            self.canvas = None
        if self.toolbar:
            self.toolbar.destroy()
            self.toolbar = None
        for widget in self.plot_frame.winfo_children():
            widget.destroy()
        customtkinter.CTkLabel(
            self.plot_frame,
            text="Los resultados de la simulacion se mostraran aqui.\n\n"
                 "Ejecute una simulacion para ver las graficas.",
            font=customtkinter.CTkFont(size=16),
            text_color=ColorPalette.TEXT_SECONDARY
        ).grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

    def display_results(self, df):
        """Mostrar resultados completos de la simulacion."""
        self.simulation_df = df
        if df is None or df.empty:
            messagebox.showinfo("Resultados", "La simulacion no produjo datos para graficar.")
            return

        try:
            # Calcular metricas
            apogee = df['z'].max()
            vel_total = np.sqrt(df['vx']**2 + df['vy']**2 + df['vz']**2)
            max_velocity = vel_total.max()
            max_mach = df['Machs'].max() if 'Machs' in df else 0
            landing_dist = np.sqrt(df['x'].iloc[-1]**2 + df['y'].iloc[-1]**2)

            # Tiempo de vuelo (hasta que z vuelve a 0 despues del apogeo)
            apogee_idx = df['z'].idxmax()
            post_apogee = df.loc[apogee_idx:]
            landed = post_apogee[post_apogee['z'] <= 0]
            flight_time = landed['t'].iloc[0] if not landed.empty else df['t'].iloc[-1]

            # Actualizar resumen
            self.summary_labels['apogee'].configure(text=f"Apogeo: {apogee:.1f} m")
            self.summary_labels['max_vel'].configure(text=f"Vel. Max: {max_velocity:.1f} m/s")
            self.summary_labels['max_mach'].configure(text=f"Mach Max: {max_mach:.3f}")
            self.summary_labels['flight_time'].configure(text=f"T. Vuelo: {flight_time:.1f} s")
            self.summary_labels['landing_dist'].configure(text=f"Dist. Impacto: {landing_dist:.1f} m")

            self._draw_summary_plots(df)
        except Exception as e:
            messagebox.showerror("Error al Graficar",
                                 f"Ocurrio un error al generar las graficas:\n{e}")
            import traceback
            traceback.print_exc()
            self.show_placeholder_message()

    def _on_plot_type_change(self, choice):
        if self.simulation_df is not None:
            if choice == "Resumen (6 graficas)":
                self._draw_summary_plots(self.simulation_df)
            elif choice == "Fuerzas":
                self._draw_forces_plots(self.simulation_df)
            elif choice == "Aerodinamica":
                self._draw_aero_plots(self.simulation_df)
            elif choice == "Trayectoria 3D":
                self._draw_3d_trajectory(self.simulation_df)
            elif choice == "Masa y CG/CP":
                self._draw_mass_cg_plots(self.simulation_df)

    def _clear_plot_area(self):
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
            self.canvas = None
        if self.toolbar:
            self.toolbar.destroy()
            self.toolbar = None
        for widget in self.plot_frame.winfo_children():
            widget.destroy()

    def _show_figure(self, fig):
        self._clear_plot_area()
        self.canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.plot_frame, pack_toolbar=False)
        self.toolbar.update()
        self.toolbar.grid(row=1, column=0, sticky="ew")

    def _style_axis(self, ax, title, xlabel, ylabel):
        ax.set_title(title, fontsize=10, fontweight='bold', color='white')
        ax.set_xlabel(xlabel, fontsize=9, color='#ccc')
        ax.set_ylabel(ylabel, fontsize=9, color='#ccc')
        ax.tick_params(colors='#aaa', labelsize=8)
        ax.set_facecolor('#1a1a2e')
        ax.grid(True, linestyle='--', alpha=0.3, color='#555')

    def _draw_summary_plots(self, df):
        fig = Figure(figsize=(12, 7), dpi=100, facecolor='#16213e')
        t = df['t']
        vel = np.sqrt(df['vx']**2 + df['vy']**2 + df['vz']**2)

        # 1. Altitud vs Tiempo
        ax1 = fig.add_subplot(2, 3, 1)
        ax1.plot(t, df['z'], color='#00d4ff', linewidth=1.2)
        apogee_idx = df['z'].idxmax()
        ax1.axhline(y=df['z'].max(), color='#ff6b6b', linestyle='--', alpha=0.5, linewidth=0.8)
        ax1.plot(t.iloc[apogee_idx], df['z'].iloc[apogee_idx], 'r^', markersize=8)
        ax1.annotate(f"  {df['z'].max():.0f} m", (t.iloc[apogee_idx], df['z'].iloc[apogee_idx]),
                     color='#ff6b6b', fontsize=8)
        self._style_axis(ax1, "Altitud", "Tiempo (s)", "Altitud (m)")

        # 2. Velocidad vs Tiempo
        ax2 = fig.add_subplot(2, 3, 2)
        ax2.plot(t, vel, color='#ffd93d', linewidth=1.2)
        ax2.plot(t.iloc[vel.idxmax()], vel.max(), 'r^', markersize=8)
        self._style_axis(ax2, "Velocidad", "Tiempo (s)", "Velocidad (m/s)")

        # 3. Aceleracion vs Tiempo
        ax3 = fig.add_subplot(2, 3, 3)
        if 'accels' in df:
            ax3.plot(t, df['accels'] / 9.81, color='#ff6b6b', linewidth=1.0)
            self._style_axis(ax3, "Aceleracion", "Tiempo (s)", "Aceleracion (g)")
        else:
            accel = np.gradient(vel, t)
            ax3.plot(t, accel / 9.81, color='#ff6b6b', linewidth=1.0)
            self._style_axis(ax3, "Aceleracion", "Tiempo (s)", "Aceleracion (g)")

        # 4. Mach vs Tiempo
        ax4 = fig.add_subplot(2, 3, 4)
        if 'Machs' in df:
            ax4.plot(t, df['Machs'], color='#6bcb77', linewidth=1.2)
            ax4.axhline(y=1.0, color='#ff6b6b', linestyle='--', alpha=0.5, linewidth=0.8, label='Mach 1')
            ax4.legend(fontsize=8, facecolor='#1a1a2e', edgecolor='#555', labelcolor='white')
        self._style_axis(ax4, "Numero de Mach", "Tiempo (s)", "Mach")

        # 5. Angulo de ataque vs Tiempo
        ax5 = fig.add_subplot(2, 3, 5)
        if 'Alphas' in df:
            ax5.plot(t, np.degrees(df['Alphas']), color='#c084fc', linewidth=1.0)
        self._style_axis(ax5, "Angulo de Ataque", "Tiempo (s)", "Alpha (deg)")

        # 6. Trayectoria X-Z
        ax6 = fig.add_subplot(2, 3, 6)
        dist_h = np.sqrt(df['x']**2 + df['y']**2)
        ax6.plot(dist_h, df['z'], color='#00d4ff', linewidth=1.2)
        ax6.plot(dist_h.iloc[apogee_idx], df['z'].iloc[apogee_idx], 'r^', markersize=8)
        self._style_axis(ax6, "Trayectoria", "Distancia Horizontal (m)", "Altitud (m)")

        fig.tight_layout(pad=2.0)
        self._show_figure(fig)

    def _draw_forces_plots(self, df):
        fig = Figure(figsize=(12, 7), dpi=100, facecolor='#16213e')
        t = df['t']

        ax1 = fig.add_subplot(2, 2, 1)
        if 'Tmags' in df:
            ax1.plot(t, df['Tmags'], color='#ff6b6b', linewidth=1.2)
        self._style_axis(ax1, "Empuje", "Tiempo (s)", "Empuje (N)")

        ax2 = fig.add_subplot(2, 2, 2)
        if 'Dmags' in df:
            ax2.plot(t, df['Dmags'], color='#ffd93d', linewidth=1.2)
        self._style_axis(ax2, "Arrastre", "Tiempo (s)", "Arrastre (N)")

        ax3 = fig.add_subplot(2, 2, 3)
        if 'Nmags' in df:
            ax3.plot(t, df['Nmags'], color='#6bcb77', linewidth=1.2)
        self._style_axis(ax3, "Fuerza Normal", "Tiempo (s)", "Normal (N)")

        ax4 = fig.add_subplot(2, 2, 4)
        if 'Tmags' in df and 'Dmags' in df:
            ax4.plot(t, df['Tmags'], color='#ff6b6b', label='Empuje', linewidth=1.0)
            ax4.plot(t, df['Dmags'], color='#ffd93d', label='Arrastre', linewidth=1.0)
            if 'Nmags' in df:
                ax4.plot(t, df['Nmags'], color='#6bcb77', label='Normal', linewidth=1.0)
            ax4.legend(fontsize=8, facecolor='#1a1a2e', edgecolor='#555', labelcolor='white')
        self._style_axis(ax4, "Todas las Fuerzas", "Tiempo (s)", "Fuerza (N)")

        fig.tight_layout(pad=2.0)
        self._show_figure(fig)

    def _draw_aero_plots(self, df):
        fig = Figure(figsize=(12, 7), dpi=100, facecolor='#16213e')
        t = df['t']

        ax1 = fig.add_subplot(2, 2, 1)
        if 'Cds' in df:
            ax1.plot(t, df['Cds'], color='#ffd93d', linewidth=1.0)
        self._style_axis(ax1, "Coeficiente de Arrastre", "Tiempo (s)", "Cd")

        ax2 = fig.add_subplot(2, 2, 2)
        if 'Machs' in df:
            ax2.plot(t, df['Machs'], color='#6bcb77', linewidth=1.2)
            ax2.axhline(y=1.0, color='#ff6b6b', linestyle='--', alpha=0.5)
        self._style_axis(ax2, "Numero de Mach", "Tiempo (s)", "Mach")

        ax3 = fig.add_subplot(2, 2, 3)
        if 'Alphas' in df:
            ax3.plot(t, np.degrees(df['Alphas']), color='#c084fc', linewidth=1.0)
        self._style_axis(ax3, "Angulo de Ataque", "Tiempo (s)", "Alpha (deg)")

        ax4 = fig.add_subplot(2, 2, 4)
        if 'Gammas' in df:
            ax4.plot(t, np.degrees(df['Gammas']), color='#00d4ff', linewidth=1.0)
        self._style_axis(ax4, "Angulo de Trayectoria", "Tiempo (s)", "Gamma (deg)")

        fig.tight_layout(pad=2.0)
        self._show_figure(fig)

    def _draw_3d_trajectory(self, df):
        fig = Figure(figsize=(10, 8), dpi=100, facecolor='#16213e')
        ax = fig.add_subplot(111, projection='3d')
        ax.set_facecolor('#1a1a2e')
        ax.plot(df['x'], df['y'], df['z'], color='#00d4ff', linewidth=1.5)
        apogee_idx = df['z'].idxmax()
        ax.scatter(df['x'].iloc[apogee_idx], df['y'].iloc[apogee_idx],
                   df['z'].iloc[apogee_idx], color='red', s=60, marker='^', label='Apogeo')
        ax.scatter(df['x'].iloc[0], df['y'].iloc[0], df['z'].iloc[0],
                   color='lime', s=60, marker='o', label='Lanzamiento')
        ax.set_xlabel('X (m)', color='#aaa')
        ax.set_ylabel('Y (m)', color='#aaa')
        ax.set_zlabel('Z (m)', color='#aaa')
        ax.set_title('Trayectoria 3D', color='white', fontweight='bold')
        ax.legend(fontsize=9)
        ax.tick_params(colors='#aaa')
        fig.tight_layout()
        self._show_figure(fig)

    def _draw_mass_cg_plots(self, df):
        fig = Figure(figsize=(12, 7), dpi=100, facecolor='#16213e')
        t = df['t']

        ax1 = fig.add_subplot(2, 2, 1)
        if 'masavuelo' in df:
            ax1.plot(t, df['masavuelo'], color='#ffd93d', linewidth=1.2)
        self._style_axis(ax1, "Masa del Cohete", "Tiempo (s)", "Masa (kg)")

        ax2 = fig.add_subplot(2, 2, 2)
        if 'CGs' in df and 'CPs' in df:
            ax2.plot(t, df['CGs'], color='#6bcb77', label='CG', linewidth=1.2)
            ax2.plot(t, df['CPs'], color='#ff6b6b', label='CP', linewidth=1.2)
            ax2.legend(fontsize=8, facecolor='#1a1a2e', edgecolor='#555', labelcolor='white')
        self._style_axis(ax2, "Centro de Gravedad y Presion", "Tiempo (s)", "Posicion (m)")

        ax3 = fig.add_subplot(2, 2, 3)
        if 'thetas' in df:
            ax3.plot(t, np.degrees(df['thetas']), color='#c084fc', linewidth=1.0)
        self._style_axis(ax3, "Angulo Pitch", "Tiempo (s)", "Theta (deg)")

        ax4 = fig.add_subplot(2, 2, 4)
        if 'omegas' in df:
            ax4.plot(t, np.degrees(df['omegas']), color='#00d4ff', linewidth=1.0)
        self._style_axis(ax4, "Velocidad Angular", "Tiempo (s)", "Omega (deg/s)")

        fig.tight_layout(pad=2.0)
        self._show_figure(fig)

    # ---------- Exportacion ----------
    def export_csv(self):
        if self.simulation_df is None:
            messagebox.showwarning("Sin Datos", "Ejecute una simulacion primero.")
            return
        now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            initialfile=f"simulacion_{now}.csv",
            filetypes=[("CSV Files", "*.csv")],
            title="Exportar Datos CSV")
        if not filepath:
            return
        try:
            self.simulation_df.to_csv(filepath, index=False)
            messagebox.showinfo("Exportado", f"Datos guardados en:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar CSV:\n{e}")

    def export_json(self):
        if self.simulation_df is None:
            messagebox.showwarning("Sin Datos", "Ejecute una simulacion primero.")
            return
        df = self.simulation_df
        now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            initialfile=f"resumen_{now}.json",
            filetypes=[("JSON Files", "*.json")],
            title="Exportar Resumen JSON")
        if not filepath:
            return
        try:
            vel = np.sqrt(df['vx']**2 + df['vy']**2 + df['vz']**2)
            summary = {
                "fecha_simulacion": now,
                "apogeo_m": float(df['z'].max()),
                "velocidad_maxima_ms": float(vel.max()),
                "mach_maximo": float(df['Machs'].max()) if 'Machs' in df else 0,
                "aceleracion_maxima_g": float(df['accels'].max() / 9.81) if 'accels' in df else 0,
                "distancia_impacto_m": float(np.sqrt(df['x'].iloc[-1]**2 + df['y'].iloc[-1]**2)),
                "tiempo_vuelo_s": float(df['t'].iloc[-1]),
                "masa_inicial_kg": float(df['masavuelo'].iloc[0]) if 'masavuelo' in df else 0,
                "masa_final_kg": float(df['masavuelo'].iloc[-1]) if 'masavuelo' in df else 0,
            }
            with open(filepath, 'w') as f:
                json.dump(summary, f, indent=4)
            messagebox.showinfo("Exportado", f"Resumen guardado en:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar JSON:\n{e}")

    def export_plots(self):
        if self.simulation_df is None:
            messagebox.showwarning("Sin Datos", "Ejecute una simulacion primero.")
            return
        dirpath = filedialog.askdirectory(title="Seleccionar carpeta para guardar graficas")
        if not dirpath:
            return
        try:
            df = self.simulation_df
            plot_methods = [
                ("resumen", self._draw_summary_plots),
                ("fuerzas", self._draw_forces_plots),
                ("aerodinamica", self._draw_aero_plots),
                ("trayectoria_3d", self._draw_3d_trajectory),
                ("masa_cg_cp", self._draw_mass_cg_plots),
            ]
            saved = []
            for name, method in plot_methods:
                method(df)
                if self.canvas:
                    fpath = os.path.join(dirpath, f"{name}.png")
                    self.canvas.figure.savefig(fpath, dpi=200, bbox_inches='tight',
                                                facecolor=self.canvas.figure.get_facecolor())
                    saved.append(fpath)
            messagebox.showinfo("Graficas Guardadas",
                                f"Se guardaron {len(saved)} graficas en:\n{dirpath}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron guardar las graficas:\n{e}")



# =============================================================================
# Pestana: Estabilidad (CG/CP)
# =============================================================================
class StabilityTab(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.configure(fg_color=ColorPalette.BG_FRAME)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Controles superiores
        control_frame = customtkinter.CTkFrame(self)
        control_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.calc_button = customtkinter.CTkButton(
            control_frame, text="Calcular CG y CP",
            command=self.calculate_stability, fg_color=ColorPalette.ACCENT_VIOLET)
        self.calc_button.pack(side="left", padx=10, pady=10)

        # Semaforo de estabilidad
        self.stability_indicator = customtkinter.CTkLabel(
            control_frame, text="  ESTABILIDAD: --  ",
            font=customtkinter.CTkFont(size=14, weight="bold"),
            corner_radius=8, fg_color="#555")
        self.stability_indicator.pack(side="left", padx=10, pady=10)

        # Tabla de componentes
        self.table_frame = customtkinter.CTkFrame(self)
        self.table_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.table_frame.grid_columnconfigure(0, weight=1)
        self.table_frame.grid_rowconfigure(0, weight=1)
        self.create_table()

        # Resumen
        summary_frame = customtkinter.CTkFrame(self)
        summary_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        summary_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        font_big = customtkinter.CTkFont(size=18, weight="bold")
        self.cg_total_label = customtkinter.CTkLabel(summary_frame, text="CG Total: -- m", font=font_big)
        self.cg_total_label.grid(row=0, column=0, padx=10, pady=10)
        self.cp_total_label = customtkinter.CTkLabel(summary_frame, text="CP Total: -- m", font=font_big)
        self.cp_total_label.grid(row=0, column=1, padx=10, pady=10)
        self.margin_label = customtkinter.CTkLabel(summary_frame, text="Margen Estatico: -- cal", font=font_big)
        self.margin_label.grid(row=0, column=2, padx=10, pady=10)
        self.mass_label = customtkinter.CTkLabel(summary_frame, text="Masa Total: -- kg", font=font_big)
        self.mass_label.grid(row=0, column=3, padx=10, pady=10)

    def create_table(self):
        style = ttk.Style(self)
        style.theme_use("default")
        style.configure("Treeview", background="#9BB6FF", foreground="black",
                         rowheight=25, fieldbackground="#F0F0F0")
        style.map("Treeview", background=[('selected', '#347083')])
        style.configure("Treeview.Heading", background="#D3D3D3",
                         font=('Calibri', 10, 'bold'))

        self.tree = ttk.Treeview(self.table_frame,
                                 columns=("Componente", "Masa", "CG", "CP", "CN"),
                                 show="headings")
        self.tree.heading("Componente", text="Componente")
        self.tree.heading("Masa", text="Masa (kg)")
        self.tree.heading("CG", text="CG (m)")
        self.tree.heading("CP", text="CP (m)")
        self.tree.heading("CN", text="CN")
        self.tree.column("Componente", width=150)
        self.tree.column("Masa", width=100)
        self.tree.column("CG", width=100)
        self.tree.column("CP", width=100)
        self.tree.column("CN", width=100)

        scrollbar = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

    def calculate_stability(self):
        app = self.winfo_toplevel()
        params = app.rocket_tab.get_params()
        if params is None:
            messagebox.showerror("Error", "Parametros del cohete no validos.")
            return

        for item in self.tree.get_children():
            self.tree.delete(item)

        # Calcular CG y CP de cada componente usando las formulas del backend
        total_mass = 0
        sum_mass_cg = 0
        sum_cn_cp = 0
        total_cn = 0
        component_data = []

        # Definir componentes con sus propiedades
        components_def = [
            ("Nariz", params.get('nose_mass', 0), 0.0,
             params.get('nose_len', 0) * 3/4, params.get('nose_len', 0) * 0.466, 2.0),
            ("Coples", params.get('coples_mass', 0), params.get('nose_len', 0),
             params.get('coples_len', 0) / 2, 0, 0),
            ("Tubo Recup.", params.get('tubo_recup_mass', 0),
             params.get('nose_len', 0) + params.get('coples_len', 0),
             params.get('tubo_recup_len', 0) / 2, 0, 0),
            ("Transferidor", params.get('transfer_mass', 0),
             params.get('nose_len', 0) + params.get('coples_len', 0) + params.get('tubo_recup_len', 0),
             params.get('transfer_len', 0) / 2, 0, 0),
            ("Tanque", params.get('tanque_vacio_mass', 0),
             sum([params.get(k, 0) for k in ['nose_len', 'coples_len', 'tubo_recup_len', 'transfer_len']]),
             params.get('tanque_vacio_len', 0) / 2, 0, 0),
            ("Oxidante", params.get('oxidante_mass', 0),
             sum([params.get(k, 0) for k in ['nose_len', 'coples_len', 'tubo_recup_len', 'transfer_len']]),
             params.get('tanque_vacio_len', 0) / 2, 0, 0),
        ]

        # Posicion acumulada para componentes posteriores
        pos_after_tank = sum([params.get(k, 0) for k in [
            'nose_len', 'coples_len', 'tubo_recup_len', 'transfer_len', 'tanque_vacio_len']])

        components_def.extend([
            ("Valvulas", params.get('valvulas_mass', 0), pos_after_tank,
             params.get('valvulas_len', 0) / 2, 0, 0),
            ("Camara Comb.", params.get('cc_mass', 0),
             pos_after_tank + params.get('valvulas_len', 0),
             params.get('cc_len', 0) / 2, 0, 0),
            ("Grano", params.get('grano_mass', 0),
             pos_after_tank + params.get('valvulas_len', 0),
             params.get('cc_len', 0) / 2, 0, 0),
        ])

        pos_cc_end = pos_after_tank + params.get('valvulas_len', 0) + params.get('cc_len', 0)

        # Aletas (tienen CN significativo)
        fin_num = int(params.get('fin_num', 4))
        fin_span = params.get('fin_span', 0.1)
        fin_cr = params.get('fin_root_chord', 0.2)
        fin_ct = params.get('fin_tip_chord', 0.1)
        fin_xr = 0.2
        rad_fus = diam_ext_val = params.get('nose_diam', 0.152) / 2

        # CN de aletas (formula Barrowman)
        try:
            raiz = np.sqrt(1 + (2 * fin_span / (fin_cr + fin_ct))**2)
            cn_fins = (1 + rad_fus / (fin_span + rad_fus)) * (
                (4 * fin_num * (fin_span / (rad_fus * 2))**2) / (1 + raiz))
        except (ZeroDivisionError, ValueError):
            cn_fins = 0

        # CP de aletas
        try:
            cp_fins = (fin_xr / 3) * ((fin_cr + 2 * fin_ct) / (fin_cr + fin_ct)) + \
                      (1 / 6) * ((fin_cr + fin_ct) - (fin_cr * fin_ct / (fin_cr + fin_ct)))
        except ZeroDivisionError:
            cp_fins = 0

        components_def.append(("Aletas", params.get('fin_mass', 0), pos_cc_end,
                                fin_cr / 2, cp_fins, cn_fins))

        # Boattail
        bt_df = params.get('bt_diam_front', 0.152)
        bt_dr = params.get('bt_diam_rear', 0.132)
        try:
            cn_bt = (2 / bt_df**2) * (bt_dr**2 - bt_df**2)
        except ZeroDivisionError:
            cn_bt = 0
        components_def.append(("Boattail", params.get('bt_mass', 0), pos_cc_end,
                                params.get('bt_len', 0) / 2, params.get('bt_len', 0) / 3, cn_bt))

        # Componentes internos
        components_def.extend([
            ("Avionica", params.get('avionics_mass', 0), params.get('avionics_pos_z', 0.2), 0.1, 0, 0),
            ("Carga Util", params.get('cu_mass', 0), params.get('cu_pos_z', 0.5), 0.15, 0, 0),
            ("Drogue", params.get('drogue_mass', 0), params.get('drogue_pos_z', 1.0), 0.08, 0, 0),
            ("Main", params.get('main_mass', 0), params.get('main_pos_z', 1.4), 0.15, 0, 0),
        ])

        for name, mass, pos_front, cg_local, cp_local, cn in components_def:
            cg_abs = pos_front + cg_local
            cp_abs = pos_front + cp_local if cn != 0 else 0
            total_mass += mass
            sum_mass_cg += mass * cg_abs
            if cn != 0:
                sum_cn_cp += cn * cp_abs
                total_cn += cn
            component_data.append((name, mass, cg_abs, cp_abs if cn != 0 else None, cn))

        # Insertar en tabla
        for name, mass, cg, cp, cn in component_data:
            self.tree.insert("", "end", values=(
                name, f"{mass:.3f}", f"{cg:.3f}",
                f"{cp:.3f}" if cp is not None else "N/A",
                f"{cn:.3f}" if cn != 0 else "0"))

        # Totales
        cg_total = sum_mass_cg / total_mass if total_mass > 0 else 0
        cp_total = sum_cn_cp / total_cn if total_cn > 0 else 0
        main_diam = params.get('nose_diam', 0.152)
        margin = (cp_total - cg_total) / main_diam if main_diam > 0 else 0

        self.cg_total_label.configure(text=f"CG Total: {cg_total:.3f} m")
        self.cp_total_label.configure(text=f"CP Total: {cp_total:.3f} m")
        self.margin_label.configure(text=f"Margen Estatico: {margin:.2f} cal")
        self.mass_label.configure(text=f"Masa Total: {total_mass:.2f} kg")

        # Semaforo de estabilidad
        if margin >= 1.5:
            self.stability_indicator.configure(
                text="  ESTABLE  ", fg_color=ColorPalette.STABILITY_OK, text_color="white")
        elif margin >= 1.0:
            self.stability_indicator.configure(
                text="  MARGINAL  ", fg_color=ColorPalette.STABILITY_WARN, text_color="black")
        else:
            self.stability_indicator.configure(
                text="  INESTABLE  ", fg_color=ColorPalette.STABILITY_DANGER, text_color="white")



# =============================================================================
# Pestana: Log de Consola
# =============================================================================
class LogTab(customtkinter.CTkFrame):
    """Panel de log/consola para registrar eventos de la simulacion."""
    def __init__(self, master):
        super().__init__(master)
        self.configure(fg_color=ColorPalette.BG_FRAME)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.text_widget = customtkinter.CTkTextbox(
            self, font=customtkinter.CTkFont(family="Consolas", size=12),
            fg_color="#0a0a1a", text_color="#00ff88", corner_radius=8)
        self.text_widget.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        btn_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")
        customtkinter.CTkButton(btn_frame, text="Limpiar Log",
                                command=self.clear, fg_color=ColorPalette.BUTTON_RED,
                                width=100).pack(side="left", padx=5)
        customtkinter.CTkButton(btn_frame, text="Copiar al Portapapeles",
                                command=self.copy_to_clipboard, width=160).pack(side="left", padx=5)

        self.log("=== Rocket-Sim UNAM - Log de Sesion ===")
        self.log(f"Sesion iniciada: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        if BACKEND_AVAILABLE:
            self.log("[OK] Backend cargado correctamente")
        else:
            self.log("[WARN] Backend no disponible - modo demo activo")
        if MAP_AVAILABLE:
            self.log("[OK] Mapa interactivo disponible")
        else:
            self.log("[WARN] tkintermapview no instalado - mapa deshabilitado")

    def log(self, message, level="INFO"):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        prefix = {"INFO": "[INFO]", "WARN": "[WARN]", "ERROR": "[ERROR]",
                  "OK": "[ OK ]", "SIM": "[SIM ]"}.get(level, "[INFO]")
        self.text_widget.insert("end", f"{timestamp} {prefix} {message}\n")
        self.text_widget.see("end")

    def clear(self):
        self.text_widget.delete("1.0", "end")
        self.log("Log limpiado")

    def copy_to_clipboard(self):
        content = self.text_widget.get("1.0", "end")
        self.clipboard_clear()
        self.clipboard_append(content)


# =============================================================================
# Aplicacion Principal
# =============================================================================
class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.configure(fg_color=ColorPalette.BG_FRAME)
        self.title("Simulador de Trayectoria de Cohetes - Propulsion UNAM")
        self.geometry("1400x900")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        customtkinter.set_appearance_mode("Dark")
        customtkinter.set_default_color_theme("dark-blue")

        # --- Layout principal ---
        self.main_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.main_frame.grid_rowconfigure(0, weight=1)

        self.left_frame = customtkinter.CTkFrame(self.main_frame)
        self.left_frame.grid(row=0, column=0, sticky="nsew")
        self.left_frame.grid_rowconfigure(0, weight=1)
        self.left_frame.grid_columnconfigure(0, weight=1)

        self.right_frame = customtkinter.CTkFrame(self.main_frame)
        self.right_frame.grid_rowconfigure(1, weight=1)
        self.right_frame.grid_columnconfigure(0, weight=1)

        # --- Pestanas ---
        self.tab_view = customtkinter.CTkTabview(self.left_frame, command=self._on_tab_change)
        self.tab_view.grid(row=0, column=0, sticky="nsew")
        self.tab_view.add("Cohete")
        self.tab_view.add("Tablas de Datos")
        self.tab_view.add("Simulacion")
        self.tab_view.add("Analisis (CG-CP)")
        self.tab_view.add("Resultados")
        self.tab_view.add("Log")

        self.rocket_tab = RocketTab(self.tab_view.tab("Cohete"))
        self.rocket_tab.pack(expand=True, fill="both")

        self.data_tables_tab = DataTablesTab(self.tab_view.tab("Tablas de Datos"))
        self.data_tables_tab.pack(expand=True, fill="both")

        self.sim_env_tab = SimulationEnvironmentTab(self.tab_view.tab("Simulacion"))
        self.sim_env_tab.pack(expand=True, fill="both")

        self.stability_tab = StabilityTab(self.tab_view.tab("Analisis (CG-CP)"))
        self.stability_tab.pack(expand=True, fill="both")

        self.results_tab = ResultsTab(self.tab_view.tab("Resultados"))
        self.results_tab.pack(expand=True, fill="both")

        self.log_tab = LogTab(self.tab_view.tab("Log"))
        self.log_tab.pack(expand=True, fill="both")

        # --- Panel lateral: Visualizacion del cohete ---
        self.vis_label = customtkinter.CTkLabel(
            self.right_frame, text="Visualizacion del Cohete",
            font=customtkinter.CTkFont(size=16, weight="bold"))
        self.vis_label.grid(row=0, column=0, padx=10, pady=10)

        self.vis_canvas_frame = customtkinter.CTkFrame(self.right_frame)
        self.vis_canvas_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.vis_canvas_frame.grid_rowconfigure(0, weight=1)
        self.vis_canvas_frame.grid_columnconfigure(0, weight=1)

        # --- Barra de control inferior ---
        self.control_frame = customtkinter.CTkFrame(self, height=80)
        self.control_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")
        self.control_frame.grid_columnconfigure(1, weight=1)
        self.create_control_widgets()

        # Estado
        self.simulation_thread = None
        self.last_simulation_df = None
        self._on_tab_change()
        self.after(100, self.draw_rocket)

        # --- Atajos de teclado ---
        self.bind('<Control-r>', lambda e: self.run_simulation())
        self.bind('<Control-s>', lambda e: self.save_configuration())
        self.bind('<Control-o>', lambda e: self.load_configuration())
        self.bind('<F5>', lambda e: self.draw_rocket())

    def _on_tab_change(self):
        current = self.tab_view.get()
        if current == "Cohete":
            self.main_frame.grid_columnconfigure(0, weight=2)
            self.main_frame.grid_columnconfigure(1, weight=1, minsize=10)
            self.right_frame.grid(row=0, column=1, padx=(2, 0), sticky="nsew")
        else:
            self.right_frame.grid_remove()
            self.main_frame.grid_columnconfigure(0, weight=1)
            self.main_frame.grid_columnconfigure(1, weight=0)

    def create_control_widgets(self):
        button_frame = customtkinter.CTkFrame(self.control_frame)
        button_frame.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.run_button = customtkinter.CTkButton(
            button_frame, text="Ejecutar Simulacion",
            fg_color=ColorPalette.BUTTON_GREEN, command=self.run_simulation)
        self.run_button.pack(side="left", padx=5)
        ToolTip(self.run_button, "Ejecutar simulacion completa (Ctrl+R)")

        btn_update = customtkinter.CTkButton(
            button_frame, text="Actualizar Cohete",
            fg_color=ColorPalette.ACCENT_VIOLET, command=self.draw_rocket)
        btn_update.pack(side="left", padx=5)
        ToolTip(btn_update, "Redibujar el cohete con los parametros actuales (F5)")

        btn_save = customtkinter.CTkButton(
            button_frame, text="Guardar Config",
            command=self.save_configuration)
        btn_save.pack(side="left", padx=5)
        ToolTip(btn_save, "Guardar configuracion del cohete a JSON (Ctrl+S)")

        btn_load = customtkinter.CTkButton(
            button_frame, text="Cargar Config",
            command=self.load_configuration)
        btn_load.pack(side="left", padx=5)
        ToolTip(btn_load, "Cargar configuracion desde JSON (Ctrl+O)")

        btn_reset = customtkinter.CTkButton(
            button_frame, text="Resetear Defaults",
            fg_color=ColorPalette.BUTTON_RED, command=self.reset_defaults)
        btn_reset.pack(side="left", padx=5)
        ToolTip(btn_reset, "Restaurar valores predeterminados del Xitle II")

        # Barra de progreso y estado
        status_frame = customtkinter.CTkFrame(self.control_frame)
        status_frame.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        status_frame.grid_columnconfigure(0, weight=1)

        self.progress_bar = customtkinter.CTkProgressBar(status_frame)
        self.progress_bar.set(0)
        self.progress_bar.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

        self.status_label = customtkinter.CTkLabel(status_frame, text="Listo")
        self.status_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        # Indicador de backend
        backend_text = "Backend: Conectado" if BACKEND_AVAILABLE else "Backend: Demo"
        backend_color = ColorPalette.STABILITY_OK if BACKEND_AVAILABLE else ColorPalette.STABILITY_WARN
        self.backend_label = customtkinter.CTkLabel(
            status_frame, text=backend_text, text_color=backend_color,
            font=customtkinter.CTkFont(size=11))
        self.backend_label.grid(row=1, column=0, padx=10, pady=5, sticky="e")

    def collect_all_params(self):
        params_list = [self.rocket_tab.get_params(), self.sim_env_tab.get_params()]
        if any(p is None for p in params_list):
            return None
        all_params = {}
        for p in params_list:
            all_params.update(p)
        return all_params

    def run_simulation(self):
        # Validar parametros del cohete
        ok, msgs = self.rocket_tab.validate_params()
        if not ok:
            messagebox.showerror("Error de Validacion - Cohete",
                                 "Errores encontrados:\n\n" + "\n".join(msgs))
            self.log_tab.log("Simulacion cancelada: errores en parametros del cohete", "ERROR")
            return

        # Validar parametros de simulacion
        ok, msgs = self.sim_env_tab.validate_params()
        if not ok:
            messagebox.showerror("Error de Validacion - Simulacion",
                                 "Errores encontrados:\n\n" + "\n".join(msgs))
            self.log_tab.log("Simulacion cancelada: errores en parametros de simulacion", "ERROR")
            return

        params = self.collect_all_params()
        if params is None:
            messagebox.showerror("Error", "Revise los valores numericos.")
            return

        # Verificar archivos CSV
        thrust_path = self.data_tables_tab.filepaths.get('thrust', '')
        drag_path = self.data_tables_tab.filepaths.get('drag', '')

        if BACKEND_AVAILABLE and (not thrust_path or not drag_path):
            messagebox.showerror("Faltan Datos",
                                 "Cargue los archivos de Empuje y Arrastre en la pestana 'Tablas de Datos'.")
            self.log_tab.log("Simulacion cancelada: faltan archivos CSV", "ERROR")
            return

        if self.simulation_thread and self.simulation_thread.is_alive():
            messagebox.showwarning("Simulacion en Curso", "Espere a que termine la simulacion actual.")
            return

        self.run_button.configure(state="disabled")
        self.progress_bar.set(0)
        self.results_tab.show_placeholder_message()
        self.tab_view.set("Resultados")

        self.log_tab.log("Iniciando simulacion...", "SIM")
        self.log_tab.log(f"  Integrador: {params.get('integrator', 'DOP853')}", "SIM")
        self.log_tab.log(f"  dt = {params.get('sim_time_step', 0.01)} s, t_max = {params.get('sim_max_time', 400)} s", "SIM")

        self.simulation_thread = threading.Thread(
            target=self.simulation_worker, args=(params,), daemon=True)
        self.simulation_thread.start()

    def simulation_worker(self, params):
        try:
            data_tables = self.data_tables_tab.filepaths
            results = run_real_simulation(
                params, data_tables,
                lambda p: self.after(0, self.update_progress, p),
                lambda s: self.after(0, self.update_status, s))
            self.after(0, self.simulation_finished, results)
        except Exception as e:
            self.after(0, self.simulation_failed, e)

    def simulation_finished(self, results):
        self.run_button.configure(state="normal")
        self.last_simulation_df = results
        self.results_tab.display_results(results)

        # Log de resultados
        if results is not None and not results.empty:
            apogee = results['z'].max()
            vel = np.sqrt(results['vx']**2 + results['vy']**2 + results['vz']**2)
            self.log_tab.log(f"Simulacion completada exitosamente", "OK")
            self.log_tab.log(f"  Apogeo: {apogee:.1f} m", "SIM")
            self.log_tab.log(f"  Vel. Max: {vel.max():.1f} m/s", "SIM")
            self.log_tab.log(f"  Mach Max: {results['Machs'].max():.3f}", "SIM")
            self.log_tab.log(f"  Puntos de datos: {len(results)}", "SIM")

    def simulation_failed(self, error):
        self.run_button.configure(state="normal")
        self.update_status(f"Error: {error}")
        self.log_tab.log(f"Error en simulacion: {error}", "ERROR")
        messagebox.showerror("Error de Simulacion",
                             f"Ocurrio un error en el backend:\n\n{error}")

    def update_progress(self, value):
        self.progress_bar.set(value)

    def update_status(self, message):
        self.status_label.configure(text=message)
        self.log_tab.log(message, "SIM")

    def draw_rocket(self):
        params = self.rocket_tab.get_params()
        if params is None:
            messagebox.showerror("Error de Parametros", "No se puede dibujar el cohete.")
            return
        for widget in self.vis_canvas_frame.winfo_children():
            widget.destroy()

        fig = Figure(figsize=(5, 8), dpi=100, facecolor='#16213e')
        ax = fig.add_subplot(111)
        ax.set_aspect('equal', adjustable='box')
        ax.set_facecolor('#1a1a2e')

        components = [
            {'name': 'coples', 'len_key': 'coples_len', 'diam_key': 'coples_diam_ext', 'color': "#FFFFFF"},
            {'name': 'tubo_recup', 'len_key': 'tubo_recup_len', 'diam_key': 'tubo_recup_diam_ext', 'color': '#ADD8E6'},
            {'name': 'transfer', 'len_key': 'transfer_len', 'diam_key': 'transfer_diam_ext', 'color': '#87CEEB'},
            {'name': 'tanque', 'len_key': 'tanque_vacio_len', 'diam_key': 'tanque_vacio_diam_ext', 'color': '#6495ED'},
            {'name': 'valvulas', 'len_key': 'valvulas_len', 'diam_key': 'valvulas_diam_ext', 'color': '#4682B4'},
            {'name': 'cc', 'len_key': 'cc_len', 'diam_key': 'cc_diam_ext', 'color': '#5F9EA0'},
        ]

        # Dibujar componentes de abajo hacia arriba (nariz arriba)
        # Primero calcular posiciones secuenciales
        current_z = 0
        positions = {}

        nose_len = params.get('nose_len', 0.81)
        nose_diam = params.get('nose_diam', 0.152)
        positions['nose'] = current_z
        current_z += nose_len

        for comp in components:
            length = params.get(comp['len_key'], 0)
            diam = params.get(comp['diam_key'], 0)
            positions[comp['name']] = current_z
            ax.add_patch(patches.Rectangle((-diam/2, current_z), diam, length,
                                            facecolor=comp['color'], edgecolor='black', linewidth=0.5))
            current_z += length

        # Nariz (triangulo en la punta)
        ax.add_patch(patches.Polygon(
            [(-nose_diam/2, positions['nose'] + nose_len),
             (nose_diam/2, positions['nose'] + nose_len),
             (0, positions['nose'])],
            facecolor='#D9534F', edgecolor='black', linewidth=0.5))

        # Boattail
        bt_len = params.get('bt_len', 0.12)
        bt_d1 = params.get('bt_diam_front', 0.152)
        bt_d2 = params.get('bt_diam_rear', 0.132)
        ax.add_patch(patches.Polygon(
            [(-bt_d1/2, current_z), (bt_d1/2, current_z),
             (bt_d2/2, current_z + bt_len), (-bt_d2/2, current_z + bt_len)],
            facecolor='#5BC0DE', edgecolor='black', linewidth=0.5))

        # Aletas
        if params.get('fin_num', 0) >= 3:
            fin_pos = current_z - params.get('cc_len', 0.43)
            root_c = params.get('fin_root_chord', 0.3)
            tip_c = params.get('fin_tip_chord', 0.1)
            span = params.get('fin_span', 0.11)
            body_diam = params.get('cc_diam_ext', 0.152)
            sweep_dist = (root_c - tip_c) / 2

            fin_right = [(body_diam/2, fin_pos), (body_diam/2, fin_pos + root_c),
                         (body_diam/2 + span, fin_pos + root_c - sweep_dist),
                         (body_diam/2 + span, fin_pos + sweep_dist)]
            ax.add_patch(patches.Polygon(fin_right, facecolor='#F0AD4E', edgecolor='black', linewidth=0.5))
            ax.add_patch(patches.Polygon([(-x, y) for x, y in fin_right],
                                          facecolor='#F0AD4E', edgecolor='black', linewidth=0.5))

        total_len = current_z + bt_len

        # Marcadores CG y CP (estimados)
        # CG: estimacion rapida basada en masas
        try:
            total_mass = sum(params.get(k, 0) for k in params if '_mass' in k and isinstance(params.get(k, 0), (int, float)))
            if total_mass > 0:
                cg_est = total_len * 0.55  # Estimacion simplificada
                cp_est = total_len * 0.65  # CP mas atras que CG
                ax.axhline(y=cg_est, color='lime', linestyle='-', linewidth=1.5, alpha=0.7)
                ax.annotate(' CG', (nose_diam/2 + 0.01, cg_est), color='lime', fontsize=9, fontweight='bold')
                ax.axhline(y=cp_est, color='red', linestyle='-', linewidth=1.5, alpha=0.7)
                ax.annotate(' CP', (nose_diam/2 + 0.01, cp_est), color='red', fontsize=9, fontweight='bold')
        except Exception:
            pass

        max_diam = nose_diam * 2
        ax.set_xlim(-max_diam, max_diam)
        ax.set_ylim(-0.1, total_len + 0.2)
        ax.grid(True, linestyle='--', alpha=0.2, color='#555')
        ax.set_title("Esquema del Cohete", color='white', fontweight='bold')
        ax.tick_params(colors='#aaa')
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.vis_canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        self.log_tab.log("Dibujo del cohete actualizado", "OK")

    def save_configuration(self):
        params = self.collect_all_params()
        if params is None:
            messagebox.showerror("Error", "No se pueden guardar datos invalidos.")
            return
        # Incluir paths de archivos CSV
        params['_csv_thrust'] = self.data_tables_tab.filepaths.get('thrust', '')
        params['_csv_drag'] = self.data_tables_tab.filepaths.get('drag', '')
        params['_csv_mass'] = self.data_tables_tab.filepaths.get('mass', '')

        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json")],
            title="Guardar Configuracion")
        if not filepath:
            return
        try:
            with open(filepath, 'w') as f:
                json.dump(params, f, indent=4)
            self.update_status(f"Configuracion guardada en {os.path.basename(filepath)}")
            self.log_tab.log(f"Configuracion guardada: {filepath}", "OK")
        except Exception as e:
            messagebox.showerror("Error al Guardar", f"No se pudo guardar el archivo:\n{e}")

    def load_configuration(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("JSON Files", "*.json")], title="Cargar Configuracion")
        if not filepath:
            return
        try:
            with open(filepath, 'r') as f:
                params = json.load(f)

            all_widgets = {**self.rocket_tab.widgets, **self.sim_env_tab.widgets}
            loaded_count = 0
            for name, widget in all_widgets.items():
                if name not in params:
                    continue
                if isinstance(widget, customtkinter.CTkEntry):
                    widget.delete(0, "end")
                    widget.insert(0, str(params[name]))
                    widget.configure(border_width=0)
                    loaded_count += 1
                elif isinstance(widget, customtkinter.CTkOptionMenu):
                    try:
                        widget.set(params[name])
                        loaded_count += 1
                    except Exception:
                        pass

            self.update_status(f"Configuracion cargada desde {os.path.basename(filepath)}")
            self.log_tab.log(f"Configuracion cargada: {filepath} ({loaded_count} campos)", "OK")

            # Cargar CSVs referenciados
            for data_type, key in [("thrust", "_csv_thrust"), ("drag", "_csv_drag"), ("mass", "_csv_mass")]:
                csv_path = params.get(key, '')
                if csv_path and os.path.exists(csv_path):
                    self.data_tables_tab.load_csv(data_type, csv_path)
                    self.log_tab.log(f"  CSV cargado: {data_type} = {os.path.basename(csv_path)}", "OK")

            self.draw_rocket()
            self.sim_env_tab.update_map_position()
        except Exception as e:
            messagebox.showerror("Error al Cargar", f"No se pudo cargar el archivo:\n{e}")
            self.log_tab.log(f"Error al cargar configuracion: {e}", "ERROR")

    def reset_defaults(self):
        confirm = messagebox.askyesno("Confirmar Reset",
                                      "Desea restaurar todos los valores predeterminados del Xitle II?\n\n"
                                      "Esto reemplazara todos los valores actuales.")
        if confirm:
            self.rocket_tab.reset_to_defaults()
            self.draw_rocket()
            self.log_tab.log("Valores restaurados a defaults del Xitle II", "OK")


if __name__ == "__main__":
    app = App()
    app.mainloop()
