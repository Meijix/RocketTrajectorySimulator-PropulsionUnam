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

# Agregar la ruta del directorio que contiene los paquetes al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Import necessary modules
from Simulador.src.condiciones_init import *
from Paquetes.PaqueteFisica.vuelo import *
from Paquetes.PaqueteFisica.viento import Viento
from Paquetes.PaqueteFisica.riel import Torrelanzamiento
from Paquetes.PaqueteFisica.atmosfera import atmosfera
from Paquetes.PaqueteFisica.componentes import Componente, Cono, Cilindro, Aletas, Boattail
from Paquetes.PaqueteFisica.cohete import Cohete

class SimuladorCohetesAvanzado:
    def __init__(self, master):
        azul = '#052c53'
        azul = '#022D36'#peacock
        azul = '#151E3D'#denim
        #azul = '#112B4B'#denim
        rojo = '#90091d'
        #teal = '#48AAAD'
        font_selection = ('Lucida Sans Unicode', 10)
        self.master = master
        self.master.title("Simulador de Cohetes Suborbitales Avanzado")
        self.master.geometry("1200x800")
        self.master.configure(bg=azul)  # Azul marino oscuro

        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TButton', font = font_selection, background= rojo, foreground='white')
        self.style.configure('TLabel', font = font_selection, background=azul, foreground='white')
        self.style.configure('TEntry', font = font_selection)
        self.style.configure('TNotebook', background=azul)
        self.style.configure('TNotebook.Tab', background=azul, foreground='white')
        self.style.map('TNotebook.Tab', background=[('selected', azul)], foreground=[('selected', 'white')])
        self.style.configure('TFrame', background=azul)

        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)
        
        self.rocket = None
        diam_ext=0.152
        espesor=0.03
        nariz = Cono("Nariz", 0.8 , np.array([0.0, 0.0, 0.0]), 0.81, diam_ext, "ogiva")
        fuselaje = Cilindro("Coples",1.5, np.array([0.0,0.0, nariz.bottom[2]]),0.176, diam_ext, diam_ext-espesor)
        aletas= Aletas("Aletas", 1.1, np.array([0.0, 0.0, fuselaje.bottom[2]]), diam_ext, 4, 0.11, 0.3, 0.1, 0.2, 25)
        boattail = Boattail("Boattail", 0.251, np.array([0.0, 0.0, fuselaje.bottom[2]]), 0.12, diam_ext, 0.132, espesor)
        self.lista_componentes = {'Nariz': nariz ,'Fuselaje': fuselaje, 'Aletas': aletas, 'Boattail': boattail}
        
        self.create_rocket_tab()
        self.create_csv_import_tab()
        self.create_input_tab()
        self.create_trajectory_tab()
        self.create_position_tab()
        self.create_forces_tab()
        self.create_angles_tab()
        self.create_stability_tab()
        self.create_wind_tab()
        self.create_summary_tab()

        self.simulation_done = False

    def create_rocket_tab(self):
        rocket_frame = ttk.Frame(self.notebook)
        self.notebook.add(rocket_frame, text="Cohete")

        # Nose Cone
        self.create_section(rocket_frame, "Nariz (Cono):", 0, 0)
        self.nose_length = self.create_entry(rocket_frame, 1, 0, "Longitud (m):", self.lista_componentes['Nariz'].long)
        self.nose_diameter = self.create_entry(rocket_frame, 2, 0, "Diámetro (m):", self.lista_componentes['Nariz'].diam)
        self.nose_mass = self.create_entry(rocket_frame, 3, 0, "Masa (kg):", self.lista_componentes['Nariz'].masa)
        self.nose_geometry = self.create_combobox(rocket_frame, 4, 0, "Geometría:", ["conica", "ogiva", "parabolica", "eliptica"], self.lista_componentes['Nariz'].geom)

        # Body
        self.create_section(rocket_frame, "Fuselaje:", 0, 2)
        self.body_length = self.create_entry(rocket_frame, 1, 2, "Longitud (m):", self.lista_componentes['Fuselaje'].long)
        self.body_diameter = self.create_entry(rocket_frame, 2, 2, "Diámetro exterior (m):", self.lista_componentes['Fuselaje'].diam_ext)
        self.body_thickness = self.create_entry(rocket_frame, 3, 2, "Espesor (m):", (self.lista_componentes['Fuselaje'].diam_ext - self.lista_componentes['Fuselaje'].diam_int) / 2)
        self.body_mass = self.create_entry(rocket_frame, 4, 2, "Masa (kg):", self.lista_componentes['Fuselaje'].masa)

        # Fins
        self.create_section(rocket_frame, "Aletas:", 0, 4)
        self.fin_count = self.create_entry(rocket_frame, 1, 4, "Número de aletas:", self.lista_componentes['Aletas'].numf)
        self.fin_span = self.create_entry(rocket_frame, 2, 4, "Envergadura (m):", self.lista_componentes['Aletas'].semispan)
        self.fin_root_chord = self.create_entry(rocket_frame, 3, 4, "Cuerda raíz (m):", self.lista_componentes['Aletas'].C_r)
        self.fin_tip_chord = self.create_entry(rocket_frame, 4, 4, "Cuerda punta (m):", self.lista_componentes['Aletas'].C_t)
        self.fin_sweep = self.create_entry(rocket_frame, 5, 4, "Ángulo de barrido (grados):", np.degrees(self.lista_componentes['Aletas'].mid_sweep))
        self.fin_mass = self.create_entry(rocket_frame, 6, 4, "Masa total de aletas (kg):", self.lista_componentes['Aletas'].masa)

        # Boattail
        self.create_section(rocket_frame, "Boattail:", 7, 0)
        self.boattail_length = self.create_entry(rocket_frame, 8, 0, "Longitud (m):", self.lista_componentes['Boattail'].long)
        self.boattail_front_diameter = self.create_entry(rocket_frame, 9, 0, "Diámetro frontal (m):", self.lista_componentes['Boattail'].dF)
        self.boattail_rear_diameter = self.create_entry(rocket_frame, 10, 0, "Diámetro trasero (m):", self.lista_componentes['Boattail'].dR)
        self.boattail_mass = self.create_entry(rocket_frame, 11, 0, "Masa (kg):", self.lista_componentes['Boattail'].masa)

        # Create Rocket button
        self.btn_create_rocket = ttk.Button(rocket_frame, text="Actualizar Cohete", command=self.create_rocket)
        self.btn_create_rocket.grid(row=12, column=0, columnspan=6, pady=20)

        # Save Data button
        self.btn_save_rocket = ttk.Button(rocket_frame, text="Guardar Datos", command=lambda: self.save_tab_data("rocket"))
        self.btn_save_rocket.grid(row=12, column=4, columnspan=2, pady=20)

    def create_rocket(self):
        try:
        # Tablas de Cd, empuje y masa
            self.thrust_curve = r'C:\Users\Natalia\OneDrive\Tesis\GithubCode\SimuladorVueloNat\3DOF-Rocket-PU\Archivos\MegaPunisherBien.csv'
            self.cd_vs_mach = r'C:\Users\Natalia\OneDrive\Tesis\GithubCode\SimuladorVueloNat\3DOF-Rocket-PU\Archivos\cdmachXitle.csv'
            self.mass_vs_time = r'C:\Users\Natalia\OneDrive\Tesis\GithubCode\SimuladorVueloNat\3DOF-Rocket-PU\Archivos\MegaPunisherFatMasadot.csv'
        

            nariz = Cono("Nariz", float(self.nose_mass.get()), 0.0, float(self.nose_length.get()), float(self.nose_diameter.get()), self.nose_geometry.get())
            
            fuselaje = Cilindro("Fuselaje", float(self.body_mass.get()), float(self.nose_length.get()), float(self.body_length.get()), float(self.body_diameter.get()), float(self.body_diameter.get()) - 2*float(self.body_thickness.get()))
            
            aletas = Aletas("Aletas", float(self.fin_mass.get()), float(self.nose_length.get()) + float(self.body_length.get()) - float(self.fin_root_chord.get()),float(self.body_diameter.get()), int(self.fin_count.get()), float(self.fin_span.get()),float(self.fin_root_chord.get()), float(self.fin_tip_chord.get()), 0.0, np.deg2rad(float(self.fin_sweep.get())))
            
            boattail = Boattail("Boattail", float(self.boattail_mass.get()), float(self.nose_length.get()) + float(self.body_length.get()),
                                float(self.boattail_length.get()), float(self.boattail_front_diameter.get()),
                                float(self.boattail_rear_diameter.get()), float(self.body_thickness.get()))
            # Create rocket components
            self.componentes_de_cohete = {'Nariz': nariz ,'Fuselaje': fuselaje, 'Aletas': aletas, 'Boattail': boattail}
            self.rocket = Cohete("Xitle", "hibrido", self.componentes_de_cohete, self.componentes_de_cohete, self.cd_vs_mach, self.thrust_curve, self.mass_vs_time, riel)
        
    
        ####################################################
            # Update rocket properties
            self.rocket.d_ext = float(self.body_diameter.get())
            self.rocket.calcular_propiedades()

            messagebox.showinfo("Éxito", "Cohete actualizado exitosamente")
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar el cohete: {str(e)}")

    def create_section(self, parent, text, row, column):
        ttk.Label(parent, text=text, font=('Fontana', 12, 'bold')).grid(row=row, column=column, columnspan=2, sticky="w", padx=5, pady=10)

    def create_entry(self, parent, row, column, label, default_value):
        ttk.Label(parent, text=label).grid(row=row, column=column, sticky="w", padx=5, pady=5)
        entry = ttk.Entry(parent)
        entry.grid(row=row, column=column+1, padx=5, pady=5, sticky="ew")
        entry.insert(0, str(default_value))
        return entry

    def create_combobox(self, parent, row, column, label, values, default_value):
        ttk.Label(parent, text=label).grid(row=row, column=column, sticky="w", padx=5, pady=5)
        combobox = ttk.Combobox(parent, values=values)
        combobox.grid(row=row, column=column+1, padx=5, pady=5, sticky="ew")
        combobox.set(default_value)
        return combobox
