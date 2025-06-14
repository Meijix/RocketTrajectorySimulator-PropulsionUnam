import customtkinter
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import os
import json
import threading
import time
import pandas as pd
import numpy as np
import sys

# --- Matplotlib Integration ---
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.patches as patches

# --- Map Integration ---
# User needs to install this library: pip install tkintermapview
from tkintermapview import TkinterMapView

# --- Backend Integration (Temporarily Disabled) ---
# The following imports are commented out to run the GUI independently.
# try:
#     project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
#     if project_root not in sys.path:
#         sys.path.insert(0, project_root)

#     from Simulador.src.XitleFileMod import Cohete
#     from Simulador.src import condiciones_init
#     from Simulador.src import VueloLibre, VueloParacaidas
#     from Simulador.Resultados import listas_resultados
# except ImportError as e:
#     messagebox.showerror("Error de Backend", f"No se pudieron importar los módulos del simulador. Asegúrese de que la estructura de carpetas es correcta.\n\nError: {e}")
#     sys.exit()


# --- Placeholder Simulation Function ---
def placeholder_run_simulation(params, progress_callback, status_callback):
    """
    Placeholder for the simulation logic. Runs independently of the backend.
    """
    try:
        status_callback("Iniciando simulación de prueba...")
        print("Parámetros de Simulación Recibidos:", json.dumps(params, indent=2, sort_keys=True))
        
        # Simulate a process taking time
        for i in range(101):
            time.sleep(0.02)
            progress_callback(i / 100.0)

        status_callback("Simulación de prueba completada.")
        
        # Return dummy data for visualization
        results = {
            'apogee': np.random.uniform(3000, 4500), 
            'max_velocity': np.random.uniform(300, 400), 
            'landing_distance': np.random.uniform(500, 1500),
            'time': np.linspace(0, 100, 500).tolist(), 
            'altitude': (np.linspace(0, 100, 500) * 60 - 0.5 * np.linspace(0, 100, 500)**2).tolist(),
            'velocity': (60 - np.linspace(0, 100, 500)).tolist()
        }
        return results
    except Exception as e:
        raise e

