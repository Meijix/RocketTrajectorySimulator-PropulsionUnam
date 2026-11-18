import customtkinter
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import os
import json
import sys
import time
import webbrowser
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
import pandas as pd
import numpy as np

# --- Matplotlib Integration ---
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.patches as patches

# --- Map Integration ---
from tkintermapview import TkinterMapView

# tkintermapview crea imágenes de Tk desde hilos en segundo plano. Con Tk 9 eso cierra
# la aplicación con un fallo de segmentación (comprobado con Tk 9.0.3), así que el mapa
# solo se muestra con Tk 8.x; con Tk 9 se muestran las coordenadas en texto.
MAPA_DISPONIBLE = tk.TkVersion < 9

# --- Backend del simulador ---
# Se agrega la raíz del proyecto al path para poder ejecutar tanto
# `python -m Simulador.GUI.ModernGUI` como `python Simulador/GUI/ModernGUI.py`.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from Simulador.GUI import backend, mapa
from Simulador.Visualizacion.graficas_cargas import graficar_envolvente, tabla_envolvente, texto_maximos
from Paquetes.PaqueteFisica import resistencia

class ColorPalette:
    # Fondo y estructura
    BG_MAIN = "#050253"       # Azul marino profundo (fondo principal)
    BG_FRAME = "#233969"      # Azul grisáceo oscuro (frames y secciones)
    BG_ENTRY = "#E2EAF4"   
    BUTTON_RED = "#ef4444" 
    BUTTON_GREEN = "#00792C"   # Azul muy claro / gris azulado (campos de entrada)
    ACCENT_CYAN = "#15D0FF"  # Cyan para títulos
    ACCENT_BLUE= "#0211B7"  # Azul para títulos
    ACCENT_VIOLET = "#5A00C0"  # Violeta para títulos
    ACCENT_Orange = "#C66907"  # Naranja para títulos

    TEXT_PRIMARY = "#FFFFFF"  # Blanco para texto principal
    TEXT_SECONDARY = "#E2EAF4"  # Gris claro para texto secundario
    TEXT_ENTRY = "#050253"



