import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import pandas as pd
import json
import time
from datetime import datetime
import sys
import os
import traceback # Para imprimir tracebacks detallados
import math # Asegurarse que math está importado

# --- Manejo de Dependencias ---
SCIPY_AVAILABLE = False
CUSTOM_INTEGRATORS_AVAILABLE = False
VISUALIZATION_AVAILABLE = False

try:
    from scipy.integrate import solve_ivp
    SCIPY_AVAILABLE = True
    print("SciPy encontrado y cargado.")
except ImportError:
    print("Advertencia: SciPy no está instalado. Los métodos de solve_ivp no estarán disponibles.")

try:
    # Ajusta esta ruta si tu estructura de directorios es diferente.
    # Sube dos niveles desde Simulador/GUI/ para llegar a la raíz del proyecto
    package_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    if package_path not in sys.path:
        sys.path.append(package_path)
        print(f"Añadido al path: {package_path}")

    # Importa los módulos necesarios desde tus paquetes
    from Simulador.src.condiciones_init import latitud_cord, longitud_cord, altitud_cord, fecha, riel, viento_actual, atmosfera_actual
    from Paquetes.PaqueteFisica.vuelo import Vuelo
    from Paquetes.PaqueteFisica.viento import Viento
    from Paquetes.PaqueteFisica.riel import Torrelanzamiento
    from Paquetes.PaqueteFisica.atmosfera import atmosfera
    from Paquetes.PaqueteFisica.componentes import Componente, Cono, Cilindro, Aletas, Boattail # Importa clases de componentes
    from Paquetes.PaqueteFisica.cohete import Cohete
    print("Módulos de Física cargados.")

    # Intenta importar integradores personalizados desde la ruta correcta
    try:
        from Paquetes.PaqueteEDOs.integradores import Euler, RungeKutta4 # Asume que estas clases existen
        CUSTOM_INTEGRATORS_AVAILABLE = True
        print("Integradores personalizados (Euler, RungeKutta4) encontrados en Paquetes.PaqueteEDOs.integradores.")
    except ImportError:
        print("Advertencia: No se encontraron los integradores personalizados (Euler, RungeKutta4) en Paquetes.PaqueteEDOs.integradores.")

    # Intenta importar la función de dibujo
    try:
        from Paquetes.utils.dibujar_cohete2 import dibujar_cohete2
        VISUALIZATION_AVAILABLE = True
        print("Función dibujar_cohete2 encontrada en Paquetes.utils.dibujar_cohete2.")
    except ImportError:
        print("Advertencia: No se encontró la función 'dibujar_cohete2' en Paquetes.utils.dibujar_cohete2. La pestaña de visualización estará deshabilitada.")


except ImportError as e:
    messagebox.showerror("Error de Importación de Física/Utils",
                         f"No se pudieron importar módulos necesarios: {e}\n"
                         f"Asegúrate de que los paquetes 'Simulador', 'Paquetes' y 'Paquetes.utils' estén en la ruta correcta:\n{package_path}\n"
                         f"Traceback: {traceback.format_exc()}")
    sys.exit(1)
except Exception as e:
    messagebox.showerror("Error Inesperado en Importación", f"Ocurrió un error durante la inicialización: {e}\nTraceback: {traceback.format_exc()}")
    sys.exit(1)