class RocketTab(customtkinter.CTkScrollableFrame):
    """Tab for defining all physical components of the rocket based on Xitle configuration."""
    def __init__(self, master):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        self.widgets = {}

        # --- Main Sections ---
        self.external_components_frame = self.create_main_section_frame("Componentes Externos")
        self.internal_components_frame = self.create_main_section_frame("Componentes Internos")
        self.combustible_frame = self.create_main_section_frame("Combustibles")
        
        self.external_components_frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="col_ext")
        self.internal_components_frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="col_int")
        self.combustible_frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="col_comb")

        # --- Populate External Components ---
        self.create_nariz_frame(self.external_components_frame, column=0); self.create_coples_frame(self.external_components_frame, column=0)
        self.create_tubo_recuperacion_frame(self.external_components_frame, column=0); self.create_transferidor_frame(self.external_components_frame, column=1)
        self.create_tanque_vacio_frame(self.external_components_frame, column=1); self.create_valvulas_frame(self.external_components_frame, column=1)
        self.create_camara_combustion_frame(self.external_components_frame, column=2); self.create_boattail_frame(self.external_components_frame, column=2)
        self.create_aletas_frame(self.external_components_frame, column=2); self.create_avionica_frame(self.internal_components_frame, column=0)
        self.create_carga_util_frame(self.internal_components_frame, column=0); self.create_drogue_frame(self.internal_components_frame, column=1)
        self.create_main_chute_frame(self.internal_components_frame, column=1); self.create_motor_frame(self.internal_components_frame, column=0)
        self.create_oxidante_frame(self.combustible_frame, column=0); self.create_grano_frame(self.combustible_frame, column=1)

    def create_labeled_widget(self, master, w_type, name, label_text, default_value, row, values=None):
        label = customtkinter.CTkLabel(master, text=label_text); label.grid(row=row, column=0, padx=10, pady=(5,0), sticky="w")
        if w_type == "entry": widget = customtkinter.CTkEntry(master, placeholder_text=str(default_value)); widget.insert(0, str(default_value))
        elif w_type == "option": widget = customtkinter.CTkOptionMenu(master, values=values); widget.set(default_value)
        widget.grid(row=row, column=1, padx=10, pady=(5,0), sticky="ew"); self.widgets[name] = widget

    def create_main_section_frame(self, title):
        frame = customtkinter.CTkFrame(self); frame.grid(column=0, padx=10, pady=10, sticky="ew")
        frame_title = customtkinter.CTkLabel(frame, text=title, font=customtkinter.CTkFont(size=16, weight="bold"))
        frame_title.grid(row=0, column=0, columnspan=3, pady=(10,5), padx=10, sticky="w"); return frame

    def create_sub_frame(self, master, title, column):
        current_row = sum(1 for w in master.winfo_children() if isinstance(w, customtkinter.CTkFrame) and w.grid_info().get('column') == str(column))
        frame = customtkinter.CTkFrame(master); frame.grid(row=current_row + 1, column=column, padx=10, pady=10, sticky="new")
        frame.grid_columnconfigure(1, weight=1)
        frame_title = customtkinter.CTkLabel(frame, text=title, font=customtkinter.CTkFont(size=14, weight="bold"))
        frame_title.grid(row=0, column=0, columnspan=2, pady=(10, 5), padx=10, sticky="w"); return frame

    def create_nariz_frame(self, master, column):
        frame = self.create_sub_frame(master, "Nariz (Cono)", column)
        self.create_labeled_widget(frame, "entry", "nose_len", "Longitud (m):", 0.8, 1); self.create_labeled_widget(frame, "entry", "nose_mass", "Masa (kg):", 0.81, 2)
        self.create_labeled_widget(frame, "entry", "nose_pos_z", "Posición Z (m):", 4.3, 3); self.create_labeled_widget(frame, "entry", "nose_diam", "Diámetro (m):", 0.152, 4)
        self.create_labeled_widget(frame, "option", "nose_shape", "Geometría:", "ogiva", 5, ["ogiva", "Cónico", "Elíptico"])

    def create_coples_frame(self, master, column):
        frame = self.create_sub_frame(master, "Coples", column)
        self.create_labeled_widget(frame, "entry", "coples_len", "Longitud (m):", 1.5, 1); self.create_labeled_widget(frame, "entry", "coples_mass", "Masa (kg):", 0.176, 2)
        self.create_labeled_widget(frame, "entry", "coples_pos_z", "Posición Z (m):", 3.5, 3); self.create_labeled_widget(frame, "entry", "coples_diam_ext", "Diámetro Ext (m):", 0.152, 4)
        self.create_labeled_widget(frame, "entry", "coples_diam_int", "Diámetro Int (m):", 0.149, 5)

    def create_tubo_recuperacion_frame(self, master, column):
        frame = self.create_sub_frame(master, "Tubo Recuperación", column)
        self.create_labeled_widget(frame, "entry", "tubo_recup_len", "Longitud (m):", 2.3, 1); self.create_labeled_widget(frame, "entry", "tubo_recup_mass", "Masa (kg):", 0.92, 2)
        self.create_labeled_widget(frame, "entry", "tubo_recup_pos_z", "Posición Z (m):", 2.0, 3); self.create_labeled_widget(frame, "entry", "tubo_recup_diam_ext", "Diámetro Ext (m):", 0.152, 4)
        self.create_labeled_widget(frame, "entry", "tubo_recup_diam_int", "Diámetro Int (m):", 0.149, 5)

    def create_transferidor_frame(self, master, column):
        frame = self.create_sub_frame(master, "Transferidor", column)
        self.create_labeled_widget(frame, "entry", "transfer_len", "Longitud (m):", 1.0, 1); self.create_labeled_widget(frame, "entry", "transfer_mass", "Masa (kg):", 0.25, 2)
        self.create_labeled_widget(frame, "entry", "transfer_pos_z", "Posición Z (m):", 1.7, 3); self.create_labeled_widget(frame, "entry", "transfer_diam_ext", "Diámetro Ext (m):", 0.152, 4)
        self.create_labeled_widget(frame, "entry", "transfer_diam_int", "Diámetro Int (m):", 0.149, 5)

    def create_tanque_vacio_frame(self, master, column):
        frame = self.create_sub_frame(master, "Tanque Vacío", column)
        self.create_labeled_widget(frame, "entry", "tanque_vacio_len", "Longitud (m):", 8.7, 1); self.create_labeled_widget(frame, "entry", "tanque_vacio_mass", "Masa (kg):", 1.25, 2)
        self.create_labeled_widget(frame, "entry", "tanque_vacio_pos_z", "Posición Z (m):", 1.2, 3); self.create_labeled_widget(frame, "entry", "tanque_vacio_diam_ext", "Diámetro Ext (m):", 0.152, 4)
        self.create_labeled_widget(frame, "entry", "tanque_vacio_diam_int", "Diámetro Int (m):", 0.149, 5)

    def create_valvulas_frame(self, master, column):
        frame = self.create_sub_frame(master, "Válvulas", column)
        self.create_labeled_widget(frame, "entry", "valvulas_len", "Longitud (m):", 2.4, 1); self.create_labeled_widget(frame, "entry", "valvulas_mass", "Masa (kg):", 0.167, 2)
        self.create_labeled_widget(frame, "entry", "valvulas_pos_z", "Posición Z (m):", 0.8, 3); self.create_labeled_widget(frame, "entry", "valvulas_diam_ext", "Diámetro Ext (m):", 0.152, 4)
        self.create_labeled_widget(frame, "entry", "valvulas_diam_int", "Diámetro Int (m):", 0.149, 5)

    def create_camara_combustion_frame(self, master, column):
        frame = self.create_sub_frame(master, "Cámara de Combustión", column)
        self.create_labeled_widget(frame, "entry", "cc_len", "Longitud (m):", 4.3, 1); self.create_labeled_widget(frame, "entry", "cc_mass", "Masa (kg):", 0.573, 2)
        self.create_labeled_widget(frame, "entry", "cc_pos_z", "Posición Z (m):", 0.4, 3); self.create_labeled_widget(frame, "entry", "cc_diam_ext", "Diámetro Ext (m):", 0.152, 4)
        self.create_labeled_widget(frame, "entry", "cc_diam_int", "Diámetro Int (m):", 0.102, 5)

    def create_boattail_frame(self, master, column):
        frame = self.create_sub_frame(master, "Boattail", column)
        self.create_labeled_widget(frame, "entry", "bt_len", "Longitud (m):", 0.12, 1); self.create_labeled_widget(frame, "entry", "bt_mass", "Masa (kg):", 0.251, 2)
        self.create_labeled_widget(frame, "entry", "bt_pos_z", "Posición Z (m):", 0.0, 3); self.create_labeled_widget(frame, "entry", "bt_diam_front", "Diámetro Frontal (m):", 0.152, 4)
        self.create_labeled_widget(frame, "entry", "bt_diam_rear", "Diámetro Trasero (m):", 0.132, 5); self.create_labeled_widget(frame, "entry", "bt_espesor", "Espesor (m):", 0.003, 6)

    def create_aletas_frame(self, master, column):
        frame = self.create_sub_frame(master, "Aletas", column)
        self.create_labeled_widget(frame, "entry", "fin_num", "Número:", 4, 1); self.create_labeled_widget(frame, "entry", "fin_mass", "Masa Total (kg):", 1.1, 2)
        self.create_labeled_widget(frame, "entry", "fin_pos_z", "Posición Z (m):", 0.2, 3); self.create_labeled_widget(frame, "entry", "fin_span", "Envergadura (m):", 0.11, 4)
        self.create_labeled_widget(frame, "entry", "fin_root_chord", "Cuerda Raíz (m):", 0.3, 5); self.create_labeled_widget(frame, "entry", "fin_tip_chord", "Cuerda Punta (m):", 0.1, 6)
        self.create_labeled_widget(frame, "entry", "fin_sweep", "Ángulo de barrido (grados):", 25, 7)

    def create_avionica_frame(self, master, column):
        frame = self.create_sub_frame(master, "Aviónica", column)
        self.create_labeled_widget(frame, "entry", "avionics_mass", "Masa (kg):", 0.21, 1); self.create_labeled_widget(frame, "entry", "avionics_pos_z", "Posición Z (m):", 0.20, 2)
        
    def create_carga_util_frame(self, master, column):
        frame = self.create_sub_frame(master, "Carga Útil", column)
        self.create_labeled_widget(frame, "entry", "cu_mass", "Masa (kg):", 0.3, 1); self.create_labeled_widget(frame, "entry", "cu_pos_z", "Posición Z (m):", 0.50, 2)

    def create_drogue_frame(self, master, column):
        frame = self.create_sub_frame(master, "Drogue", column)
        self.create_labeled_widget(frame, "entry", "drogue_mass", "Masa (kg):", 0.17, 1); self.create_labeled_widget(frame, "entry", "drogue_pos_z", "Posición Z (m):", 1.0, 2)
        self.create_labeled_widget(frame, "entry", "drogue_chute_diam", "Diámetro Paracaídas (m):", 0.8, 3); self.create_labeled_widget(frame, "entry", "drogue_cd", "Cd Paracaídas:", 0.7, 4)

    def create_main_chute_frame(self, master, column):
        frame = self.create_sub_frame(master, "Main (Paracaídas)", column)
        self.create_labeled_widget(frame, "entry", "main_mass", "Masa (kg):", 0.30, 1); self.create_labeled_widget(frame, "entry", "main_pos_z", "Posición Z (m):", 1.4, 2)
        self.create_labeled_widget(frame, "entry", "main_chute_diam", "Diámetro Paracaídas (m):", 2.0, 3); self.create_labeled_widget(frame, "entry", "main_cd", "Cd Paracaídas:", 1.8, 4)
        self.create_labeled_widget(frame, "entry", "main_deploy_alt", "Alt. Despliegue (m):", 450, 5)

    def create_motor_frame(self, master, column):
        frame = self.create_sub_frame(master, "Motor (Masa)", column)
        self.create_labeled_widget(frame, "entry", "motor_mass_inert", "Masa Inerte (kg):", 3.2, 1); self.create_labeled_widget(frame, "entry", "motor_pos_z", "Posición (m):", 0.45, 2)
    
    def create_oxidante_frame(self, master, column):
        frame = self.create_sub_frame(master, "Oxidante (NOX)", column)
        self.create_labeled_widget(frame, "entry", "oxidante_mass", "Masa (kg):", 12.0, 1)

    def create_grano_frame(self, master, column):
        frame = self.create_sub_frame(master, "Grano (Combustible Sólido)", column)
        self.create_labeled_widget(frame, "entry", "grano_mass", "Masa (kg):", 4.0, 1)

    def get_params(self):
        params = {}
        try:
            for name, widget in self.widgets.items():
                val = widget.get();
                try: params[name] = float(val) if '.' in val or 'e' in val.lower() else int(val)
                except (ValueError, TypeError): params[name] = val
            return params
        except Exception as e: print(f"Error al obtener parámetros: {e}"); return None
    
