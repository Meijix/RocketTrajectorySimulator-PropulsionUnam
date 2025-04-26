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

except ImportError as e:
    messagebox.showerror("Error de Importación de Física",
                         f"No se pudieron importar módulos de física necesarios: {e}\n"
                         f"Asegúrate de que los paquetes 'Simulador' y 'Paquetes' estén en la ruta correcta:\n{package_path}\n"
                         f"Traceback: {traceback.format_exc()}")
    sys.exit(1)
except Exception as e:
    messagebox.showerror("Error Inesperado en Importación", f"Ocurrió un error durante la inicialización: {e}\nTraceback: {traceback.format_exc()}")
    sys.exit(1)


class SimuladorCohetesAvanzado:
    """
    Clase principal para la interfaz gráfica del simulador de cohetes suborbitales.
    Permite selección de método de integración. Usa valores Xitle por defecto.
    Nombres de propiedades ajustados según clases de componentes.py.
    Intenta cargar CSVs predeterminados al inicio considerando la estructura de archivos.
    """
    def __init__(self, master):
        self.master = master
        self.master.title("Simulador de Cohetes Suborbitales Avanzado (Props Ajustadas)")
        self.master.geometry("1200x850")

        # --- Estilos ---
        azul = '#151E3D' # Dark Denim
        rojo = '#90091d' # Dark Red
        font_selection = ('Lucida Sans Unicode', 10)
        self.master.configure(bg=azul)
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TButton', font=font_selection, background=rojo, foreground='white', borderwidth=1)
        self.style.map('TButton', background=[('active', '#b80b25')]) # Hover/active color
        self.style.configure('TLabel', font=font_selection, background=azul, foreground='white')
        self.style.configure('TEntry', font=font_selection, fieldbackground='white', foreground='black')
        self.style.configure('TCombobox', font=font_selection, fieldbackground='white', foreground='black')
        self.style.configure('TNotebook', background=azul)
        self.style.configure('TNotebook.Tab', font=font_selection, background=azul, foreground='gray', padding=[5, 2])
        self.style.map('TNotebook.Tab', background=[('selected', azul)], foreground=[('selected', 'white')])
        self.style.configure('TFrame', background=azul)
        self.style.configure('Horizontal.TProgressbar', background=rojo)
        # Estilo para botones de visualización
        self.style.configure('Vis.TButton', font=font_selection, background='#ADD8E6', foreground='black', borderwidth=1) # Light Blue
        self.style.map('Vis.TButton', background=[('active', '#87CEEB')]) # Sky Blue on hover

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


        # --- Valores Predeterminados del Cohete Xitle (Ajustados) ---
        self.diam_ext_xitle = 0.152
        self.espesor_xitle = 0.003
        long_nariz_xitle = 0.81; masa_nariz_xitle = 0.8; geom_nariz_xitle = "ogiva"; diam_nariz_xitle = self.diam_ext_xitle
        self.long_fus_xitle = 0.176 + 0.92 + 0.25 + 1.25 + 0.167 + 0.573; masa_fus_xitle = 1.5 + 2.3 + 1.0 + 8.7 + 2.4 + 4.3
        diam_ext_fus_xitle = self.diam_ext_xitle; diam_int_fus_xitle = self.diam_ext_xitle - 2 * self.espesor_xitle
        num_aletas_xitle = 4; enverg_aletas_xitle = 0.11; cuerda_r_aletas_xitle = 0.3; cuerda_p_aletas_xitle = 0.1
        barrido_aletas_xitle = 25; masa_aletas_xitle = 1.1
        long_boat_xitle = 0.12; diam_boat_frontal_xitle = self.diam_ext_xitle; diam_boat_tras_xitle = 0.132
        masa_boat_xitle = 0.251; espesor_boat_xitle = self.espesor_xitle
        masa_motor_xitle = 8.7 + 2.4 + 4.3; self.long_motor_xitle = 1.25 + 0.167 + 0.573; self.diam_motor_xitle = self.diam_ext_xitle

        # --- Inicialización del Objeto Cohete con valores Xitle y nombres correctos ---
        try:
            # Crear componentes usando los nombres de atributos de las clases
            nariz_init = Cono("Nariz", masa_nariz_xitle, np.array([0.0, 0.0, 0.0]),
                              longitud=long_nariz_xitle, diametro=diam_nariz_xitle, geometria=geom_nariz_xitle)
            pos_fus_init = np.array([0.0, 0.0, nariz_init.bottom[2]]) # Usa el .bottom calculado por Cono
            fuselaje_init = Cilindro("Fuselaje", masa_fus_xitle, pos_fus_init,
                                     longitud=self.long_fus_xitle, diametroexterior=diam_ext_fus_xitle, diametrointerior=diam_int_fus_xitle)
            # Asume montaje al final del fuselaje combinado
            pos_aletas_init = np.array([0.0, 0.0, fuselaje_init.bottom[2] - cuerda_r_aletas_xitle])
            aletas_init = Aletas("Aletas", masa_aletas_xitle, pos_aletas_init,
                                 diametro=diam_ext_fus_xitle, # diametro del fuselaje donde se monta
                                 numf=num_aletas_xitle, semispan=enverg_aletas_xitle,
                                 C_r=cuerda_r_aletas_xitle, C_t=cuerda_p_aletas_xitle,
                                 X_R=0.0, # X_R no está en la GUI, se asume 0? O se calcula desde sweep? -> Se usa mid_sweep
                                 mid_sweep=np.deg2rad(barrido_aletas_xitle))
            pos_boat_init = np.array([0.0, 0.0, fuselaje_init.bottom[2]])
            boattail_init = Boattail("Boattail", masa_boat_xitle, pos_boat_init,
                                     longitud=long_boat_xitle, diamF_boat=diam_boat_frontal_xitle,
                                     diamR_boat=diam_boat_tras_xitle, espesor=espesor_boat_xitle)
            # Posición del motor estimada (centrada en la longitud combinada tanque+valvulas+CC)
            pos_motor_init_z = pos_fus_init[2] + (self.long_fus_xitle - self.long_motor_xitle / 2) # Centrado en la sección del motor
            pos_motor_init = np.array([0.0, 0.0, pos_motor_init_z])
            motor_init = Componente("Motor", masa_motor_xitle, pos_motor_init) # Usa Componente base

            # --- WORKAROUND: Establecer explícitamente CG y CP para el componente Motor base ---
            motor_init.CG = np.array([0.0, 0.0, self.long_motor_xitle / 2.0])
            motor_init.CP = np.zeros(3); motor_init.CN = 0
            # --- Fin WORKAROUND ---

            self.lista_componentes_init_gui = {
                'Nariz': nariz_init, 'Fuselaje': fuselaje_init, 'Aletas': aletas_init,
                'Boattail': boattail_init, 'Motor': motor_init
            }

            # --- Crear instancia de Cohete (inicialmente sin rutas CSV, se cargarán después) ---
            # Pasar None para las rutas, se actualizarán después de intentar cargar defaults
            self.rocket = Cohete("Xitle (Default)", "hibrido", self.lista_componentes_init_gui, self.lista_componentes_init_gui,
                                 None, None, None, riel)
            self.rocket.d_ext = self.diam_ext_xitle
            # calcular_propiedades se llamará después de cargar los CSVs

        except NameError as e:
             messagebox.showwarning("Advertencia Componentes", f"No se pudieron crear los componentes iniciales (Xitle). Clase no definida: {e}")
             self.lista_componentes_init_gui = {}
             self.rocket = None
        except TypeError as e:
             messagebox.showerror("Error Argumentos", f"Error al crear componente inicial (Xitle), revisa argumentos: {e}\n{traceback.format_exc()}")
             self.lista_componentes_init_gui = {}
             self.rocket = None
        except Exception as e:
            messagebox.showerror("Error Cohete Inicial", f"Error creando cohete inicial (Xitle): {e}\n{traceback.format_exc()}")
            self.lista_componentes_init_gui = {}
            self.rocket = None

        # --- Interfaz Gráfica ---
        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)

        # Crear pestañas
        self.create_rocket_tab()
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


    # --- Funciones Auxiliares de GUI (sin cambios) ---
    def create_section(self, parent, text, row, column, columnspan=2):
        ttk.Label(parent, text=text, font=('Lucida Sans Unicode', 11, 'bold'), foreground='#48AAAD') \
           .grid(row=row, column=column, columnspan=columnspan, sticky="w", padx=5, pady=(10, 2))

    def create_entry(self, parent, row, column, label, default_value=""):
        ttk.Label(parent, text=label).grid(row=row, column=column, sticky="w", padx=5, pady=2)
        entry = ttk.Entry(parent, width=15)
        entry.grid(row=row, column=column+1, padx=5, pady=2, sticky="ew")
        entry.insert(0, str(default_value))
        return entry

    def create_combobox(self, parent, row, column, label, values, default_value, textvariable=None):
        ttk.Label(parent, text=label).grid(row=row, column=column, sticky="w", padx=5, pady=2)
        combobox = ttk.Combobox(parent, values=values, state="readonly", width=13, textvariable=textvariable)
        combobox.grid(row=row, column=column+1, padx=5, pady=2, sticky="ew")
        if default_value in values:
            combobox.set(default_value)
        elif values:
            combobox.current(0)
        return combobox

    def show_no_simulation_message(self, frame):
        for widget in frame.winfo_children(): widget.destroy()
        label = ttk.Label(frame, text="Realice una simulación para ver los resultados", font=('Lucida Sans Unicode', 14))
        label.pack(expand=True, padx=20, pady=20)

    # --- Pestaña: Definición del Cohete (Etiquetas y defaults ajustados) ---
    def create_rocket_tab(self):
        """Crea la pestaña para definir las propiedades del cohete, usando defaults Xitle y nombres ajustados."""
        self.rocket_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.rocket_frame, text="Cohete")

        col1_frame = ttk.Frame(self.rocket_frame); col1_frame.grid(row=0, column=0, padx=10, pady=5, sticky="nw")
        col2_frame = ttk.Frame(self.rocket_frame); col2_frame.grid(row=0, column=1, padx=10, pady=5, sticky="nw")
        col3_frame = ttk.Frame(self.rocket_frame); col3_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        # Helper para obtener atributos iniciales de forma segura
        def get_init_attr(comp_name, attr_name, default_val):
            # Accede a la lista de componentes creada en __init__
            comp = getattr(self, 'lista_componentes_init_gui', {}).get(comp_name)
            # Devuelve el atributo si existe, sino el valor por defecto
            return getattr(comp, attr_name, default_val) if comp else default_val

        # Nariz (Cono) - Usando nombres de atributos de la clase Cono
        self.create_section(col1_frame, "Nariz (Cono):", 0, 0)
        self.nose_length = self.create_entry(col1_frame, 1, 0, "Longitud (long):", f"{get_init_attr('Nariz', 'long', 0.81):.2f}")
        self.nose_diameter = self.create_entry(col1_frame, 2, 0, "Diámetro base (diam):", f"{get_init_attr('Nariz', 'diam', 0.152):.3f}")
        self.nose_mass = self.create_entry(col1_frame, 3, 0, "Masa:", f"{get_init_attr('Nariz', 'masa', 0.8):.1f}")
        self.nose_geometry = self.create_combobox(col1_frame, 4, 0, "Geometría (geom):", ["conica", "ogiva", "parabolica", "eliptica"], get_init_attr('Nariz', 'geom', "ogiva"))

        # Fuselaje (Cilindro) - Usando nombres de atributos de la clase Cilindro
        fus_long_def = get_init_attr('Fuselaje', 'long', 3.336)
        # CORRECCIÓN: Obtener diam_ext y diam_int usando get_init_attr
        fus_diam_ext_def = get_init_attr('Fuselaje', 'diam_ext', self.diam_ext_xitle) # Usa valor de __init__ como fallback
        fus_diam_int_def = get_init_attr('Fuselaje', 'diam_int', self.diam_ext_xitle - 2 * self.espesor_xitle) # Usa valores de __init__ como fallback
        fus_mass_def = get_init_attr('Fuselaje', 'masa', 20.2)
        # Calcular espesor basado en los diámetros obtenidos
        fus_thick_def = (fus_diam_ext_def - fus_diam_int_def) / 2 if fus_diam_ext_def > 0 and fus_diam_int_def > 0 else self.espesor_xitle

        self.create_section(col1_frame, "Fuselaje (Cilindro):", 5, 0)
        self.body_length = self.create_entry(col1_frame, 6, 0, "Longitud (long):", f"{fus_long_def:.3f}")
        self.body_diameter = self.create_entry(col1_frame, 7, 0, "Diámetro ext. (diam_ext):", f"{fus_diam_ext_def:.3f}")
        self.body_thickness = self.create_entry(col1_frame, 8, 0, "Espesor pared:", f"{fus_thick_def:.3f}") # Calculado
        self.body_mass = self.create_entry(col1_frame, 9, 0, "Masa:", f"{fus_mass_def:.1f}")

        # Aletas - Usando nombres de atributos de la clase Aletas
        fin_count_def = get_init_attr('Aletas', 'numf', 4)
        fin_span_def = get_init_attr('Aletas', 'semispan', 0.11)
        fin_root_chord_def = get_init_attr('Aletas', 'C_r', 0.3)
        fin_tip_chord_def = get_init_attr('Aletas', 'C_t', 0.1)
        fin_sweep_def = np.degrees(get_init_attr('Aletas', 'mid_sweep', np.deg2rad(25)))
        fin_mass_def = get_init_attr('Aletas', 'masa', 1.1)

        self.create_section(col2_frame, "Aletas:", 0, 0)
        self.fin_count = self.create_entry(col2_frame, 1, 0, "Número (numf):", fin_count_def)
        self.fin_span = self.create_entry(col2_frame, 2, 0, "Envergadura (semispan):", f"{fin_span_def:.2f}")
        self.fin_root_chord = self.create_entry(col2_frame, 3, 0, "Cuerda Raíz (C_r):", f"{fin_root_chord_def:.1f}")
        self.fin_tip_chord = self.create_entry(col2_frame, 4, 0, "Cuerda Punta (C_t):", f"{fin_tip_chord_def:.1f}")
        self.fin_sweep = self.create_entry(col2_frame, 5, 0, "Barrido Medio (°):", f"{fin_sweep_def:.0f}") # mid_sweep
        self.fin_mass = self.create_entry(col2_frame, 6, 0, "Masa total:", f"{fin_mass_def:.1f}")

        # Boattail - Usando nombres de atributos de la clase Boattail
        boat_len_def = get_init_attr('Boattail', 'long', 0.12)
        boat_dF_def = get_init_attr('Boattail', 'dF', 0.152)
        boat_dR_def = get_init_attr('Boattail', 'dR', 0.132)
        boat_mass_def = get_init_attr('Boattail', 'masa', 0.251)

        self.create_section(col2_frame, "Boattail:", 7, 0)
        self.boattail_length = self.create_entry(col2_frame, 8, 0, "Longitud (long):", f"{boat_len_def:.2f}")
        self.boattail_front_diameter = self.create_entry(col2_frame, 9, 0, "Diámetro Frontal (dF):", f"{boat_dF_def:.3f}")
        self.boattail_rear_diameter = self.create_entry(col2_frame, 10, 0, "Diámetro Trasero (dR):", f"{boat_dR_def:.3f}")
        self.boattail_mass = self.create_entry(col2_frame, 11, 0, "Masa:", f"{boat_mass_def:.3f}")

        # Motor (Sección GUI para masa/dimensiones estructurales)
        motor_mass_def = get_init_attr('Motor', 'masa', 15.4) # Masa tanque + valvulas + CC
        # CORRECCIÓN: Usar el valor numérico default directamente si get_init_attr falla
        motor_len_def = get_init_attr('Motor', 'long', 1.99) # Valor default numérico
        motor_diam_def = get_init_attr('Motor', 'diam', self.diam_ext_xitle) # Valor default numérico

        self.create_section(col2_frame, "Motor (Estructural):", 12, 0)
        self.motor_mass = self.create_entry(col2_frame, 13, 0, "Masa (sin prop.):", f"{motor_mass_def:.1f}")
        self.motor_length = self.create_entry(col2_frame, 14, 0, "Longitud:", f"{motor_len_def:.3f}")
        self.motor_diameter = self.create_entry(col2_frame, 15, 0, "Diámetro:", f"{motor_diam_def:.3f}")

        # Buttons
        self.btn_update_rocket = ttk.Button(col3_frame, text="Actualizar Cohete", command=self.update_rocket_from_gui)
        self.btn_update_rocket.pack(side=tk.LEFT, padx=5, pady=10)
        self.btn_save_rocket = ttk.Button(col3_frame, text="Guardar Definición", command=lambda: self.save_tab_data("rocket"))
        self.btn_save_rocket.pack(side=tk.LEFT, padx=5, pady=10)
        self.btn_load_rocket = ttk.Button(col3_frame, text="Cargar Definición", command=lambda: self.load_tab_data("rocket"))
        self.btn_load_rocket.pack(side=tk.LEFT, padx=5, pady=10)

    # --- Populate Rocket Tab (Usa nombres de atributos correctos) ---
    def populate_rocket_tab(self):
        """Rellena los campos de la pestaña Cohete con datos del objeto self.rocket."""
        if not self.rocket or not hasattr(self.rocket, 'componentes'): return
        try:
            # Nariz
            nariz = self.rocket.componentes.get('Nariz')
            if nariz:
                self.nose_length.delete(0, tk.END); self.nose_length.insert(0, str(getattr(nariz, 'long', '')))
                self.nose_diameter.delete(0, tk.END); self.nose_diameter.insert(0, str(getattr(nariz, 'diam', '')))
                self.nose_mass.delete(0, tk.END); self.nose_mass.insert(0, str(getattr(nariz, 'masa', '')))
                if hasattr(nariz, 'geom') and nariz.geom in self.nose_geometry['values']: self.nose_geometry.set(nariz.geom)
            # Fuselaje
            fuselaje = self.rocket.componentes.get('Fuselaje')
            if fuselaje:
                self.body_length.delete(0, tk.END); self.body_length.insert(0, str(getattr(fuselaje, 'long', '')))
                diam_ext = getattr(fuselaje, 'diam_ext', 0.0)
                diam_int = getattr(fuselaje, 'diam_int', 0.0)
                self.body_diameter.delete(0, tk.END); self.body_diameter.insert(0, str(diam_ext))
                thickness = (diam_ext - diam_int) / 2 if diam_ext > 0 and diam_int > 0 else 0.0
                self.body_thickness.delete(0, tk.END); self.body_thickness.insert(0, f"{thickness:.4f}")
                self.body_mass.delete(0, tk.END); self.body_mass.insert(0, str(getattr(fuselaje, 'masa', '')))
            # Aletas
            aletas = self.rocket.componentes.get('Aletas')
            if aletas:
                self.fin_count.delete(0, tk.END); self.fin_count.insert(0, str(getattr(aletas, 'numf', '')))
                self.fin_span.delete(0, tk.END); self.fin_span.insert(0, str(getattr(aletas, 'semispan', '')))
                self.fin_root_chord.delete(0, tk.END); self.fin_root_chord.insert(0, str(getattr(aletas, 'C_r', '')))
                self.fin_tip_chord.delete(0, tk.END); self.fin_tip_chord.insert(0, str(getattr(aletas, 'C_t', '')))
                sweep_rad = getattr(aletas, 'mid_sweep', 0.0)
                self.fin_sweep.delete(0, tk.END); self.fin_sweep.insert(0, f"{np.degrees(sweep_rad):.1f}")
                self.fin_mass.delete(0, tk.END); self.fin_mass.insert(0, str(getattr(aletas, 'masa', '')))
            # Boattail
            boattail = self.rocket.componentes.get('Boattail')
            if boattail:
                self.boattail_length.delete(0, tk.END); self.boattail_length.insert(0, str(getattr(boattail, 'long', '')))
                self.boattail_front_diameter.delete(0, tk.END); self.boattail_front_diameter.insert(0, str(getattr(boattail, 'dF', '')))
                self.boattail_rear_diameter.delete(0, tk.END); self.boattail_rear_diameter.insert(0, str(getattr(boattail, 'dR', '')))
                self.boattail_mass.delete(0, tk.END); self.boattail_mass.insert(0, str(getattr(boattail, 'masa', '')))
            # Motor (Estructural)
            motor = self.rocket.componentes.get('Motor')
            if motor:
                self.motor_mass.delete(0, tk.END); self.motor_mass.insert(0, str(getattr(motor, 'masa', '')))
                # Usa getattr con default 'N/A' ya que Componente base no tiene long/diam
                self.motor_length.delete(0, tk.END); self.motor_length.insert(0, str(getattr(motor, 'long', 'N/A')))
                self.motor_diameter.delete(0, tk.END); self.motor_diameter.insert(0, str(getattr(motor, 'diam', 'N/A')))
        except tk.TclError as e: messagebox.showerror("Error GUI", f"Error al actualizar campos: {e}")
        except AttributeError as e: messagebox.showwarning("Atributo Faltante", f"Falta atributo en componente: {e}")
        except Exception as e: messagebox.showerror("Error Inesperado", f"Error al poblar pestaña cohete: {e}\n{traceback.format_exc()}")

    # --- Update Rocket from GUI (Usa __init__ de clases Componente y workaround para Motor) ---
    def update_rocket_from_gui(self):
        """Actualiza el objeto self.rocket con datos de la GUI, usando los __init__ correctos."""
        try:
            # --- Validar y Obtener Datos Numéricos ---
            def get_float(entry, name):
                try: return float(entry.get())
                except ValueError: raise ValueError(f"Valor inválido para '{name}': '{entry.get()}'")
            def get_int(entry, name):
                try: return int(entry.get())
                except ValueError: raise ValueError(f"Valor inválido para '{name}': '{entry.get()}'")

            # Nariz
            val_l_nariz=get_float(self.nose_length,"Longitud Nariz")
            val_d_nariz=get_float(self.nose_diameter,"Diámetro Nariz")
            val_m_nariz=get_float(self.nose_mass,"Masa Nariz")
            val_g_nariz=self.nose_geometry.get()
            # Fuselaje
            val_l_fus=get_float(self.body_length,"Longitud Fuselaje")
            val_d_ext_fus=get_float(self.body_diameter,"Diámetro Ext. Fuselaje")
            val_thick_fus=get_float(self.body_thickness,"Espesor Fuselaje")
            val_m_fus=get_float(self.body_mass,"Masa Fuselaje")
            val_d_int_fus = val_d_ext_fus - 2 * val_thick_fus # Calcular diámetro interno
            if val_d_int_fus <= 0: raise ValueError("Espesor de fuselaje inválido (diámetro interno <= 0).")
            # Aletas
            val_n_aletas=get_int(self.fin_count,"Número Aletas")
            val_s_aletas=get_float(self.fin_span,"Envergadura Aletas")
            val_cr_aletas=get_float(self.fin_root_chord,"Cuerda Raíz Aletas")
            val_ct_aletas=get_float(self.fin_tip_chord,"Cuerda Punta Aletas")
            val_sweep_aletas_deg=get_float(self.fin_sweep,"Barrido Medio Aletas")
            val_m_aletas=get_float(self.fin_mass,"Masa Aletas")
            # Boattail
            val_l_boat=get_float(self.boattail_length,"Longitud Boattail")
            val_df_boat=get_float(self.boattail_front_diameter,"Diámetro Frontal Boattail")
            val_dr_boat=get_float(self.boattail_rear_diameter,"Diámetro Trasero Boattail")
            val_m_boat=get_float(self.boattail_mass,"Masa Boattail")
            val_e_boat = val_thick_fus # Asumir mismo espesor que fuselaje para consistencia
            # Motor (Estructural)
            val_m_motor=get_float(self.motor_mass,"Masa Motor")
            val_l_motor=get_float(self.motor_length,"Longitud Motor")
            val_d_motor=get_float(self.motor_diameter,"Diámetro Motor")

            # --- Crear/Actualizar Componentes usando __init__ correctos ---
            # Posiciones se calculan secuencialmente
            nariz = Cono("Nariz", val_m_nariz, np.array([0.,0.,0.]),
                         longitud=val_l_nariz, diametro=val_d_nariz, geometria=val_g_nariz)
            pos_fus = np.array([0., 0., nariz.bottom[2]]) # Posición inicial del fuselaje

            fuselaje = Cilindro("Fuselaje", val_m_fus, pos_fus,
                                longitud=val_l_fus, diametroexterior=val_d_ext_fus, diametrointerior=val_d_int_fus)
            pos_boat = np.array([0., 0., fuselaje.bottom[2]]) # Posición inicial del boattail

            boattail = Boattail("Boattail", val_m_boat, pos_boat,
                                longitud=val_l_boat, diamF_boat=val_df_boat, diamR_boat=val_dr_boat, espesor=val_e_boat)
            # Posición aletas relativa al fuselaje (ej: al final, ajustado por cuerda raíz)
            pos_aletas = np.array([0., 0., fuselaje.bottom[2] - val_cr_aletas])

            aletas = Aletas("Aletas", val_m_aletas, pos_aletas,
                            diametro=val_d_ext_fus, # Diametro fuselaje donde se monta
                            numf=val_n_aletas, semispan=val_s_aletas,
                            C_r=val_cr_aletas, C_t=val_ct_aletas,
                            X_R=0.0, # Asumir 0 si no está en GUI
                            mid_sweep=np.deg2rad(val_sweep_aletas_deg))

            # Posición del motor (Ejemplo: centrado en su longitud, al final del fuselaje)
            pos_motor_z = pos_fus[2] + val_l_fus - val_l_motor / 2 # Centrado en su propia longitud
            pos_motor = np.array([0., 0., pos_motor_z])
            # Usar Componente base para el motor estructural de la GUI
            motor = Componente("Motor", val_m_motor, pos_motor)

            # --- WORKAROUND: Establecer explícitamente CG y CP para el componente Motor base ---
            # Asume que el CG del motor estructural está en su centro geométrico
            motor.CG = np.array([0.0, 0.0, val_l_motor / 2.0])
            # Asume que el CP del motor estructural es 0 (o en su origen relativo) y su CN es 0
            motor.CP = np.zeros(3) # Evita NoneType
            motor.CN = 0           # Evita posible división por cero o error si se usa
            # --- Fin WORKAROUND ---


            # Diccionario de componentes para actualizar el objeto Cohete
            componentes_actualizados_gui = {'Nariz': nariz, 'Fuselaje': fuselaje, 'Aletas': aletas, 'Boattail': boattail, 'Motor': motor}

            # --- Actualizar el Objeto Cohete ---
            if self.rocket is None:
                # Si no había cohete, crea uno nuevo usando las rutas cargadas (o None)
                print("Creando nuevo objeto Cohete desde GUI...")
                self.rocket = Cohete("Cohete GUI", "desconocido",
                                     componentes_actualizados_gui, componentes_actualizados_gui,
                                     self.loaded_cd_path, self.loaded_thrust_path, self.loaded_mass_path, riel)
            else:
                # Actualiza el cohete existente
                print("Actualizando objeto Cohete existente desde GUI...")
                self.rocket.componentes = componentes_actualizados_gui
                self.rocket.componentes_externos = componentes_actualizados_gui # Asume mismos para aero
                # Actualizar rutas y recargar tablas si es necesario (o si cambiaron)
                # CORRECCIÓN: Asignar rutas a atributos temporales si Cohete no los guarda
                #             y llamar a los métodos de carga explícitamente.
                temp_cd_path = self.loaded_cd_path
                temp_thrust_path = self.loaded_thrust_path
                temp_mass_path = self.loaded_mass_path
                try:
                    if temp_cd_path and hasattr(self.rocket, 'cargar_tabla_Cd'):
                         self.rocket.cargar_tabla_Cd(temp_cd_path)
                    if temp_thrust_path and temp_mass_path and hasattr(self.rocket, 'cargar_tablas_motor'):
                         self.rocket.cargar_tablas_motor(temp_thrust_path, temp_mass_path)
                except Exception as e:
                     print(f"Advertencia: Error al recargar tablas CSV en Cohete: {e}")


            # Actualiza propiedades clave del cohete
            self.rocket.d_ext = val_d_ext_fus # Diámetro de referencia
            self.rocket.calcular_propiedades() # Recalcular CG, CP, Masa, etc.

            messagebox.showinfo("Éxito", "Cohete actualizado desde la GUI.")
            print(f"Cohete actualizado. CG: {self.rocket.CG[2]:.3f} m, CP: {self.rocket.CP[2]:.3f} m (estático)")

        except (ValueError, AssertionError) as e: messagebox.showerror("Error Validación", str(e))
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
                     # CORRECCION: Usar los nombres de atributo correctos de cohete.py
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
                      # CORRECCION: Usar los nombres de atributo correctos de cohete.py
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
                           # CORRECCION: Usar los nombres de atributo correctos de cohete.py
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


    # --- Tab: Simulation Parameters (Sin cambios) ---
    def create_input_tab(self):
        self.input_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.input_frame, text="Parámetros de Simulación")
        col1_frame = ttk.Frame(self.input_frame); col1_frame.grid(row=0, column=0, padx=10, pady=5, sticky="nw")
        col2_frame = ttk.Frame(self.input_frame); col2_frame.grid(row=0, column=1, padx=10, pady=5, sticky="nw")
        col3_frame = ttk.Frame(self.input_frame); col3_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        self.create_section(col1_frame, "Sitio de Lanzamiento:", 0, 0)
        self.latitud = self.create_entry(col1_frame, 1, 0, "Latitud (°):", getattr(riel, 'latitud', latitud_cord))
        self.longitud = self.create_entry(col1_frame, 2, 0, "Longitud (°):", getattr(riel, 'longitud', longitud_cord))
        self.altitud = self.create_entry(col1_frame, 3, 0, "Altitud (m):", getattr(riel, 'altitud', altitud_cord))
        self.fecha = self.create_entry(col1_frame, 4, 0, "Fecha (YYYY-MM-DD):", fecha.strftime('%Y-%m-%d') if isinstance(fecha, datetime) else fecha)
        self.create_section(col1_frame, "Riel de Lanzamiento:", 5, 0)
        self.longitud_riel = self.create_entry(col1_frame, 6, 0, "Longitud (m):", getattr(riel, 'longitud', 5.0))
        self.angulo_riel = self.create_entry(col1_frame, 7, 0, "Ángulo Elevación (°):", np.rad2deg(getattr(riel, 'angulo', np.deg2rad(85))))
        self.create_section(col2_frame, "Viento (Modelo Simple):", 0, 0)
        self.vel_base_viento = self.create_entry(col2_frame, 1, 0, "Velocidad Base (m/s):", getattr(viento_actual, 'vel_base', 0))
        self.vel_mean_viento = self.create_entry(col2_frame, 2, 0, "Velocidad Media (m/s):", getattr(viento_actual, 'vel_mean', 5))
        self.vel_var_viento = self.create_entry(col2_frame, 3, 0, "Variación Velocidad:", getattr(viento_actual, 'vel_var', 2))
        self.var_ang_viento = self.create_entry(col2_frame, 4, 0, "Variación Ángulo (°):", getattr(viento_actual, 'var_ang', 10))
        self.create_section(col2_frame, "Simulación:", 5, 0)
        self.t_max = self.create_entry(col2_frame, 6, 0, "Tiempo Máximo (s):", 800)
        self.dt = self.create_entry(col2_frame, 7, 0, "Paso de Tiempo (s):", 0.01)
        integrator_options = []; default_integrator = ""
        if CUSTOM_INTEGRATORS_AVAILABLE: integrator_options.extend(['Euler', 'RungeKutta4']); default_integrator = 'RungeKutta4'
        if SCIPY_AVAILABLE: scipy_methods = ['RK45', 'RK23', 'DOP853', 'Radau', 'BDF', 'LSODA']; integrator_options.extend(scipy_methods);
        if not default_integrator and SCIPY_AVAILABLE: default_integrator = 'RK45'
        if not integrator_options: integrator_options = ["N/A"]; default_integrator = "N/A"
        self.integrator_method_combo = self.create_combobox(col2_frame, 8, 0, "Método Integración:", integrator_options, default_integrator, textvariable=self.selected_integrator)
        if not SCIPY_AVAILABLE and not CUSTOM_INTEGRATORS_AVAILABLE: self.integrator_method_combo.config(state=tk.DISABLED)
        self.btn_simular = ttk.Button(col3_frame, text="Iniciar Simulación", command=self.run_simulation); self.btn_simular.pack(side=tk.LEFT, padx=5, pady=10)
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

    # --- Simulation Logic (Ajustado para verificar rutas y tablas CSV y corregir print) ---
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

    # --- Save/Load Configuration Data (Refactored Validation) ---
    def save_tab_data(self, tab_name):
        """Saves configuration data from Rocket or Input tab to JSON."""
        data = {}
        if tab_name == "rocket":
            try:
                # Collect data from rocket tab widgets
                data = {
                    "version": 1.1, "description": "Definición cohete",
                    "nose_length": self.nose_length.get(),"nose_diameter": self.nose_diameter.get(),"nose_mass": self.nose_mass.get(),"nose_geometry": self.nose_geometry.get(),
                    "body_length": self.body_length.get(),"body_diameter": self.body_diameter.get(),"body_thickness": self.body_thickness.get(),"body_mass": self.body_mass.get(),
                    "fin_count": self.fin_count.get(),"fin_span": self.fin_span.get(),"fin_root_chord": self.fin_root_chord.get(),"fin_tip_chord": self.fin_tip_chord.get(),"fin_sweep": self.fin_sweep.get(),"fin_mass": self.fin_mass.get(),
                    "boattail_length": self.boattail_length.get(),"boattail_front_diameter": self.boattail_front_diameter.get(),"boattail_rear_diameter": self.boattail_rear_diameter.get(),"boattail_mass": self.boattail_mass.get(),
                    "motor_mass": self.motor_mass.get(),"motor_length": self.motor_length.get(),"motor_diameter": self.motor_diameter.get()
                }

                # --- Refactored Validation ---
                required_numeric = ["nose_length", "nose_diameter", "nose_mass",
                                   "body_length", "body_diameter", "body_thickness", "body_mass",
                                   "fin_count", "fin_span", "fin_root_chord", "fin_tip_chord", "fin_sweep", "fin_mass",
                                   "boattail_length", "boattail_front_diameter", "boattail_rear_diameter", "boattail_mass",
                                   "motor_mass", "motor_length", "motor_diameter"]

                for key in required_numeric:
                    value_str = data.get(key) # Get value safely
                    if not value_str:
                        raise ValueError(f"Campo '{key}' está vacío.")
                    try:
                        if 'count' in key:
                            int(value_str) # Try int conversion
                        else:
                            float(value_str) # Try float conversion
                    except ValueError:
                        # Raise a more specific error if conversion fails
                        raise ValueError(f"Valor inválido para '{key}': '{value_str}' no es un número válido.")

                # Check nose_geometry separately
                if not data.get("nose_geometry"):
                    raise ValueError("Campo 'nose_geometry' está vacío.")
                # --- End of Refactored Validation ---

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
                # Map JSON keys to GUI widgets
                mapping = { "nose_length": self.nose_length, "nose_diameter": self.nose_diameter, "nose_mass": self.nose_mass, "nose_geometry": self.nose_geometry, "body_length": self.body_length, "body_diameter": self.body_diameter, "body_thickness": self.body_thickness, "body_mass": self.body_mass, "fin_count": self.fin_count, "fin_span": self.fin_span, "fin_root_chord": self.fin_root_chord, "fin_tip_chord": self.fin_tip_chord, "fin_sweep": self.fin_sweep, "fin_mass": self.fin_mass, "boattail_length": self.boattail_length, "boattail_front_diameter": self.boattail_front_diameter, "boattail_rear_diameter": self.boattail_rear_diameter, "boattail_mass": self.boattail_mass, "motor_mass": self.motor_mass, "motor_length": self.motor_length, "motor_diameter": self.motor_diameter }
                # Populate widgets
                for key, widget in mapping.items():
                    if key in data: value = str(data[key]);
                    if isinstance(widget, ttk.Entry): widget.delete(0, tk.END); widget.insert(0, value)
                    elif isinstance(widget, ttk.Combobox):
                        if value in widget['values']: widget.set(value)
                        else: print(f"Advertencia: Valor '{value}' para '{key}' no es opción válida."); widget.set(widget['values'][0])
                    else: print(f"Advertencia: Clave '{key}' no encontrada en JSON.")
                self.update_rocket_from_gui()
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