class SimuladorCohetesAvanzado:
    """
    Clase principal para la interfaz gráfica del simulador de cohetes suborbitales.
    Permite selección de método de integración. Usa valores Xitle por defecto.
    Muestra componentes externos e internos en pestañas separadas.
    Incluye pestaña de visualización del cohete.
    Intenta cargar CSVs predeterminados al inicio considerando la estructura de archivos.
    """
    def __init__(self, master):
        self.master = master
        self.master.title("Simulador de Cohetes Suborbitales Avanzado (Xitle Detallado)")
        self.master.geometry("1200x950") # Aumentar altura para más campos

        # --- Estilos ---
        azul = '#151E3D' # Dark Denim
        rojo = '#90091d' # Dark Red
        verde_sim = '#228B22' # Forest Green
        morado_upd = '#8A2BE2' # BlueViolet
        font_selection = ('Lucida Sans Unicode', 10)
        self.master.configure(bg=azul)
        self.style = ttk.Style()
        self.style.theme_use('clam')
        # Estilo Botón Simular (Verde)
        self.style.configure('Sim.TButton', font=(font_selection[0], font_selection[1], 'bold'), background=verde_sim, foreground='white', borderwidth=1)
        self.style.map('Sim.TButton', background=[('active', '#2E8B57')]) # Sea Green on hover
        # Estilo Botón Actualizar (Morado)
        self.style.configure('Update.TButton', font=font_selection, background=morado_upd, foreground='white', borderwidth=1)
        self.style.map('Update.TButton', background=[('active', '#9932CC')]) # DarkOrchid on hover
        # Estilo Botones Normales (Rojo)
        self.style.configure('TButton', font=font_selection, background=rojo, foreground='white', borderwidth=1)
        self.style.map('TButton', background=[('active', '#b80b25')]) # Hover/active color
        # Estilo Botones Visualizar CSV (Azul Claro)
        self.style.configure('Vis.TButton', font=font_selection, background='#ADD8E6', foreground='black', borderwidth=1) # Light Blue
        self.style.map('Vis.TButton', background=[('active', '#87CEEB')]) # Sky Blue on hover
        # Otros estilos
        self.style.configure('TLabel', font=font_selection, background=azul, foreground='white')
        self.style.configure('TEntry', font=font_selection, fieldbackground='white', foreground='black')
        self.style.configure('TCombobox', font=font_selection, fieldbackground='white', foreground='black')
        self.style.configure('TNotebook', background=azul)
        self.style.configure('TNotebook.Tab', font=font_selection, background=azul, foreground='gray', padding=[5, 2])
        self.style.map('TNotebook.Tab', background=[('selected', azul)], foreground=[('selected', 'white')])
        self.style.configure('TFrame', background=azul)
        self.style.configure('Horizontal.TProgressbar', background=rojo)


        # --- Variables de Estado ---
        self.rocket = None
        self.thrust_data = None # DataFrame for thrust curve (for plotting)
        self.cd_data = None     # DataFrame for Cd vs Mach (for plotting)
        self.mass_data = None   # DataFrame for Mass vs Time (for plotting)
        self.loaded_thrust_path = None # Path to the loaded thrust CSV
        self.loaded_cd_path = None     # Path to the loaded Cd CSV
        self.loaded_mass_path = None   # Path to the loaded mass CSV
        self.simulation_data = None
        self.simulation_summary = None
        self.simulation_done = False
        self.selected_integrator = tk.StringVar() # Para el combobox del integrador
        self.component_widgets = {} # Diccionario para guardar widgets de componentes

        # --- Rutas Predeterminadas de Archivos CSV (Ajustadas a la estructura) ---
        script_dir = os.path.dirname(os.path.abspath(__file__)) # Directorio del script actual
        project_root = os.path.abspath(os.path.join(script_dir, '..', '..')) # Sube dos niveles
        self.default_cd_file_path = os.path.join(project_root, "Archivos", "DatosVuelo", "cdmachXitle.csv")
        self.default_thrust_file_path = os.path.join(project_root, "Archivos", "CurvasEmpuje", "MegaPunisherBien.csv")
        self.default_mass_file_path = os.path.join(project_root, "Archivos", "CurvasEmpuje", "MegaPunisherFatMasadot.csv")
        print(f"Ruta raíz detectada: {project_root}")
        print(f"Ruta default Cd: {self.default_cd_file_path}")
        print(f"Ruta default Empuje: {self.default_thrust_file_path}")
        print(f"Ruta default Masa: {self.default_mass_file_path}")


        # --- Valores Predeterminados del Cohete Xitle (Directamente de XitleFile.py) ---
        self.xitle_defaults = {
            "diam_ext": 0.152, "espesor": 0.003,
            "nariz": {"masa": 0.8, "longitud": 0.81, "geometria": "ogiva"},
            "coples": {"masa": 1.5, "longitud": 0.176},
            "tubo_recup": {"masa": 2.3, "longitud": 0.92},
            "transfer": {"masa": 1.0, "longitud": 0.25},
            "tanquevacio": {"masa": 8.7, "longitud": 1.25},
            "valvulas": {"masa": 2.4, "longitud": 0.167},
            "cc": {"masa": 4.3, "longitud": 0.573}, # Clave en minúsculas como en XitleFile
            "aletas": {"masa": 1.1, "numf": 4, "semispan": 0.11, "C_r": 0.3, "C_t": 0.1, "mid_sweep_deg": 25},
            "boattail": {"masa": 0.251, "longitud": 0.12, "dR": 0.132},
            # Valores predeterminados para internos (si se añaden a la GUI)
            "avionica": {"masa": 0.5, "longitud": 0.1}, # Ejemplo
            "cu": {"masa": 1.0, "longitud": 0.2},        # Ejemplo (Carga Útil)
            "drogue": {"masa": 0.1, "diametro": 0.6},   # Ejemplo (Paracaídas)
            "main": {"masa": 0.3, "diametro": 1.5}       # Ejemplo (Paracaídas)
        }

        # --- Inicialización del Objeto Cohete con componentes Xitle detallados ---
        self.xitle_components_init = {}
        current_z = 0.0 # Posición inicial Z
        try:
            # Nariz
            cfg = self.xitle_defaults["nariz"]
            d_ext = self.xitle_defaults["diam_ext"]
            nariz_init = Cono("Nariz", cfg["masa"], np.array([0.0, 0.0, current_z]),
                              longitud=cfg["longitud"], diametro=d_ext, geometria=cfg["geometria"])
            self.xitle_components_init["Nariz"] = nariz_init
            current_z = nariz_init.bottom[2]

            # Componentes Cilíndricos (en orden)
            cilindros_keys = ["coples", "tubo_recup", "transfer", "tanquevacio", "valvulas", "cc"] # Clave 'cc' en minúsculas
            for key in cilindros_keys:
                cfg = self.xitle_defaults[key]
                d_int = d_ext - 2 * self.xitle_defaults["espesor"]
                comp_key_title = key.replace("_", " ").capitalize() # Para nombre del objeto
                comp = Cilindro(comp_key_title, cfg["masa"], np.array([0.0, 0.0, current_z]),
                                longitud=cfg["longitud"], diametroexterior=d_ext, diametrointerior=d_int)
                # Workaround para componentes base
                comp.CG = np.array([0.0, 0.0, cfg["longitud"] / 2.0]) # CG en centro geométrico
                comp.CP = np.zeros(3); comp.CN = 0
                self.xitle_components_init[comp_key_title] = comp # Usar clave capitalizada
                current_z = comp.bottom[2]

            # Aletas (posición relativa al final del último cilindro - CC)
            cfg_aletas = self.xitle_defaults["aletas"]
            # Usar la Z final del último componente cilíndrico (CC)
            pos_aletas_init = np.array([0.0, 0.0, current_z - cfg_aletas["C_r"]]) # Montaje por cuerda raíz al final de CC
            aletas_init = Aletas("Aletas", cfg_aletas["masa"], pos_aletas_init,
                                 diametro=d_ext, numf=cfg_aletas["numf"], semispan=cfg_aletas["semispan"],
                                 C_r=cfg_aletas["C_r"], C_t=cfg_aletas["C_t"], X_R=0.0,
                                 mid_sweep=np.deg2rad(cfg_aletas["mid_sweep_deg"]))
            self.xitle_components_init["Aletas"] = aletas_init

            # Boattail (después del último cilindro - CC)
            cfg_boat = self.xitle_defaults["boattail"]
            pos_boat_init = np.array([0.0, 0.0, current_z]) # Al final de CC
            boattail_init = Boattail("Boattail", cfg_boat["masa"], pos_boat_init,
                                     longitud=cfg_boat["longitud"], diamF_boat=d_ext,
                                     diamR_boat=cfg_boat["dR"], espesor=self.xitle_defaults["espesor"])
            self.xitle_components_init["Boattail"] = boattail_init

            # Crear instancia inicial del cohete pasando el diccionario COMPLETO
            # Definir explícitamente componentes externos para Cohete.__init__
            external_keys_init = ["Nariz", "Coples", "Tubo recup", "Transfer", "Tanquevacio", "Valvulas", "Cc", "Boattail"]
            external_components_init = {k: v for k, v in self.xitle_components_init.items() if k in external_keys_init}

            self.rocket = Cohete("Xitle (Default)", "hibrido", self.xitle_components_init, external_components_init,
                                 None, None, None, riel)
            self.rocket.d_ext = self.diam_ext_xitle # Establecer diámetro de referencia explícitamente
            # calcular_propiedades se llamará después de cargar CSVs

        except KeyError as e:
             messagebox.showerror("Error Clave Xitle", f"No se encontró la clave '{e}' en xitle_defaults.")
             self.xitle_components_init = {}
             self.rocket = None
        except NameError as e:
             messagebox.showwarning("Advertencia Componentes", f"No se pudieron crear los componentes iniciales (Xitle). Clase no definida: {e}")
             self.xitle_components_init = {}
             self.rocket = None
        except TypeError as e:
             messagebox.showerror("Error Argumentos", f"Error al crear componente inicial (Xitle), revisa argumentos: {e}\n{traceback.format_exc()}")
             self.xitle_components_init = {}
             self.rocket = None
        except Exception as e:
            messagebox.showerror("Error Cohete Inicial", f"Error creando cohete inicial (Xitle): {e}\n{traceback.format_exc()}")
            self.xitle_components_init = {}
            self.rocket = None

        # --- Interfaz Gráfica ---
        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)

        # Crear pestañas en el orden deseado
        self.create_rocket_tabs() # Crea las pestañas de componentes externos e internos
        self.create_visualization_tab() # Crear la pestaña de visualización DESPUÉS de las de componentes
        self.create_csv_import_tab() # Crea etiquetas y botones de visualización
        self.create_input_tab()
        self.create_trajectory_tab()
        self.create_position_tab()
        self.create_forces_tab()
        self.create_angles_tab()
        self.create_stability_tab()
        self.create_wind_tab()
        self.create_summary_tab()


        # --- Cargar Datos CSV Predeterminados (Ahora que los elementos GUI existen) ---
        # Los botones de visualización se pasan para poder habilitarlos
        self._load_and_store_csv("thrust", self.default_thrust_file_path, self.thrust_file_label, self.btn_visualize_thrust)
        self._load_and_store_csv("cd_vs_mach", self.default_cd_file_path, self.cd_file_label, self.btn_visualize_cd)
        self._load_and_store_csv("mass_vs_time", self.default_mass_file_path, self.mass_file_label, self.btn_visualize_mass)

        # --- Actualizar Objeto Cohete con rutas CSV y calcular propiedades ---
        if self.rocket:
            # Llamar a los métodos de carga de Cohete usando las rutas almacenadas en la GUI
            try:
                if self.loaded_cd_path:
                    self.rocket.cargar_tabla_Cd(self.loaded_cd_path)
                if self.loaded_thrust_path and self.loaded_mass_path:
                    self.rocket.cargar_tablas_motor(self.loaded_thrust_path, self.loaded_mass_path)
                self.rocket.calcular_propiedades() # Calcular con datos cargados
                print("Propiedades del Cohete recalculadas con datos CSV predeterminados.")
            except AttributeError as ae:
                 print(f"Advertencia: Error llamando métodos de carga en Cohete ({ae}). Asegúrate que Cohete tiene 'cargar_tabla_Cd' y 'cargar_tablas_motor'.")
            except Exception as e:
                 print(f"Advertencia: Error al cargar tablas CSV en Cohete: {e}")


        # --- Intentar graficar datos predeterminados ---
        if self.thrust_data is not None:
            self.plot_csv_data("thrust")
        elif self.cd_data is not None:
            self.plot_csv_data("cd_vs_mach")
        elif self.mass_data is not None:
            self.plot_csv_data("mass_vs_time")
        else:
             self.plot_csv_data("none") # Mostrar gráfica vacía si no se cargaron defaults

    # --- Helper function to load default CSV ---
    def _load_and_store_csv(self, data_type, file_path, label_widget, visualize_button):
        """Intenta cargar un archivo CSV predeterminado, valida columnas,
           almacena DataFrame y ruta, y actualiza GUI."""
        df = None
        loaded_path = None # Variable local para la ruta cargada en esta llamada
        try:
            print(f"Intentando cargar predeterminado: {file_path}")
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Archivo no encontrado en la ruta: {file_path}")

            df = pd.read_csv(file_path)
            file_name = os.path.basename(file_path)
            print(f"Cargado: {file_name}")
            loaded_path = file_path # Guardar ruta si la carga fue exitosa

            if data_type == "thrust":
                # Verificar/Renombrar columnas
                if 'Time' in df.columns and 'Thrust' in df.columns: pass
                elif df.shape[1] >= 2:
                    print(f"Advertencia: Renombrando columnas de {file_name} a ['Time', 'Thrust']")
                    df.columns = ['Time', 'Thrust'] + list(df.columns[2:])
                else: raise ValueError("Archivo de empuje no tiene 2 columnas.")
                self.thrust_data = df
                self.loaded_thrust_path = loaded_path # Almacenar ruta en el objeto GUI
                label_widget.config(text=f"Empuje: {file_name}")
                visualize_button.config(state=tk.NORMAL) # Habilitar botón

            elif data_type == "cd_vs_mach":
                 # Verificar/Renombrar columnas
                 if 'Mach' in df.columns and 'Cd' in df.columns: pass
                 elif df.shape[1] >= 2:
                      print(f"Advertencia: Renombrando columnas de {file_name} a ['Mach', 'Cd']")
                      df.columns = ['Mach', 'Cd'] + list(df.columns[2:])
                 else: raise ValueError("Archivo Cd vs Mach no tiene 2 columnas.")
                 self.cd_data = df
                 self.loaded_cd_path = loaded_path # Almacenar ruta en el objeto GUI
                 label_widget.config(text=f"Arrastre: {file_name}")
                 visualize_button.config(state=tk.NORMAL) # Habilitar botón

            elif data_type == "mass_vs_time":
                 # Verificar columnas necesarias para cohete.py
                 expected_cols = ['Time (s)', 'Oxidizer Mass (kg)', 'Fuel Mass (kg)']
                 if all(col in df.columns for col in expected_cols):
                      self.mass_data = df # Almacenar DataFrame completo
                      self.loaded_mass_path = loaded_path # Almacenar ruta en el objeto GUI
                      label_widget.config(text=f"Masa: {file_name}")
                      visualize_button.config(state=tk.NORMAL) # Habilitar botón
                 else:
                      # Intentar formato simple 'Time', 'Mass' para graficar
                      if 'Time' in df.columns and 'Mass' in df.columns:
                           print(f"Advertencia: {file_name} tiene formato simple ['Time', 'Mass']. Se usará para graficar, pero Cohete espera formato detallado.")
                           self.mass_data = df
                           self.loaded_mass_path = None # No es el formato esperado por Cohete
                           label_widget.config(text=f"Masa: {file_name} (Simple)")
                           visualize_button.config(state=tk.NORMAL) # Habilitar botón
                      elif df.shape[1] >= 2:
                           print(f"Advertencia: Renombrando columnas de {file_name} a ['Time', 'Mass'] (formato simple).")
                           df.columns = ['Time', 'Mass'] + list(df.columns[2:])
                           self.mass_data = df
                           self.loaded_mass_path = None
                           label_widget.config(text=f"Masa: {file_name} (Simple)")
                           visualize_button.config(state=tk.NORMAL) # Habilitar botón
                      else:
                           raise ValueError(f"Archivo de masa no tiene columnas esperadas: {expected_cols} ni formato simple ['Time', 'Mass']")

        except FileNotFoundError:
            print(f"Advertencia: Archivo CSV predeterminado no encontrado: {file_path}")
            label_widget.config(text=f"{data_type.capitalize()}: No cargado (Falta archivo)")
            visualize_button.config(state=tk.DISABLED)
        except pd.errors.EmptyDataError:
            print(f"Advertencia: Archivo CSV predeterminado está vacío: {file_path}")
            label_widget.config(text=f"{data_type.capitalize()}: No cargado (Vacío)")
            visualize_button.config(state=tk.DISABLED)
        except Exception as e:
            print(f"Advertencia: Error al cargar o procesar CSV predeterminado '{os.path.basename(file_path)}': {e}")
            label_widget.config(text=f"{data_type.capitalize()}: Error carga")
            visualize_button.config(state=tk.DISABLED)
            # Resetear datos si falla la carga
            if data_type == "thrust": self.thrust_data = None; self.loaded_thrust_path = None
            elif data_type == "cd_vs_mach": self.cd_data = None; self.loaded_cd_path = None
            elif data_type == "mass_vs_time": self.mass_data = None; self.loaded_mass_path = None


    # --- Funciones Auxiliares de GUI ---
    def create_section(self, parent, text, row, column, columnspan=4): # Aumentar columnspan
        """Crea una etiqueta de sección."""
        ttk.Label(parent, text=text, font=('Lucida Sans Unicode', 11, 'bold'), foreground='#48AAAD') \
           .grid(row=row, column=column, columnspan=columnspan, sticky="w", padx=5, pady=(10, 2))

    def create_entry(self, parent, comp_key, param_name, label_text, default_value, row, col):
        """Crea una etiqueta y un campo de entrada, y lo guarda en self.component_widgets."""
        full_key = f"{comp_key}_{param_name}"
        ttk.Label(parent, text=label_text).grid(row=row, column=col, sticky="w", padx=5, pady=2)
        entry = ttk.Entry(parent, width=15)
        entry.grid(row=row, column=col + 1, padx=5, pady=2, sticky="ew")
        entry.insert(0, str(default_value))
        self.component_widgets[full_key] = entry # Guardar referencia al widget
        return entry

    def create_combobox(self, parent, comp_key, param_name, label_text, values, default_value, row, col):
        """Crea una etiqueta y un combobox, y lo guarda en self.component_widgets."""
        full_key = f"{comp_key}_{param_name}"
        ttk.Label(parent, text=label_text).grid(row=row, column=col, sticky="w", padx=5, pady=2)
        combobox = ttk.Combobox(parent, values=values, state="readonly", width=13)
        combobox.grid(row=row, column=col + 1, padx=5, pady=2, sticky="ew")
        if default_value in values:
            combobox.set(default_value)
        elif values:
            combobox.current(0)
        self.component_widgets[full_key] = combobox # Guardar referencia al widget
        return combobox

    def show_no_simulation_message(self, frame):
        for widget in frame.winfo_children(): widget.destroy()
        label = ttk.Label(frame, text="Realice una simulación para ver los resultados", font=('Lucida Sans Unicode', 14))
        label.pack(expand=True, padx=20, pady=20)

    # --- Pestañas de Definición del Cohete (Externos e Internos) ---
    def create_rocket_tabs(self):
        """Crea las pestañas para componentes externos e internos."""
        self.component_widgets = {} # Reiniciar diccionario de widgets

        # Crear frames contenedores principales para cada pestaña
        ext_frame_main = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(ext_frame_main, text="Componentes Externos")

        int_frame_main = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(int_frame_main, text="Componentes Internos")

        # --- Configurar Scroll para Pestaña Externa ---
        ext_canvas = tk.Canvas(ext_frame_main, bg=self.style.lookup('TFrame', 'background'), highlightthickness=0)
        ext_scrollbar = ttk.Scrollbar(ext_frame_main, orient="vertical", command=ext_canvas.yview)
        ext_scrollable_frame = ttk.Frame(ext_canvas)
        ext_scrollable_frame.bind("<Configure>", lambda e: ext_canvas.configure(scrollregion=ext_canvas.bbox("all")))
        ext_canvas_window = ext_canvas.create_window((0, 0), window=ext_scrollable_frame, anchor="nw")
        ext_canvas.configure(yscrollcommand=ext_scrollbar.set)
        ext_canvas.pack(side="left", fill="both", expand=True); ext_scrollbar.pack(side="right", fill="y")
        # Ajustar ancho del frame interior al canvas
        ext_frame_main.bind('<Configure>', lambda e: ext_canvas.itemconfig(ext_canvas_window, width=e.width))


        # --- Configurar Scroll para Pestaña Interna ---
        int_canvas = tk.Canvas(int_frame_main, bg=self.style.lookup('TFrame', 'background'), highlightthickness=0)
        int_scrollbar = ttk.Scrollbar(int_frame_main, orient="vertical", command=int_canvas.yview)
        int_scrollable_frame = ttk.Frame(int_canvas)
        int_scrollable_frame.bind("<Configure>", lambda e: int_canvas.configure(scrollregion=int_canvas.bbox("all")))
        int_canvas_window = int_canvas.create_window((0, 0), window=int_scrollable_frame, anchor="nw")
        int_canvas.configure(yscrollcommand=int_scrollbar.set)
        int_canvas.pack(side="left", fill="both", expand=True); int_scrollbar.pack(side="right", fill="y")
        # Ajustar ancho del frame interior al canvas
        int_frame_main.bind('<Configure>', lambda e: int_canvas.itemconfig(int_canvas_window, width=e.width))


        # --- Layout de Componentes (según clasificación externa/interna) ---
        external_layout = [
            ("Nariz", ["masa", "longitud", "geometria"]),
            ("Coples", ["masa", "longitud", "diametroexterior", "diametrointerior"]),
            ("Tubo_recup", ["masa", "longitud", "diametroexterior", "diametrointerior"]),
            ("Transfer", ["masa", "longitud", "diametroexterior", "diametrointerior"]),
            ("Tanquevacio", ["masa", "longitud", "diametroexterior", "diametrointerior"]),
            ("Valvulas", ["masa", "longitud", "diametroexterior", "diametrointerior"]),
            ("Cc", ["masa", "longitud", "diametroexterior", "diametrointerior"]),
            ("Boattail", ["masa", "longitud", "diamF_boat", "diamR_boat", "espesor"])
        ]
        internal_layout = [
            ("Aletas", ["masa", "numf", "semispan", "C_r", "C_t", "mid_sweep_deg"]),
            # Añadir aquí Avionica, CU, Drogue, Main si se definen parámetros editables
            # Ejemplo: ("Avionica", ["masa", "posicion_z_relativa"])
            # Ejemplo: ("CU", ["masa", "longitud"])
            # Ejemplo: ("Drogue", ["masa", "diametro", "Cd"])
            # Ejemplo: ("Main", ["masa", "diametro", "Cd"])
        ]

        # Función auxiliar para crear widgets de componentes en un frame
        def create_component_widgets(parent_frame, layout):
            current_row = 0
            # Configurar columnas para que se expandan uniformemente
            parent_frame.columnconfigure(0, weight=1)
            parent_frame.columnconfigure(1, weight=1)
            parent_frame.columnconfigure(2, weight=1)
            parent_frame.columnconfigure(3, weight=1)

            for comp_key_lower, params in layout:
                comp_key_title = comp_key_lower.replace("_", " ").capitalize()
                # Asegurar que la clave 'cc' se maneje correctamente
                defaults_key = comp_key_lower if comp_key_lower != "cc" else "cc"
                comp_defaults = self.xitle_defaults.get(defaults_key, {})
                comp_type = "Cilindro" # Tipo por defecto
                if comp_key_lower == "nariz": comp_type = "Cono"
                elif comp_key_lower == "aletas": comp_type = "Aletas"
                elif comp_key_lower == "boattail": comp_type = "Boattail"

                self.create_section(parent_frame, f"{comp_key_title} ({comp_type}):", current_row, 0, columnspan=4)
                current_row += 1

                col_idx = 0
                for param in params:
                    label_text = f"{param}:"
                    default_val = comp_defaults.get(param, "")
                    # Formatear valores numéricos
                    if isinstance(default_val, (int, float)):
                        if abs(default_val) < 0.01 and default_val != 0: default_val_str = f"{default_val:.3e}"
                        elif abs(default_val) > 1000: default_val_str = f"{default_val:.3e}"
                        elif param in ["masa", "semispan", "C_t", "C_r", "longitud", "diametroexterior", "diametrointerior", "diamF_boat", "diamR_boat", "espesor"]: default_val_str = f"{default_val:.3f}"
                        elif param == "mid_sweep_deg": default_val_str = f"{default_val:.1f}"
                        else: default_val_str = str(default_val)
                    else: default_val_str = str(default_val)

                    if param == "geometria":
                        self.create_combobox(parent_frame, comp_key_lower, param, label_text,
                                             ["conica", "ogiva", "parabolica", "eliptica"], default_val_str,
                                             current_row, col_idx * 2)
                    else:
                        self.create_entry(parent_frame, comp_key_lower, param, label_text,
                                          default_val_str, current_row, col_idx * 2)

                    col_idx += 1
                    if col_idx >= 2: col_idx = 0; current_row += 1
                if col_idx != 0: current_row += 1 # Asegura empezar en nueva fila
                current_row += 1 # Espacio extra

        # Crear widgets en los frames correspondientes
        create_component_widgets(ext_scrollable_frame, external_layout)
        create_component_widgets(int_scrollable_frame, internal_layout)

        # --- Botón Actualizar Cohete (Individual para cada pestaña) ---
        btn_update_ext = ttk.Button(ext_frame_main, text="Actualizar Cohete", command=self.update_rocket_from_gui, style='Update.TButton')
        btn_update_ext.pack(side="bottom", pady=10, padx=5)

        btn_update_int = ttk.Button(int_frame_main, text="Actualizar Cohete", command=self.update_rocket_from_gui, style='Update.TButton')
        btn_update_int.pack(side="bottom", pady=10, padx=5)


    # --- Populate Rocket Tabs (Actualizado para componentes individuales) ---
    def populate_rocket_tabs(self):
        """Rellena los campos en las pestañas de componentes con datos del objeto self.rocket."""
        if not self.rocket or not hasattr(self.rocket, 'componentes'): return

        print("Poblando pestañas de Cohete...")
        for comp_key, comp_obj in self.rocket.componentes.items():
            comp_key_lower = comp_key.lower().replace(" ", "_") # Clave para widgets
            # print(f"  Poblando componente: {comp_key} (clave widget: {comp_key_lower})")
            for param_name, widget in self.component_widgets.items():
                # Extraer la clave del componente y el nombre del parámetro del widget_key
                widget_comp_key, widget_param_name = param_name.split('_', 1)

                if widget_comp_key == comp_key_lower:
                    # Intentar obtener el valor del atributo del objeto componente
                    value = getattr(comp_obj, widget_param_name, None)
                    # Mapeo de nombres de atributos de clase a claves de widget (si son diferentes)
                    if value is None and widget_param_name == "mid_sweep_deg": value = np.degrees(getattr(comp_obj, "mid_sweep", 0.0))
                    elif value is None and widget_param_name == "diametroexterior": value = getattr(comp_obj, "diam_ext", None)
                    elif value is None and widget_param_name == "diametrointerior": value = getattr(comp_obj, "diam_int", None)
                    elif value is None and widget_param_name == "diamF_boat": value = getattr(comp_obj, "dF", None)
                    elif value is None and widget_param_name == "diamR_boat": value = getattr(comp_obj, "dR", None)
                    elif value is None and widget_param_name == "espesor": value = getattr(comp_obj, "e", None)
                    elif value is None and widget_param_name == "longitud": value = getattr(comp_obj, "long", None) # Para Cono/Boattail
                    elif value is None and widget_param_name == "geometria": value = getattr(comp_obj, "geom", None) # Para Cono

                    if value is not None:
                        # Formatear valor para mostrar
                        if isinstance(value, (int, float)):
                            if abs(value) < 0.01 and value != 0: value_str = f"{value:.3e}"
                            elif abs(value) > 1000: value_str = f"{value:.3e}"
                            elif widget_param_name in ["masa", "semispan", "C_t", "C_r", "longitud", "diametroexterior", "diametrointerior", "diamF_boat", "diamR_boat", "espesor"]: value_str = f"{value:.3f}"
                            elif widget_param_name == "mid_sweep_deg": value_str = f"{value:.1f}"
                            else: value_str = str(value)
                        else:
                            value_str = str(value)

                        # Actualizar widget
                        try:
                            if isinstance(widget, ttk.Entry):
                                widget.delete(0, tk.END); widget.insert(0, value_str)
                            elif isinstance(widget, ttk.Combobox):
                                if value_str in widget['values']: widget.set(value_str)
                                else: widget.set(widget['values'][0])
                        except tk.TclError as e: print(f"Error Tcl al actualizar widget {param_name}: {e}")
                    # else: print(f"Advertencia: Atributo '{widget_param_name}' no encontrado en componente '{comp_key}'.")

        print("Pestañas de Cohete pobladas.")

    
        # --- Nueva Pestaña: Visualización Cohete ---
    def create_visualization_tab(self):
        """Crea la pestaña para visualizar el cohete."""
        self.vis_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.vis_frame, text="Visualización Cohete")

        # Frame para el botón y el canvas
        vis_content_frame = ttk.Frame(self.vis_frame)
        vis_content_frame.pack(expand=True, fill="both", pady=(0, 5)) # Padding inferior para botones

        # Botón para generar la visualización
        btn_visualize = ttk.Button(vis_content_frame, text="Generar Visualización", command=self.visualize_rocket)
        btn_visualize.pack(pady=10)
        if not VISUALIZATION_AVAILABLE:
            btn_visualize.config(state=tk.DISABLED)
            ttk.Label(vis_content_frame, text="Función 'dibujar_cohete2' no encontrada.", foreground="orange").pack()

        # Canvas para la gráfica del cohete
        self.fig_vis, self.ax_vis = plt.subplots(figsize=(10, 4))
        self.canvas_vis = FigureCanvasTkAgg(self.fig_vis, master=vis_content_frame)
        self.canvas_widget_vis = self.canvas_vis.get_tk_widget()
        self.canvas_widget_vis.pack(fill=tk.BOTH, expand=True, pady=5)
        self.ax_vis.set_title("Visualización del Vehículo")
        self.ax_vis.set_xlabel("Longitud (m)")
        self.ax_vis.set_ylabel("Eje transversal (m)")
        self.ax_vis.set_aspect('equal', adjustable='box')
        self.ax_vis.grid(True, linestyle='--', alpha=0.7)
        self.fig_vis.tight_layout()
        self.canvas_vis.draw() # Dibuja el canvas vacío inicialmente

        # --- Botones Guardar/Cargar Definición ---
        vis_button_frame = ttk.Frame(self.vis_frame)
        vis_button_frame.pack(side="bottom", fill="x", pady=5)

        btn_save_rocket_vis = ttk.Button(vis_button_frame, text="Guardar Definición", command=lambda: self.save_tab_data("rocket"))
        btn_save_rocket_vis.pack(side=tk.LEFT, padx=5)
        btn_load_rocket_vis = ttk.Button(vis_button_frame, text="Cargar Definición", command=lambda: self.load_tab_data("rocket"))
        btn_load_rocket_vis.pack(side=tk.LEFT, padx=5)

    def visualize_rocket(self):
        """Genera la visualización del cohete basado en los componentes actuales."""
        if not VISUALIZATION_AVAILABLE:
            messagebox.showwarning("Visualización no disponible", "La función 'dibujar_cohete2' no se encontró.")
            return
        if self.rocket is None or not hasattr(self.rocket, 'componentes') or not self.rocket.componentes:
            messagebox.showwarning("Sin Cohete", "No hay un cohete definido o componentes para visualizar.")
            return

        print("Generando visualización del cohete...")
        self.ax_vis.clear() # Limpiar gráfica anterior

        try:
            # Extraer datos necesarios del objeto self.rocket
            # Usar getattr con defaults por si algún componente falta
            nariz = self.rocket.componentes.get("Nariz")
            aletas = self.rocket.componentes.get("Aletas")
            boattail = self.rocket.componentes.get("Boattail")

            # Calcular longitud total del fuselaje (suma de longitudes de cilindros)
            cilindros_keys = ["Coples", "Tubo recup", "Transfer", "Tanquevacio", "Valvulas", "Cc"]
            long_fuselaje_total = 0
            for key in cilindros_keys:
                comp = self.rocket.componentes.get(key)
                if comp:
                    long_fuselaje_total += getattr(comp, 'long', 0)

            long_nariz = getattr(nariz, 'long', 0)
            diam_ext = getattr(self.rocket, 'd_ext', 0.152) # Usar el diámetro de referencia
            root_aletas = getattr(aletas, 'C_r', 0)
            tip_aletas = getattr(aletas, 'C_t', 0)
            fin_height = getattr(aletas, 'span', getattr(aletas, 'semispan', 0) * 2) # span o 2*semispan
            long_boat = getattr(boattail, 'long', 0)
            rear_boat = getattr(boattail, 'dR', diam_ext) # Default al diámetro externo si no hay boattail

            # Calcular CG/CP total (ya deberían estar calculados en self.rocket)
            cg_total_z = self.rocket.CG[2] if self.rocket.CG is not None else 0
            cp_total_z = self.rocket.CP[2] if self.rocket.CP is not None else 0

            # Listas de CGs/CPs de componentes (todos los componentes)
            CG_list = []
            CP_list = []
            # Iterar sobre TODOS los componentes en el orden en que están en el cohete (asumido por __init__)
            component_order_keys = ["Nariz", "Coples", "Tubo recup", "Transfer", "Tanquevacio", "Valvulas", "Cc", "Aletas", "Boattail"]
            for key in component_order_keys:
                 comp = self.rocket.componentes.get(key)
                 if comp:
                      # La posición del CG/CP en la gráfica es relativa al inicio del cohete
                      pos_CG = getattr(comp, 'posicion', np.zeros(3))[2] + getattr(comp, 'CG', np.zeros(3))[2]
                      pos_CP = getattr(comp, 'posicion', np.zeros(3))[2] + getattr(comp, 'CP', np.zeros(3))[2]
                      CG_list.append(pos_CG)
                      CP_list.append(pos_CP)

            y_scatter = np.zeros(len(CG_list)) # Array Y para scatter

            # Llamar a la función de dibujo
            dibujar_cohete2(self.ax_vis, angle=0, x_cm=cg_total_z, y_cm=0,
                            body_l=long_fuselaje_total, body_w=diam_ext,
                            nose_l=long_nariz, fin_tip=tip_aletas, fin_root=root_aletas,
                            fin_h=fin_height, boattail_length=long_boat, boat_rear=rear_boat)

            # Dibujar puntos de CG/CP
            self.ax_vis.scatter(CG_list, y_scatter, color='darkorange', s=50, alpha=0.8, marker="P", label="CGs componentes")
            self.ax_vis.scatter(CP_list, y_scatter, color='yellowgreen', s=50, alpha=0.8, marker="X", label="CPs componentes")
            self.ax_vis.scatter(cg_total_z, 0, color='red', marker="P", s=150, label="CG total")
            self.ax_vis.scatter(cp_total_z, 0, color='dodgerblue', marker="X", s=150, label="CP total")

            # Estética del gráfico
            self.ax_vis.set_aspect("equal")
            self.ax_vis.set_title("Visualización del Vehículo", fontsize=12, weight='bold')
            self.ax_vis.set_xlabel("Longitud (m)")
            self.ax_vis.set_ylabel("Eje transversal (m)")
            self.ax_vis.set_ylim(-0.5, 0.5) # Limitar eje y para mejor visualización
            self.ax_vis.legend(loc="best", fontsize=8)
            self.ax_vis.grid(True, linestyle='--', alpha=0.7)
            self.fig_vis.tight_layout()
            self.canvas_vis.draw() # Redibujar el canvas

        except ImportError:
             messagebox.showerror("Error", "No se pudo importar 'dibujar_cohete2'. Verifica la ruta.")
        except AttributeError as e:
             messagebox.showerror("Error Atributo", f"Falta un atributo necesario en el cohete o sus componentes para la visualización: {e}")
             print(traceback.format_exc())
        except Exception as e:
            messagebox.showerror("Error Visualización", f"Ocurrió un error al generar la visualización:\n{e}")
            print(traceback.format_exc())

    # --- Update Rocket from GUI (Actualizado para componentes individuales) ---
    def update_rocket_from_gui(self):
        """Actualiza el objeto self.rocket con datos de la GUI, usando los __init__ correctos."""
        print("Actualizando cohete desde GUI...")
        componentes_actualizados = {}
        current_z = 0.0
        d_ext_ref = None # Para guardar el diámetro del primer cilindro

        try:
            def get_float(widget_key, name):
                try: return float(self.component_widgets[widget_key].get())
                except ValueError: raise ValueError(f"Valor inválido para '{name}': '{self.component_widgets[widget_key].get()}'")
                except KeyError: raise KeyError(f"Widget no encontrado: {widget_key}")
            def get_int(widget_key, name):
                try: return int(self.component_widgets[widget_key].get())
                except ValueError: raise ValueError(f"Valor inválido para '{name}': '{self.component_widgets[widget_key].get()}'")
                except KeyError: raise KeyError(f"Widget no encontrado: {widget_key}")
            def get_str(widget_key):
                 try: return self.component_widgets[widget_key].get()
                 except KeyError: raise KeyError(f"Widget no encontrado: {widget_key}")

            # --- Leer y crear componentes en orden ---
            # Nariz
            l_nariz = get_float("nariz_longitud", "Longitud Nariz")
            d_nariz = get_float("nariz_diametro", "Diámetro Nariz")
            m_nariz = get_float("nariz_masa", "Masa Nariz")
            g_nariz = get_str("nariz_geometria")
            nariz = Cono("Nariz", m_nariz, np.array([0.,0.,0.]), longitud=l_nariz, diametro=d_nariz, geometria=g_nariz)
            componentes_actualizados["Nariz"] = nariz
            current_z = nariz.bottom[2]

            # Componentes Cilíndricos (Externos e Internos según layout)
            cilindros_keys_lower = ["coples", "tubo_recup", "transfer", "tanquevacio", "valvulas", "cc"]
            for key in cilindros_keys_lower:
                comp_key_title = key.replace("_", " ").capitalize()
                l_comp = get_float(f"{key}_longitud", f"Longitud {comp_key_title}")
                m_comp = get_float(f"{key}_masa", f"Masa {comp_key_title}")
                d_ext_comp = get_float(f"{key}_diametroexterior", f"Diámetro Ext {comp_key_title}")
                d_int_comp = get_float(f"{key}_diametrointerior", f"Diámetro Int {comp_key_title}")
                if d_int_comp >= d_ext_comp or d_int_comp <= 0: raise ValueError(f"Diámetros inválidos para {comp_key_title}")

                comp = Cilindro(comp_key_title, m_comp, np.array([0., 0., current_z]),
                                longitud=l_comp, diametroexterior=d_ext_comp, diametrointerior=d_int_comp)
                comp.CG = np.array([0.0, 0.0, l_comp / 2.0]) # Workaround CG
                comp.CP = np.zeros(3); comp.CN = 0 # Workaround CP/CN
                componentes_actualizados[comp_key_title] = comp
                current_z = comp.bottom[2]
                if d_ext_ref is None: d_ext_ref = d_ext_comp # Guardar primer diámetro externo

            # Aletas (Internas según la nueva definición)
            n_aletas = get_int("aletas_numf", "Número Aletas")
            s_aletas = get_float("aletas_semispan", "Envergadura Aletas")
            cr_aletas = get_float("aletas_C_r", "Cuerda Raíz Aletas")
            ct_aletas = get_float("aletas_C_t", "Cuerda Punta Aletas")
            sweep_aletas_deg = get_float("aletas_mid_sweep_deg", "Barrido Medio Aletas")
            m_aletas = get_float("aletas_masa", "Masa Aletas")
            # Calcular posición de aletas (relativa al final del último cilindro)
            pos_aletas = np.array([0., 0., current_z - cr_aletas])
            aletas = Aletas("Aletas", m_aletas, pos_aletas,
                            diametro=d_ext_ref, # Usar diámetro de referencia
                            numf=n_aletas, semispan=s_aletas,
                            C_r=cr_aletas, C_t=ct_aletas,
                            X_R=0.0, mid_sweep=np.deg2rad(sweep_aletas_deg))
            componentes_actualizados["Aletas"] = aletas

            # Boattail (Externo)
            l_boat = get_float("boattail_longitud", "Longitud Boattail")
            df_boat = get_float("boattail_diamF_boat", "Diámetro Frontal Boattail")
            dr_boat = get_float("boattail_diamR_boat", "Diámetro Trasero Boattail")
            m_boat = get_float("boattail_masa", "Masa Boattail")
            e_boat = get_float("boattail_espesor", "Espesor Boattail")
            pos_boat = np.array([0., 0., current_z]) # Al final del último cilindro
            boattail = Boattail("Boattail", m_boat, pos_boat,
                                longitud=l_boat, diamF_boat=df_boat, diamR_boat=dr_boat, espesor=e_boat)
            componentes_actualizados["Boattail"] = boattail

            # --- Actualizar el Objeto Cohete ---
            if self.rocket is None:
                print("Creando nuevo objeto Cohete desde GUI...")
                # Crear cohete con todos los componentes y las rutas CSV actuales
                external_keys_for_cohete = ["Nariz", "Coples", "Tubo recup", "Transfer", "Tanquevacio", "Valvulas", "Cc", "Boattail"]
                external_components_dict = {k: v for k, v in componentes_actualizados.items() if k in external_keys_for_cohete}
                self.rocket = Cohete("Cohete GUI", "hibrido",
                                     componentes_actualizados, external_components_dict,
                                     self.loaded_cd_path, self.loaded_thrust_path, self.loaded_mass_path, riel)
            else:
                print("Actualizando objeto Cohete existente desde GUI...")
                self.rocket.componentes = componentes_actualizados
                # Definir componentes externos explícitamente según la nueva clasificación
                external_keys_for_cohete = ["Nariz", "Coples", "Tubo recup", "Transfer", "Tanquevacio", "Valvulas", "Cc", "Boattail"]
                self.rocket.componentes_externos = {k: v for k, v in componentes_actualizados.items() if k in external_keys_for_cohete}

                # Recargar tablas CSV si las rutas existen
                try:
                    if self.loaded_cd_path and hasattr(self.rocket, 'cargar_tabla_Cd'):
                         self.rocket.cargar_tabla_Cd(self.loaded_cd_path)
                    if self.loaded_thrust_path and self.loaded_mass_path and hasattr(self.rocket, 'cargar_tablas_motor'):
                         self.rocket.cargar_tablas_motor(self.loaded_thrust_path, self.loaded_mass_path)
                except Exception as e:
                     print(f"Advertencia: Error al recargar tablas CSV en Cohete: {e}")


            # Actualiza propiedades clave del cohete
            self.rocket.d_ext = d_ext_ref if d_ext_ref is not None else self.diam_ext_xitle # Usar diámetro de referencia
            self.rocket.calcular_propiedades() # Recalcular CG, CP, Masa, etc.

            messagebox.showinfo("Éxito", "Cohete actualizado desde la GUI.")
            print(f"Cohete actualizado. CG: {self.rocket.CG[2]:.3f} m, CP: {self.rocket.CP[2]:.3f} m (estático)")

        except (ValueError, AssertionError, KeyError) as e: messagebox.showerror("Error Validación/Clave", str(e))
        except NameError as e: messagebox.showerror("Error Clase", f"Clase de componente no encontrada: {e}")
        except TypeError as e: messagebox.showerror("Error Argumentos", f"Error al crear componente, revisa argumentos: {e}\n{traceback.format_exc()}")
        except Exception as e: messagebox.showerror("Error", f"Error al actualizar cohete: {e}\n{traceback.format_exc()}")


    # --- Tab: Import CSV (Añadidos botones de visualización) ---
    def create_csv_import_tab(self):
        """Crea la pestaña para importar datos desde archivos CSV."""
        self.csv_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.csv_frame, text="Importar Curvas")

        # Frame para botones
        button_frame = ttk.Frame(self.csv_frame); button_frame.pack(pady=5, fill=tk.X)
        # Frame para gráficas
        self.plot_frame = ttk.Frame(self.csv_frame); self.plot_frame.pack(pady=5, fill=tk.BOTH, expand=True)

        # --- Fila 1: Botones de Importación ---
        self.thrust_button = ttk.Button(button_frame, text="Importar Empuje (T vs t)", command=lambda: self.import_csv_data("thrust"));
        self.thrust_button.grid(row=0, column=0, padx=5, pady=2, sticky='ew')
        self.cd_button = ttk.Button(button_frame, text="Importar Arrastre (Cd vs Mach)", command=lambda: self.import_csv_data("cd_vs_mach"));
        self.cd_button.grid(row=0, column=1, padx=5, pady=2, sticky='ew')
        self.mass_button = ttk.Button(button_frame, text="Importar Masa (M vs t)", command=lambda: self.import_csv_data("mass_vs_time"));
        self.mass_button.grid(row=0, column=2, padx=5, pady=2, sticky='ew')

        # --- Fila 2: Etiquetas de Archivos Cargados ---
        self.thrust_file_label = ttk.Label(button_frame, text="Empuje: No cargado", width=30, anchor='w');
        self.thrust_file_label.grid(row=1, column=0, padx=5, pady=1, sticky='ew')
        self.cd_file_label = ttk.Label(button_frame, text="Arrastre: No cargado", width=30, anchor='w');
        self.cd_file_label.grid(row=1, column=1, padx=5, pady=1, sticky='ew')
        self.mass_file_label = ttk.Label(button_frame, text="Masa: No cargado", width=30, anchor='w');
        self.mass_file_label.grid(row=1, column=2, padx=5, pady=1, sticky='ew')

        # --- Fila 3: Botones de Visualización ---
        self.btn_visualize_thrust = ttk.Button(button_frame, text="Visualizar Empuje", command=lambda: self.plot_csv_data("thrust"), state=tk.DISABLED, style='Vis.TButton')
        self.btn_visualize_thrust.grid(row=2, column=0, padx=5, pady=2, sticky='ew')
        self.btn_visualize_cd = ttk.Button(button_frame, text="Visualizar Arrastre", command=lambda: self.plot_csv_data("cd_vs_mach"), state=tk.DISABLED, style='Vis.TButton')
        self.btn_visualize_cd.grid(row=2, column=1, padx=5, pady=2, sticky='ew')
        self.btn_visualize_mass = ttk.Button(button_frame, text="Visualizar Masa", command=lambda: self.plot_csv_data("mass_vs_time"), state=tk.DISABLED, style='Vis.TButton')
        self.btn_visualize_mass.grid(row=2, column=2, padx=5, pady=2, sticky='ew')

        # Ajustar configuración de columnas para que se expandan
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        button_frame.columnconfigure(2, weight=1)


        # Canvas para gráficas (se crea uno y se reutiliza)
        self.fig_csv, self.ax_csv = plt.subplots(figsize=(8, 4)); self.canvas_csv = FigureCanvasTkAgg(self.fig_csv, master=self.plot_frame)
        self.canvas_widget_csv = self.canvas_csv.get_tk_widget(); self.canvas_widget_csv.pack(fill=tk.BOTH, expand=True)
        self.ax_csv.set_title("Visualización de Datos CSV"); self.ax_csv.grid(True); self.fig_csv.tight_layout()

    # --- Importar CSV (Ajustado para habilitar botones de visualización) ---
    def import_csv_data(self, data_type):
        """Importa datos desde un archivo CSV seleccionado por el usuario."""
        file_path = filedialog.askopenfilename(title=f"Seleccionar CSV para {data_type}", filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if not file_path: return # User cancelled
        try:
            df = pd.read_csv(file_path)
            file_name = os.path.basename(file_path)
            print(f"Importando manualmente: {file_name} para {data_type}")

            visualize_button = None # Botón a habilitar

            if data_type == "thrust":
                # Verificar/Renombrar columnas
                if 'Time' in df.columns and 'Thrust' in df.columns: pass
                elif df.shape[1] >= 2:
                    print(f"Advertencia: Renombrando columnas de {file_name} a ['Time', 'Thrust']")
                    df.columns = ['Time', 'Thrust'] + list(df.columns[2:])
                else: raise ValueError("Archivo de empuje no tiene 2 columnas.")
                self.thrust_data = df
                self.loaded_thrust_path = file_path # Actualiza la ruta cargada
                label_widget = self.thrust_file_label
                visualize_button = self.btn_visualize_thrust
                if self.rocket:
                     # Actualizar ruta en cohete y recargar tablas
                     if hasattr(self.rocket, 'cargar_tablas_motor') and self.loaded_mass_path: # Necesita también la de masa
                         try:
                             self.rocket.cargar_tablas_motor(self.loaded_thrust_path, self.loaded_mass_path)
                             print("Tabla de empuje/masa recargada en Cohete.")
                         except Exception as e:
                             print(f"Advertencia: Error al recargar tabla de empuje/masa en Cohete: {e}")

            elif data_type == "cd_vs_mach":
                 # Verificar/Renombrar columnas
                 if 'Mach' in df.columns and 'Cd' in df.columns: pass
                 elif df.shape[1] >= 2:
                      print(f"Advertencia: Renombrando columnas de {file_name} a ['Mach', 'Cd']")
                      df.columns = ['Mach', 'Cd'] + list(df.columns[2:])
                 else: raise ValueError("Archivo Cd vs Mach no tiene 2 columnas.")
                 self.cd_data = df
                 self.loaded_cd_path = file_path # Actualiza la ruta cargada
                 label_widget = self.cd_file_label
                 visualize_button = self.btn_visualize_cd
                 if self.rocket:
                      if hasattr(self.rocket, 'cargar_tabla_Cd'):
                          try:
                              self.rocket.cargar_tabla_Cd(self.loaded_cd_path) # Recarga tabla
                              print("Tabla Cd recargada en Cohete.")
                          except Exception as e:
                              print(f"Advertencia: Error al recargar tabla Cd en Cohete: {e}")

            elif data_type == "mass_vs_time":
                 # Verificar columnas necesarias para cohete.py
                 expected_cols_detailed = ['Time (s)', 'Oxidizer Mass (kg)', 'Fuel Mass (kg)']
                 is_detailed_format = all(col in df.columns for col in expected_cols_detailed)
                 label_widget = self.mass_file_label
                 visualize_button = self.btn_visualize_mass

                 if is_detailed_format:
                      print(f"Detectado formato detallado de masa en: {file_name}")
                      self.mass_data = df # Almacenar DataFrame completo
                      self.loaded_mass_path = file_path
                      if self.rocket:
                           if hasattr(self.rocket, 'cargar_tablas_motor') and self.loaded_thrust_path: # Necesita también la de empuje
                                try:
                                    self.rocket.cargar_tablas_motor(self.loaded_thrust_path, self.loaded_mass_path) # Recarga tablas
                                    print("Tabla de empuje/masa recargada en Cohete.")
                                except Exception as e:
                                    print(f"Advertencia: Error al recargar tabla de empuje/masa en Cohete: {e}")
                      label_widget.config(text=f"Masa: {file_name}")
                      visualize_button.config(state=tk.NORMAL) # Habilitar botón
                      messagebox.showinfo("Éxito", f"Masa detallada '{file_name}' importada.")
                 else:
                      # Intentar formato simple 'Time', 'Mass' para graficar
                      if 'Time' in df.columns and 'Mass' in df.columns:
                           print(f"Advertencia: {file_name} tiene formato simple ['Time', 'Mass']. Se usará para graficar, pero Cohete espera formato detallado.")
                           self.mass_data = df # Almacenar para graficar
                           self.loaded_mass_path = None # Indicar que no es el formato esperado por Cohete
                           if self.rocket: self.rocket.tabla_masa_fpath = None # Limpiar ruta en cohete
                           label_widget.config(text=f"Masa: {file_name} (Simple)")
                           visualize_button.config(state=tk.NORMAL) # Habilitar botón
                           messagebox.showinfo("Éxito", f"Masa simple '{file_name}' importada.")
                      elif df.shape[1] >= 2:
                           print(f"Advertencia: Renombrando columnas de {file_name} a ['Time', 'Mass'] (formato simple).")
                           df.columns = ['Time', 'Mass'] + list(df.columns[2:])
                           self.mass_data = df
                           self.loaded_mass_path = None
                           if self.rocket: self.rocket.tabla_masa_fpath = None
                           label_widget.config(text=f"Masa: {file_name} (Simple)")
                           visualize_button.config(state=tk.NORMAL) # Habilitar botón
                           messagebox.showinfo("Éxito", f"Masa simple '{file_name}' importada.")
                      else:
                           raise ValueError(f"Archivo de masa no tiene columnas esperadas: {expected_cols_detailed} ni formato simple ['Time', 'Mass']")

            # Actualizar etiqueta y botón si no es el caso de masa
            if data_type != "mass_vs_time":
                label_widget.config(text=f"{data_type.split('_')[0].capitalize()}: {file_name}")
                visualize_button.config(state=tk.NORMAL)

            self.plot_csv_data(data_type) # Graficar después de cargar/procesar
            if self.rocket: self.rocket.calcular_propiedades() # Recalcular siempre

        except FileNotFoundError: messagebox.showerror("Error", f"Archivo no encontrado: {file_path}")
        except pd.errors.EmptyDataError: messagebox.showerror("Error", f"CSV vacío: {file_path}")
        except ValueError as e: messagebox.showerror("Error Columnas", f"Error procesando {file_name}: {e}")
        except Exception as e: messagebox.showerror("Error", f"Error al importar CSV '{os.path.basename(file_path)}':\n{e}\n{traceback.format_exc()}")

    # --- Graficar CSV (Ajustado para graficar masa total) ---
    def plot_csv_data(self, data_type):
        """Grafica los datos CSV importados en el canvas."""
        self.ax_csv.clear(); x_label, y_label, title = "", "", ""; data_to_plot_x, data_to_plot_y = None, None

        if data_type == "thrust" and self.thrust_data is not None:
            data_to_plot_x = self.thrust_data.iloc[:, 0]
            data_to_plot_y = self.thrust_data.iloc[:, 1]
            x_label, y_label, title = 'Tiempo (s)', 'Empuje (N)', 'Curva de Empuje'
        elif data_type == "cd_vs_mach" and self.cd_data is not None:
            data_to_plot_x = self.cd_data.iloc[:, 0]
            data_to_plot_y = self.cd_data.iloc[:, 1]
            x_label, y_label, title = 'Mach', 'Cd', 'Cd vs Mach'
        elif data_type == "mass_vs_time" and self.mass_data is not None:
            # Intentar graficar masa total si están las columnas detalladas
            expected_cols_detailed = ['Time (s)', 'Oxidizer Mass (kg)', 'Fuel Mass (kg)']
            if all(col in self.mass_data.columns for col in expected_cols_detailed):
                data_to_plot_x = self.mass_data['Time (s)']
                # Sumar masas de oxidante y combustible para graficar masa de propelente
                data_to_plot_y = self.mass_data['Oxidizer Mass (kg)'] + self.mass_data['Fuel Mass (kg)']
                x_label, y_label, title = 'Tiempo (s)', 'Masa Propelente (kg)', 'Masa de Propelente vs Tiempo'
            elif 'Time' in self.mass_data.columns and 'Mass' in self.mass_data.columns: # Formato simple
                data_to_plot_x = self.mass_data['Time']
                data_to_plot_y = self.mass_data['Mass']
                x_label, y_label, title = 'Tiempo (s)', 'Masa (kg)', 'Masa vs Tiempo (Simple)'
        elif data_type == "none": # Para mostrar gráfica vacía inicial
             pass
        else: # Si se llama con tipo inválido o datos son None
             self.ax_csv.text(0.5, 0.5, f"Importe datos para visualizar", ha='center', va='center', transform=self.ax_csv.transAxes)

        if data_to_plot_x is not None and data_to_plot_y is not None:
            try:
                self.ax_csv.plot(data_to_plot_x, data_to_plot_y, marker='.', linestyle='-')
                self.ax_csv.set_xlabel(x_label); self.ax_csv.set_ylabel(y_label); self.ax_csv.set_title(title)
                self.ax_csv.grid(True);
            except Exception as e: messagebox.showerror("Error Graficación", f"No se pudo graficar {data_type}: {e}")
        else:
             self.ax_csv.set_title("Visualización de Datos CSV"); self.ax_csv.grid(False);

        self.fig_csv.tight_layout(); self.canvas_csv.draw()


    # --- Tab: Simulation Parameters (Botón Simular con estilo verde) ---
    def create_input_tab(self):
        """Crea la pestaña para configurar los parámetros de lanzamiento y simulación."""
        self.input_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.input_frame, text="Parámetros de Simulación")

        col1_frame = ttk.Frame(self.input_frame); col1_frame.grid(row=0, column=0, padx=10, pady=5, sticky="nw")
        col2_frame = ttk.Frame(self.input_frame); col2_frame.grid(row=0, column=1, padx=10, pady=5, sticky="nw")
        col3_frame = ttk.Frame(self.input_frame); col3_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        # Launch Site (Col 1)
        self.create_section(col1_frame, "Sitio de Lanzamiento:", 0, 0)
        # CORRECCIÓN: Pasar clave única y argumentos row/col explícitos
        self.latitud = self.create_entry(parent=col1_frame, comp_key="input", param_name="latitud", label_text="Latitud (°):", default_value=getattr(riel, 'latitud', latitud_cord), row=1, col=0)
        self.longitud = self.create_entry(parent=col1_frame, comp_key="input", param_name="longitud", label_text="Longitud (°):", default_value=getattr(riel, 'longitud', longitud_cord), row=2, col=0)
        self.altitud = self.create_entry(parent=col1_frame, comp_key="input", param_name="altitud", label_text="Altitud (m):", default_value=getattr(riel, 'altitud', altitud_cord), row=3, col=0)
        self.fecha = self.create_entry(parent=col1_frame, comp_key="input", param_name="fecha", label_text="Fecha (YYYY-MM-DD):", default_value=fecha.strftime('%Y-%m-%d') if isinstance(fecha, datetime) else fecha, row=4, col=0)

        # Launch Rail (Col 1)
        self.create_section(col1_frame, "Riel de Lanzamiento:", 5, 0)
        self.longitud_riel = self.create_entry(parent=col1_frame, comp_key="input", param_name="longitud_riel", label_text="Longitud (m):", default_value=getattr(riel, 'longitud', 5.0), row=6, col=0)
        self.angulo_riel = self.create_entry(parent=col1_frame, comp_key="input", param_name="angulo_riel", label_text="Ángulo Elevación (°):", default_value=np.rad2deg(getattr(riel, 'angulo', np.deg2rad(85))), row=7, col=0)

        # Wind (Col 2)
        self.create_section(col2_frame, "Viento (Modelo Simple):", 0, 0)
        self.vel_base_viento = self.create_entry(parent=col2_frame, comp_key="input", param_name="vel_base_viento", label_text="Velocidad Base (m/s):", default_value=getattr(viento_actual, 'vel_base', 0), row=1, col=0)
        self.vel_mean_viento = self.create_entry(parent=col2_frame, comp_key="input", param_name="vel_mean_viento", label_text="Velocidad Media (m/s):", default_value=getattr(viento_actual, 'vel_mean', 5), row=2, col=0)
        self.vel_var_viento = self.create_entry(parent=col2_frame, comp_key="input", param_name="vel_var_viento", label_text="Variación Velocidad:", default_value=getattr(viento_actual, 'vel_var', 2), row=3, col=0)
        self.var_ang_viento = self.create_entry(parent=col2_frame, comp_key="input", param_name="var_ang_viento", label_text="Variación Ángulo (°):", default_value=getattr(viento_actual, 'var_ang', 10), row=4, col=0)

        # Simulation (Col 2)
        self.create_section(col2_frame, "Simulación:", 5, 0)
        self.t_max = self.create_entry(parent=col2_frame, comp_key="input", param_name="t_max", label_text="Tiempo Máximo (s):", default_value=800, row=6, col=0)
        self.dt = self.create_entry(parent=col2_frame, comp_key="input", param_name="dt", label_text="Paso de Tiempo (s):", default_value=0.01, row=7, col=0)

        # Integrator Selection (Col 2)
        integrator_options = []
        default_integrator = ""
        if CUSTOM_INTEGRATORS_AVAILABLE: integrator_options.extend(['Euler', 'RungeKutta4']); default_integrator = 'RungeKutta4'
        if SCIPY_AVAILABLE: scipy_methods = ['RK45', 'RK23', 'DOP853', 'Radau', 'BDF', 'LSODA']; integrator_options.extend(scipy_methods);
        if not default_integrator and SCIPY_AVAILABLE: default_integrator = 'RK45'
        if not integrator_options: integrator_options = ["N/A"]; default_integrator = "N/A"
        # CORRECCIÓN: Pasar clave única y argumentos row/col explícitos
        self.integrator_method_combo = self.create_combobox(parent=col2_frame, comp_key="input", param_name="integrator_method", label_text="Método Integración:", values=integrator_options, default_value=default_integrator, row=8, col=0)
        self.integrator_method_combo.configure(textvariable=self.selected_integrator) # Asociar variable
        if not SCIPY_AVAILABLE and not CUSTOM_INTEGRATORS_AVAILABLE: self.integrator_method_combo.config(state=tk.DISABLED)

        # Buttons and Progress (Bottom Frame)
        # CORRECCIÓN: Aplicar estilo 'Sim.TButton' al botón de simular
        self.btn_simular = ttk.Button(col3_frame, text="Iniciar Simulación", command=self.run_simulation, style='Sim.TButton')
        self.btn_simular.pack(side=tk.LEFT, padx=5, pady=10)
        if not SCIPY_AVAILABLE and not CUSTOM_INTEGRATORS_AVAILABLE: self.btn_simular.config(state=tk.DISABLED)

        self.btn_save_input = ttk.Button(col3_frame, text="Guardar Parámetros", command=lambda: self.save_tab_data("input")); self.btn_save_input.pack(side=tk.LEFT, padx=5, pady=10)
        self.btn_load_input = ttk.Button(col3_frame, text="Cargar Parámetros", command=lambda: self.load_tab_data("input")); self.btn_load_input.pack(side=tk.LEFT, padx=5, pady=10)
        self.progress = ttk.Progressbar(col3_frame, orient="horizontal", length=300, mode="determinate", style='Horizontal.TProgressbar'); self.progress.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.X, expand=True)
        self.progress_label = ttk.Label(col3_frame, text="Listo para simular"); self.progress_label.pack(side=tk.LEFT, padx=5, pady=10)

    # --- Update Simulation Parameters (Sin cambios) ---
    def update_simulation_parameters(self):
        try:
            def get_float(entry, name):
                try: return float(entry.get())
                except ValueError: raise ValueError(f"Inválido '{name}': '{entry.get()}'")
            riel.latitud = get_float(self.latitud, "Latitud"); riel.longitud = get_float(self.longitud, "Longitud"); riel.altitud = get_float(self.altitud, "Altitud")
            riel.longitud = get_float(self.longitud_riel, "Longitud Riel"); riel.angulo = np.deg2rad(get_float(self.angulo_riel, "Ángulo Riel"))
            global fecha; fecha_str = self.fecha.get()
            try: fecha = datetime.strptime(fecha_str, '%Y-%m-%d')
            except ValueError: raise ValueError("Fecha inválida (YYYY-MM-DD)")
            viento_actual.vel_base = get_float(self.vel_base_viento, "Viento Base"); viento_actual.vel_mean = get_float(self.vel_mean_viento, "Viento Medio")
            viento_actual.vel_var = get_float(self.vel_var_viento, "Viento Var Vel"); viento_actual.var_ang = get_float(self.var_ang_viento, "Viento Var Ang")
            t_max_sim = get_float(self.t_max, "Tiempo Máximo"); dt_sim = get_float(self.dt, "Paso Tiempo"); integrator_method = self.selected_integrator.get()
            if integrator_method == "N/A": raise ValueError("Método de integración no disponible/seleccionado.")
            if hasattr(viento_actual, 'actualizar_viento3D'): viento_actual.actualizar_viento3D(); print(f"Viento actualizado: {viento_actual.vector}")
            else: print("Advertencia: Viento no tiene 'actualizar_viento3D'.")
            return t_max_sim, dt_sim, integrator_method
        except ValueError as e: messagebox.showerror("Error Validación Parámetros", str(e)); return None, None, None
        except Exception as e: messagebox.showerror("Error", f"Error al actualizar parámetros: {e}\n{traceback.format_exc()}"); return None, None, None

    # --- Results Tabs Creation (Sin cambios) ---
    def create_results_tab(self, tab_name, title): frame = ttk.Frame(self.notebook, padding="10"); self.notebook.add(frame, text=title); self.show_no_simulation_message(frame); return frame
    def create_trajectory_tab(self): self.trajectory_frame = self.create_results_tab("trajectory", "Trayectoria 3D")
    def create_position_tab(self): self.position_frame = self.create_results_tab("position", "Posición/Velocidad")
    def create_forces_tab(self): self.forces_frame = self.create_results_tab("forces", "Fuerzas")
    def create_angles_tab(self): self.angles_frame = self.create_results_tab("angles", "Ángulos")
    def create_stability_tab(self): self.stability_frame = self.create_results_tab("stability", "Estabilidad")
    def create_wind_tab(self): self.wind_frame = self.create_results_tab("wind", "Viento Relativo")
    def create_summary_tab(self): self.summary_frame = self.create_results_tab("summary", "Resumen"); self.summary_text_widget = tk.Text(self.summary_frame, wrap="word", height=20, width=80, font=('Courier New', 10), relief=tk.FLAT, bg=self.style.lookup('TFrame', 'background'), fg='white', state=tk.DISABLED)

    # --- Simulation Logic (Corregido 'accangs' y verificación CSV) ---
    def run_simulation(self):
        """Runs the flight simulation using the selected integration method."""
        self.simulation_done = False
        if self.rocket is None: messagebox.showerror("Error", "Cohete no definido."); return

        # --- Verificar que las rutas CSV necesarias estén cargadas en la GUI ---
        missing_files = []
        if not self.loaded_cd_path: missing_files.append("Arrastre (Cd vs Mach)")
        if not self.loaded_thrust_path: missing_files.append("Empuje (T vs t)")
        if not self.loaded_mass_path: missing_files.append("Masa (M vs t)")

        if missing_files:
             messagebox.showerror("Error", f"Faltan datos CSV necesarios: {', '.join(missing_files)}. Impórtelos manualmente o asegúrese de que los archivos predeterminados existen.")
             return

        # --- Verificar que las tablas de datos estén cargadas en el objeto Cohete ---
        missing_tables = []
        if not hasattr(self.rocket, 'CdTable') or self.rocket.CdTable is None: missing_tables.append("CdTable")
        if not hasattr(self.rocket, 'motorThrustTable') or self.rocket.motorThrustTable is None: missing_tables.append("motorThrustTable")
        if not hasattr(self.rocket, 'motorMassTable') or self.rocket.motorMassTable is None: missing_tables.append("motorMassTable")

        if missing_tables:
            messagebox.showerror("Error Interno", f"Las tablas de datos CSV ({', '.join(missing_tables)}) no están cargadas en el objeto Cohete. Intente recargar los archivos CSV o reiniciar.")
            return
        # --- Fin verificación CSV ---


        t_max_sim, dt_sim, integrator_method = self.update_simulation_parameters()
        if t_max_sim is None: return
        self.progress['value'] = 0; self.progress['mode'] = 'indeterminate'; self.progress.start(); self.progress_label.config(text=f"Simulando ({integrator_method})..."); self.master.update_idletasks()
        try:
            vuelo_obj = Vuelo(self.rocket, atmosfera_actual, viento_actual)
            initial_state = np.array([0, 0, riel.altitud, 0, 0, 0, riel.angulo, 0]); t_span = (0, t_max_sim)
            # CORRECCIÓN: Usar self.rocket.masa en lugar de self.rocket.masa_total
            print(f"Iniciando simulación: t_max={t_max_sim}, dt={dt_sim}, método={integrator_method}"); print(f"Cohete: {self.rocket.nombre}, Masa inicial: {self.rocket.masa:.2f} kg"); print(f"Condiciones iniciales: {initial_state}"); print(f"Viento Vector: {viento_actual.vector}")
            inicio_tiempo = time.time(); tiempos_out, states_out = None, None
            # CORRECCIÓN: Verificar y usar 'fun_derivs'
            if not hasattr(vuelo_obj, 'fun_derivs'):
                 raise AttributeError("Clase 'Vuelo' necesita método 'fun_derivs(t, state)'.")
            def dynamics(t, y): return vuelo_obj.fun_derivs(t, y) # Usar fun_derivs

            if integrator_method in ['RK45', 'RK23', 'DOP853', 'Radau', 'BDF', 'LSODA']:
                if not SCIPY_AVAILABLE: raise RuntimeError("SciPy no disponible."); print(f"Usando solve_ivp: {integrator_method}")
                sol = solve_ivp(dynamics, t_span, initial_state, method=integrator_method, dense_output=True, max_step=dt_sim*10)
                if not sol.success: raise RuntimeError(f"solve_ivp falló ({integrator_method}): {sol.message}")
                tiempos_out = np.arange(t_span[0], t_span[1] + dt_sim, dt_sim); states_out = sol.sol(tiempos_out).T; print(f"solve_ivp completado. {len(tiempos_out)} puntos.")
            elif integrator_method in ['Euler', 'RungeKutta4']:
                if not CUSTOM_INTEGRATORS_AVAILABLE: raise RuntimeError(f"Integrador '{integrator_method}' no disponible."); print(f"Usando integrador: {integrator_method}")
                n_steps = int(t_max_sim / dt_sim); tiempos_out = np.linspace(t_span[0], t_span[1], n_steps + 1); states_out = np.zeros((n_steps + 1, len(initial_state))); states_out[0] = initial_state
                current_state, current_t = initial_state, tiempos_out[0]
                integrator = Euler(dynamics, current_t, current_state, dt_sim) if integrator_method == 'Euler' else RungeKutta4(dynamics, current_t, current_state, dt_sim)
                for i in range(n_steps):
                    if not hasattr(integrator, 'step'): raise AttributeError(f"Clase {integrator_method} necesita método 'step()'.")
                    current_state = integrator.step(); current_t = tiempos_out[i+1]; states_out[i+1] = current_state
                    if hasattr(integrator, 't'): integrator.t = current_t;
                    if hasattr(integrator, 'y'): integrator.y = current_state;
                print(f"Integración personalizada completada. {len(tiempos_out)} puntos.")
            else: raise ValueError(f"Método integración desconocido: {integrator_method}")
            fin_tiempo = time.time(); print(f"Integración numérica completada en {fin_tiempo - inicio_tiempo:.2f} s.")
            print("Iniciando post-procesamiento..."); num_puntos = len(tiempos_out)
            CPs, CGs, masavuelo, viento_mags, viento_dirs = (np.zeros(num_puntos) for _ in range(5)); viento_vecs, Tvecs, Dvecs, Nvecs = (np.zeros((num_puntos, 3)) for _ in range(4)); accels_lin, accels_ang, Gammas, Alphas, torcas, Cds, Machs = (np.zeros(num_puntos) for _ in range(7))

            # --- CORRECCIÓN: Usar los nombres de métodos correctos de vuelo.py ---
            required_methods_vuelo = ['calc_arrastre_normal', 'calc_empuje', 'calc_alpha', 'calc_aero', 'accangular'] # Métodos de Vuelo
            required_methods_cohete = ['actualizar_masa', 'calc_CG', 'calc_CP'] # Métodos/atributos de Cohete (accedidos vía vuelo_obj.vehiculo)

            for method_name in required_methods_vuelo:
                 if not hasattr(vuelo_obj, method_name): print(f"ADVERTENCIA: Vuelo no tiene método '{method_name}'.")
            for method_name in required_methods_cohete:
                 if not hasattr(vuelo_obj.vehiculo, method_name): print(f"ADVERTENCIA: Cohete no tiene método/atributo '{method_name}'.")

            for i in range(num_puntos):
                t, state = tiempos_out[i], states_out[i]
                pos = state[0:3]
                vel = state[3:6]
                theta = state[6]
                omega = state[7] # omega = theta_dot

                try:
                    # Actualizar masa y CG del cohete (dependen del tiempo)
                    vuelo_obj.vehiculo.actualizar_masa(t) # Llama al método de Cohete
                    masavuelo[i] = vuelo_obj.vehiculo.masa
                    # CG y CP se recalculan dentro de actualizar_masa si es necesario
                    CGs[i] = vuelo_obj.vehiculo.CG[2] # Accede al atributo Z del CG
                    CPs[i] = vuelo_obj.vehiculo.CP[2] # Accede al atributo Z del CP

                    # Calcular viento relativo
                    v_viento = vuelo_obj.viento.vector # Obtener vector de viento actual
                    v_rel = vel - v_viento

                    # Calcular ángulos
                    alpha = vuelo_obj.calc_alpha(v_rel, theta)
                    gamma = math.atan2(vel[2], vel[0]) if vel[0] != 0 or vel[2] != 0 else 0 # Evitar atan2(0,0)
                    Alphas.append(alpha)
                    Gammas.append(gamma)

                    # Calcular fuerzas aerodinámicas y Cd/Mach
                    # calc_arrastre_normal devuelve Dmag, Nmag, Cd, mach
                    Dmag, Nmag, Cd, mach = vuelo_obj.calc_arrastre_normal(pos, v_rel, alpha)
                    # calc_aero devuelve Dvec, Nvec
                    Dvec, Nvec = vuelo_obj.calc_aero(pos, v_rel, theta)
                    Cds.append(Cd)
                    Machs.append(mach)
                    Dvecs.append(Dvec)
                    Nvecs.append(Nvec)

                    # Calcular empuje
                    Tvec = vuelo_obj.calc_empuje(t, theta)
                    Tvecs.append(Tvec)

                    # Calcular gravedad
                    grav = calc_gravedad(pos[2])
                    Gvec = np.array([0, 0, -grav])

                    # Calcular aceleraciones y torcas
                    accel = Gvec + (Dvec + Nvec + Tvec) / vuelo_obj.vehiculo.masa
                    accels_lin.append(np.linalg.norm(accel)) # Guardar magnitud de aceleración lineal

                    # Calcular aceleración angular y torca
                    if np.linalg.norm(pos) > vuelo_obj.vehiculo.riel.longitud: # Solo calcular fuera del riel
                        palanca, accang, torca = vuelo_obj.accangular(theta, Dvec, Nvec, Gvec)
                    else:
                        palanca, accang, torca = np.zeros(3), 0.0, 0.0 # Dentro del riel

                    palancas.append(palanca)
                    accels_ang.append(accang) # CORRECCIÓN: Usar accels_ang consistentemente
                    torcas.append(torca)

                    # Guardar datos del viento
                    viento_vuelo_vecs.append(v_viento)
                    viento_vuelo_mags.append(np.linalg.norm(v_viento))
                    # Calcular dirección del viento (ej. azimut en plano XY)
                    wind_dir_rad = math.atan2(v_viento[1], v_viento[0]) if v_viento[0] != 0 or v_viento[1] != 0 else 0
                    viento_vuelo_dirs.append(wind_dir_rad)


                except AttributeError as ae: print(f"Error atributo post-proc t={t:.2f}: {ae}. Usando default."); pass
                except Exception as ex: print(f"Error post-proc t={t:.2f}: {ex}. Usando default."); print(traceback.format_exc()); pass
            print("Post-procesamiento completado.")
            posiciones = states_out[:, 0:3]; velocidades = states_out[:, 3:6]; thetas = states_out[:, 6]; omegas = states_out[:, 7]; Tmags = np.linalg.norm(Tvecs, axis=1); Dmags = np.linalg.norm(Dvecs, axis=1); Nmags = np.linalg.norm(Nvecs, axis=1); stability = [(cp - cg) / self.rocket.d_ext if self.rocket.d_ext > 0 else 0 for cp, cg in zip(CPs, CGs)]
            idx_apogeo = np.argmax(posiciones[:, 2]) if len(posiciones) > 0 else 0; max_altitude = posiciones[idx_apogeo, 2] if len(posiciones) > 0 else 0; tiempo_apogeo = tiempos_out[idx_apogeo] if len(tiempos_out) > 0 else 0; velocidades_mag = np.linalg.norm(velocidades, axis=1); idx_max_vel = np.argmax(velocidades_mag) if len(velocidades_mag) > 0 else 0; max_speed = velocidades_mag[idx_max_vel] if len(velocidades_mag) > 0 else 0; tiempo_max_vel = tiempos_out[idx_max_vel] if len(tiempos_out) > 0 else 0; max_mach = Machs[idx_max_vel] if len(Machs) > idx_max_vel else 0
            idx_impacto_candidates = np.where((posiciones[:, 2] <= riel.altitud) & (tiempos_out > tiempo_apogeo))[0] if len(tiempos_out) > 0 else []; tiempo_impacto = tiempos_out[idx_impacto_candidates[0]] if len(idx_impacto_candidates) > 0 else tiempos_out[-1] if len(tiempos_out) > 0 else 0; pos_impacto = posiciones[idx_impacto_candidates[0], 0:2] if len(idx_impacto_candidates) > 0 else posiciones[-1, 0:2] if len(posiciones) > 0 else [0,0]; distancia_impacto = np.linalg.norm(pos_impacto); max_accel_linear = np.max(accels_lin) if len(accels_lin) > 0 else 0; max_accel_angular = np.max(accels_ang) if len(accels_ang) > 0 else 0 # CORRECCIÓN: Usar accels_ang
            self.simulation_data = pd.DataFrame({ 'Tiempo (s)': tiempos_out, 'X (m)': posiciones[:, 0], 'Y (m)': posiciones[:, 1], 'Z (m)': posiciones[:, 2], 'Vx (m/s)': velocidades[:, 0], 'Vy (m/s)': velocidades[:, 1], 'Vz (m/s)': velocidades[:, 2], 'Velocidad (m/s)': velocidades_mag, 'Theta (rad)': thetas, 'Omega (rad/s)': omegas, 'CP (m)': CPs, 'CG (m)': CGs, 'Masa (kg)': masavuelo, 'Viento Mag (m/s)': viento_vuelo_mags, 'Viento Dir (rad)': viento_vuelo_dirs, 'Viento X': viento_vecs[:,0], 'Viento Y': viento_vecs[:,1], 'Viento Z': viento_vecs[:,2], 'Empuje (N)': Tmags, 'Arrastre (N)': Dmags, 'Normal (N)': Nmags, 'Accel Lin (m/s^2)': accels_lin, 'Accel Ang (rad/s^2)': accels_ang, 'Gamma (rad)': Gammas, 'Alpha (rad)': Alphas, 'Torca (Nm)': torcas, 'Cd': Cds, 'Mach': Machs, 'Estabilidad (cal)': stability })
            self.simulation_summary = { 'Método Integración': integrator_method, 'Paso de Tiempo (s)': dt_sim if integrator_method in ['Euler', 'RungeKutta4'] else 'Adaptativo (solve_ivp)', 'Diámetro Cohete (m)': self.rocket.d_ext, 'Masa Inicial (kg)': self.rocket.masa, 'Masa Final (kg)': masavuelo[-1] if len(masavuelo) > 0 else 'N/A', 'Tiempo MECO (s)': getattr(self.rocket, 't_MECO', 'N/A'), 'Tiempo Salida Riel (s)': getattr(vuelo_obj, 'tiempo_salida_riel', 'N/A'), 'Tiempo Apogeo (s)': tiempo_apogeo, 'Altitud Máxima (m)': max_altitude, 'Tiempo Velocidad Máxima (s)': tiempo_max_vel, 'Velocidad Máxima (m/s)': max_speed, 'Mach Máximo': max_mach, 'Aceleración Lineal Máx (m/s²)': max_accel_linear, 'Aceleración Angular Máx (rad/s²)': max_accel_angular, 'Tiempo Impacto (s)': tiempo_impacto, 'Distancia Impacto (m)': distancia_impacto, }
            self.update_plots(); self.update_summary_tab(); self.simulation_done = True
            self.progress.stop(); self.progress['mode'] = 'determinate'; self.progress['value'] = 100; self.progress_label.config(text="Simulación completada")
            self.save_simulation_results()
        except AttributeError as e: messagebox.showerror("Error de Atributo", f"Falta atributo/método: {e}\n{traceback.format_exc()}"); self.progress.stop(); self.progress_label.config(text="Error simulación")
        except IndexError as e: messagebox.showerror("Error de Índice", f"Error acceso datos: {e}\n{traceback.format_exc()}"); self.progress.stop(); self.progress_label.config(text="Error simulación")
        except RuntimeError as e: messagebox.showerror("Error de Ejecución", f"Fallo simulación: {e}\n{traceback.format_exc()}"); self.progress.stop(); self.progress_label.config(text="Error simulación")
        except Exception as e: messagebox.showerror("Error de Simulación", f"Error inesperado: {e}\n{traceback.format_exc()}"); self.progress.stop(); self.progress_label.config(text="Error simulación")

    # --- Update Plots (Sin cambios) ---
    def update_plots(self):
        if self.simulation_data is None: print("No hay datos para graficar."); return
        tiempos = self.simulation_data['Tiempo (s)']
        self.plot_trajectory(tiempos, self.simulation_data[['X (m)', 'Y (m)', 'Z (m)']].values)
        self.plot_position_velocity(tiempos, self.simulation_data['Z (m)'], self.simulation_data['Velocidad (m/s)'])
        self.plot_forces(tiempos, self.simulation_data['Empuje (N)'], self.simulation_data['Arrastre (N)'], self.simulation_data['Normal (N)'])
        self.plot_angles(tiempos, self.simulation_data['Theta (rad)'], self.simulation_data['Gamma (rad)'], self.simulation_data['Alpha (rad)'])
        self.plot_stability(tiempos, self.simulation_data['CP (m)'], self.simulation_data['CG (m)'], self.simulation_data['Estabilidad (cal)'])
        self.plot_wind(tiempos, self.simulation_data['Viento Mag (m/s)'], self.simulation_data['Viento Dir (rad)'])

    def _plot_on_tab(self, frame, plot_func, *args, **kwargs):
        for widget in frame.winfo_children(): widget.destroy()
        try: fig, ax = plt.subplots(figsize=(8, 6)); plot_func(ax, *args, **kwargs); ax.grid(True); fig.tight_layout(); canvas = FigureCanvasTkAgg(fig, master=frame); canvas.draw(); canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        except Exception as e: messagebox.showerror("Error Graficación", f"No se pudo generar gráfica: {e}\n{traceback.format_exc()}"); ttk.Label(frame, text=f"Error al graficar:\n{e}", foreground="red").pack(expand=True)

    def plot_trajectory(self, tiempos, posiciones):
        frame = self.trajectory_frame;
        for widget in frame.winfo_children(): widget.destroy()
        try:
            fig = plt.figure(figsize=(8, 6)); ax = fig.add_subplot(111, projection='3d'); ax.plot(posiciones[:, 0], posiciones[:, 1], posiciones[:, 2], label='Trayectoria')
            if len(posiciones) > 0: idx_apogeo = np.argmax(posiciones[:, 2]); ax.scatter(posiciones[idx_apogeo, 0], posiciones[idx_apogeo, 1], posiciones[idx_apogeo, 2], color='red', s=50, label=f'Apogeo ({posiciones[idx_apogeo, 2]:.0f} m)'); max_range = np.max(np.abs(posiciones)) * 1.1 if np.max(np.abs(posiciones)) > 0 else 10; ax.set_xlim(-max_range, max_range); ax.set_ylim(-max_range, max_range); ax.set_zlim(0, max(10, posiciones[idx_apogeo, 2] * 1.1))
            ax.set_xlabel('X (m)'); ax.set_ylabel('Y (m)'); ax.set_zlabel('Altitud (Z) (m)'); ax.set_title('Trayectoria 3D del Cohete'); ax.legend(); ax.grid(True); fig.tight_layout(); canvas = FigureCanvasTkAgg(fig, master=frame); canvas.draw(); canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        except Exception as e: messagebox.showerror("Error Graficando Trayectoria", f"Error: {e}\n{traceback.format_exc()}"); ttk.Label(frame, text=f"Error graficando trayectoria:\n{e}", foreground="red").pack(expand=True)

    def plot_position_velocity(self, tiempos, altitudes, velocidades_mag):
        def _draw(ax): ax2 = ax.twinx(); l1, = ax.plot(tiempos, altitudes, color='blue', label='Altitud'); ax.set_xlabel('Tiempo (s)'); ax.set_ylabel('Altitud (m)', color='blue'); ax.tick_params(axis='y', labelcolor='blue'); l2, = ax2.plot(tiempos, velocidades_mag, color='red', label='Velocidad'); ax2.set_ylabel('Velocidad (m/s)', color='red'); ax2.tick_params(axis='y', labelcolor='red'); ax.set_title('Altitud y Velocidad vs Tiempo'); ax.legend([l1, l2], [l.get_label() for l in [l1, l2]])
        self._plot_on_tab(self.position_frame, _draw)

    def plot_forces(self, tiempos, Tmags, Dmags, Nmags):
        def _draw(ax): ax.plot(tiempos, Tmags, label='Empuje (T)'); ax.plot(tiempos, Dmags, label='Arrastre (D)'); ax.plot(tiempos, Nmags, label='Normal (N)'); ax.set_xlabel('Tiempo (s)'); ax.set_ylabel('Fuerza (N)'); ax.set_title('Magnitud de Fuerzas vs Tiempo'); ax.legend(); ax.set_yscale('log'); ax.grid(True, which='both', linestyle='--', linewidth=0.5)
        self._plot_on_tab(self.forces_frame, _draw)

    def plot_angles(self, tiempos, thetas, Gammas, Alphas):
        def _draw(ax): ax.plot(tiempos, np.rad2deg(thetas), label='Pitch (Theta)'); ax.plot(tiempos, np.rad2deg(Gammas), label='Trayectoria (Gamma)'); ax.plot(tiempos, np.rad2deg(Alphas), label='Ataque (Alpha)'); ax.set_xlabel('Tiempo (s)'); ax.set_ylabel('Ángulo (grados)'); ax.set_title('Ángulos de Vuelo vs Tiempo'); ax.legend()
        self._plot_on_tab(self.angles_frame, _draw)

    def plot_stability(self, tiempos, CPs, CGs, stability):
        def _draw(ax): ax2 = ax.twinx(); l1, = ax.plot(tiempos, CPs, color='cyan', label='CP'); l2, = ax.plot(tiempos, CGs, color='magenta', label='CG'); ax.set_xlabel('Tiempo (s)'); ax.set_ylabel('Posición Longitudinal (m)', color='black'); ax.tick_params(axis='y', labelcolor='black'); l3, = ax2.plot(tiempos, stability, color='orange', linestyle='--', label='Margen Estático'); ax2.set_ylabel('Margen Estático (calibres)', color='orange'); ax2.tick_params(axis='y', labelcolor='orange'); l4 = ax2.axhline(1.0, color='gray', linestyle=':', linewidth=1, label='Estabilidad Mín (1 cal)'); ax.set_title('Estabilidad Longitudinal vs Tiempo'); ax.legend([l1, l2, l3, l4], [l.get_label() for l in [l1, l2, l3, l4]], loc='best')
        self._plot_on_tab(self.stability_frame, _draw)

    def plot_wind(self, tiempos, viento_mags, viento_dirs):
        def _draw(ax): ax2 = ax.twinx(); l1, = ax.plot(tiempos, viento_mags, color='green', label='Magnitud Viento Rel'); ax.set_xlabel('Tiempo (s)'); ax.set_ylabel('Velocidad (m/s)', color='green'); ax.tick_params(axis='y', labelcolor='green'); viento_dirs_deg = (np.rad2deg(viento_dirs) + 180) % 360 - 180; l2, = ax2.plot(tiempos, viento_dirs_deg, color='purple', linestyle=':', label='Dirección Viento Rel'); ax2.set_ylabel('Dirección (grados)', color='purple'); ax2.tick_params(axis='y', labelcolor='purple'); ax2.set_ylim(-180, 180); ax.set_title('Viento Relativo vs Tiempo'); ax.legend([l1, l2], [l.get_label() for l in [l1, l2]])
        self._plot_on_tab(self.wind_frame, _draw)

    # --- Summary Tab ---
    def update_summary_tab(self):
        """Updates the summary tab with data from self.simulation_summary."""
        for widget in self.summary_frame.winfo_children(): widget.destroy() # Clear frame
        if self.simulation_summary is None: self.show_no_simulation_message(self.summary_frame); return

        # Recreate the text widget to display summary
        self.summary_text_widget = tk.Text(self.summary_frame, wrap="word", height=25, width=80,
                                           font=('Courier New', 10), relief=tk.SOLID, borderwidth=1,
                                           bg='#2E2E2E', fg='white', state=tk.NORMAL) # Enable to insert
        self.summary_text_widget.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        summary_str = "--- Resumen de la Simulación ---\n\n"
        # Put integrator method and dt first if they exist
        if 'Método Integración' in self.simulation_summary:
             summary_str += f"{'Método Integración':<35}: {self.simulation_summary['Método Integración']:>15}\n"
        if 'Paso de Tiempo (s)' in self.simulation_summary:
             summary_str += f"{'Paso de Tiempo (s)':<35}: {self.simulation_summary['Paso de Tiempo (s)']:>15}\n"
        summary_str += "-"*52 + "\n" # Separator

        # Add the rest of the summary items
        for key, value in self.simulation_summary.items():
            if key not in ['Método Integración', 'Paso de Tiempo (s)']: # Avoid duplicates
                if isinstance(value, float): summary_str += f"{key:<35}: {value:>15.2f}\n"
                elif isinstance(value, str): summary_str += f"{key:<35}: {value:>15}\n"
                else: summary_str += f"{key:<35}: {str(value):>15}\n"

        self.summary_text_widget.insert(tk.END, summary_str)
        self.summary_text_widget.config(state=tk.DISABLED) # Disable editing

        # Button to save summary
        save_summary_btn = ttk.Button(self.summary_frame, text="Guardar Resumen (.txt)",
                                      command=self.save_summary_to_file)
        save_summary_btn.pack(pady=5)

    # --- Save Summary (Corrected try-except block) ---
    def save_summary_to_file(self):
        """Saves the content of the summary tab to a text file."""
        if not hasattr(self, 'summary_text_widget') or self.simulation_summary is None:
            messagebox.showwarning("Sin Datos", "No hay resumen de simulación para guardar.")
            return

        file_path = filedialog.asksaveasfilename(
            title="Guardar Resumen",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if not file_path:
            return # User cancelled

        # --- Corrected try-except block ---
        try:
            # Get text content from the Text widget
            summary_str = self.summary_text_widget.get("1.0", tk.END)
            # Write the content to the selected file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(summary_str)
            # Show success message
            messagebox.showinfo("Éxito", f"Resumen guardado en:\n{file_path}")
        except Exception as e:
            # Show error message if saving fails
            messagebox.showerror("Error Guardar", f"No se pudo guardar el archivo de resumen:\n{e}")
        # No finally block needed here unless there's cleanup to do regardless of success/failure

    # --- Save/Load Configuration Data (Actualizado para componentes individuales) ---
    def save_tab_data(self, tab_name):
        """Saves configuration data from Rocket or Input tab to JSON."""
        data = {}
        if tab_name == "rocket":
            try:
                data = { "version": 1.2, "description": "Definición detallada cohete (Xitle)"}
                # Iterar sobre los widgets guardados para componentes
                for key, widget in self.component_widgets.items():
                    # Solo guardar widgets que pertenecen a las pestañas de cohete
                    if key.startswith(("nariz_", "coples_", "tubo_recup_", "transfer_", "tanquevacio_",
                                       "valvulas_", "cc_", "aletas_", "boattail_")):
                        data[key] = widget.get()

                # Validación básica (solo si los campos no están vacíos)
                for key, value in data.items():
                    if key not in ["version", "description", "nariz_geometria"]:
                        if not value: raise ValueError(f"Campo '{key}' está vacío.")
                        # Intentar conversión básica, pero no fallar si no es número (ej. geometria)
                        try:
                            if 'count' in key or 'numf' in key: int(value)
                            elif key != "nariz_geometria": float(value)
                        except ValueError:
                             # Permitir no numéricos como geometria
                             if key != "nariz_geometria":
                                 raise ValueError(f"Valor inválido para '{key}': '{value}'")
            except ValueError as e:
                 messagebox.showerror("Error Validación", f"Datos cohete: {e}"); return
            except Exception as e:
                 messagebox.showerror("Error", f"Error recopilando datos cohete: {e}"); return

        elif tab_name == "input":
            try:
                # Collect data from input tab widgets
                data = {
                    "version": 1.1, "description": "Parámetros simulación",
                    "latitud": self.latitud.get(),"longitud": self.longitud.get(),"altitud": self.altitud.get(),"fecha": self.fecha.get(),
                    "longitud_riel": self.longitud_riel.get(),"angulo_riel": self.angulo_riel.get(),
                    "vel_base_viento": self.vel_base_viento.get(),"vel_mean_viento": self.vel_mean_viento.get(),"vel_var_viento": self.vel_var_viento.get(),"var_ang_viento": self.var_ang_viento.get(),
                    "t_max": self.t_max.get(),"dt": self.dt.get(),
                    "integrator_method": self.selected_integrator.get() # Save integrator
                }
                # Basic validation
                for key, value in data.items():
                     if key not in ["version", "description", "fecha", "integrator_method"]:
                          if not value: raise ValueError(f"Campo '{key}' vacío.")
                          float(value) # Try float conversion
                     if key == 'fecha': datetime.strptime(value, '%Y-%m-%d') # Validate date format
                     if key == 'integrator_method' and value == 'N/A': raise ValueError("Método integrador no válido.")
            except ValueError as e: messagebox.showerror("Error Validación", f"Parámetros simulación: {e}"); return
            except Exception as e: messagebox.showerror("Error", f"Error recopilando parámetros: {e}"); return
        else:
            messagebox.showerror("Error Interno", f"Pestaña no reconocida para guardar: {tab_name}"); return

        # Ask user for save location
        file_path = filedialog.asksaveasfilename(title=f"Guardar Configuración {tab_name.capitalize()}", defaultextension=".json", filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if file_path:
            try:
                # Write data to JSON file
                with open(file_path, 'w', encoding='utf-8') as f: json.dump(data, f, indent=4)
                messagebox.showinfo("Éxito", f"Configuración '{tab_name}' guardada en:\n{file_path}")
            except Exception as e: messagebox.showerror("Error Guardar", f"No se pudo guardar JSON:\n{e}")

    def load_tab_data(self, tab_name):
        """Loads configuration data from a JSON file into the corresponding tab."""
        # Ask user for file location
        file_path = filedialog.askopenfilename(title=f"Cargar Configuración {tab_name.capitalize()}", filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if not file_path: return # User cancelled
        try:
            # Read JSON data
            with open(file_path, 'r', encoding='utf-8') as f: data = json.load(f)
            if tab_name == "rocket":
                # Populate widgets based on saved keys
                for key, widget in self.component_widgets.items():
                    # Solo cargar widgets que pertenecen a las pestañas de cohete
                    if key.startswith(("nariz_", "coples_", "tubo_recup_", "transfer_", "tanquevacio_",
                                       "valvulas_", "cc_", "aletas_", "boattail_")):
                        if key in data:
                            value = str(data[key])
                            if isinstance(widget, ttk.Entry):
                                widget.delete(0, tk.END); widget.insert(0, value)
                            elif isinstance(widget, ttk.Combobox):
                                if value in widget['values']: widget.set(value)
                                else: print(f"Advertencia: Valor '{value}' para '{key}' no es opción válida."); widget.set(widget['values'][0])
                        else:
                            print(f"Advertencia: Clave '{key}' no encontrada en JSON cargado.")
                self.update_rocket_from_gui() # Actualizar objeto cohete con datos cargados
            elif tab_name == "input":
                # Map JSON keys to GUI widgets
                mapping = { "latitud": self.latitud, "longitud": self.longitud, "altitud": self.altitud, "fecha": self.fecha, "longitud_riel": self.longitud_riel, "angulo_riel": self.angulo_riel, "vel_base_viento": self.vel_base_viento, "vel_mean_viento": self.vel_mean_viento, "vel_var_viento": self.vel_var_viento, "var_ang_viento": self.var_ang_viento, "t_max": self.t_max, "dt": self.dt, "integrator_method": self.integrator_method_combo }
                # Populate widgets
                for key, widget in mapping.items():
                     if key in data: value = str(data[key]);
                     if isinstance(widget, ttk.Entry): widget.delete(0, tk.END); widget.insert(0, value)
                     elif isinstance(widget, ttk.Combobox):
                         if value in widget['values']: widget.set(value)
                         else: print(f"Advertencia: Método integrador '{value}' no es opción válida."); widget.set(widget['values'][0])
                     else: print(f"Advertencia: Clave '{key}' no encontrada en JSON.")
                self.update_simulation_parameters()
            messagebox.showinfo("Éxito", f"Configuración '{tab_name}' cargada desde:\n{file_path}")
        except FileNotFoundError: messagebox.showerror("Error", f"Archivo no encontrado: {file_path}")
        except json.JSONDecodeError: messagebox.showerror("Error", f"JSON inválido: {file_path}")
        except Exception as e: messagebox.showerror("Error Cargar", f"No se pudo cargar/procesar JSON:\n{e}\n{traceback.format_exc()}")

    # --- Save Simulation Results CSV (Sin cambios) ---
    def save_simulation_results(self):
        if self.simulation_data is None: print("No hay datos de simulación para guardar."); return
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S"); default_filename = f"simulacion_resultados_{self.selected_integrator.get()}_{timestamp}.csv"
        file_path = filedialog.asksaveasfilename(title="Guardar Resultados Completos", initialfile=default_filename, defaultextension=".csv", filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if not file_path: return
        try: self.simulation_data.to_csv(file_path, index=False, encoding='utf-8'); messagebox.showinfo("Éxito", f"Resultados guardados en:\n{file_path}")
        except Exception as e: messagebox.showerror("Error Guardar", f"No se pudo guardar CSV:\n{e}")

# --- Main Entry Point (Sin cambios) ---
if __name__ == "__main__":
    try: root = tk.Tk(); app = SimuladorCohetesAvanzado(root); root.mainloop()
    except Exception as e: error_msg = f"Error fatal al iniciar el simulador:\n{e}\n\n{traceback.format_exc()}";
    try: root_err = tk.Tk(); root_err.withdraw(); messagebox.showerror("Error Fatal", error_msg)
    except: print("\n--- ERROR FATAL ---"); print(error_msg); print("-------------------\n")