class RocketTab(customtkinter.CTkScrollableFrame):
    """Tab for defining all physical components of the rocket based on Xitle configuration."""
    
    def __init__(self, master):
        super().__init__(master)
        
        # Configurar color de fondo oscuro
        #self.configure(fg_color=ColorPalette.BG_MAIN)
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
        colors = [ColorPalette.ACCENT_CYAN, ColorPalette.ACCENT_CYAN, ColorPalette.ACCENT_CYAN,]
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

    def campo(self, frame, name, label_text, row, unit=""):
        """Campo numérico cuyo valor inicial es el del Xitle II (backend.PARAMS_XITLE)."""
        return self.create_labeled_widget(frame, "entry", name, label_text, backend.PARAMS_XITLE[name], row, unit=unit)

    def create_tubo_frame(self, master, title, prefijo, row, column):
        """Sección cilíndrica del fuselaje: longitud, masa, posición y diámetros."""
        frame = self.create_sub_frame(master, title, row, column)
        self.campo(frame, f"{prefijo}_len", "Longitud", 1, "m")
        self.campo(frame, f"{prefijo}_mass", "Masa", 2, "kg")
        self.campo(frame, f"{prefijo}_pos_z", "Posición Z", 3, "m")
        self.campo(frame, f"{prefijo}_diam_ext", "Diámetro Ext", 4, "m")
        self.campo(frame, f"{prefijo}_diam_int", "Diámetro Int", 5, "m")
        self.create_labeled_widget(frame, "option", f"{prefijo}_material", "Material", backend.PARAMS_XITLE[f"{prefijo}_material"], 6,
                                   values=list(backend.MATERIALES))

    def create_interno_frame(self, master, title, prefijo, campo_masa, etiqueta_masa, row, column):
        """Componente interno: masa, posición y longitud."""
        frame = self.create_sub_frame(master, title, row, column)
        self.campo(frame, campo_masa, etiqueta_masa, 1, "kg")
        self.campo(frame, f"{prefijo}_pos_z", "Posición Z", 2, "m")
        self.campo(frame, f"{prefijo}_len", "Longitud", 3, "m")
        return frame

    def create_nariz_frame(self, master, row, column):
        """Nariz (Cono)"""
        frame = self.create_sub_frame(master, "🚀 Nariz (Cono)", row, column)
        self.campo(frame, "nose_len", "Longitud", 1, "m")
        self.campo(frame, "nose_mass", "Masa", 2, "kg")
        self.campo(frame, "nose_pos_z", "Posición Z", 3, "m")
        self.campo(frame, "nose_diam", "Diámetro", 4, "m")
        self.create_labeled_widget(frame, "option", "nose_shape", "Geometría", backend.PARAMS_XITLE["nose_shape"], 5,
                                 values=list(backend.GEOMETRIAS_NARIZ))

    def create_coples_frame(self, master, row, column):
        self.create_tubo_frame(master, "🔗 Coples", "coples", row, column)

    def create_tubo_recuperacion_frame(self, master, row, column):
        self.create_tubo_frame(master, "📦 Tubo Recuperación", "tubo_recup", row, column)

    def create_transferidor_frame(self, master, row, column):
        self.create_tubo_frame(master, "⚡ Transferidor", "transfer", row, column)

    def create_tanque_vacio_frame(self, master, row, column):
        self.create_tubo_frame(master, "🛢️ Tanque Oxidante (vacío)", "tanque_vacio", row, column)

    def create_valvulas_frame(self, master, row, column):
        self.create_tubo_frame(master, "🔧 Válvulas", "valvulas", row, column)

    def create_camara_combustion_frame(self, master, row, column):
        self.create_tubo_frame(master, "🔥 Cámara Combustión", "cc", row, column)

    def create_boattail_frame(self, master, row, column):
        """Boattail (Tobera)"""
        frame = self.create_sub_frame(master, "🔻 Boattail/Tobera", row, column)
        self.campo(frame, "bt_len", "Longitud", 1, "m")
        self.campo(frame, "bt_mass", "Masa", 2, "kg")
        self.campo(frame, "bt_pos_z", "Posición Z", 3, "m")
        self.campo(frame, "bt_diam_front", "Diám. Frontal", 4, "m")
        self.campo(frame, "bt_diam_rear", "Diám. Trasero", 5, "m")
        self.campo(frame, "bt_espesor", "Espesor", 6, "m")

    def create_aletas_frame(self, master, row, column):
        """Aletas"""
        frame = self.create_sub_frame(master, "🦅 Aletas", row, column)
        self.campo(frame, "fin_num", "Número", 1)
        self.campo(frame, "fin_mass", "Masa Total", 2, "kg")
        self.campo(frame, "fin_pos_z", "Posición Z", 3, "m")
        self.campo(frame, "fin_span", "Envergadura", 4, "m")
        self.campo(frame, "fin_root_chord", "Cuerda Raíz", 5, "m")
        self.campo(frame, "fin_tip_chord", "Cuerda Punta", 6, "m")
        self.campo(frame, "fin_xr", "Retraso c. punta", 7, "m")
        self.campo(frame, "fin_sweep", "Ángulo barrido", 8, "°")
        self.campo(frame, "fin_thickness", "Espesor", 9, "m")
        self.create_labeled_widget(frame, "option", "fin_material", "Material", backend.PARAMS_XITLE["fin_material"], 10,
                                   values=list(backend.MATERIALES))

    def create_avionica_frame(self, master, row, column):
        self.create_interno_frame(master, "📡 Aviónica", "avionics", "avionics_mass", "Masa", row, column)

    def create_carga_util_frame(self, master, row, column):
        self.create_interno_frame(master, "📦 Carga Útil", "cu", "cu_mass", "Masa", row, column)

    def create_motor_frame(self, master, row, column):
        """Masa inerte adicional del motor (0 = no se incluye)"""
        self.create_interno_frame(master, "⚙️ Motor (opcional)", "motor", "motor_mass_inert", "Masa Inerte", row, column)

    def create_drogue_frame(self, master, row, column):
        """Paracaídas drogue: es el que el simulador despliega en el apogeo"""
        frame = self.create_interno_frame(master, "🪂 Drogue", "drogue", "drogue_mass", "Masa", row, column)
        self.campo(frame, "drogue_chute_diam", "Diám. Paracaídas", 4, "m")
        self.campo(frame, "drogue_cd", "Coef. Arrastre", 5)
        self.campo(frame, "drogue_fill", "Const. de llenado", 6)

    def create_main_chute_frame(self, master, row, column):
        """Paracaídas principal: se abre en el descenso, a la altura indicada sobre el sitio"""
        frame = self.create_interno_frame(master, "🪂 Main (Principal)", "main", "main_mass", "Masa", row, column)
        self.campo(frame, "main_chute_diam", "Diám. Paracaídas", 4, "m")
        self.campo(frame, "main_cd", "Coef. Arrastre", 5)
        self.campo(frame, "main_deploy_alt", "Alt. Despliegue", 6, "m")
        self.campo(frame, "main_fill", "Const. de llenado", 7)

    def create_oxidante_frame(self, master, row, column):
        """Oxidante"""
        frame = self.create_sub_frame(master, "💧 Oxidante (N₂O)", row, column)
        self.campo(frame, "oxidante_mass", "Masa inicial", 1, "kg")
        self.campo(frame, "oxidante_pos_z", "Posición Z", 2, "m")
        self.campo(frame, "oxidante_len", "Longitud", 3, "m")
        self.campo(frame, "oxidante_diam", "Diámetro", 4, "m")

    def create_grano_frame(self, master, row, column):
        """Combustible Sólido"""
        frame = self.create_sub_frame(master, "🔥 Grano (Combustible)", row, column)
        self.campo(frame, "grano_mass", "Masa inicial", 1, "kg")
        self.campo(frame, "grano_pos_z", "Posición Z", 2, "m")
        self.campo(frame, "grano_length", "Longitud", 3, "m")
        self.campo(frame, "grano_outer_diam", "Diám. Exterior", 4, "m")
        self.campo(frame, "grano_inner_diam", "Diám. Interior", 5, "m")

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
        
        if MAPA_DISPONIBLE:
            self.map_widget = TkinterMapView(
                map_container,
                width=400,
                height=350,
                corner_radius=10
            )
            self.map_widget.pack(fill="both", expand=True, padx=5, pady=5)
        else:
            self.map_widget = None
            self.map_label = customtkinter.CTkLabel(map_container, text="", width=400, height=350, justify="center")
            self.map_label.pack(fill="both", expand=True, padx=5, pady=5)

        # Establecer posición inicial basada en los valores por defecto
        self.update_map_position()

    def update_map_position(self):
        """Actualizar la posición del mapa basándose en las coordenadas actuales"""
        try:
            lat = float(self.widgets['launch_lat'].get()) if 'launch_lat' in self.widgets else 19.5
            lon = float(self.widgets['launch_lon'].get()) if 'launch_lon' in self.widgets else -98
        except ValueError:
            return
        if self.map_widget is None:
            self.map_label.configure(text=f"Sitio de lanzamiento\n{lat:.4f}°, {lon:.4f}°\n\n(El mapa interactivo requiere Tk 8.x;\nesta instalación usa Tk {tk.TkVersion})")
            return
        self.map_widget.set_position(lat, lon)
        self.map_widget.delete_all_marker()
        self.map_widget.set_marker(lat, lon, text="Sitio de Lanzamiento")
        self.map_widget.set_zoom(12)

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
            border_width=0
        )
        frame.grid(row=row, column=column, rowspan=rowspan, columnspan=colspan, 
                  padx=10, pady=10, sticky="nsew")
        
        # Título del frame
        title_label = customtkinter.CTkLabel(
            frame, 
            text=title, 
            font=customtkinter.CTkFont(size=20, weight="bold"),
            text_color= ColorPalette.ACCENT_CYAN,
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(10, 10), padx=10, sticky="w")
        
        return frame

    def campo(self, frame, name, label_text, row):
        """Campo cuyo valor inicial viene de backend.PARAMS_XITLE."""
        return self.create_labeled_widget(frame, "entry", name, label_text, backend.PARAMS_XITLE[name], row)

    def nota(self, frame, texto, row):
        customtkinter.CTkLabel(frame, text=texto, text_color=ColorPalette.TEXT_SECONDARY, font=customtkinter.CTkFont(size=11),
                               justify="left").grid(row=row, column=0, columnspan=2, padx=15, pady=(2, 8), sticky="w")

    def create_launch_site_frame(self, row, column):
        """Frame de Sitio de Lanzamiento y atmósfera del día"""
        frame = self.create_frame("Sitio de Lanzamiento:", row, column)
        self.campo(frame, "launch_lat", "Latitud (°):", 1)
        self.campo(frame, "launch_lon", "Longitud (°):", 2)
        self.campo(frame, "launch_alt", "Altitud (m s. n. m.):", 3)
        self.campo(frame, "launch_date", "Fecha (YYYY-MM-DD):", 4)
        self.campo(frame, "atm_delta_t", "ΔT respecto a ISA (°C):", 5)
        self.campo(frame, "atm_pressure_hpa", "Presión en el sitio (hPa):", 6)
        self.nota(frame, "Por defecto: Spaceport America, 22-jun-2024 (vuelo del Xitle II).\n"
                         "ΔT = 0 y presión vacía dan la atmósfera estándar a esa altitud.", 7)

    def create_wind_frame(self, row, column):
        """Frame de Viento"""
        frame = self.create_frame("Viento:", row, column)
        self.create_labeled_widget(frame, "option", "wind_mode", "Modelo:", backend.PARAMS_XITLE["wind_mode"], 1,
                                   backend.VIENTOS, width=250)
        self.campo(frame, "wind_base_speed", "Velocidad Base (m/s):", 2)
        self.campo(frame, "wind_from", "Viene de (° desde el norte):", 3)
        self.campo(frame, "wind_mean_speed", "Ráfaga Media (m/s):", 4)
        self.campo(frame, "wind_speed_var", "Variación Ráfaga (m/s):", 5)
        self.campo(frame, "wind_angle_var", "Variación Ángulo (°):", 6)
        self.campo(frame, "wind_seed", "Semilla (vacío = aleatorio):", 7)
        self.nota(frame, "El perfil del día usa el viento por niveles de altura del 22-jun-2024.\n"
                         "Los campos de velocidad, dirección y ráfaga solo aplican al modelo constante.\n"
                         "Dirección: de dónde viene el viento (0° = norte, 90° = este).", 8)

    def create_rail_frame(self, row, column):
        """Frame de Riel de Lanzamiento"""
        frame = self.create_frame("Riel de Lanzamiento:", row, column)
        self.campo(frame, "rail_len", "Longitud (m):", 1)
        self.campo(frame, "rail_angle", "Ángulo Elevación (°):", 2)
        self.campo(frame, "rail_azimuth", "Azimut (° desde el norte):", 3)
        self.nota(frame, "Azimut: rumbo hacia el que se inclina el riel (0° = norte, 90° = este).", 4)

    def create_simulation_frame(self, row, column):
        """Frame de Simulación"""
        frame = self.create_frame("Simulación:", row, column)
        self.campo(frame, "sim_max_time", "Tiempo Máximo (s):", 1)   # la simulación termina antes si hay impacto
        self.campo(frame, "sim_time_step", "Paso de Tiempo (s):", 2)
        self.create_labeled_widget(frame, "option", "integrator", "Método Integración:",
                                   backend.PARAMS_XITLE["integrator"], 3, backend.INTEGRADORES)
        self.campo(frame, "load_gust", "Ráfaga de diseño (m/s):", 5)
        self.create_labeled_widget(frame, "option", "recovery", "Recuperación:",
                                   backend.PARAMS_XITLE["recovery"], 4, backend.RECUPERACION, width=230)

    def get_params(self):
        """Parámetros del entorno y de la simulación (números donde aplica)."""
        params = {}
        for name, widget in self.widgets.items():
            val = widget.get()
            try:
                params[name] = float(val)
            except (ValueError, TypeError):
                params[name] = val
        return params


