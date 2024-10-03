import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import pandas as pd
import json
from math import pi
import time

# Importar las clases y funciones necesarias del archivo de simulación
# Nota: Asegúrate de que estos archivos estén en el mismo directorio
from condiciones_init import *
from Xitle import *
from Vuelo import *
from Viento import Viento

class SimuladorCohetesAvanzado:
    def __init__(self, master):
        self.master = master
        self.master.title("Simulador de Cohetes Suborbitales Avanzado")
        self.master.geometry("1200x800")

        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(expand=True, fill="both")

        self.create_input_tab()
        self.create_trajectory_tab()
        self.create_position_tab()
        self.create_forces_tab()
        self.create_angles_tab()
        self.create_stability_tab()
        self.create_wind_tab()
        self.create_summary_tab()

    def create_input_tab(self):
        input_frame = ttk.Frame(self.notebook)
        self.notebook.add(input_frame, text="Entrada")

        # Parámetros de entrada
        ttk.Label(input_frame, text="Ángulo del riel (grados):").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.angulo_riel = ttk.Entry(input_frame)
        self.angulo_riel.grid(row=0, column=1, padx=5, pady=5)
        self.angulo_riel.insert(0, str(np.rad2deg(riel.angulo)))

        ttk.Label(input_frame, text="Tiempo máximo de simulación (s):").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.t_max = ttk.Entry(input_frame)
        self.t_max.grid(row=1, column=1, padx=5, pady=5)
        self.t_max.insert(0, "800")

        ttk.Label(input_frame, text="Paso de tiempo (s):").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.dt = ttk.Entry(input_frame)
        self.dt.grid(row=2, column=1, padx=5, pady=5)
        self.dt.insert(0, "0.01")

        ttk.Label(input_frame, text="Velocidad base del viento (m/s):").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.vel_base_viento = ttk.Entry(input_frame)
        self.vel_base_viento.grid(row=3, column=1, padx=5, pady=5)
        self.vel_base_viento.insert(0, "10")

        self.btn_simular = ttk.Button(input_frame, text="Simular", command=self.simular)
        self.btn_simular.grid(row=4, column=0, columnspan=2, pady=20)

    def create_trajectory_tab(self):
        self.trajectory_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.trajectory_frame, text="Trayectoria 3D")

    def create_position_tab(self):
        self.position_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.position_frame, text="Posición y Velocidad")

    def create_forces_tab(self):
        self.forces_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.forces_frame, text="Fuerzas")

    def create_angles_tab(self):
        self.angles_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.angles_frame, text="Ángulos")

    def create_stability_tab(self):
        self.stability_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.stability_frame, text="Estabilidad")

    def create_wind_tab(self):
        self.wind_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.wind_frame, text="Viento")

    def create_summary_tab(self):
        self.summary_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.summary_frame, text="Resumen")

    def simular(self):
        # Obtener valores de entrada
        riel.angulo = np.deg2rad(float(self.angulo_riel.get()))
        t_max = float(self.t_max.get())
        dt = float(self.dt.get())
        vel_base_viento = float(self.vel_base_viento.get())

        # Configuración inicial
        Xitle.parachute_added = False
        Xitle.parachute_active1 = False

        x0, y0, z0 = 0, 0, 0
        vx0, vy0, vz0 = 0, 0, 0
        theta0, omega0 = riel.angulo, 0
        estado = np.array([x0, y0, z0, vx0, vy0, vz0, theta0, omega0])

        # Simulación
        inicio = time.time()
        print("Simulando...")

        viento_actual = Viento(vel_base=vel_base_viento, vel_mean=2, vel_var=0.01, var_ang=20)
        viento_actual.actualizar_viento3D()
        print("Viento actual", viento_actual.vector)

        vuelo1 = Vuelo(Xitle, atmosfera_actual, viento_actual)
        tiempos, sim, CPs, CGs, masavuelo, viento_vuelo_mags, viento_vuelo_dirs, viento_vuelo_vecs, Tvecs, Dvecs, Nvecs, accels, palancas, accangs, Gammas, Alphas, torcas, Cds, Machs = vuelo1.simular_vuelo(estado, t_max, dt, dt)

        fin = time.time()
        print(f"Tiempo de ejecución: {fin-inicio:.1f}s")

        # Procesar datos
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

        stability = [(CP - CG) / Xitle.d_ext for CP, CG in zip(CPs, CGs)]

        max_altitude = max(posiciones[:, 2])
        max_speed = max(np.linalg.norm(velocidades, axis=1))

        # Actualizar gráficos
        self.plot_trajectory(tiempos, posiciones)
        self.plot_position_velocity(tiempos, posiciones, velocidades)
        self.plot_forces(tiempos, Tmags, Dmags, Nmags)
        self.plot_angles(tiempos, thetas, Gammas, Alphas)
        self.plot_stability(tiempos, CPs, CGs, stability)
        self.plot_wind(tiempos, viento_vuelo_mags, viento_vuelo_dirs)
        self.update_summary(vuelo1, max_altitude, max_speed, np.max(accels), np.max(accangs))

        # Guardar datos
        self.save_data(tiempos, posiciones, velocidades, thetas, omegas, CPs, CGs, masavuelo,
                       viento_vuelo_mags, viento_vuelo_dirs, viento_vuelo_vecs, Tmags, Dmags, Nmags,
                       Txs, Tys, Tzs, Dxs, Dys, Dzs, Nxs, Nys, Nzs, accels, palancas, accangs,
                       Gammas, Alphas, torcas, Cds, Machs, stability)

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

        Diámetro externo del cohete: {Xitle.d_ext:.2f} m
        Tiempo de MECO: {Xitle.t_MECO:.2f} s
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
        
        # Guardar datos en CSV
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

        # Guardar datos importantes en JSON
        datos_a_guardar = {
            'd_ext': Xitle.d_ext,
            't_MECO': Xitle.t_MECO,
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

if __name__ == "__main__":
    root = tk.Tk()
    app = SimuladorCohetesAvanzado(root)
    root.mainloop()