class SimulationEnvironmentTab(customtkinter.CTkScrollableFrame):
    def __init__(self, master):
        super().__init__(master)
        self.grid_columnconfigure((0, 1), weight=1, uniform="col")
        self.widgets = {}
        self.create_launch_site_frame(column=0); self.create_wind_frame(column=0)
        self.create_rail_frame(column=1); self.create_simulation_frame(column=1)
        self.create_motor_performance_frame(column=1)
    
    def create_labeled_widget(self, master, w_type, name, label_text, default_value, row, values=None):
        label = customtkinter.CTkLabel(master, text=label_text); label.grid(row=row, column=0, padx=10, pady=5, sticky="w")
        if w_type == "entry": widget = customtkinter.CTkEntry(master, placeholder_text=str(default_value)); widget.insert(0, str(default_value))
        elif w_type == "option": widget = customtkinter.CTkOptionMenu(master, values=values); widget.set(default_value)
        elif w_type == "switch": widget = customtkinter.CTkSwitch(master, text=label_text); label.grid_forget()
        widget.grid(row=row, column=1, padx=10, pady=5, sticky="ew"); self.widgets[name] = widget

    def create_frame(self, title, column):
        current_row = sum(1 for w in self.winfo_children() if isinstance(w, customtkinter.CTkFrame) and w.grid_info().get('column') == str(column))
        frame = customtkinter.CTkFrame(self); frame.grid(row=current_row, column=column, padx=10, pady=10, sticky="new")
        frame.grid_columnconfigure(1, weight=1)
        title = customtkinter.CTkLabel(frame, text=title, font=customtkinter.CTkFont(size=14, weight="bold"))
        title.grid(row=0, column=0, columnspan=2, pady=(10, 5), padx=10, sticky="w"); return frame

    def create_launch_site_frame(self, column):
        frame = self.create_frame("Parámetros del Sitio de Lanzamiento", column)
        self.create_labeled_widget(frame, "entry", "launch_lat", "Latitud:", 19.5, 1); self.create_labeled_widget(frame, "entry", "launch_lon", "Longitud:", -98.8, 2)
        self.create_labeled_widget(frame, "entry", "launch_alt", "Altitud (m):", 1400, 3); self.create_labeled_widget(frame, "entry", "launch_date", "Fecha (YYYY-MM-DD):", "2024-11-06", 4)
        map_frame = customtkinter.CTkFrame(frame); map_frame.grid(row=5, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        map_frame.grid_columnconfigure(0, weight=1); map_frame.grid_rowconfigure(0, weight=1)
        self.map_widget = TkinterMapView(map_frame, width=300, height=200, corner_radius=10); self.map_widget.pack(fill="both", expand=True)
        self.map_widget.set_position(19.5, -98.8); self.map_widget.set_marker(19.5, -98.8)
        update_map_button = customtkinter.CTkButton(frame, text="Actualizar Mapa", command=self.update_map); update_map_button.grid(row=6, column=0, columnspan=2, padx=10, pady=(0,10))

    def update_map(self):
        try: lat = float(self.widgets['launch_lat'].get()); lon = float(self.widgets['launch_lon'].get()); self.map_widget.set_position(lat, lon, marker=True); self.map_widget.set_zoom(12)
        except ValueError: messagebox.showerror("Error de Coordenadas", "Latitud y longitud deben ser valores numéricos.")

    def create_rail_frame(self, column):
        frame = self.create_frame("Parámetros del Riel de Lanzamiento", column)
        self.create_labeled_widget(frame, "entry", "rail_len", "Longitud (m):", 6.0, 1); self.create_labeled_widget(frame, "entry", "rail_angle", "Ángulo (grados):", 85.0, 2)

    def create_wind_frame(self, column):
        frame = self.create_frame("Parámetros del Viento", column)
        self.create_labeled_widget(frame, "entry", "wind_base_speed", "Velocidad base (m/s):", 5, 1); self.create_labeled_widget(frame, "entry", "wind_mean_speed", "Velocidad media (m/s):", 3, 2)
        self.create_labeled_widget(frame, "entry", "wind_speed_var", "Variación de velocidad:", 2, 3); self.create_labeled_widget(frame, "entry", "wind_angle_var", "Variación de ángulo (grados):", 10.0, 4)

    def create_simulation_frame(self, column):
        frame = self.create_frame("Parámetros de Simulación", column)
        self.create_labeled_widget(frame, "entry", "sim_max_time", "Tiempo máximo (s):", 800, 1); self.create_labeled_widget(frame, "entry", "sim_time_step", "Paso de tiempo (s):", 0.01, 2)
        self.create_labeled_widget(frame, "option", "integrator", "Integrador:", "DOP853", 3, ["DOP853", "RK45", "RK23", "Euler"])
        self.create_labeled_widget(frame, "switch", "use_parachutes", "Simular con Paracaídas", True, 4)

    def create_motor_performance_frame(self, column):
        frame = self.create_frame("Motor (Rendimiento)", column)
        self.create_labeled_widget(frame, "entry", "propellant_mass", "Masa de Propelente (kg):", 4.88, 1)
        script_dir = os.path.dirname(__file__); thrust_curves_path = os.path.join(script_dir, "..", "..", "Archivos", "CurvasEmpuje")
        try:
            thrust_files = [f for f in os.listdir(thrust_curves_path) if f.endswith(('.csv', '.eng'))] if os.path.isdir(thrust_curves_path) else []
            if not thrust_files: thrust_files = ["No se encontraron archivos"]
        except FileNotFoundError: thrust_files = ["Directorio no encontrado"]
        self.create_labeled_widget(frame, "option", "thrust_curve", "Curva de Empuje:", thrust_files[0] if "No" not in thrust_files[0] else "", 2, thrust_files)

    def get_params(self):
        params = {}
        try:
            for name, widget in self.widgets.items():
                val = widget.get()
                if isinstance(widget, customtkinter.CTkSwitch): params[name] = bool(val)
                else:
                    try: params[name] = float(val) if '.' in val else int(val)
                    except (ValueError, TypeError): params[name] = val
            return params
        except Exception: return None

class DataTablesTab(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1); self.grid_rowconfigure(2, weight=1)
        self.dataframes = {"thrust": None, "drag": None, "mass": None}
        self.filepaths = {"thrust": "No cargado", "drag": "No cargado", "mass": "No cargado"}
        self.top_frame = customtkinter.CTkFrame(self); self.top_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10); self.top_frame.grid_columnconfigure((0,1,2), weight=1)
        self.mid_frame = customtkinter.CTkFrame(self); self.mid_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0,10)); self.mid_frame.grid_columnconfigure((0,1,2), weight=1)
        self.plot_frame = customtkinter.CTkFrame(self, fg_color="#E5E5E5"); self.plot_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
        self.plot_frame.grid_columnconfigure(0, weight=1); self.plot_frame.grid_rowconfigure(0, weight=1); self.canvas = None
        self.create_importers(); self.show_placeholder_message()

    def create_importers(self):
        btn1=customtkinter.CTkButton(self.top_frame,text="Importar Empuje (T vs t)",command=lambda:self.load_csv("thrust"));self.lbl1=customtkinter.CTkLabel(self.mid_frame,text="Empuje: No cargado");btn2=customtkinter.CTkButton(self.mid_frame,text="Visualizar Empuje",command=lambda:self.visualize_data("thrust"))
        btn1.grid(row=0,column=0,padx=5,pady=5,sticky="ew");self.lbl1.grid(row=0,column=0,padx=5,pady=5);btn2.grid(row=1,column=0,padx=5,pady=5)
        btn3=customtkinter.CTkButton(self.top_frame,text="Importar Arrastre (Cd vs Mach)",command=lambda:self.load_csv("drag"));self.lbl2=customtkinter.CTkLabel(self.mid_frame,text="Cd_vs_mach: No cargado");btn4=customtkinter.CTkButton(self.mid_frame,text="Visualizar Arrastre",command=lambda:self.visualize_data("drag"))
        btn3.grid(row=0,column=1,padx=5,pady=5,sticky="ew");self.lbl2.grid(row=0,column=1,padx=5,pady=5);btn4.grid(row=1,column=1,padx=5,pady=5)
        btn5=customtkinter.CTkButton(self.top_frame,text="Importar Masa (M vs t)",command=lambda:self.load_csv("mass"));self.lbl3=customtkinter.CTkLabel(self.mid_frame,text="Masa: No cargado");btn6=customtkinter.CTkButton(self.mid_frame,text="Visualizar Masa",command=lambda:self.visualize_data("mass"))
        btn5.grid(row=0,column=2,padx=5,pady=5,sticky="ew");self.lbl3.grid(row=0,column=2,padx=5,pady=5);btn6.grid(row=1,column=2,padx=5,pady=5)

    def load_csv(self, data_type, filepath=None):
        if filepath is None: filepath = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")], title=f"Importar {data_type}")
        if not filepath: return
        try:
            df = pd.read_csv(filepath, header=None, names=['x', 'y'], comment='#', skip_blank_lines=True, on_bad_lines='skip').apply(pd.to_numeric, errors='coerce').dropna()
            self.dataframes[data_type] = df; self.filepaths[data_type] = filepath
            if data_type=="thrust":self.lbl1.configure(text=f"Empuje: {os.path.basename(filepath)}")
            elif data_type=="drag":self.lbl2.configure(text=f"Cd_vs_mach: {os.path.basename(filepath)}")
            elif data_type=="mass":self.lbl3.configure(text=f"Masa: {os.path.basename(filepath)}")
            self.visualize_data(data_type)
        except Exception as e: messagebox.showerror("Error al Cargar CSV", f"No se pudo leer el archivo.\nError: {e}")

    def show_placeholder_message(self):
        for w in self.plot_frame.winfo_children():w.destroy()
        customtkinter.CTkLabel(self.plot_frame,text="Seleccione un tipo de dato para visualizar la gráfica.",font=customtkinter.CTkFont(size=16)).pack(expand=True);self.canvas=None
        
    def visualize_data(self, data_type):
        df = self.dataframes.get(data_type)
        if df is None: messagebox.showwarning("Sin Datos", f"Cargue un archivo para '{data_type}'."); return
        for w in self.plot_frame.winfo_children():w.destroy()
        fig=Figure(figsize=(8,6),dpi=100,facecolor="#FFFFFF");ax=fig.add_subplot(111)
        titles={"thrust":"Curva de Empuje","drag":"Curva de Arrastre","mass":"Curva de Masa"}; x_labels={"thrust":"Tiempo (s)","drag":"Mach","mass":"Tiempo (s)"}; y_labels={"thrust":"Empuje (N)","drag":"Cd","mass":"Masa (kg)"}
        ax.plot(df['x'],df['y'],marker='.',linestyle='-',markersize=3,color='#0078D7'); ax.set_title(titles[data_type]);ax.set_xlabel(x_labels[data_type]);ax.set_ylabel(y_labels[data_type])
        ax.grid(True,linestyle='--',alpha=0.6);fig.tight_layout()
        self.canvas=FigureCanvasTkAgg(fig,master=self.plot_frame);self.canvas.draw();self.canvas.get_tk_widget().pack(fill="both",expand=True)