class DataTablesTab(customtkinter.CTkFrame):
    """Tablas del motor y de arrastre. Arranca con los archivos del Xitle II incluidos en el repositorio."""

    TITULOS = {"thrust": "Empuje", "drag": "Cd_vs_mach", "mass": "Masa"}
    # Columnas que el simulador necesita en cada archivo CSV
    COLUMNAS = {
        "thrust": ["time", "thrust"],
        "drag": ["mach", "cd"],
        "mass": ["Time (s)", "Oxidizer Mass (kg)", "Fuel Mass (kg)"],
    }

    def __init__(self, master):
        super().__init__(master)
        self.configure(fg_color=ColorPalette.BG_FRAME)
        self.grid_columnconfigure(0, weight=1); self.grid_rowconfigure(2, weight=1)
        self.dataframes = {"thrust": None, "drag": None, "mass": None}
        self.filepaths = {"thrust": "No cargado", "drag": "No cargado", "mass": "No cargado"}
        self.top_frame = customtkinter.CTkFrame(self); self.top_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10); self.top_frame.grid_columnconfigure((0,1,2), weight=1)
        self.mid_frame = customtkinter.CTkFrame(self); self.mid_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0,10)); self.mid_frame.grid_columnconfigure((0,1,2), weight=1)
        self.plot_frame = customtkinter.CTkFrame(self, fg_color="#E5E5E5"); self.plot_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
        self.plot_frame.grid_columnconfigure(0, weight=1); self.plot_frame.grid_rowconfigure(0, weight=1); self.canvas = None
        self.create_importers(); self.show_placeholder_message()
        # Cargar las tablas por defecto (sin graficar) para que se pueda simular de inmediato
        for data_type, ruta in backend.RUTAS_XITLE.items():
            if os.path.isfile(ruta):
                self.load_csv(data_type, ruta, visualizar=False, avisar=False)

    def create_importers(self):
        textos = {"thrust": "Importar Empuje (T vs t)", "drag": "Importar Arrastre (Cd vs Mach)", "mass": "Importar Masa (M vs t)"}
        ver = {"thrust": "Visualizar Empuje", "drag": "Visualizar Arrastre", "mass": "Visualizar Masa"}
        self.labels = {}
        for col, data_type in enumerate(("thrust", "drag", "mass")):
            customtkinter.CTkButton(self.top_frame, text=textos[data_type], fg_color=ColorPalette.ACCENT_Orange,
                                    command=lambda d=data_type: self.load_csv(d)).grid(row=0, column=col, padx=5, pady=5, sticky="ew")
            self.labels[data_type] = customtkinter.CTkLabel(self.mid_frame, text=f"{self.TITULOS[data_type]}: No cargado")
            self.labels[data_type].grid(row=0, column=col, padx=5, pady=5)
            customtkinter.CTkButton(self.mid_frame, text=ver[data_type], fg_color=ColorPalette.ACCENT_BLUE,
                                    command=lambda d=data_type: self.visualize_data(d)).grid(row=1, column=col, padx=5, pady=5)

    def leer_tabla(self, data_type, filepath):
        """Lee el CSV, comprueba las columnas que usa el simulador y devuelve un DataFrame (x, y) para graficar."""
        tabla = pd.read_csv(filepath)
        tabla.columns = [str(c).strip() for c in tabla.columns]
        requeridas = self.COLUMNAS[data_type]
        faltan = [c for c in requeridas if c not in tabla.columns]
        if faltan:
            raise ValueError(f"El archivo debe tener las columnas {requeridas}; faltan {faltan}.")
        x = pd.to_numeric(tabla[requeridas[0]], errors="coerce")
        y = sum(pd.to_numeric(tabla[c], errors="coerce") for c in requeridas[1:])   # masa: oxidante + grano
        return pd.DataFrame({"x": x, "y": y}).dropna()

    def load_csv(self, data_type, filepath=None, visualizar=True, avisar=True):
        if filepath is None: filepath = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")], title=f"Importar {data_type}")
        if not filepath: return
        try:
            df = self.leer_tabla(data_type, filepath)
            self.dataframes[data_type] = df; self.filepaths[data_type] = filepath
            self.labels[data_type].configure(text=f"{self.TITULOS[data_type]}: {os.path.basename(filepath)}")
            if visualizar: self.visualize_data(data_type)
        except Exception as e:
            if avisar: messagebox.showerror("Error al Cargar CSV", f"No se pudo leer el archivo.\nError: {e}")
            else: print(f"No se pudo cargar {filepath}: {e}")

    def show_placeholder_message(self):
        for w in self.plot_frame.winfo_children():w.destroy()
        customtkinter.CTkLabel(self.plot_frame,text="Seleccione un tipo de dato para visualizar la gráfica.",font=customtkinter.CTkFont(size=16)).pack(expand=True);self.canvas=None

    def visualize_data(self, data_type):
        df = self.dataframes.get(data_type)
        if df is None: messagebox.showwarning("Sin Datos", f"Cargue un archivo para '{data_type}'."); return
        for w in self.plot_frame.winfo_children():w.destroy()
        fig=Figure(figsize=(8,6),dpi=100,facecolor="#FFFFFF");ax=fig.add_subplot(111)
        titles={"thrust":"Curva de Empuje","drag":"Curva de Arrastre","mass":"Masa de propelente (oxidante + grano)"}; x_labels={"thrust":"Tiempo (s)","drag":"Mach","mass":"Tiempo (s)"}; y_labels={"thrust":"Empuje (N)","drag":"Cd","mass":"Masa (kg)"}
        ax.plot(df['x'],df['y'],marker='.',linestyle='-',markersize=3,color='#0078D7'); ax.set_title(titles[data_type]);ax.set_xlabel(x_labels[data_type]);ax.set_ylabel(y_labels[data_type])
        ax.grid(True,linestyle='--',alpha=0.6);fig.tight_layout()
        self.canvas=FigureCanvasTkAgg(fig,master=self.plot_frame);self.canvas.draw();self.canvas.get_tk_widget().pack(fill="both",expand=True)


def _fmt(valor, formato, vacio="--"):
    """Formatea un número que puede no existir (por ejemplo, si no hubo impacto)."""
    return vacio if valor is None else format(valor, formato)