###############################################################################################################
###############################################################################################################
    def create_input_tab(self):
        input_frame = ttk.Frame(self.notebook)
        self.notebook.add(input_frame, text="Parámetros de Simulación")

        # Launch site parameters
        self.create_section(input_frame, "Parámetros del sitio de lanzamiento", 0, 0)
        self.latitud = self.create_entry(input_frame, 1, 0, "Latitud:", latitud_cord)
        self.longitud = self.create_entry(input_frame, 2, 0, "Longitud:", longitud_cord)
        self.altitud = self.create_entry(input_frame, 3, 0, "Altitud (m):", altitud_cord)
        self.fecha = self.create_entry(input_frame, 4, 0, "Fecha (YYYY-MM-DD):", fecha)

        # Launch rail parameters
        self.create_section(input_frame, "Parámetros del riel de lanzamiento", 0, 2)
        self.longitud_riel = self.create_entry(input_frame, 1, 2, "Longitud del riel (m):", riel.longitud)
        self.angulo_riel = self.create_entry(input_frame, 2, 2, "Ángulo del riel (grados):", np.rad2deg(riel.angulo))

        # Wind parameters
        self.create_section(input_frame, "Parámetros del viento", 5, 0)
        self.vel_base_viento = self.create_entry(input_frame, 6, 0, "Velocidad base (m/s):", viento_actual.vel_base)
        self.vel_mean_viento = self.create_entry(input_frame, 7, 0, "Velocidad media (m/s):", viento_actual.vel_mean)
        self.vel_var_viento = self.create_entry(input_frame, 8, 0, "Variación de velocidad:", viento_actual.vel_var)
        self.var_ang_viento = self.create_entry(input_frame, 9, 0, "Variación de ángulo (grados):", viento_actual.var_ang)

        # Simulation parameters
        self.create_section(input_frame, "Parámetros de simulación", 5, 2)
        self.t_max = self.create_entry(input_frame, 6, 2, "Tiempo máximo (s):", 800)
        self.dt = self.create_entry(input_frame, 7, 2, "Paso de tiempo (s):", 0.01)

        self.btn_simular = ttk.Button(input_frame, text="Simular", command=self.simular)
        self.btn_simular.grid(row=10, column=0, columnspan=4, pady=20)

        # Save Data button
        self.btn_save_input = ttk.Button(input_frame, text="Guardar Datos", command=lambda: self.save_tab_data("input"))
        self.btn_save_input.grid(row=10, column=2, columnspan=2, pady=20)

        # Progress bar
        self.progress = ttk.Progressbar(input_frame, orient="horizontal", length=200, mode="indeterminate")
        self.progress.grid(row=11, column=0, columnspan=4, pady=10)

        self.progress_label = ttk.Label(input_frame, text="")
        self.progress_label.grid(row=12, column=0, columnspan=4)
