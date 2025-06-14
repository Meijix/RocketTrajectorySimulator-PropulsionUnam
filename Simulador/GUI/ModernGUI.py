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

class ColorPalette:
    # Fondo y estructura
    BG_MAIN = "#050253"       # Azul marino profundo (fondo principal)
    BG_FRAME = "#CDDDFF"      # Azul grisáceo oscuro (frames y secciones)
    BG_ENTRY = "#E2EAF4"   
    BUTTON_RED = "#ef4444" 
    BUTTON_GREEN = "#10b981"   # Azul muy claro / gris azulado (campos de entrada)
    ACCENT_CYAN = "#15D0FF"  # Cyan para títulos
    ACCENT_BLUE= "#0069C0"  # Azul para títulos
    ACCENT_VIOLET = "#8b5cf6"  # Violeta para títulos

    TEXT_PRIMARY = "#FFFFFF"  # Blanco para texto principal
    TEXT_SECONDARY = "#E2EAF4"  # Gris claro para texto secundario
    TEXT_ENTRY = "#050253"



class RocketTab(customtkinter.CTkScrollableFrame):
    """Tab for defining all physical components of the rocket based on Xitle configuration."""
    
    def __init__(self, master):
        super().__init__(master)
        
        # Configurar color de fondo oscuro
        self.configure(fg_color=ColorPalette.BG_MAIN)
        self.grid_columnconfigure(0, weight=1)
        self.widgets = {}

        # --- Main Sections ---
        self.external_components_frame = self.create_main_section_frame("Componentes Externos", 0)
        self.internal_components_frame = self.create_main_section_frame("Componentes Internos", 1)
        self.combustible_frame = self.create_main_section_frame("Propelentes", 2)
        
        # Configurar columnas para cada sección
        self.external_components_frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="col_ext")
        self.internal_components_frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="col_int")
        self.combustible_frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="col_comb")

        # --- Populate External Components ---
        # Primera fila
        self.create_nariz_frame(self.external_components_frame, row=1, column=0)
        self.create_coples_frame(self.external_components_frame, row=1, column=1)
        self.create_tubo_recuperacion_frame(self.external_components_frame, row=1, column=2)
        
        # Segunda fila
        self.create_transferidor_frame(self.external_components_frame, row=2, column=0)
        self.create_tanque_vacio_frame(self.external_components_frame, row=2, column=1)
        self.create_valvulas_frame(self.external_components_frame, row=2, column=2)
        
        # Tercera fila
        self.create_camara_combustion_frame(self.external_components_frame, row=3, column=0)
        self.create_boattail_frame(self.external_components_frame, row=3, column=1)
        self.create_aletas_frame(self.external_components_frame, row=3, column=2)
        
        # --- Populate Internal Components ---
        # Primera fila
        self.create_avionica_frame(self.internal_components_frame, row=1, column=0)
        self.create_carga_util_frame(self.internal_components_frame, row=1, column=1)
        self.create_motor_frame(self.internal_components_frame, row=1, column=2)
        
        # Segunda fila
        self.create_drogue_frame(self.internal_components_frame, row=2, column=0)
        self.create_main_chute_frame(self.internal_components_frame, row=2, column=1)
        
        # --- Populate Propellants ---
        self.create_oxidante_frame(self.combustible_frame, row=1, column=0)
        self.create_grano_frame(self.combustible_frame, row=1, column=1)

    def create_labeled_widget(self, master, w_type, name, label_text, default_value, row, 
                            values=None, unit="", tooltip=None):
        """Crear widget con etiqueta y unidad opcional"""
        
        # Crear frame contenedor
        container = customtkinter.CTkFrame(master, fg_color="transparent")
        container.grid(row=row, column=0, columnspan=2, padx=8, pady=3, sticky="ew")
        container.grid_columnconfigure(1, weight=1)
        
        # Crear label con unidad si se proporciona
        label_full = f"{label_text} {unit}:" if unit else f"{label_text}:"
        label = customtkinter.CTkLabel(
            container, 
            text=label_full,
            text_color=ColorPalette.TEXT_PRIMARY,
            font=customtkinter.CTkFont(size=12),
            anchor="w",
            width=140
        )
        label.grid(row=0, column=0, padx=(5, 5), sticky="w")
        
        # Crear widget según tipo
        if w_type == "entry":
            widget = customtkinter.CTkEntry(
                container,
                fg_color=ColorPalette.BG_ENTRY,
                text_color=ColorPalette.TEXT_ENTRY,
                border_width=0,
                corner_radius=6,
                height=28,
                font=customtkinter.CTkFont(size=12)
            )
            widget.insert(0, str(default_value))
        elif w_type == "option":
            widget = customtkinter.CTkOptionMenu(
                container,
                values=values,
                fg_color=ColorPalette.BG_ENTRY,
                text_color=ColorPalette.TEXT_ENTRY,
                button_color=ColorPalette.BG_ENTRY,
                button_hover_color=ColorPalette.TEXT_SECONDARY,
                dropdown_fg_color=ColorPalette.BG_ENTRY,
                dropdown_text_color=ColorPalette.TEXT_ENTRY,
                dropdown_hover_color=ColorPalette.TEXT_SECONDARY,
                corner_radius=6,
                height=28,
                font=customtkinter.CTkFont(size=12)
            )
            widget.set(default_value)
        
        widget.grid(row=0, column=1, padx=(0, 5), sticky="ew")
        self.widgets[name] = widget
        
        # Agregar tooltip si se proporciona
        if tooltip:
            self.create_tooltip(widget, tooltip)
        
        return widget

    def create_main_section_frame(self, title, section_row):
        """Crear frame principal de sección con estilo mejorado"""
        frame = customtkinter.CTkFrame(
            self,
            fg_color=ColorPalette.BG_FRAME,
            corner_radius=10,
            border_width=0
        )
        frame.grid(row=section_row, column=0, padx=15, pady=10, sticky="ew")
        
        # Título de la sección con icono o color distintivo
        colors = [ColorPalette.ACCENT_BLUE, ColorPalette.ACCENT_BLUE, ColorPalette.ACCENT_BLUE,]
        title_color = colors[section_row % len(colors)]
        
        frame_title = customtkinter.CTkLabel(
            frame,
            text=f"▶ {title}",
            font=customtkinter.CTkFont(size=18, weight="bold"),
            text_color=title_color
        )
        frame_title.grid(row=0, column=0, columnspan=3, pady=(15, 10), padx=20, sticky="w")
        
        return frame

    def create_sub_frame(self, master, title, row, column):
        """Crear sub-frame para componente con estilo consistente"""
        frame = customtkinter.CTkFrame(
            master,
            fg_color=ColorPalette.BG_MAIN,
            corner_radius=8
        )
        frame.grid(row=row, column=column, padx=8, pady=8, sticky="nsew")
        frame.grid_columnconfigure(0, weight=1)
        
        # Título del componente
        frame_title = customtkinter.CTkLabel(
            frame,
            text=title,
            font=customtkinter.CTkFont(size=14, weight="bold"),
            text_color=ColorPalette.TEXT_PRIMARY
        )
        frame_title.grid(row=0, column=0, columnspan=2, pady=(10, 5), padx=10, sticky="w")
        
        return frame

    def create_nariz_frame(self, master, row, column):
        """Nariz (Cono)"""
        frame = self.create_sub_frame(master, "🚀 Nariz (Cono)", row, column)
        self.create_labeled_widget(frame, "entry", "nose_len", "Longitud", 0.81, 1, unit="m")
        self.create_labeled_widget(frame, "entry", "nose_mass", "Masa", 0.81, 2, unit="kg")
        self.create_labeled_widget(frame, "entry", "nose_pos_z", "Posición Z", 4.3, 3, unit="m")
        self.create_labeled_widget(frame, "entry", "nose_diam", "Diámetro", 0.152, 4, unit="m")
        self.create_labeled_widget(frame, "option", "nose_shape", "Geometría", "ogiva", 5, 
                                 values=["ogiva", "Cónico", "Elíptico", "Parabólico"])

    def create_coples_frame(self, master, row, column):
        """Coples"""
        frame = self.create_sub_frame(master, "🔗 Coples", row, column)
        self.create_labeled_widget(frame, "entry", "coples_len", "Longitud", 0.15, 1, unit="m")
        self.create_labeled_widget(frame, "entry", "coples_mass", "Masa", 0.176, 2, unit="kg")
        self.create_labeled_widget(frame, "entry", "coples_pos_z", "Posición Z", 3.5, 3, unit="m")
        self.create_labeled_widget(frame, "entry", "coples_diam_ext", "Diámetro Ext", 0.152, 4, unit="m")
        self.create_labeled_widget(frame, "entry", "coples_diam_int", "Diámetro Int", 0.149, 5, unit="m")

    def create_tubo_recuperacion_frame(self, master, row, column):
        """Tubo de Recuperación"""
        frame = self.create_sub_frame(master, "📦 Tubo Recuperación", row, column)
        self.create_labeled_widget(frame, "entry", "tubo_recup_len", "Longitud", 0.3, 1, unit="m")
        self.create_labeled_widget(frame, "entry", "tubo_recup_mass", "Masa", 0.92, 2, unit="kg")
        self.create_labeled_widget(frame, "entry", "tubo_recup_pos_z", "Posición Z", 2.75, 3, unit="m")
        self.create_labeled_widget(frame, "entry", "tubo_recup_diam_ext", "Diámetro Ext", 0.152, 4, unit="m")
        self.create_labeled_widget(frame, "entry", "tubo_recup_diam_int", "Diámetro Int", 0.149, 5, unit="m")

    def create_transferidor_frame(self, master, row, column):
        """Transferidor"""
        frame = self.create_sub_frame(master, "⚡ Transferidor", row, column)
        self.create_labeled_widget(frame, "entry", "transfer_len", "Longitud", 0.10, 1, unit="m")
        self.create_labeled_widget(frame, "entry", "transfer_mass", "Masa", 0.25, 2, unit="kg")
        self.create_labeled_widget(frame, "entry", "transfer_pos_z", "Posición Z", 2.6, 3, unit="m")
        self.create_labeled_widget(frame, "entry", "transfer_diam_ext", "Diámetro Ext", 0.152, 4, unit="m")
        self.create_labeled_widget(frame, "entry", "transfer_diam_int", "Diámetro Int", 0.149, 5, unit="m")

    def create_tanque_vacio_frame(self, master, row, column):
        """Tanque de Oxidante"""
        frame = self.create_sub_frame(master, "🛢️ Tanque Oxidante", row, column)
        self.create_labeled_widget(frame, "entry", "tanque_vacio_len", "Longitud", 0.87, 1, unit="m")
        self.create_labeled_widget(frame, "entry", "tanque_vacio_mass", "Masa", 1.25, 2, unit="kg")
        self.create_labeled_widget(frame, "entry", "tanque_vacio_pos_z", "Posición Z", 1.2, 3, unit="m")
        self.create_labeled_widget(frame, "entry", "tanque_vacio_diam_ext", "Diámetro Ext", 0.152, 4, unit="m")
        self.create_labeled_widget(frame, "entry", "tanque_vacio_diam_int", "Diámetro Int", 0.149, 5, unit="m")

    def create_valvulas_frame(self, master, row, column):
        """Sistema de Válvulas"""
        frame = self.create_sub_frame(master, "🔧 Válvulas", row, column)
        self.create_labeled_widget(frame, "entry", "valvulas_len", "Longitud", 0.24, 1, unit="m")
        self.create_labeled_widget(frame, "entry", "valvulas_mass", "Masa", 0.167, 2, unit="kg")
        self.create_labeled_widget(frame, "entry", "valvulas_pos_z", "Posición Z", 0.8, 3, unit="m")
        self.create_labeled_widget(frame, "entry", "valvulas_diam_ext", "Diámetro Ext", 0.152, 4, unit="m")
        self.create_labeled_widget(frame, "entry", "valvulas_diam_int", "Diámetro Int", 0.149, 5, unit="m")

    def create_camara_combustion_frame(self, master, row, column):
        """Cámara de Combustión"""
        frame = self.create_sub_frame(master, "🔥 Cámara Combustión", row, column)
        self.create_labeled_widget(frame, "entry", "cc_len", "Longitud", 0.43, 1, unit="m")
        self.create_labeled_widget(frame, "entry", "cc_mass", "Masa", 0.573, 2, unit="kg")
        self.create_labeled_widget(frame, "entry", "cc_pos_z", "Posición Z", 0.4, 3, unit="m")
        self.create_labeled_widget(frame, "entry", "cc_diam_ext", "Diámetro Ext", 0.152, 4, unit="m")
        self.create_labeled_widget(frame, "entry", "cc_diam_int", "Diámetro Int", 0.102, 5, unit="m")

    def create_boattail_frame(self, master, row, column):
        """Boattail (Tobera)"""
        frame = self.create_sub_frame(master, "🔻 Boattail/Tobera", row, column)
        self.create_labeled_widget(frame, "entry", "bt_len", "Longitud", 0.12, 1, unit="m")
        self.create_labeled_widget(frame, "entry", "bt_mass", "Masa", 0.251, 2, unit="kg")
        self.create_labeled_widget(frame, "entry", "bt_pos_z", "Posición Z", 0.06, 3, unit="m")
        self.create_labeled_widget(frame, "entry", "bt_diam_front", "Diám. Frontal", 0.152, 4, unit="m")
        self.create_labeled_widget(frame, "entry", "bt_diam_rear", "Diám. Trasero", 0.132, 5, unit="m")
        self.create_labeled_widget(frame, "entry", "bt_espesor", "Espesor", 0.003, 6, unit="m")

    def create_aletas_frame(self, master, row, column):
        """Aletas"""
        frame = self.create_sub_frame(master, "🦅 Aletas", row, column)
        self.create_labeled_widget(frame, "entry", "fin_num", "Número", 4, 1, unit="")
        self.create_labeled_widget(frame, "entry", "fin_mass", "Masa Total", 1.1, 2, unit="kg")
        self.create_labeled_widget(frame, "entry", "fin_pos_z", "Posición Z", 0.2, 3, unit="m")
        self.create_labeled_widget(frame, "entry", "fin_span", "Envergadura", 0.11, 4, unit="m")
        self.create_labeled_widget(frame, "entry", "fin_root_chord", "Cuerda Raíz", 0.3, 5, unit="m")
        self.create_labeled_widget(frame, "entry", "fin_tip_chord", "Cuerda Punta", 0.1, 6, unit="m")
        self.create_labeled_widget(frame, "entry", "fin_sweep", "Ángulo barrido", 25, 7, unit="°")

    def create_avionica_frame(self, master, row, column):
        """Aviónica"""
        frame = self.create_sub_frame(master, "📡 Aviónica", row, column)
        self.create_labeled_widget(frame, "entry", "avionics_mass", "Masa", 0.21, 1, unit="kg")
        self.create_labeled_widget(frame, "entry", "avionics_pos_z", "Posición Z", 3.2, 2, unit="m")
        
    def create_carga_util_frame(self, master, row, column):
        """Carga Útil"""
        frame = self.create_sub_frame(master, "📦 Carga Útil", row, column)
        self.create_labeled_widget(frame, "entry", "cu_mass", "Masa", 0.3, 1, unit="kg")
        self.create_labeled_widget(frame, "entry", "cu_pos_z", "Posición Z", 4.0, 2, unit="m")

    def create_motor_frame(self, master, row, column):
        """Motor"""
        frame = self.create_sub_frame(master, "⚙️ Motor", row, column)
        self.create_labeled_widget(frame, "entry", "motor_mass_inert", "Masa Inerte", 3.2, 1, unit="kg")
        self.create_labeled_widget(frame, "entry", "motor_pos_z", "Posición Z", 0.45, 2, unit="m")

    def create_drogue_frame(self, master, row, column):
        """Paracaídas Drogue"""
        frame = self.create_sub_frame(master, "🪂 Drogue", row, column)
        self.create_labeled_widget(frame, "entry", "drogue_mass", "Masa", 0.17, 1, unit="kg")
        self.create_labeled_widget(frame, "entry", "drogue_pos_z", "Posición Z", 2.9, 2, unit="m")
        self.create_labeled_widget(frame, "entry", "drogue_chute_diam", "Diám. Paracaídas", 0.8, 3, unit="m")
        self.create_labeled_widget(frame, "entry", "drogue_cd", "Coef. Arrastre", 0.7, 4, unit="")
        self.create_labeled_widget(frame, "entry", "drogue_deploy_alt", "Alt. Despliegue", 100, 5, unit="m", 
                                 tooltip="Altitud sobre el apogeo para desplegar")

    def create_main_chute_frame(self, master, row, column):
        """Paracaídas Principal"""
        frame = self.create_sub_frame(master, "🪂 Main (Principal)", row, column)
        self.create_labeled_widget(frame, "entry", "main_mass", "Masa", 0.30, 1, unit="kg")
        self.create_labeled_widget(frame, "entry", "main_pos_z", "Posición Z", 2.9, 2, unit="m")
        self.create_labeled_widget(frame, "entry", "main_chute_diam", "Diám. Paracaídas", 2.0, 3, unit="m")
        self.create_labeled_widget(frame, "entry", "main_cd", "Coef. Arrastre", 1.8, 4, unit="")
        self.create_labeled_widget(frame, "entry", "main_deploy_alt", "Alt. Despliegue", 450, 5, unit="m",
                                 tooltip="Altitud AGL para desplegar el paracaídas principal")

    def create_oxidante_frame(self, master, row, column):
        """Oxidante"""
        frame = self.create_sub_frame(master, "💧 Oxidante (N₂O)", row, column)
        self.create_labeled_widget(frame, "entry", "oxidante_mass", "Masa", 12.0, 1, unit="kg")
        self.create_labeled_widget(frame, "entry", "oxidante_density", "Densidad", 1220, 2, unit="kg/m³")
        self.create_labeled_widget(frame, "entry", "oxidante_temp", "Temperatura", 20, 3, unit="°C")

    def create_grano_frame(self, master, row, column):
        """Combustible Sólido"""
        frame = self.create_sub_frame(master, "🔥 Grano (Combustible)", row, column)
        self.create_labeled_widget(frame, "entry", "grano_mass", "Masa", 4.88, 1, unit="kg")
        self.create_labeled_widget(frame, "entry", "grano_length", "Longitud", 0.35, 2, unit="m")
        self.create_labeled_widget(frame, "entry", "grano_outer_diam", "Diám. Exterior", 0.098, 3, unit="m")
        self.create_labeled_widget(frame, "entry", "grano_inner_diam", "Diám. Interior", 0.030, 4, unit="m")
        self.create_labeled_widget(frame, "option", "grano_config", "Configuración", "BATES", 5,
                                 values=["BATES", "Estrella", "Finocyl", "Moonburner"])

    def create_tooltip(self, widget, text):
        """Crear tooltip para un widget (placeholder para implementación futura)"""
        # Por ahora, solo un placeholder
        pass

    def get_params(self):
        """Obtener todos los parámetros del cohete"""
        params = {}
        try:
            for name, widget in self.widgets.items():
                val = widget.get()
                try:
                    # Intentar convertir a número
                    params[name] = float(val) if '.' in val or 'e' in val.lower() else int(val)
                except (ValueError, TypeError):
                    # Si no es número, guardar como string
                    params[name] = val
            return params
        except Exception as e:
            print(f"Error al obtener parámetros: {e}")
            return None

    def validate_params(self):
        """Validar que los parámetros sean coherentes"""
        params = self.get_params()
        if not params:
            return False, "Error al obtener parámetros"
        
        # Validaciones básicas
        validations = [
            (params.get('nose_len', 0) > 0, "La longitud de la nariz debe ser mayor a 0"),
            (params.get('fin_num', 0) >= 3, "El número de aletas debe ser al menos 3"),
            (params.get('oxidante_mass', 0) > 0, "La masa de oxidante debe ser mayor a 0"),
            (params.get('grano_mass', 0) > 0, "La masa de combustible debe ser mayor a 0"),
        ]
        
        for valid, message in validations:
            if not valid:
                return False, message
        
        return True, "Parámetros válidos"

    def reset_to_defaults(self):
        """Resetear todos los valores a los defaults del Xitle"""
        # Implementar si es necesario
        pass