class ResultsTab(customtkinter.CTkFrame):
    """Pestaña para mostrar los resultados de la simulación."""

    def __init__(self, parent):
        super().__init__(parent)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Contenedor para las gráficas ---
        self.plot_frame=customtkinter.CTkFrame(self)
        self.plot_frame.grid(row=0,column=0,sticky="nsew",padx=10,pady=10)
        self.plot_frame.grid_columnconfigure(0,weight=1)
        self.plot_frame.grid_rowconfigure(0,weight=1)

        # --- Contenedor para el resumen ---
        self.summary_frame=customtkinter.CTkFrame(self,height=100)
        self.summary_frame.grid(row=1,column=0,sticky="ew",padx=10,pady=(0,10))
        self.summary_frame.grid_columnconfigure((0,1,2,3),weight=1)

        # Variables para matplotlib
        self.canvas = None
        self.toolbar = None
        self.df = None

        self.create_summary_widgets()
        self.show_placeholder_message()

    def create_summary_widgets(self):
        """Crea las etiquetas para los datos clave de la simulación."""
        font_style = customtkinter.CTkFont(size=14, weight="bold")
        textos = {
            "apogeo": "Apogeo: -- m", "vel_max": "Vel. Máxima: -- m/s", "distancia": "Cayó en: --",
            "riel": "Salida del riel: --", "impacto": "Impacto: --", "margen": "Margen estático mín.: -- cal",
        }
        self.labels = {}
        for i, (clave, texto) in enumerate(textos.items()):
            self.labels[clave] = customtkinter.CTkLabel(self.summary_frame, text=texto, font=font_style)
            self.labels[clave].grid(row=i // 3, column=i % 3, padx=10, pady=6)
        self.export_button = customtkinter.CTkButton(self.summary_frame, text="Exportar CSV", state="disabled", command=self.export_csv)
        self.export_button.grid(row=0, column=3, rowspan=2, padx=10, pady=6)

    def show_placeholder_message(self):
        """Limpia el canvas y muestra un mensaje inicial."""
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
            self.canvas = None
        if self.toolbar:
            self.toolbar.destroy()
            self.toolbar = None

        # Limpiar cualquier widget residual en el frame
        for widget in self.plot_frame.winfo_children():
            widget.destroy()

        # Mostrar mensaje
        placeholder_label = customtkinter.CTkLabel(self.plot_frame, text="Los resultados de la simulación se mostrarán aquí.", font=customtkinter.CTkFont(size=16))
        placeholder_label.grid(row=0, column=0, sticky="nsew")

    def export_csv(self):
        if self.df is None: return
        filepath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")], title="Exportar resultados")
        if not filepath: return
        try:
            self.df.to_csv(filepath, index=False)
        except Exception as e:
            messagebox.showerror("Error al Exportar", f"No se pudo guardar el archivo:\n{e}")

    def display_results(self, df, resumen):
        """Actualiza el resumen y dibuja las gráficas del vuelo."""
        self.show_placeholder_message() # Limpiar el área antes de dibujar

        if df is None or df.empty:
            messagebox.showinfo("Resultados", "La simulación no produjo datos para graficar.")
            return

        try:
            self.df = df
            self.export_button.configure(state="normal")

            # 1. Resumen
            r = resumen
            self.labels["apogeo"].configure(text=f"Apogeo: {r['apogeo']:.0f} m (t = {r['t_apogeo']:.1f} s)")
            self.labels["vel_max"].configure(text=f"Vel. Máxima: {r['vel_max']:.1f} m/s (Mach {r['mach_max']:.2f})")
            self.labels["distancia"].configure(text=f"Cayó en {r['lat_impacto']:.5f}°, {r['lon_impacto']:.5f}° · a {r['distancia']:.0f} m, rumbo {r['rumbo_impacto']:.0f}°")
            self.labels["riel"].configure(text=f"Salida del riel: {_fmt(r['t_salida_riel'], '.2f')} s a {_fmt(r['vel_salida_riel'], '.1f')} m/s")
            if r["t_impacto"] is None:
                self.labels["impacto"].configure(text=f"Sin impacto antes de t = {r['t_final']:.0f} s")
            else:
                texto = f"Impacto: {r['t_impacto']:.1f} s a {r['vel_impacto']:.1f} m/s"
                if r.get("t_principal") is not None:
                    texto += f" · principal abierto a {r['altura_principal']:.0f} m (bajaba a {r['vel_antes_principal']:.0f} m/s)"
                    if r.get("fuerza_apertura_principal") is not None:
                        texto += f", carga de apertura {r['fuerza_apertura_principal']:.0f} N ({r['g_apertura_principal']:.1f} g)"
                self.labels["impacto"].configure(text=texto)
            self.labels["margen"].configure(text=f"Margen estático mín.: {r['margen_min']:.2f} cal")

            # 2. Figura con seis gráficas
            fig = Figure(figsize=(9, 6), dpi=100, facecolor="#FFFFFF")
            t = df["t"]
            eventos = [(r["t_MECO"], "orange", "Fin de quemado"), (r["t_apogeo"], "green", "Apogeo")]
            leyenda_eventos = "Líneas punteadas: naranja = fin de quemado, verde = apogeo"
            if r.get("t_principal") is not None:
                eventos.append((r["t_principal"], "purple", "Paracaídas principal"))
                leyenda_eventos += ", morado = apertura del paracaídas principal"

            def panel(pos, y, titulo, ylabel, color):
                ax = fig.add_subplot(2, 3, pos)
                ax.plot(t, y, color=color, linewidth=1.3)
                for te, c, _ in eventos:
                    if te <= t.iloc[-1]: ax.axvline(te, color=c, linestyle="--", linewidth=0.9)
                ax.set_title(titulo, fontsize=10); ax.set_xlabel("Tiempo (s)", fontsize=8); ax.set_ylabel(ylabel, fontsize=8)
                ax.tick_params(labelsize=8); ax.grid(True, linestyle="--", alpha=0.5)
                return ax

            panel(1, df["z"], "Altitud", "z (m)", "#0B5CAD")
            panel(2, df["velocidad"], "Velocidad", "|v| (m/s)", "#B5460F")
            panel(3, df["aceleracion"], "Aceleración", "|a| (m/s²)", "#6A3DAD")
            panel(4, df["mach"], "Número de Mach", "Mach", "#0E7C6B")

            # Ángulo de ataque: solo entre la salida del riel y el apogeo (después no es representativo)
            t0 = r["t_salida_riel"] or 0.0
            tramo = df[(df["t"] >= t0) & (df["t"] <= r["t_apogeo"])]
            ax = fig.add_subplot(2, 3, 5)
            ax.plot(tramo["t"], tramo["alpha"], color="#A32D5A", linewidth=1.3)
            ax.set_title("Ángulo de ataque (riel → apogeo)", fontsize=10); ax.set_xlabel("Tiempo (s)", fontsize=8); ax.set_ylabel("α (°)", fontsize=8)
            ax.tick_params(labelsize=8); ax.grid(True, linestyle="--", alpha=0.5)

            ax = fig.add_subplot(2, 3, 6)
            ax.plot(df["x"], df["z"], color="#0B5CAD", linewidth=1.3)
            ax.set_title("Trayectoria (plano de vuelo)", fontsize=10); ax.set_xlabel("x (m)", fontsize=8); ax.set_ylabel("z (m)", fontsize=8)
            ax.tick_params(labelsize=8); ax.grid(True, linestyle="--", alpha=0.5)

            fig.text(0.5, 0.005, leyenda_eventos, ha="center", fontsize=8, color="#444444")
            fig.tight_layout(pad=1.5, rect=(0, 0.02, 1, 1))

            # 3. Dibujar el canvas y la barra de herramientas en el plot_frame
            for widget in self.plot_frame.winfo_children():
                widget.destroy()
            self.canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
            self.canvas.draw()
            canvas_widget = self.canvas.get_tk_widget()
            canvas_widget.grid(row=0, column=0, sticky="nsew")

            self.toolbar = NavigationToolbar2Tk(self.canvas, self.plot_frame, pack_toolbar=False)
            self.toolbar.update()
            self.toolbar.grid(row=1, column=0, sticky="ew")

        except Exception as e:
            messagebox.showerror("Error al Graficar", f"Ocurrió un error al generar las gráficas:\n{e}")
            self.show_placeholder_message()


class MapTab(customtkinter.CTkFrame):
    """Mapa real (OpenStreetMap) con el sitio de lanzamiento, la trayectoria y el punto de impacto."""

    def __init__(self, parent):
        super().__init__(parent)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.df = None
        self.resumen = None
        self.canvas = None

        info = customtkinter.CTkFrame(self)
        info.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))
        info.grid_columnconfigure(0, weight=1)
        fuente = customtkinter.CTkFont(size=14, weight="bold")
        self.lanzamiento_label = customtkinter.CTkLabel(info, text="Lanzamiento: --", font=fuente, anchor="w")
        self.lanzamiento_label.grid(row=0, column=0, sticky="w", padx=12, pady=(8, 2))
        self.impacto_label = customtkinter.CTkLabel(info, text="Impacto simulado: --", font=fuente, anchor="w")
        self.impacto_label.grid(row=1, column=0, sticky="w", padx=12, pady=2)
        self.real_label = customtkinter.CTkLabel(info, text="", anchor="w")
        self.real_label.grid(row=2, column=0, sticky="w", padx=12, pady=(2, 8))
        self.copy_button = customtkinter.CTkButton(info, text="Copiar coordenadas de impacto", state="disabled", command=self.copiar)
        self.copy_button.grid(row=0, column=1, padx=10, pady=(8, 2))
        self.browser_button = customtkinter.CTkButton(info, text="Abrir mapa interactivo", state="disabled",
                                                      fg_color=ColorPalette.ACCENT_BLUE, command=self.abrir_en_navegador)
        self.browser_button.grid(row=1, column=1, padx=10, pady=2)

        self.plot_frame = customtkinter.CTkFrame(self)
        self.plot_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.plot_frame.grid_columnconfigure(0, weight=1)
        self.plot_frame.grid_rowconfigure(0, weight=1)
        self.show_placeholder_message()

    def show_placeholder_message(self):
        for widget in self.plot_frame.winfo_children():
            widget.destroy()
        self.canvas = None
        customtkinter.CTkLabel(self.plot_frame, text="Ejecute una simulación para ver en el mapa dónde despega y dónde cae el cohete.",
                               font=customtkinter.CTkFont(size=16)).grid(row=0, column=0, sticky="nsew")

    def copiar(self):
        if self.resumen is None: return
        self.clipboard_clear()
        self.clipboard_append(f"{self.resumen['lat_impacto']:.6f}, {self.resumen['lon_impacto']:.6f}")

    def abrir_en_navegador(self):
        if self.df is None: return
        try:
            ruta = mapa.escribir_html(backend.datos_mapa_interactivo(self.df, self.resumen))
            webbrowser.open("file://" + ruta)
        except Exception as e:
            messagebox.showerror("Mapa", f"No se pudo abrir el mapa interactivo:\n{e}")

    def display(self, df, resumen):
        """Dibuja el mapa de la zona con la trayectoria simulada (y la real, si es el mismo sitio)."""
        self.df, self.resumen = df, resumen
        r = resumen
        final = "Impacto simulado" if r["t_impacto"] is not None else "Punto final simulado (sin impacto)"
        self.lanzamiento_label.configure(text=f"Lanzamiento: {r['lat_lanzamiento']:.5f}°, {r['lon_lanzamiento']:.5f}°  ·  {r['altitud_sitio']:.0f} m s. n. m.  ·  azimut {r['azimut_riel']:.0f}°")
        self.impacto_label.configure(text=f"{final}: {r['lat_impacto']:.5f}°, {r['lon_impacto']:.5f}°  ·  a {r['distancia']:.0f} m del sitio, rumbo {r['rumbo_impacto']:.0f}°")
        real = r.get("vuelo_real")
        if real:
            d_real, rumbo_real = backend.distancia_y_rumbo(r["lat_lanzamiento"], r["lon_lanzamiento"], real["ultimo"]["lat"], real["ultimo"]["lon"])
            separacion, _ = backend.distancia_y_rumbo(r["lat_impacto"], r["lon_impacto"], real["ultimo"]["lat"], real["ultimo"]["lon"])
            self.real_label.configure(text=f"Vuelo real: último punto GPS en {real['ultimo']['lat']:.5f}°, {real['ultimo']['lon']:.5f}° ({real['ultimo']['nota']}), "
                                           f"a {d_real:.0f} m del sitio, rumbo {rumbo_real:.0f}°  ·  a {separacion:.0f} m del impacto simulado")
        else:
            self.real_label.configure(text="")
        self.copy_button.configure(state="normal"); self.browser_button.configure(state="normal")

        for widget in self.plot_frame.winfo_children():
            widget.destroy()
        try:
            fondo = r.get("mapa")
            zoom = fondo["zoom"] if fondo else 14
            fig = Figure(figsize=(8, 6), dpi=100, facecolor="#FFFFFF")
            ax = fig.add_subplot(111)
            if fondo:
                ax.imshow(fondo["imagen"], extent=fondo["extent"], interpolation="bilinear")

            px = lambda lat, lon: mapa.a_pixeles(lat, lon, zoom)
            x, y = px(df["latitud"], df["longitud"])
            ax.plot(x, y, color="#1F4FD8", linewidth=2.5, label="Trayectoria simulada")
            if real:
                gps = np.array(real["trayectoria"])
                xr, yr = px(gps[:, 0], gps[:, 1])
                ax.plot(xr, yr, color="#C8102E", linewidth=2.5, linestyle="--", label="Vuelo real (GPS)")
                ax.plot(*px(real["ultimo"]["lat"], real["ultimo"]["lon"]), marker="X", color="#C8102E", markersize=12,
                        markeredgecolor="white", linestyle="none", label="Último punto GPS")
            ax.plot(*px(r["lat_lanzamiento"], r["lon_lanzamiento"]), marker="^", color="#1A7F37", markersize=13,
                    markeredgecolor="white", linestyle="none", label="Lanzamiento")
            ax.plot(*px(r["lat_apogeo"], r["lon_apogeo"]), marker="o", color="#E6A700", markersize=10,
                    markeredgecolor="white", linestyle="none", label=f"Apogeo ({r['apogeo']:.0f} m)")
            ax.plot(*px(r["lat_impacto"], r["lon_impacto"]), marker="X", color="#1F4FD8", markersize=13,
                    markeredgecolor="white", linestyle="none", label=final)

            if fondo:
                izq, der, abajo, arriba = fondo["limites"]
                ax.set_xlim(izq, der); ax.set_ylim(abajo, arriba)
            else:
                ax.margins(0.25); ax.invert_yaxis()
                ax.text(0.5, 0.02, "Sin conexión: no se pudo descargar el mapa de fondo", transform=ax.transAxes, ha="center", fontsize=9, color="#555555")
            ax.set_aspect("equal"); ax.set_xticks([]); ax.set_yticks([])

            # Barra de escala de 1 km
            metros_por_pixel = 156543.03392 * np.cos(np.radians(r["lat_lanzamiento"])) / 2 ** zoom
            x0, x1 = ax.get_xlim(); y0, y1 = ax.get_ylim()
            bx, by = x0 + 0.04 * (x1 - x0), y0 + 0.05 * (y1 - y0)
            ax.plot([bx, bx + 1000 / metros_por_pixel], [by, by], color="black", linewidth=3, solid_capstyle="butt")
            ax.text(bx, by + 0.015 * (y1 - y0), "1 km", fontsize=9, va="bottom")
            if fondo:
                ax.text(0.995, 0.005, fondo["atribucion"], transform=ax.transAxes, ha="right", va="bottom", fontsize=7,
                        bbox=dict(facecolor="white", alpha=0.7, edgecolor="none", pad=1.5))
            ax.legend(loc="upper left", bbox_to_anchor=(1.02, 1.0), fontsize=9, framealpha=0.9, borderaxespad=0)   # fuera del mapa
            fig.tight_layout(pad=0.5)

            self.canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
            self.canvas.draw()
            self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        except Exception as e:
            messagebox.showerror("Mapa", f"No se pudo dibujar el mapa:\n{e}")
            self.show_placeholder_message()