######################################################################################################
######################################################################################################
    def create_csv_import_tab(self):
        self.csv_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.csv_frame, text="Importar CSV")

        self.thrust_button = ttk.Button(self.csv_frame, text="Importar Curva de Empuje", command=lambda: self.import_csv_data("thrust"))
        self.thrust_button.pack(pady=10)

        self.thrust_plot_button = ttk.Button(self.csv_frame, text="Graficar Curva de Empuje", command=self.plot_thrust_csv, state="disabled")
        self.thrust_plot_button.pack(pady=10)

        self.cd_button = ttk.Button(self.csv_frame, text="Importar Cd vs Mach", command=lambda: self.import_csv_data("cd_vs_mach"))
        self.cd_button.pack(pady=10)

        self.cd_plot_button = ttk.Button(self.csv_frame, text="Graficar Cd vs Mach", command=self.plot_cd_csv, state="disabled")
        self.cd_plot_button.pack(pady=10)

        self.mass_button = ttk.Button(self.csv_frame, text="Importar Masa vs Tiempo", command=lambda: self.import_csv_data("mass_vs_time"))
        self.mass_button.pack(pady=10)

        self.mass_plot_button = ttk.Button(self.csv_frame, text="Graficar Masa vs Tiempo", command=self.plot_mass_csv, state="disabled")
        self.mass_plot_button.pack(pady=10)

        self.thrust_plot_frame = ttk.Frame(self.csv_frame)
        self.thrust_plot_frame.pack(fill=tk.BOTH, expand=True)

        self.cd_plot_frame = ttk.Frame(self.csv_frame)
        self.cd_plot_frame.pack(fill=tk.BOTH, expand=True)

        self.mass_plot_frame = ttk.Frame(self.csv_frame)
        self.mass_plot_frame.pack(fill=tk.BOTH, expand=True)

    def import_csv_data(self, data_type):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            df = pd.read_csv(file_path)
            if data_type == "thrust":
                self.rocket.curva_empuje = df
                self.thrust_plot_button.config(state="normal")
                messagebox.showinfo("Éxito", "Curva de empuje importada correctamente")
            elif data_type == "cd_vs_mach":
                self.rocket.cd_vs_mach = df
                self.cd_plot_button.config(state="normal")
                messagebox.showinfo("Éxito", "Cd vs Mach importado correctamente")
            elif data_type == "mass_vs_time":
                self.rocket.masa_vs_tiempo = df
                self.mass_plot_button.config(state="normal")
                messagebox.showinfo("Éxito", "Masa vs Tiempo importada correctamente")

    def plot_thrust_csv(self):
        for widget in self.thrust_plot_frame.winfo_children():
            widget.destroy()

        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(self.rocket.curva_empuje.iloc[:, 0], self.rocket.curva_empuje.iloc[:, 1])
        ax.set_xlabel('Tiempo (s)')
        ax.set_ylabel('Empuje (N)')
        ax.set_title('Curva de Empuje')

        canvas = FigureCanvasTkAgg(fig, master=self.thrust_plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def plot_cd_csv(self):
        for widget in self.cd_plot_frame.winfo_children():
            widget.destroy()

        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(self.rocket.cd_vs_mach.iloc[:, 0], self.rocket.cd_vs_mach.iloc[:, 1])
        ax.set_xlabel('Mach')
        ax.set_ylabel('Cd')
        ax.set_title('Cd vs Mach')

        canvas = FigureCanvasTkAgg(fig, master=self.cd_plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def plot_mass_csv(self):
        for widget in self.mass_plot_frame.winfo_children():
            widget.destroy()

        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(self.rocket.masa_vs_tiempo.iloc[:, 0], self.rocket.masa_vs_tiempo.iloc[:, 1])
        ax.set_xlabel('Tiempo (s)')
        ax.set_ylabel('Masa (kg)')
        ax.set_title('Masa vs Tiempo')

        canvas = FigureCanvasTkAgg(fig, master=self.mass_plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def save_csv_data(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if file_path:
            if self.rocket.curva_empuje is not None:
                self.rocket.curva_empuje.to_csv(file_path, index=False)
                messagebox.showinfo("Éxito", "Curva de empuje guardada correctamente")
            elif self.rocket.cd_vs_mach is not None:
                self.rocket.cd_vs_mach.to_csv(file_path, index=False)
                messagebox.showinfo("Éxito", "Cd vs Mach guardado correctamente")
            elif self.rocket.masa_vs_tiempo is not None:
                self.rocket.masa_vs_tiempo.to_csv(file_path, index=False)
                messagebox.showinfo("Éxito", "Masa vs Tiempo guardada correctamente")
            else:
                messagebox.showerror("Error", "No hay datos para guardar")
############################################################################################
############################################################################################
    def create_trajectory_tab(self):
        self.trajectory_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.trajectory_frame, text="Trayectoria 3D")
        self.show_no_simulation_message(self.trajectory_frame)

    def create_position_tab(self):
        self.position_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.position_frame, text="Posición y Velocidad")
        self.show_no_simulation_message(self.position_frame)

    def create_forces_tab(self):
        self.forces_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.forces_frame, text="Fuerzas")
        self.show_no_simulation_message(self.forces_frame)

    def create_angles_tab(self):
        self.angles_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.angles_frame, text="Ángulos")
        self.show_no_simulation_message(self.angles_frame)

    def create_stability_tab(self):
        self.stability_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.stability_frame, text="Estabilidad")
        self.show_no_simulation_message(self.stability_frame)

    def create_wind_tab(self):
        self.wind_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.wind_frame, text="Viento")
        self.show_no_simulation_message(self.wind_frame)

    def create_summary_tab(self):
        self.summary_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.summary_frame, text="Resumen")
        self.show_no_simulation_message(self.summary_frame)

    def show_no_simulation_message(self, frame):
        label = ttk.Label(frame, text="Aún no se ha realizado simulación", font=('Arial', 14))
        label.pack(expand=True)