class ResultsTab(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1); self.grid_rowconfigure(0, weight=1)
        self.plot_frame=customtkinter.CTkFrame(self); self.plot_frame.grid(row=0,column=0,sticky="nsew",padx=10,pady=10)
        self.plot_frame.grid_columnconfigure(0,weight=1); self.plot_frame.grid_rowconfigure(0,weight=1)
        self.summary_frame=customtkinter.CTkFrame(self,height=100); self.summary_frame.grid(row=1,column=0,sticky="ew",padx=10,pady=(0,10))
        self.summary_frame.grid_columnconfigure((0,1,2),weight=1); self.canvas,self.toolbar=None,None
        self.create_summary_widgets(); self.show_placeholder_message()

    def create_summary_widgets(self):
        self.apogee_label=customtkinter.CTkLabel(self.summary_frame,text="Apogeo: -- m",font=customtkinter.CTkFont(size=14,weight="bold")); self.apogee_label.grid(row=0,column=0,pady=10)
        self.max_vel_label=customtkinter.CTkLabel(self.summary_frame,text="Vel. Máxima: -- m/s",font=customtkinter.CTkFont(size=14,weight="bold")); self.max_vel_label.grid(row=0,column=1,pady=10)
        self.landing_dist_label=customtkinter.CTkLabel(self.summary_frame,text="Dist. Aterrizaje: -- m",font=customtkinter.CTkFont(size=14,weight="bold")); self.landing_dist_label.grid(row=0,column=2,pady=10)

    def show_placeholder_message(self):
        if self.canvas:self.canvas.get_tk_widget().destroy()
        if self.toolbar:self.toolbar.destroy()
        for w in self.plot_frame.winfo_children():w.destroy()
        customtkinter.CTkLabel(self.plot_frame,text="Los resultados de la simulación se mostrarán aquí.",font=customtkinter.CTkFont(size=16)).grid(row=0,column=0,sticky="nsew")

    def display_results(self, results):
        self.show_placeholder_message()
        self.apogee_label.configure(text=f"Apogeo: {results['apogee']:.2f} m"); self.max_vel_label.configure(text=f"Vel. Máxima: {results['max_velocity']:.2f} m/s")
        self.landing_dist_label.configure(text=f"Dist. Aterrizaje: {results['landing_distance']:.2f} m")
        fig=Figure(figsize=(8,6),dpi=100);ax1=fig.add_subplot(211);ax1.plot(results['time'],results['altitude'],color='#0078D7');ax1.set_title("Altitud vs. Tiempo")
        ax1.set(xlabel="Tiempo (s)",ylabel="Altitud (m)");ax1.grid(True,linestyle='--',alpha=0.6)
        ax2=fig.add_subplot(212);ax2.plot(results['time'],results['velocity'],color='#D9534F');ax2.set_title("Velocidad vs. Tiempo")
        ax2.set(xlabel="Tiempo (s)",ylabel="Velocidad (m/s)");ax2.grid(True,linestyle='--',alpha=0.6);fig.tight_layout(pad=3.0)
        self.canvas=FigureCanvasTkAgg(fig,master=self.plot_frame);self.canvas.draw();canvas_widget=self.canvas.get_tk_widget();canvas_widget.grid(row=0,column=0,sticky="nsew")
        self.toolbar=NavigationToolbar2Tk(self.canvas,self.plot_frame,pack_toolbar=False); self.toolbar.update();self.toolbar.grid(row=1,column=0,sticky="ew")