class LoadsTab(customtkinter.CTkFrame):
    """Cargas estructurales durante el ascenso: fuerza axial, cortante y momento flector a lo largo del cohete."""

    def __init__(self, parent):
        super().__init__(parent)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.env = None
        self.canvas = None
        self.toolbar = None

        info = customtkinter.CTkFrame(self)
        info.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))
        info.grid_columnconfigure(0, weight=1)
        self.texto = customtkinter.CTkLabel(info, text="", justify="left", anchor="w", font=customtkinter.CTkFont(size=13))
        self.texto.grid(row=0, column=0, sticky="w", padx=12, pady=8)
        self.export_button = customtkinter.CTkButton(info, text="Exportar CSV", state="disabled", command=self.export_csv)
        self.export_button.grid(row=0, column=1, padx=10, pady=8)

        self.plot_frame = customtkinter.CTkFrame(self)
        self.plot_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.plot_frame.grid_columnconfigure(0, weight=1)
        self.plot_frame.grid_rowconfigure(0, weight=1)
        self.show_placeholder_message()

    def show_placeholder_message(self):
        for widget in self.plot_frame.winfo_children():
            widget.destroy()
        self.canvas = None; self.toolbar = None
        self.texto.configure(text="Cargas a lo largo del cohete durante el ascenso (hasta el apogeo).")
        customtkinter.CTkLabel(self.plot_frame, text="Ejecute una simulación para ver la fuerza axial, el cortante y el momento flector.",
                               font=customtkinter.CTkFont(size=16)).grid(row=0, column=0, sticky="nsew")

    def export_csv(self):
        if self.env is None: return
        filepath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")], title="Exportar cargas")
        if not filepath: return
        try:
            tabla_envolvente(self.env).to_csv(filepath, index=False)
        except Exception as e:
            messagebox.showerror("Error al Exportar", f"No se pudo guardar el archivo:\n{e}")

    def display(self, resumen):
        env = resumen.get("cargas")
        if env is None:
            self.show_placeholder_message(); return
        self.env = env
        lineas = texto_maximos(env)
        if resumen.get("fuerza_apertura_principal") is not None:
            lineas.append(f"Apertura del paracaídas principal: {resumen['fuerza_apertura_principal']:.0f} N ({resumen['g_apertura_principal']:.1f} g)")
        elif resumen.get("fuerza_apertura_drogue") is not None:
            lineas.append(f"Apertura del drogue: {resumen['fuerza_apertura_drogue']:.0f} N ({resumen['g_apertura_drogue']:.1f} g)")
        if resumen.get("resistencia"):
            lineas += resistencia.texto_resumen(resumen["resistencia"])
        self.texto.configure(text="\n".join(lineas))
        self.export_button.configure(state="normal")
        for widget in self.plot_frame.winfo_children():
            widget.destroy()
        try:
            fig = Figure(figsize=(9, 7), dpi=100, facecolor="#FFFFFF")
            graficar_envolvente(fig, env)
            self.canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
            self.canvas.draw()
            self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
            self.toolbar = NavigationToolbar2Tk(self.canvas, self.plot_frame, pack_toolbar=False)
            self.toolbar.update()
            self.toolbar.grid(row=1, column=0, sticky="ew")
        except Exception as e:
            messagebox.showerror("Cargas", f"No se pudieron dibujar las cargas:\n{e}")
            self.show_placeholder_message()


