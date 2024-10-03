import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import math

class SimuladorCohetes:
    def __init__(self, master):
        self.master = master
        self.master.title("Simulador de Cohetes Suborbitales")
        self.master.geometry("800x600")

        self.create_widgets()

    def create_widgets(self):
        # Frame para los controles
        control_frame = ttk.Frame(self.master, padding="10")
        control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Etiquetas y campos de entrada
        ttk.Label(control_frame, text="Masa inicial (kg):").grid(row=0, column=0, sticky=tk.W)
        self.masa_inicial = ttk.Entry(control_frame)
        self.masa_inicial.grid(row=0, column=1)
        self.masa_inicial.insert(0, "1000")

        ttk.Label(control_frame, text="Empuje (N):").grid(row=1, column=0, sticky=tk.W)
        self.empuje = ttk.Entry(control_frame)
        self.empuje.grid(row=1, column=1)
        self.empuje.insert(0, "20000")

        ttk.Label(control_frame, text="Tiempo de quemado (s):").grid(row=2, column=0, sticky=tk.W)
        self.tiempo_quemado = ttk.Entry(control_frame)
        self.tiempo_quemado.grid(row=2, column=1)
        self.tiempo_quemado.insert(0, "60")

        ttk.Label(control_frame, text="Ángulo de lanzamiento (grados):").grid(row=3, column=0, sticky=tk.W)
        self.angulo_lanzamiento = ttk.Entry(control_frame)
        self.angulo_lanzamiento.grid(row=3, column=1)
        self.angulo_lanzamiento.insert(0, "85")

        # Botón para iniciar la simulación
        self.btn_simular = ttk.Button(control_frame, text="Simular", command=self.simular)
        self.btn_simular.grid(row=4, column=0, columnspan=2, pady=10)

        # Frame para el gráfico
        self.graph_frame = ttk.Frame(self.master)
        self.graph_frame.grid(row=0, column=1, rowspan=5, padx=10, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configurar el peso de las filas y columnas
        self.master.columnconfigure(1, weight=1)
        self.master.rowconfigure(0, weight=1)

    def simular(self):
        # Obtener los valores de entrada
        m0 = float(self.masa_inicial.get())
        F = float(self.empuje.get())
        t_burn = float(self.tiempo_quemado.get())
        angle = float(self.angulo_lanzamiento.get())

        # Parámetros de la simulación
        g = 9.81  # Aceleración debido a la gravedad (m/s^2)
        Cd = 0.2  # Coeficiente de arrastre
        A = 0.5   # Área de sección transversal del cohete (m^2)
        rho = 1.225  # Densidad del aire al nivel del mar (kg/m^3)
        dt = 0.1  # Paso de tiempo para la simulación (s)

        # Inicializar arrays para almacenar los resultados
        t = np.arange(0, 1000, dt)
        x = np.zeros_like(t)
        y = np.zeros_like(t)
        vx = np.zeros_like(t)
        vy = np.zeros_like(t)

        # Condiciones iniciales
        x[0] = 0
        y[0] = 0
        vx[0] = F / m0 * math.cos(math.radians(angle)) * dt
        vy[0] = F / m0 * math.sin(math.radians(angle)) * dt

        # Simulación
        for i in range(1, len(t)):
            # Calcular la velocidad y posición
            v = math.sqrt(vx[i-1]**2 + vy[i-1]**2)
            Fd = 0.5 * Cd * A * rho * v**2  # Fuerza de arrastre

            ax = 0 if t[i] > t_burn else (F * math.cos(math.radians(angle)) - Fd * vx[i-1] / v) / m0
            ay = -g if t[i] > t_burn else (F * math.sin(math.radians(angle)) - m0 * g - Fd * vy[i-1] / v) / m0

            vx[i] = vx[i-1] + ax * dt
            vy[i] = vy[i-1] + ay * dt
            x[i] = x[i-1] + vx[i] * dt
            y[i] = y[i-1] + vy[i] * dt

            # Detener la simulación si el cohete toca el suelo
            if y[i] < 0:
                x = x[:i]
                y = y[:i]
                break

        # Crear el gráfico
        fig, ax = plt.subplots(figsize=(6, 4), dpi=100)
        ax.plot(x / 1000, y / 1000)  # Convertir a kilómetros
        ax.set_xlabel('Distancia horizontal (km)')
        ax.set_ylabel('Altitud (km)')
        ax.set_title('Trayectoria del Cohete Suborbital')
        ax.grid(True)

        # Mostrar el gráfico en la interfaz
        for widget in self.graph_frame.winfo_children():
            widget.destroy()
        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = SimuladorCohetes(root)
    root.mainloop()