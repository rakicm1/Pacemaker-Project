import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
import numpy as np


class HeartView:
    def __init__(self, master, username, user_manager):
        self.window = tk.Toplevel(master)
        self.window.title("HeartView EGM Display")
        self.window.geometry("1000x600")  # Adjusted width for the panel

        self.username = username
        self.user_manager = user_manager

        # Fetch user data
        self.user_data = self.user_manager.users.get(self.username, {})
        self.saved_values = self.user_data.get("parameters", {})
        self.mode = self.user_data.get("mode", "Unknown")

        # Extract parameters with defaults if missing
        self.lower_rate_limit = self.saved_values.get("Lower Rate Limit (ppm)", 60)
        self.upper_rate_limit = self.saved_values.get("Upper Rate Limit (ppm)", 120)
        self.amplitude = self.saved_values.get("Atrial Amplitude (V)", 1.0)

        # Main frame to hold graph and side panel
        main_frame = tk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Left frame for the graph
        graph_frame = tk.Frame(main_frame)
        graph_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.fig, self.ax = plt.subplots()
        self.time = np.linspace(0, 10, 1000)  # Simulated 10-second duration
        self.ventricular_signal = self.generate_ventricular_signal()
        self.line, = self.ax.plot(self.time, self.ventricular_signal)

        self.ax.set_title("Ventricular Signal (EGM)")
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Amplitude")

        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Use FuncAnimation to animate the graph
        self.ani = FuncAnimation(self.fig, self.update_plot, interval=100)

        # Right frame for saved values
        side_panel = tk.Frame(main_frame, width=200, bg="lightgray")
        side_panel.pack(side=tk.RIGHT, fill=tk.Y)

        tk.Label(side_panel, text="Saved Values", font=("Helvetica", 14, "bold"), bg="lightgray").pack(pady=10)

        # Display the mode
        tk.Label(side_panel, text=f"Mode: {self.mode}", font=("Helvetica", 12, "bold"), bg="lightgray").pack(anchor="w", padx=10, pady=5)

        # Display the saved parameters
        for param, value in self.saved_values.items():
            tk.Label(side_panel, text=f"{param}: {value}", font=("Helvetica", 12), bg="lightgray").pack(anchor="w", padx=10, pady=5)

        # Close button
        close_button = tk.Button(side_panel, text="Close", command=self.close_heartview)
        close_button.pack(pady=10)

    def generate_ventricular_signal(self):
        """Generate a ventricular signal based on the saved parameters."""
        # Frequency is influenced by the lower and upper rate limits
        base_frequency = (self.lower_rate_limit + self.upper_rate_limit) / 120.0  # Normalized

        # Amplitude is influenced by the atrial amplitude
        base_signal = np.sin(2 * np.pi * base_frequency * self.time) * self.amplitude  # Base sinusoidal signal

        # Noise level is a fraction of the amplitude
        noise_level = 0.1 * self.amplitude
        noise = np.random.normal(0, noise_level, len(self.time))

        ventricular_signal = base_signal + noise

        # Add R-peaks (ventricular spikes) influenced by amplitude
        peak_height = 2 * self.amplitude
        for i in range(100, len(self.time), int(1000 / base_frequency)):  # Add peaks based on frequency
            ventricular_signal[i:i + 10] += np.linspace(0, peak_height, 10)  # Sharp upward spike
            ventricular_signal[i + 10:i + 20] -= np.linspace(peak_height, 0, 10)  # Sharp downward spike

        return ventricular_signal

    def update_plot(self, frame):
        """Shift the signal to create a scrolling effect."""
        self.ventricular_signal = np.roll(self.ventricular_signal, -6)  # Scroll the signal
        self.line.set_ydata(self.ventricular_signal)
        self.canvas.draw()

    def close_heartview(self):
        self.window.destroy()