class StabilityTab(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.configure(fg_color=ColorPalette.BG_FRAME)
        self.grid_columnconfigure(0, weight=1); self.grid_rowconfigure(1, weight=1)
        control_frame = customtkinter.CTkFrame(self); control_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.calc_button = customtkinter.CTkButton(control_frame, text="Calcular CG y CP", command=self.calculate_stability); self.calc_button.pack(side="left", padx=10, pady=10)
        customtkinter.CTkLabel(control_frame, text="Posiciones medidas desde la punta de la nariz. Margen estático = (CP − CG) / diámetro.").pack(side="left", padx=10)
        self.table_frame = customtkinter.CTkFrame(self); self.table_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.table_frame.grid_columnconfigure(0, weight=1); self.table_frame.grid_rowconfigure(0, weight=1); self.create_table()
        summary_frame = customtkinter.CTkFrame(self); summary_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew"); summary_frame.grid_columnconfigure((0, 1, 2), weight=1)
        fuente = customtkinter.CTkFont(size=18, weight="bold")
        self.cg_total_label = customtkinter.CTkLabel(summary_frame, text="CG: -- m", font=fuente); self.cg_total_label.grid(row=0, column=0, padx=10, pady=10)
        self.cp_total_label = customtkinter.CTkLabel(summary_frame, text="CP: -- m", font=fuente); self.cp_total_label.grid(row=0, column=1, padx=10, pady=10)
        self.margin_label = customtkinter.CTkLabel(summary_frame, text="Margen Estático: -- cal", font=fuente); self.margin_label.grid(row=0, column=2, padx=10, pady=10)

    def create_table(self):
        style = ttk.Style(self); style.theme_use("default")
        style.configure("Treeview", background="#9BB6FF", foreground="black", rowheight=25, fieldbackground="#F0F0F0")
        style.map("Treeview", background=[('selected', '#347083')]); style.configure("Treeview.Heading", background="#D3D3D3", font=('Calibri', 10,'bold'))
        self.tree = ttk.Treeview(self.table_frame, columns=("Componente", "Masa", "CG", "CP"), show="headings")
        self.tree.heading("Componente", text="Componente"); self.tree.heading("Masa", text="Masa (kg)")
        self.tree.heading("CG", text="Centro de Gravedad (m)"); self.tree.heading("CP", text="Centro de Presión (m)")
        self.tree.grid(row=0, column=0, sticky="nsew")

    def calculate_stability(self):
        app = self.winfo_toplevel(); params = app.rocket_tab.get_params()
        if params is None: messagebox.showerror("Error", "Parámetros del cohete no válidos."); return
        try:
            est = backend.analizar_estabilidad(params, app.data_tables_tab.filepaths)
        except Exception as e:
            messagebox.showerror("Error de Estabilidad", f"No se pudo calcular la estabilidad:\n\n{e}"); return
        for item in self.tree.get_children(): self.tree.delete(item)
        for nombre, masa, cg, cp in est["filas"]:
            self.tree.insert("", "end", values=(nombre, f"{masa:.3f}", f"{cg:.3f}", "N/A" if cp is None else f"{cp:.3f}"))
        self.tree.insert("", "end", values=("TOTAL (despegue)", f"{est['masa']:.3f}", f"{est['cg']:.3f}", f"{est['cp']:.3f}"))
        self.cg_total_label.configure(text=f"CG: {est['cg']:.3f} m (despegue) · {est['cg_seco']:.3f} m (sin propelente)")
        self.cp_total_label.configure(text=f"CP: {est['cp']:.3f} m")
        self.margin_label.configure(text=f"Margen Estático: {est['margen']:.2f} cal (despegue) · {est['margen_seco']:.2f} cal (sin propelente)")


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.configure(fg_color=ColorPalette.BG_FRAME)
        self.title("Simulador de Trayectoria de Cohetes -NEMB"); self.geometry("1400x900")
        self.grid_columnconfigure(0, weight=1); self.grid_rowconfigure(0, weight=1)
        customtkinter.set_appearance_mode("Dark"); customtkinter.set_default_color_theme("dark-blue")
        self.main_frame = customtkinter.CTkFrame(self, fg_color="transparent"); self.main_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.left_frame = customtkinter.CTkFrame(self.main_frame); self.left_frame.grid(row=0, column=0, sticky="nsew")
        self.left_frame.grid_rowconfigure(0, weight=1); self.left_frame.grid_columnconfigure(0, weight=1)
        self.right_frame = customtkinter.CTkFrame(self.main_frame); self.right_frame.grid_rowconfigure(1, weight=1); self.right_frame.grid_columnconfigure(0, weight=1)
        self.tab_view = customtkinter.CTkTabview(self.left_frame, command=self._on_tab_change); self.tab_view.grid(row=0, column=0, sticky="nsew")
        self.tab_view.add("Cohete"); self.tab_view.add("Tablas de Datos"); self.tab_view.add("Simulación"); self.tab_view.add("Análisis (CG-CP)"); self.tab_view.add("Resultados"); self.tab_view.add("Mapa"); self.tab_view.add("Cargas")
        self.rocket_tab = RocketTab(self.tab_view.tab("Cohete")); self.rocket_tab.pack(expand=True, fill="both")
        self.data_tables_tab = DataTablesTab(self.tab_view.tab("Tablas de Datos")); self.data_tables_tab.pack(expand=True, fill="both")
        self.sim_env_tab = SimulationEnvironmentTab(self.tab_view.tab("Simulación")); self.sim_env_tab.pack(expand=True, fill="both")
        self.stability_tab = StabilityTab(self.tab_view.tab("Análisis (CG-CP)")); self.stability_tab.pack(expand=True, fill="both")
        self.results_tab = ResultsTab(self.tab_view.tab("Resultados")); self.results_tab.pack(expand=True, fill="both")
        self.map_tab = MapTab(self.tab_view.tab("Mapa")); self.map_tab.pack(expand=True, fill="both")
        self.loads_tab = LoadsTab(self.tab_view.tab("Cargas")); self.loads_tab.pack(expand=True, fill="both")
        self.vis_label = customtkinter.CTkLabel(self.right_frame, text="Visualización del Cohete", font=customtkinter.CTkFont(size=16, weight="bold")); self.vis_label.grid(row=0, column=0, padx=10, pady=10)
        self.vis_canvas_frame = customtkinter.CTkFrame(self.right_frame); self.vis_canvas_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.vis_canvas_frame.grid_rowconfigure(0, weight=1); self.vis_canvas_frame.grid_columnconfigure(0, weight=1)
        self.control_frame = customtkinter.CTkFrame(self, height=80); self.control_frame.grid(row=1, column=0, padx=10, pady=(0,10), sticky="ew")
        self.control_frame.grid_columnconfigure(1, weight=1); self.create_control_widgets()
        self.executor = None; self.future = None; self.sim_start = 0.0
        self._on_tab_change(); self.after(100, self.draw_rocket)

    def _on_tab_change(self):
        if self.tab_view.get() == "Cohete": self.main_frame.grid_columnconfigure(0, weight=2); self.main_frame.grid_columnconfigure(1, weight=1, minsize=10); self.right_frame.grid(row=0, column=1, padx=(2,0), sticky="nsew")
        else: self.right_frame.grid_remove(); self.main_frame.grid_columnconfigure(0, weight=1); self.main_frame.grid_columnconfigure(1, weight=0)

    def create_control_widgets(self):
        button_frame = customtkinter.CTkFrame(self.control_frame); button_frame.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.run_button = customtkinter.CTkButton(button_frame, text="Ejecutar Simulación",fg_color=ColorPalette.BUTTON_GREEN ,command=self.run_simulation); self.run_button.pack(side="left", padx=5)
        customtkinter.CTkButton(button_frame, text="Actualizar Cohete", fg_color=ColorPalette.ACCENT_VIOLET ,command=self.draw_rocket).pack(side="left", padx=5)
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

    # ------------------------------------------------------------------ Simulación
    def run_simulation(self):
        params = self.collect_all_params()
        if params is None: messagebox.showerror("Error de Validación", "Revise los valores numéricos."); return
        rutas = dict(self.data_tables_tab.filepaths)
        if any(r == "No cargado" for r in rutas.values()):
            messagebox.showerror("Faltan Datos", "Cargue los archivos de Empuje, Arrastre y Masa en 'Tablas de Datos'."); return
        if self.future is not None and not self.future.done(): messagebox.showwarning("Simulación en Curso", "Espere."); return
        try:
            backend.validar_parametros(params)
        except ValueError as e:
            messagebox.showerror("Error de Validación", str(e)); return
        self.run_button.configure(state="disabled"); self.results_tab.show_placeholder_message(); self.tab_view.set("Resultados"); self._on_tab_change()
        self.progress_bar.configure(mode="indeterminate"); self.progress_bar.start()
        # La simulación corre en otro proceso: la ventana sigue respondiendo y el cálculo
        # no comparte memoria con Tk (ejecutar el simulador en un hilo de la interfaz no es seguro).
        self.executor = ProcessPoolExecutor(max_workers=1, mp_context=multiprocessing.get_context("spawn"))
        self.future = self.executor.submit(backend.ejecutar_simulacion, params, rutas, None, True)   # con el mapa de la zona
        self.sim_start = time.time()
        self.after(200, self._poll_simulation)

    def _poll_simulation(self):
        """Revisa periódicamente, desde la interfaz, si el proceso de simulación ya terminó."""
        if not self.future.done():
            self.update_status(f"Simulando el vuelo... {time.time() - self.sim_start:.0f} s")
            self.after(200, self._poll_simulation)
            return
        self.executor.shutdown(wait=False)
        try:
            df, resumen = self.future.result()
        except Exception as e:
            self.simulation_failed(e)
        else:
            self.simulation_finished(df, resumen)

    def _stop_progress(self, valor):
        self.progress_bar.stop(); self.progress_bar.configure(mode="determinate"); self.progress_bar.set(valor)

    def simulation_finished(self, df, resumen):
        self._stop_progress(1); self.run_button.configure(state="normal")
        self.update_status(f"Simulación completada con {backend.etiqueta(resumen['integrador'])}: apogeo {resumen['apogeo']:.0f} m en t = {resumen['t_apogeo']:.1f} s")
        self.results_tab.display_results(df, resumen)
        self.map_tab.display(df, resumen)
        self.loads_tab.display(resumen)
        # Con Tk 8, marcar también el impacto y la trayectoria en el mapa de la pestaña "Simulación"
        widget_mapa = self.sim_env_tab.map_widget
        if widget_mapa is not None:
            try:
                widget_mapa.delete_all_path()
                widget_mapa.set_marker(resumen["lat_impacto"], resumen["lon_impacto"], text="Impacto simulado")
                widget_mapa.set_path(list(zip(df["latitud"].iloc[::50], df["longitud"].iloc[::50])))
            except Exception as e:
                print(f"No se pudo actualizar el mapa interactivo: {e}")

    def simulation_failed(self, error):
        self._stop_progress(0); self.run_button.configure(state="normal"); self.update_status(f"Error: {error}")
        messagebox.showerror("Error de Simulación", f"Ocurrió un error en el simulador:\n\n{error}")

    def update_progress(self, value): self.progress_bar.set(value)
    def update_status(self, message): self.status_label.configure(text=message)

    # ------------------------------------------------------------------ Esquema del cohete
    def draw_rocket(self):
        """Dibuja el cohete con la nariz arriba. El eje vertical es Z medido desde la punta de la nariz."""
        params = self.rocket_tab.get_params()
        if params is None: messagebox.showerror("Error de Parámetros", "No se puede dibujar el cohete."); return
        for widget in self.vis_canvas_frame.winfo_children(): widget.destroy()
        try:
            p = lambda clave: float(params.get(clave, 0))
            fig = Figure(figsize=(5, 8), dpi=100); ax = fig.add_subplot(111); ax.set_aspect('equal', adjustable='box')
            tubos = [('coples', "#FFFFFF"), ('tubo_recup', '#ADD8E6'), ('transfer', '#87CEEB'),
                     ('tanque_vacio', '#6495ED'), ('valvulas', '#4682B4'), ('cc', '#5F9EA0')]
            total_len = 0
            for pref, color in tubos:
                pos_z, length, diam = p(f'{pref}_pos_z'), p(f'{pref}_len'), p(f'{pref}_diam_ext')
                total_len = max(total_len, pos_z + length)
                ax.add_patch(patches.Rectangle((-diam/2, pos_z), diam, length, facecolor=color, edgecolor='black'))
            # Nariz: punta en pos_z, base en pos_z + longitud
            nose_len, nose_pos, nose_diam = p('nose_len'), p('nose_pos_z'), p('nose_diam')
            ax.add_patch(patches.Polygon([(0, nose_pos), (nose_diam/2, nose_pos+nose_len), (-nose_diam/2, nose_pos+nose_len)], facecolor='#D9534F', edgecolor='black'))
            # Boattail: diámetro frontal arriba, trasero abajo
            bt_len, bt_pos, bt_d1, bt_d2 = p('bt_len'), p('bt_pos_z'), p('bt_diam_front'), p('bt_diam_rear')
            total_len = max(total_len, nose_pos + nose_len, bt_pos + bt_len)
            ax.add_patch(patches.Polygon([(-bt_d1/2, bt_pos), (bt_d1/2, bt_pos), (bt_d2/2, bt_pos+bt_len), (-bt_d2/2, bt_pos+bt_len)], facecolor='#5BC0DE', edgecolor='black'))
            if p('fin_num') > 0:
                fin_pos, root_c, tip_c, span, xr = p('fin_pos_z'), p('fin_root_chord'), p('fin_tip_chord'), p('fin_span'), p('fin_xr')
                r = p('cc_diam_ext') / 2
                fin_points_right = [(r, fin_pos), (r, fin_pos+root_c), (r+span, fin_pos+xr+tip_c), (r+span, fin_pos+xr)]
                ax.add_patch(patches.Polygon(fin_points_right, facecolor='#F0AD4E', edgecolor='black'))
                ax.add_patch(patches.Polygon([(-x, y) for x, y in fin_points_right], facecolor='#F0AD4E', edgecolor='black'))
                total_len = max(total_len, fin_pos + max(root_c, xr + tip_c))
            # CG y CP reales (del simulador), si los parámetros y las tablas lo permiten
            try:
                est = backend.analizar_estabilidad(params, self.data_tables_tab.filepaths)
                ax.plot(0, est['cg'], marker='o', color='#1F4FD8', markersize=9, linestyle='none', label=f"CG {est['cg']:.2f} m")
                ax.plot(0, est['cp'], marker='X', color='#C8102E', markersize=9, linestyle='none', label=f"CP {est['cp']:.2f} m")
                ax.legend(loc='center left', bbox_to_anchor=(1.3, 0.5), fontsize=8, title=f"Margen: {est['margen']:.2f} cal", title_fontsize=8)   # fuera del dibujo
            except Exception as e:
                print(f"No se pudo calcular CG/CP para el esquema: {e}")
            ancho = max(nose_diam, 0.05) * 1.5 + p('fin_span')
            ax.set_xlim(-ancho, ancho); ax.set_ylim(total_len + 0.1, -0.1)   # eje invertido: nariz arriba
            ax.set_ylabel("Z desde la punta de la nariz (m)"); ax.set_xticks([]); ax.grid(True, axis='y', linestyle='--', alpha=0.4)
            ax.set_title("Esquema del Cohete"); fig.tight_layout()
            canvas = FigureCanvasTkAgg(fig, master=self.vis_canvas_frame); canvas.draw(); canvas.get_tk_widget().pack(fill="both", expand=True)
        except Exception as e:
            messagebox.showerror("Error de Parámetros", f"No se puede dibujar el cohete:\n{e}")

    # ------------------------------------------------------------------ Configuración
    def save_configuration(self):
        params = self.collect_all_params()
        if params is None: messagebox.showerror("Error", "No se pueden guardar datos inválidos."); return
        filepath = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")], title="Guardar Configuración")
        if not filepath: return
        try:
            with open(filepath, 'w', encoding='utf-8') as f: json.dump(params, f, indent=4, ensure_ascii=False)
            self.update_status(f"Configuración guardada en {os.path.basename(filepath)}")
        except Exception as e: messagebox.showerror("Error al Guardar", f"No se pudo guardar el archivo:\n{e}")

    def load_configuration(self):
        filepath = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")], title="Cargar Configuración")
        if not filepath: return
        try:
            with open(filepath, 'r', encoding='utf-8') as f: params = json.load(f)
            all_widgets = {**self.rocket_tab.widgets, **self.sim_env_tab.widgets}
            for name, widget in all_widgets.items():
                if name not in params: continue
                if isinstance(widget, customtkinter.CTkEntry): widget.delete(0, "end"); widget.insert(0, str(params[name]))
                elif isinstance(widget, customtkinter.CTkOptionMenu):
                    if params[name] in widget.cget("values"): widget.set(params[name])
            self.update_status(f"Configuración cargada desde {os.path.basename(filepath)}")
            for data_type in ["thrust", "drag", "mass"]:
                if data_type in params and os.path.exists(params[data_type]):
                    self.data_tables_tab.load_csv(data_type, params[data_type], visualizar=False)
            self.draw_rocket(); self.sim_env_tab.update_map_position()
        except Exception as e:
            messagebox.showerror("Error al Cargar", f"No se pudo cargar o leer el archivo:\n{e}")

if __name__ == "__main__":
    app = App()
    app.mainloop()