class SimulationEnvironmentTab(customtkinter.CTkScrollableFrame):
    def __init__(self, master):
        super().__init__(master)
        
        # Configurar color de fondo oscuro
        self.configure(fg_color=ColorPalette.BG_FRAME)
        
        # Configurar grid para 3 columnas donde la tercera es más pequeña para el mapa
        self.grid_columnconfigure(0, weight=1, uniform="col")
        self.grid_columnconfigure(1, weight=1, uniform="col")
        self.grid_columnconfigure(2, weight=1)
        self.widgets = {}
        
        # Crear frames según la imagen
        self.create_launch_site_frame(row=0, column=0)
        self.create_wind_frame(row=0, column=1)
        self.create_rail_frame(row=1, column=0)
        self.create_simulation_frame(row=1, column=1)
        self.create_map_frame(row=0, column=2, rowspan=2)
        


    def create_map_frame(self, row, column, rowspan):
        """Frame con mapa del sitio de lanzamiento"""
        frame = self.create_frame("Mapa: Sitio del lanzamiento", row, column, rowspan)
        
        # Crear el widget del mapa
        map_container = customtkinter.CTkFrame(frame, fg_color=ColorPalette.BG_FRAME, corner_radius=10)
        map_container.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        
        self.map_widget = TkinterMapView(
            map_container, 
            width=400, 
            height=350,
            corner_radius=10
        )
        self.map_widget.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Establecer posición inicial basada en los valores por defecto
        self.update_map_position()
    
    def update_map_position(self):
        """Actualizar la posición del mapa basándose en las coordenadas actuales"""
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
        """Crear widget con etiqueta al lado izquierdo"""
        
        # Crear frame contenedor para label y widget
        container = customtkinter.CTkFrame(master, fg_color="transparent")
        container.grid(row=row, column=0, columnspan=2, padx=5, pady=3, sticky="ew")
        container.grid_columnconfigure(1, weight=1)
        
        # Crear label
        label = customtkinter.CTkLabel(
            container, 
            text=label_text, 
            width=label_width,
            anchor="w",
            text_color="white"
        )
        label.grid(row=0, column=0, padx=(10, 5), sticky="w")
        
        # Crear widget según tipo
        if w_type == "entry":
            widget = customtkinter.CTkEntry(
                container, 
                width=width,
                fg_color="white",
                text_color="black",
                border_width=1
            )
            widget.insert(0, str(default_value))
            
            # Si es un campo de coordenadas, agregar callback para actualizar mapa
            if name in ['launch_lat', 'launch_lon']:
                widget.bind('<KeyRelease>', lambda e: self.on_coordinate_change())
                
        elif w_type == "option":
            widget = customtkinter.CTkOptionMenu(
                container, 
                values=values,
                width=width,
                fg_color="white",
                text_color="black",
                button_color="white",
                button_hover_color="#e0e0e0"
            )
            widget.set(default_value)
        elif w_type == "switch":
            widget = customtkinter.CTkSwitch(
                container, 
                text="",
                fg_color="gray",
                progress_color=ColorPalette.ACCENT_CYAN,
            )
            if default_value:
                widget.select()
        
        widget.grid(row=0, column=1, padx=(0, 10), sticky="w")
        self.widgets[name] = widget
        
        return widget
    
    def on_coordinate_change(self):
        """Callback para cuando cambian las coordenadas"""
        if hasattr(self, 'map_widget'):
            self.update_map_position()

    def create_frame(self, title, row, column, rowspan=1, colspan=1):
        """Crear frame con título y estilo consistente"""
        frame = customtkinter.CTkFrame(
            self, 
            fg_color=ColorPalette.BG_MAIN,
            corner_radius=10,
            border_width=1,
            border_color=ColorPalette.ACCENT_CYAN
        )
        frame.grid(row=row, column=column, rowspan=rowspan, columnspan=colspan, 
                  padx=10, pady=10, sticky="nsew")
        
        # Título del frame
        title_label = customtkinter.CTkLabel(
            frame, 
            text=title, 
            font=customtkinter.CTkFont(size=16, weight="bold"),
            text_color="#00b4d8"
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(10, 10), padx=10, sticky="w")
        
        return frame

    def create_launch_site_frame(self, row, column):
        """Frame de Sitio de Lanzamiento"""
        frame = self.create_frame("Sitio de Lanzamiento:", row, column)
        
        self.create_labeled_widget(frame, "entry", "launch_lat", "Latitud (°):", "19.5", 1)
        self.create_labeled_widget(frame, "entry", "launch_lon", "Longitud (°):", "-98", 2)
        self.create_labeled_widget(frame, "entry", "launch_alt", "Altitud (m):", "20", 3)
        self.create_labeled_widget(frame, "entry", "launch_date", "Fecha (YYYY-MM-DD):", "2024-11-06", 4)

    def create_wind_frame(self, row, column):
        """Frame de Viento (Modelo Simple)"""
        frame = self.create_frame("Viento (Modelo Simple):", row, column)
        
        self.create_labeled_widget(frame, "entry", "wind_base_speed", "Velocidad Base (m/s):", "5", 1)
        self.create_labeled_widget(frame, "entry", "wind_mean_speed", "Velocidad Media (m/s):", "3", 2)
        self.create_labeled_widget(frame, "entry", "wind_speed_var", "Variación Velocidad:", "2", 3)
        self.create_labeled_widget(frame, "entry", "wind_angle_var", "Variación Ángulo (°):", "10.0", 4)

    def create_rail_frame(self, row, column):
        """Frame de Riel de Lanzamiento"""
        frame = self.create_frame("Riel de Lanzamiento:", row, column)
        
        self.create_labeled_widget(frame, "entry", "rail_len", "Longitud (m):", "10", 1)
        self.create_labeled_widget(frame, "entry", "rail_angle", "Ángulo Elevación (°):", "4984.73281763816", 2)

    def create_simulation_frame(self, row, column):
        """Frame de Simulación"""
        frame = self.create_frame("Simulación:", row, column)
        
        self.create_labeled_widget(frame, "entry", "sim_max_time", "Tiempo Máximo (s):", "800", 1)
        self.create_labeled_widget(frame, "entry", "sim_time_step", "Paso de Tiempo (s):", "0.01", 2)
        self.create_labeled_widget(frame, "option", "integrator", "Método Integración:", "DOP853", 3, 
                                 ["DOP853", "RK45", "RK23", "Euler"])

    def create_motor_performance_frame(self, row, column, rowspan):
        """Frame con mapa del sitio de lanzamiento"""
        frame = self.create_frame("Listo para simular", row, column, rowspan)
        
        # Crear el widget del mapa
        map_container = customtkinter.CTkFrame(frame, fg_color="#0f172a")
        map_container.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        
        self.map_widget = TkinterMapView(
            map_container, 
            width=400, 
            height=350,
            corner_radius=10
        )
        self.map_widget.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Establecer posición inicial y marcador
        lat = float(self.widgets['launch_lat'].get() if 'launch_lat' in self.widgets else 19.5)
        lon = float(self.widgets['launch_lon'].get() if 'launch_lon' in self.widgets else -98)
        
        self.map_widget.set_position(lat, lon)
        self.map_widget.set_marker(lat, lon, text="Sitio de Lanzamiento")
        self.map_widget.set_zoom(12)

    

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
        self.title("Simulador de Trayectoria de Cohetes -NEMB"); self.geometry("1400x900")
        self.grid_columnconfigure(0, weight=1); self.grid_rowconfigure(0, weight=1)
        customtkinter.set_appearance_mode("Light"); customtkinter.set_default_color_theme("blue")
        self.main_frame = customtkinter.CTkFrame(self, fg_color="transparent"); self.main_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.left_frame = customtkinter.CTkFrame(self.main_frame); self.left_frame.grid(row=0, column=0, sticky="nsew")
        self.left_frame.grid_rowconfigure(0, weight=1); self.left_frame.grid_columnconfigure(0, weight=1)
        self.right_frame = customtkinter.CTkFrame(self.main_frame); self.right_frame.grid_rowconfigure(1, weight=1); self.right_frame.grid_columnconfigure(0, weight=1)
        self.tab_view = customtkinter.CTkTabview(self.left_frame, command=self._on_tab_change); self.tab_view.grid(row=0, column=0, sticky="nsew")
        self.tab_view.add("Cohete"); self.tab_view.add("Tablas de Datos"); self.tab_view.add("Simulación"); self.tab_view.add("Análisis (CG-CP)"); self.tab_view.add("Resultados")
        self.rocket_tab = RocketTab(self.tab_view.tab("Cohete")); self.rocket_tab.pack(expand=True, fill="both")
        self.data_tables_tab = DataTablesTab(self.tab_view.tab("Tablas de Datos")); self.data_tables_tab.pack(expand=True, fill="both")
        self.sim_env_tab = SimulationEnvironmentTab(self.tab_view.tab("Simulación")); self.sim_env_tab.pack(expand=True, fill="both")
        self.stability_tab = StabilityTab(self.tab_view.tab("Análisis (CG-CP)")); self.stability_tab.pack(expand=True, fill="both")
        self.results_tab = ResultsTab(self.tab_view.tab("Resultados")); self.results_tab.pack(expand=True, fill="both")
        self.vis_label = customtkinter.CTkLabel(self.right_frame, text="Visualización del Cohete", font=customtkinter.CTkFont(size=16, weight="bold")); self.vis_label.grid(row=0, column=0, padx=10, pady=10)
        self.vis_canvas_frame = customtkinter.CTkFrame(self.right_frame); self.vis_canvas_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.vis_canvas_frame.grid_rowconfigure(0, weight=1); self.vis_canvas_frame.grid_columnconfigure(0, weight=1)
        self.control_frame = customtkinter.CTkFrame(self, height=80); self.control_frame.grid(row=1, column=0, padx=10, pady=(0,10), sticky="ew")
        self.control_frame.grid_columnconfigure(1, weight=1); self.create_control_widgets()
        self.simulation_thread = None; self._on_tab_change(); self.after(100, self.draw_rocket)

    def _on_tab_change(self):
        if self.tab_view.get() == "Cohete": self.main_frame.grid_columnconfigure(0, weight=2); self.main_frame.grid_columnconfigure(1, weight=1, minsize=10); self.right_frame.grid(row=0, column=1, padx=(2,0), sticky="nsew")
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