##########################################################################
##########################################################################
    def simular(self):
        if self.rocket.curva_empuje is None:
            messagebox.showerror("Error", "Por favor, importe la curva de empuje antes de simular.")
            return

        if self.rocket.cd_vs_mach is None:
            messagebox.showerror("Error", "Por favor, importe la tabla de Cd vs Mach antes de simular.")
            return

        try:
            # Start progress bar
            self.progress.start()
            self.progress_label.config(text="Simulando...")
            self.master.update()

            # Update launch site parameters
            latitud_cord = float(self.latitud.get())
            longitud_cord = float(self.longitud.get())
            altitud_cord = float(self.altitud.get())
            fecha = self.fecha.get()

            # Update launch rail parameters
            riel.longitud = float(self.longitud_riel.get())
            riel.angulo = np.deg2rad(float(self.angulo_riel.get()))

            # Update wind parameters
            viento_actual.vel_base = float(self.vel_base_viento.get())
            viento_actual.vel_mean = float(self.vel_mean_viento.get())
            viento_actual.vel_var = float(self.vel_var_viento.get())
            viento_actual.var_ang = float(self.var_ang_viento.get())

            # Update simulation parameters
            t_max = float(self.t_max.get())
            dt = float(self.dt.get())

            # Simulation
            inicio = time.time()
            print("Simulando...")

            viento_actual.actualizar_viento3D()
            print("Viento actual", viento_actual.vector)

            vuelo1 = Vuelo(self.rocket, atmosfera_actual, viento_actual)
            tiempos, sim, CPs, CGs, masavuelo, viento_vuelo_mags, viento_vuelo_dirs, viento_vuelo_vecs, Tvecs, Dvecs, Nvecs, accels, palancas, accangs, Gammas, Alphas, torcas, Cds, Machs = vuelo1.simular_vuelo(np.array([0, 0, 0, 0, 0, 0, riel.angulo, 0]), t_max, dt, dt)

            fin = time.time()
            print(f"Tiempo de ejecución: {fin-inicio:.1f}s")

            # Process data
            posiciones = np.array([state[0:3] for state in sim])
            velocidades = np.array([state[3:6] for state in sim])
            thetas = np.array([state[6] for state in sim])
            omegas = np.array([state[7] for state in sim])

            Tmags = np.array([np.linalg.norm(Tvec) for Tvec in Tvecs])
            Dmags = np.array([np.linalg.norm(Dvec) for Dvec in Dvecs])
            Nmags = np.array([np.linalg.norm(Nvec) for Nvec in Nvecs])

            Txs, Tys, Tzs = zip(*Tvecs)
            Dxs, Dys, Dzs = zip(*Dvecs)
            Nxs, Nys, Nzs = zip(*Nvecs)

            wind_xs = [vec[0] for vec in viento_vuelo_vecs]
            wind_ys = [vec[1] for vec in viento_vuelo_vecs]
            wind_zs = [vec[2] for vec in viento_vuelo_vecs]

            stability = [(CP - CG) / self.rocket.d_ext for CP, CG in zip(CPs, CGs)]

            max_altitude = max(posiciones[:, 2])
            max_speed = max(np.linalg.norm(velocidades, axis=1))

            # Update graphs
            self.plot_trajectory(tiempos, posiciones)
            self.plot_position_velocity(tiempos, posiciones, velocidades)
            self.plot_forces(tiempos, Tmags, Dmags, Nmags)
            self.plot_angles(tiempos, thetas, Gammas, Alphas)
            self.plot_stability(tiempos, CPs, CGs, stability)
            self.plot_wind(tiempos, viento_vuelo_mags, viento_vuelo_dirs)
            self.update_summary(vuelo1, max_altitude, max_speed, np.max(accels), np.max(accangs))

            # Save data
            self.save_data(tiempos, posiciones, velocidades, thetas, omegas, CPs, CGs, masavuelo,viento_vuelo_mags, viento_vuelo_dirs, viento_vuelo_vecs, Tmags, Dmags, Nmags,Txs, Tys, Tzs, Dxs, Dys, Dzs, Nxs, Nys, Nzs, accels, palancas, accangs, Gammas, Alphas, torcas, Cds, Machs, stability)

            # Stop progress bar
            self.progress.stop()
            self.progress_label.config(text="Simulación completada")
            self.simulation_done = True

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during simulation: {str(e)}")
            self.progress.stop()
            self.progress_label.config(text="Error en la simulación")

    def plot_trajectory(self, tiempos, posiciones):
        for widget in self.trajectory_frame.winfo_children():
            widget.destroy()

        fig = plt.figure(figsize=(8, 6))
        ax = fig.add_subplot(111, projection='3d')
        ax.plot(posiciones[:, 0], posiciones[:, 1], posiciones[:, 2])
        ax.set_xlabel('X (m)')
        ax.set_ylabel('Y (m)')
        ax.set_zlabel('Altitud (m)')
        ax.set_title('Trayectoria 3D del Cohete')

        canvas = FigureCanvasTkAgg(fig, master=self.trajectory_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def plot_position_velocity(self, tiempos, posiciones, velocidades):
        for widget in self.position_frame.winfo_children():
            widget.destroy()

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 8))

        ax1.plot(tiempos, posiciones[:, 2])
        ax1.set_xlabel('Tiempo (s)')
        ax1.set_ylabel('Altitud (m)')
        ax1.set_title('Altitud vs Tiempo')

        velocidades_mag = np.linalg.norm(velocidades, axis=1)
        ax2.plot(tiempos, velocidades_mag)
        ax2.set_xlabel('Tiempo (s)')
        ax2.set_ylabel('Velocidad (m/s)')
        ax2.set_title('Velocidad vs Tiempo')

        canvas = FigureCanvasTkAgg(fig, master=self.position_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def plot_forces(self, tiempos, Tmags, Dmags, Nmags):
        for widget in self.forces_frame.winfo_children():
            widget.destroy()

        fig, ax = plt.subplots(figsize=(8, 6))
        ax.plot(tiempos, Tmags, label='Empuje')
        ax.plot(tiempos, Dmags, label='Arrastre')
        ax.plot(tiempos, Nmags, label='Normal')
        ax.set_xlabel('Tiempo (s)')
        ax.set_ylabel('Fuerza (N)')
        ax.set_title('Fuerzas vs Tiempo')
        ax.legend()

        canvas = FigureCanvasTkAgg(fig, master=self.forces_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def plot_angles(self, tiempos, thetas, Gammas, Alphas):
        for widget in self.angles_frame.winfo_children():
            widget.destroy()

        fig, ax = plt.subplots(figsize=(8, 6))
        ax.plot(tiempos, np.rad2deg(thetas), label='Theta')
        ax.plot(tiempos, np.rad2deg(Gammas), label='Gamma')
        ax.plot(tiempos, np.rad2deg(Alphas), label='Alpha')
        ax.set_xlabel('Tiempo (s)')
        ax.set_ylabel('Ángulo (grados)')
        ax.set_title('Ángulos vs Tiempo')
        ax.legend()

        canvas = FigureCanvasTkAgg(fig, master=self.angles_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def plot_stability(self, tiempos, CPs, CGs, stability):
        for widget in self.stability_frame.winfo_children():
            widget.destroy()

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 8))

        ax1.plot(tiempos, CPs, label='CP')
        ax1.plot(tiempos, CGs, label='CG')
        ax1.set_xlabel('Tiempo (s)')
        ax1.set_ylabel('Posición (m)')
        ax1.set_title('Centro de Presión y Centro de Gravedad vs Tiempo')
        ax1.legend()

        ax2.plot(tiempos, stability)
        ax2.set_xlabel('Tiempo (s)')
        ax2.set_ylabel('Estabilidad (calibres)')
        ax2.set_title('Estabilidad vs Tiempo')

        canvas = FigureCanvasTkAgg(fig, master=self.stability_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def plot_wind(self, tiempos, viento_vuelo_mags, viento_vuelo_dirs):
        for widget in self.wind_frame.winfo_children():
            widget.destroy()

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 8))

        ax1.plot(tiempos, viento_vuelo_mags)
        ax1.set_xlabel('Tiempo (s)')
        ax1.set_ylabel('Velocidad del viento (m/s)')
        ax1.set_title('Magnitud del viento vs Tiempo')

        ax2.plot(tiempos, np.rad2deg(viento_vuelo_dirs))
        ax2.set_xlabel('Tiempo (s)')
        ax2.set_ylabel('Dirección del viento (grados)')
        ax2.set_title('Dirección del viento vs Tiempo')

        canvas = FigureCanvasTkAgg(fig, master=self.wind_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def update_summary(self, vuelo, max_altitude, max_speed, max_accel_linear, max_accel_angular):
        for widget in self.summary_frame.winfo_children():
            widget.destroy()

        summary_text = f"""
        Resumen de la simulación:

        Diámetro externo del cohete: {self.rocket.d_ext:.2f} m
        Tiempo de MECO: {self.rocket.t_MECO:.2f} s
        Tiempo de salida del riel: {vuelo.tiempo_salida_riel:.2f} s
        Tiempo de apogeo: {vuelo.tiempo_apogeo:.2f} s
        Tiempo de impacto: {vuelo.tiempo_impacto:.2f} s
        Altitud máxima: {max_altitude:.2f} m
        Velocidad máxima: {max_speed:.2f} m/s ({max_speed/340:.2f} Mach)
        Aceleración lineal máxima: {max_accel_linear:.2f} m/s²
        Aceleración angular máxima: {max_accel_angular:.2f} rad/s²
        """

        summary_label = ttk.Label(self.summary_frame, text=summary_text, justify=tk.LEFT)
        summary_label.pack(padx=10, pady=10)

    def save_data(self, tiempos, posiciones, velocidades, thetas, omegas, CPs, CGs, masavuelo,
                viento_vuelo_mags, viento_vuelo_dirs, viento_vuelo_vecs, Tmags, Dmags, Nmags,
                Txs, Tys, Tzs, Dxs, Dys, Dzs, Nxs, Nys, Nzs, accels, palancas, accangs,
                Gammas, Alphas, torcas, Cds, Machs, stability):
        
        # Save data to CSV
        datos_simulados = pd.DataFrame({
            'tiempos': tiempos,
            'posiciones_x': posiciones[:, 0],
            'posiciones_y': posiciones[:, 1],
            'posiciones_z': posiciones[:, 2],
            'velocidades_x': velocidades[:, 0],
            'velocidades_y': velocidades[:, 1],
            'velocidades_z': velocidades[:, 2],
            'thetas': thetas,
            'omegas': omegas,
            'CPs': CPs,
            'CGs': CGs,
            'masavuelo': masavuelo,
            'viento_vuelo_mags': viento_vuelo_mags,
            'viento_vuelo_dirs': viento_vuelo_dirs,
            'wind_xs': [vec[0] for vec in viento_vuelo_vecs],
            'wind_ys': [vec[1] for vec in viento_vuelo_vecs],
            'wind_zs': [vec[2] for vec in viento_vuelo_vecs],
            'Tmags': Tmags,
            'Dmags': Dmags,
            'Nmags': Nmags,
            'Txs': Txs,
            'Tys': Tys,
            'Tzs': Tzs,
            'Dxs': Dxs,
            'Dys': Dys,
            'Dzs': Dzs,
            'Nxs': Nxs,
            'Nys': Nys,
            'Nzs': Nzs,
            'accels': accels,
            'palancas': palancas,
            'accangs': accangs,
            'Gammas': Gammas,
            'Alphas': Alphas,
            'torcas': torcas,
            'Cds': Cds,
            'Machs': Machs,
            'estabilidad': stability
        })

        datos_simulados.to_csv('datos_simulacion.csv', index=False)

        # Save important data to JSON
        datos_a_guardar = {
            'd_ext': self.rocket.d_ext,
            't_MECO': self.rocket.t_MECO,
            'tiempo_salida_riel': vuelo1.tiempo_salida_riel,
            'tiempo_apogeo': vuelo1.tiempo_apogeo,
            'tiempo_impacto': vuelo1.tiempo_impacto,
            'max_altitude': max(posiciones[:, 2]),
            'max_speed': max(np.linalg.norm(velocidades, axis=1)),
            'max_acceleration_linear': max(accels),
            'max_acceleration_angular': max(accangs)
        }

        with open('datos_simulacion.json', 'w') as f:
            json.dump(datos_a_guardar, f, indent=4)

    def save_tab_data(self, tab_name):
        if tab_name == "rocket":
            data = {
                "nose_length": self.nose_length.get(),
                "nose_diameter": self.nose_diameter.get(),
                "nose_mass": self.nose_mass.get(),
                "nose_geometry": self.nose_geometry.get(),
                "body_length": self.body_length.get(),
                "body_diameter": self.body_diameter.get(),
                "body_thickness": self.body_thickness.get(),
                "body_mass": self.body_mass.get(),
                "fin_count": self.fin_count.get(),
                "fin_span": self.fin_span.get(),
                "fin_root_chord": self.fin_root_chord.get(),
                "fin_tip_chord": self.fin_tip_chord.get(),
                "fin_sweep": self.fin_sweep.get(),
                "fin_mass": self.fin_mass.get(),
                "boattail_length": self.boattail_length.get(),
                "boattail_front_diameter": self.boattail_front_diameter.get(),
                "boattail_rear_diameter": self.boattail_rear_diameter.get(),
                "boattail_mass": self.boattail_mass.get(),
                "motor_mass": self.motor_mass.get(),
                "motor_length": self.motor_length.get(),
                "motor_diameter": self.motor_diameter.get()
            }
        elif tab_name == "input":
            data = {
                "latitud": self.latitud.get(),
                "longitud": self.longitud.get(),
                "altitud": self.altitud.get(),
                "fecha": self.fecha.get(),
                "longitud_riel": self.longitud_riel.get(),
                "angulo_riel": self.angulo_riel.get(),
                "vel_base_viento": self.vel_base_viento.get(),
                "vel_mean_viento": self.vel_mean_viento.get(),
                "vel_var_viento": self.vel_var_viento.get(),
                "var_ang_viento": self.var_ang_viento.get(),
                "t_max": self.t_max.get(),
                "dt": self.dt.get()
            }
        else:
            messagebox.showerror("Error", "Tab name not recognized")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=4)
            messagebox.showinfo("Éxito", f"Datos de la pestaña {tab_name} guardados exitosamente")

if __name__ == "__main__":
    root = tk.Tk()
    app = SimuladorCohetesAvanzado(root)
    root.mainloop()