class StabilityTab(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1); self.grid_rowconfigure(1, weight=1)
        control_frame = customtkinter.CTkFrame(self); control_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.calc_button = customtkinter.CTkButton(control_frame, text="Calcular CG y CP", command=self.calculate_stability); self.calc_button.pack(side="left", padx=10, pady=10)
        self.table_frame = customtkinter.CTkFrame(self); self.table_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.table_frame.grid_columnconfigure(0, weight=1); self.table_frame.grid_rowconfigure(0, weight=1); self.create_table()
        summary_frame = customtkinter.CTkFrame(self); summary_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew"); summary_frame.grid_columnconfigure((0, 1, 2), weight=1)
        self.cg_total_label = customtkinter.CTkLabel(summary_frame, text="CG Total: -- m", font=customtkinter.CTkFont(size=14, weight="bold")); self.cg_total_label.grid(row=0, column=0, padx=10, pady=10)
        self.cp_total_label = customtkinter.CTkLabel(summary_frame, text="CP Total: -- m", font=customtkinter.CTkFont(size=14, weight="bold")); self.cp_total_label.grid(row=0, column=1, padx=10, pady=10)
        self.margin_label = customtkinter.CTkLabel(summary_frame, text="Margen Estático: -- cal", font=customtkinter.CTkFont(size=14, weight="bold")); self.margin_label.grid(row=0, column=2, padx=10, pady=10)

    def create_table(self):
        style = ttk.Style(self); style.theme_use("default")
        style.configure("Treeview", background="#F0F0F0", foreground="black", rowheight=25, fieldbackground="#F0F0F0")
        style.map("Treeview", background=[('selected', '#347083')]); style.configure("Treeview.Heading", background="#D3D3D3", font=('Calibri', 10,'bold'))
        self.tree = ttk.Treeview(self.table_frame, columns=("Masa", "CG", "CP"), show="headings")
        self.tree.heading("Masa", text="Masa (kg)"); self.tree.heading("CG", text="Centro de Gravedad (m)"); self.tree.heading("CP", text="Centro de Presión (m)")
        self.tree.grid(row=0, column=0, sticky="nsew")

    def calculate_stability(self):
        app = self.winfo_toplevel(); params = app.rocket_tab.get_params()
        if params is None: messagebox.showerror("Error", "Parámetros del cohete no válidos."); return
        for item in self.tree.get_children(): self.tree.delete(item)
        
        # --- Placeholder Calculation Logic ---
        total_mass=0; sum_mass_cg=0; sum_area_cp=0; total_area=1e-9; component_data={}
        for name, widget in app.rocket_tab.widgets.items():
            if "_mass" in name:
                comp_name=name.replace("_mass",""); mass=params.get(name,0); pos=params.get(f"{comp_name}_pos_z",np.random.uniform(0,4))
                cp=pos if "fin" in name or "nose" in name else 0; area=np.pi*(params.get(f"{comp_name}_diam",0.152)/2)**2 if cp>0 else 0
                component_data[comp_name.replace('_',' ').title()]=(mass,pos,cp); total_mass+=mass; sum_mass_cg+=mass*pos
                if cp > 0: sum_area_cp+=area*cp; total_area+=area
        for name,(mass,cg,cp) in component_data.items(): self.tree.insert("","end",values=(f"{mass:.3f}",f"{cg:.3f}",f"{cp:.3f}" if cp>0 else "N/A"),text=name)
        cg_total=sum_mass_cg/total_mass if total_mass>0 else 0; cp_total=sum_area_cp/total_area if total_area>0 else 0
        main_diam=params.get('nose_diam',0.152); margin=(cp_total-cg_total)/main_diam if main_diam>0 else 0
        self.cg_total_label.configure(text=f"CG Total: {cg_total:.3f} m"); self.cp_total_label.configure(text=f"CP Total: {cp_total:.3f} m")
        self.margin_label.configure(text=f"Margen Estático: {margin:.2f} cal")

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("Simulador de Trayectoria de Cohetes - Propulsion UNAM v3.3"); self.geometry("1400x900")
        self.grid_columnconfigure(0, weight=1); self.grid_rowconfigure(0, weight=1)
        customtkinter.set_appearance_mode("Light"); customtkinter.set_default_color_theme("blue")
        self.main_frame = customtkinter.CTkFrame(self, fg_color="transparent"); self.main_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.left_frame = customtkinter.CTkFrame(self.main_frame); self.left_frame.grid(row=0, column=0, sticky="nsew")
        self.left_frame.grid_rowconfigure(0, weight=1); self.left_frame.grid_columnconfigure(0, weight=1)
        self.right_frame = customtkinter.CTkFrame(self.main_frame); self.right_frame.grid_rowconfigure(1, weight=1); self.right_frame.grid_columnconfigure(0, weight=1)
        self.tab_view = customtkinter.CTkTabview(self.left_frame, command=self._on_tab_change); self.tab_view.grid(row=0, column=0, sticky="nsew")
        self.tab_view.add("Cohete"); self.tab_view.add("Tablas de Datos"); self.tab_view.add("Simulación y Entorno"); self.tab_view.add("Análisis (CG-CP)"); self.tab_view.add("Resultados")
        self.rocket_tab = RocketTab(self.tab_view.tab("Cohete")); self.rocket_tab.pack(expand=True, fill="both")
        self.data_tables_tab = DataTablesTab(self.tab_view.tab("Tablas de Datos")); self.data_tables_tab.pack(expand=True, fill="both")
        self.sim_env_tab = SimulationEnvironmentTab(self.tab_view.tab("Simulación y Entorno")); self.sim_env_tab.pack(expand=True, fill="both")
        self.stability_tab = StabilityTab(self.tab_view.tab("Análisis (CG-CP)")); self.stability_tab.pack(expand=True, fill="both")
        self.results_tab = ResultsTab(self.tab_view.tab("Resultados")); self.results_tab.pack(expand=True, fill="both")
        self.vis_label = customtkinter.CTkLabel(self.right_frame, text="Visualización del Cohete", font=customtkinter.CTkFont(size=16, weight="bold")); self.vis_label.grid(row=0, column=0, padx=10, pady=10)
        self.vis_canvas_frame = customtkinter.CTkFrame(self.right_frame); self.vis_canvas_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.vis_canvas_frame.grid_rowconfigure(0, weight=1); self.vis_canvas_frame.grid_columnconfigure(0, weight=1)
        self.control_frame = customtkinter.CTkFrame(self, height=80); self.control_frame.grid(row=1, column=0, padx=10, pady=(0,10), sticky="ew")
        self.control_frame.grid_columnconfigure(1, weight=1); self.create_control_widgets()
        self.simulation_thread = None; self._on_tab_change(); self.after(100, self.draw_rocket)

    def _on_tab_change(self):
        if self.tab_view.get() == "Cohete": self.main_frame.grid_columnconfigure(0, weight=2); self.main_frame.grid_columnconfigure(1, weight=1, minsize=300); self.right_frame.grid(row=0, column=1, padx=(10,0), sticky="nsew")
        else: self.right_frame.grid_remove(); self.main_frame.grid_columnconfigure(0, weight=1); self.main_frame.grid_columnconfigure(1, weight=0)

    def create_control_widgets(self):
        button_frame = customtkinter.CTkFrame(self.control_frame); button_frame.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.run_button = customtkinter.CTkButton(button_frame, text="Ejecutar Simulación", command=self.run_simulation); self.run_button.pack(side="left", padx=5)
        customtkinter.CTkButton(button_frame, text="Actualizar Cohete", command=self.draw_rocket).pack(side="left", padx=5)
        customtkinter.CTkButton(button_frame, text="Guardar Datos", command=self.save_configuration).pack(side="left", padx=5)
        customtkinter.CTkButton(button_frame, text="Cargar Datos", command=self.load_configuration).pack(side="left", padx=5)
        status_frame = customtkinter.CTkFrame(self.control_frame); status_frame.grid(row=0, column=1, padx=10, pady=10, sticky="ew"); status_frame.grid_columnconfigure(0, weight=1)
        self.progress_bar = customtkinter.CTkProgressBar(status_frame); self.progress_bar.set(0); self.progress_bar.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        self.status_label = customtkinter.CTkLabel(status_frame, text="Listo"); self.status_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

    def collect_all_params(self):
        params_list = [self.rocket_tab.get_params(), self.sim_env_tab.get_params()]
        if any(p is None for p in params_list): return None
        all_params = {}; [all_params.update(p) for p in params_list]
        all_params.update(self.data_tables_tab.filepaths); return all_params

    def run_simulation(self):
        params = self.collect_all_params()
        if params is None: messagebox.showerror("Error de Validación", "Revise los valores numéricos."); return
        if any(p == "No cargado" for p in [params['thrust'], params['drag']]): messagebox.showerror("Faltan Datos", "Cargue los archivos de Empuje y Arrastre."); return
        if self.simulation_thread and self.simulation_thread.is_alive(): messagebox.showwarning("Simulación en Curso", "Espere."); return
        self.run_button.configure(state="disabled"); self.progress_bar.set(0); self.results_tab.show_placeholder_message(); self.tab_view.set("Resultados")
        self.simulation_thread = threading.Thread(target=self.simulation_worker, args=(params,), daemon=True); self.simulation_thread.start()

    def simulation_worker(self, params):
        try: results = run_real_simulation(params, lambda p: self.after(0, self.update_progress, p), lambda s: self.after(0, self.update_status, s)); self.after(0, self.simulation_finished, results)
        except Exception as e: self.after(0, self.simulation_failed, e)

    def simulation_finished(self, results): self.run_button.configure(state="normal"); self.results_tab.display_results(results)
    def simulation_failed(self, error): self.run_button.configure(state="normal"); self.update_status(f"Error: {error}"); messagebox.showerror("Error de Simulación", f"Ocurrió un error en el backend:\n\n{error}")
    def update_progress(self, value): self.progress_bar.set(value)
    def update_status(self, message): self.status_label.configure(text=message)
        
    def draw_rocket(self):
        params = self.rocket_tab.get_params()
        if params is None: messagebox.showerror("Error de Parámetros", "No se puede dibujar el cohete."); return
        for widget in self.vis_canvas_frame.winfo_children(): widget.destroy()
        fig = Figure(figsize=(5, 8), dpi=100); ax = fig.add_subplot(111); ax.set_aspect('equal', adjustable='box')
        components = [
            {'name':'coples','len_key':'coples_len','pos_key':'coples_pos_z','diam_key':'coples_diam_ext','color':'#B0C4DE'},
            {'name':'tubo_recuperacion','len_key':'tubo_recup_len','pos_key':'tubo_recup_pos_z','diam_key':'tubo_recup_diam_ext','color':'#ADD8E6'},
            {'name':'transferidor','len_key':'transfer_len','pos_key':'transfer_pos_z','diam_key':'transfer_diam_ext','color':'#87CEEB'},
            {'name':'tanque_vacio','len_key':'tanque_vacio_len','pos_key':'tanque_vacio_pos_z','diam_key':'tanque_vacio_diam_ext','color':'#6495ED'},
            {'name':'valvulas','len_key':'valvulas_len','pos_key':'valvulas_pos_z','diam_key':'valvulas_diam_ext','color':'#4682B4'},
            {'name':'camara_combustion','len_key':'cc_len','pos_key':'cc_pos_z','diam_key':'cc_diam_ext','color':'#5F9EA0'},
        ]
        total_len = 0
        for comp in components:
            pos_z, length, diam = params.get(comp['pos_key'],0), params.get(comp['len_key'],0), params.get(comp['diam_key'],0)
            total_len = max(total_len, pos_z + length/2)
            ax.add_patch(patches.Rectangle((-diam/2, pos_z - length/2), diam, length, facecolor=comp['color'], edgecolor='black'))
        nose_len,nose_pos,nose_diam = params.get('nose_len',0),params.get('nose_pos_z',0),params.get('nose_diam',0)
        total_len=max(total_len,nose_pos+nose_len); ax.add_patch(patches.Polygon([(-nose_diam/2,nose_pos),(nose_diam/2,nose_pos),(0,nose_pos+nose_len)],facecolor='#D9534F',edgecolor='black'))
        bt_len,bt_pos,bt_d1,bt_d2 = params.get('bt_len',0),params.get('bt_pos_z',0),params.get('bt_diam_front',0),params.get('bt_diam_rear',0)
        ax.add_patch(patches.Polygon([(-bt_d1/2,bt_pos+bt_len),(bt_d1/2,bt_pos+bt_len),(bt_d2/2,bt_pos),(-bt_d2/2,bt_pos)],facecolor='#5BC0DE',edgecolor='black'))
        if params.get('fin_num',0)>0:
            fin_pos,root_c,tip_c,span=params.get('fin_pos_z',0),params.get('fin_root_chord',0),params.get('fin_tip_chord',0),params.get('fin_span',0)
            body_diam_at_fins = params.get('cc_diam_ext', 0.152); sweep_dist = (root_c-tip_c)/2
            fin_points_right=[(body_diam_at_fins/2,fin_pos),(body_diam_at_fins/2,fin_pos+root_c),(body_diam_at_fins/2+span,fin_pos+root_c-sweep_dist),(body_diam_at_fins/2+span,fin_pos+sweep_dist)]
            ax.add_patch(patches.Polygon(fin_points_right,facecolor='#F0AD4E',edgecolor='black'));ax.add_patch(patches.Polygon([(-x,y)for x,y in fin_points_right],facecolor='#F0AD4E',edgecolor='black'))
        max_diam=params.get('nose_diam',0.152)*1.5; ax.set_xlim(-max_diam,max_diam);ax.set_ylim(-0.1,total_len+0.1);ax.grid(True,linestyle='--',alpha=0.4)
        ax.set_title("Esquema del Cohete");fig.tight_layout(); canvas=FigureCanvasTkAgg(fig,master=self.vis_canvas_frame);canvas.draw();canvas.get_tk_widget().pack(fill="both",expand=True)

    def save_configuration(self):
        params = self.collect_all_params()
        if params is None: messagebox.showerror("Error", "No se pueden guardar datos inválidos."); return
        filepath = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")], title="Guardar Configuración")
        if not filepath: return
        try:
            with open(filepath, 'w') as f: json.dump(params, f, indent=4)
            self.update_status(f"Configuración guardada en {os.path.basename(filepath)}")
        except Exception as e: messagebox.showerror("Error al Guardar", f"No se pudo guardar el archivo:\n{e}")

    def load_configuration(self):
        filepath = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")], title="Cargar Configuración")
        if not filepath: return
        try:
            with open(filepath, 'r') as f: params = json.load(f)
            all_widgets = {**self.rocket_tab.widgets, **self.sim_env_tab.widgets}
            for name, widget in all_widgets.items():
                if name not in params: continue
                if isinstance(widget, customtkinter.CTkEntry): widget.delete(0, "end"); widget.insert(0, str(params[name]))
                elif isinstance(widget, customtkinter.CTkOptionMenu):
                    if params[name] in widget.cget("values"): widget.set(params[name])
            self.update_status(f"Configuración cargada desde {os.path.basename(filepath)}")
            for data_type in ["thrust", "drag", "mass"]:
                if data_type in params and os.path.exists(params[data_type]):
                    self.data_tables_tab.load_csv(data_type, params[data_type])
            self.draw_rocket(); self.sim_env_tab.update_map()
        except Exception as e:
            messagebox.showerror("Error al Cargar", f"No se pudo cargar o leer el archivo:\n{e}")

if __name__ == "__main__":
    app = App()
    app.mainloop()
