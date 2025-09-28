import tkinter as tk
import tkinter.font as tkFont
from tkinter import ttk
import tkinter.messagebox as messagebox

from heartview import HeartView
from modes import PARAM_FOR_MODES

from serialcomm import PORTS_ARRAY

class PacemakerInterface:
    def __init__(self, parent_window, username, user_manager):
        self.username = username
        self.user_manager = user_manager
        self.parent_window = parent_window
        self.param_for_modes = PARAM_FOR_MODES  # Load mode-to-sliders mapping
        self.ports_array = PORTS_ARRAY
        # Create pacemaker window
        self.root = tk.Toplevel(parent_window)
        self.root.geometry("900x850")  # Adjusted width for wider layout
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Fonts
        title_font = tkFont.Font(family="Helvetica", size=16, weight="bold")
        tk.Label(self.root, text=f"Welcome {self.username}!", font=title_font).pack(pady=20)

        slider_frame = tk.Frame(self.root)
        slider_frame.pack(expand=True)
        self.sliders = {}  # Store all sliders
        self.create_sliders(slider_frame)



        mode_options = list(self.param_for_modes.keys())  # Get pacing modes
        self.mode_dropdown = ttk.Combobox(self.root, values=mode_options, state="readonly")
        self.mode_dropdown.set("AOO")  # Default mode
        self.mode_dropdown.place(x=680, y=40)
        self.mode_dropdown.bind("<<ComboboxSelected>>", self.update_slider_visibility)

        connection_optons = list(self.ports_array)
        self.ports_dropdown = ttk.Combobox(self.root, values=connection_optons, state="readonly")
        self.ports_dropdown.set("COM3") #Default mode
        self.ports_dropdown.place(x=680, y=10)

        # Load saved settings
        self.load_saved_settings()

        # Buttons
        tk.Button(self.root, text="Info", command=self.show_info, font=title_font, width=6).place(x=10, y=10)
        tk.Button(self.root, text="Save Settings", command=self.save_settings).place(x=10, y=650, width=150, height=40)
        tk.Button(self.root, text="Apply to HeartView", command=self.show_heartview).place(x=10, y=700, width=150, height=40)
        tk.Button(self.root, text="Sign Out", command=self.sign_out).place(x=740, y=700, width=150, height=40)
        tk.Button(self.root, text="Connect", command=self.monitor_connection).place(x=600, y=10, width=70, height=30)


        # Load saved settings
        self.load_saved_settings()

        # Initial slider visibility update
        self.update_slider_visibility()

    def save_settings_sendData(self):
        # Get the selected mode
        mode = self.mode_dropdown.get()

        # Get the list of sliders for the selected mode
        visible_parameters = self.param_for_modes.get(mode, [])

        # Collect the current slider values
        parameters = {}
        for key in visible_parameters:
            # Check if the key exists in the widget dictionary
            if key in self.slider_widgets:
                slider = self.slider_widgets[key]["slider"]
                parameters[key] = slider.get()  # Get the value from the slider

        # Save user settings
        if self.username in self.user_manager.users:
            self.user_manager.users[self.username]["mode"] = mode
            self.user_manager.users[self.username]["parameters"] = parameters

        # Save the data to persistent storage
        self.user_manager.save_users()

        # Format the data for UART transmission
        formatted_data = "; ".join(f"{key}: {value}" for key, value in parameters.items())

        # Print the data packet to the terminal
        print(f"Packet to send: {formatted_data}")

        try:
            # Initialize SerialCommunication (replace "COM3" with your actual port)
            uart = SerialCommunication(port="COM3")
            uart.send_data(formatted_data)  # Send data via UART
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send data via UART: {e}")
            print(f"Error sending data via UART: {e}")
        finally:
            if 'uart' in locals():
                uart.close_connection()  # Close the serial connection

        # Display success message
        messagebox.showinfo("Success", "Your settings have been saved and sent via UART!")
 
    def show_heartview(self):
        self.save_settings()
        # Pass the required arguments to HeartView
        HeartView(self.root, self.username, self.user_manager)

    def sign_out(self):
        self.root.destroy()  # Close the pacemaker interface window
        self.parent_window.deiconify()  # Show the login screen again

    def on_close(self):
        # Close both the pacemaker window and the main window
        self.root.destroy()
        self.parent_window.deiconify()  # Show the login screen again

    def create_sliders(self, frame):
        # Define sliders and their ranges
        slider_params = {
            "Lower Rate Limit (ppm)": (30, 175, 5),
            "Upper Rate Limit (ppm)": (50, 175, 5),
            "Maximum Sensor Rate (ppm)": (50, 175, 5),
            "Atrial Amplitude (V)": (0.1, 5.0, 0.1),
            "Ventricular Amplitude (V)": (0.1, 5.0, 0.1),
            "Atrial Pulse Width (ms)": (1, 30, 1),
            "Ventricular Pulse Width (ms)": (1, 30, 1),
            "Atrial Sensitivity (mV)": (0, 5, 0.1),
            "Ventricular Sensitivity (mV)": (0, 5, 0.1),
            "VRP (ms)": (150, 500, 10),
            "ARP (ms)": (150, 500, 10),
            "PVARP (ms)": (150, 500, 10),
            "Rate Smoothing (%)": (3, 25, 3),
            "Reaction Time (s)": (10, 50, 10),
            "Response Factor": (1, 16, 1),
            "Recovery Time (min)": (2, 16, 1),
            "Activity Threshold": (0,6,1),
            "Hysteresis": (0,1,1)
        }

        self.slider_widgets = {}

        # Create sliders and labels, but do not manage layout
        for label, (from_val, to_val, resolution) in slider_params.items():
            slider_label = tk.Label(frame, text=label)
            slider = tk.Scale(frame, from_=from_val, to=to_val, resolution=resolution, orient="horizontal")

            # Store both the label and slider without placing them
            self.slider_widgets[label] = {"label": slider_label, "slider": slider}

            # Hide them initially
            slider_label.grid_remove()
            slider.grid_remove()

        # Create Activity Threshold slider with custom labels
        activity_threshold_label = tk.Label(frame, text="Activity Threshold: V-LO")
        activity_threshold_slider = tk.Scale(frame, from_=0, to=6, orient="horizontal", showvalue=False, length=200)

        # Define the mapping of values to labels
        activity_threshold_labels = {
            0: "Activity Threshold: V-LO", 1: "Activity Threshold: LO", 2: "Activity Threshold: MED-LO", 3: "Activity Threshold: MED", 4: "Activity Threshold: HI-MED", 5: "Activity Threshold: HI", 6: "Activity Threshold: V-HI"
        }

        # Function to update label text based on slider value
        def update_activity_threshold_label(val):
            label_text = activity_threshold_labels.get(int(val), "")
            activity_threshold_label.config(text=label_text)

        # Set the custom slider to call this function on value change
        activity_threshold_slider.config(command=update_activity_threshold_label)

        # Store the activity threshold label and slider
        self.slider_widgets["Activity Threshold"] = {"label": activity_threshold_label, "slider": activity_threshold_slider}

        # Hide the activity threshold label and slider initially
        activity_threshold_label.grid_remove()
        activity_threshold_slider.grid_remove()

        # Create Hysteresis slider with ON/OFF labels
        hysteresis_label = tk.Label(frame, text="Hysteresis: OFF")
        hysteresis_slider = tk.Scale(frame, from_=0, to=1, orient="horizontal", showvalue=False, length=200)

        # Function to update label text for ON/OFF based on slider value
        def update_hysteresis_label(val):
            label_text = "Hysteresis: ON" if int(val) == 1 else "Hysteresis: OFF"
            hysteresis_label.config(text=label_text)

        # Set the custom slider to call this function on value change
        hysteresis_slider.config(command=update_hysteresis_label)

        # Store the hysteresis label and slider
        self.slider_widgets["Hysteresis"] = {"label": hysteresis_label, "slider": hysteresis_slider}

        # Hide the hysteresis label and slider initially
        hysteresis_label.grid_remove()
        hysteresis_slider.grid_remove()

    def update_slider_visibility(self, event=None):
        # Get the selected mode and corresponding sliders
        selected_mode = self.mode_dropdown.get()
        visible_sliders = self.param_for_modes.get(selected_mode, [])

        # Reset row tracker
        current_row = 0

        for label, widgets in self.slider_widgets.items():
            slider_label, slider = widgets["label"], widgets["slider"]

            if label in visible_sliders:
                # Show and place the slider and its label in the next available row
                slider_label.grid(row=current_row, column=0, padx=5, pady=5, sticky="w")
                slider.grid(row=current_row, column=1, padx=5, pady=5, sticky="ew")
                current_row += 1
            else:
                # Hide sliders not in the visible list
                slider_label.grid_remove()
                slider.grid_remove()

    def load_saved_settings(self):
        # Retrieve the user data from the user manager
        user_data = self.user_manager.users.get(self.username, {})
        
        # Get the saved parameters (if any)
        parameters = user_data.get("parameters", {})
        
        # Loop through the saved parameters and set the corresponding sliders
        for key, value in parameters.items():
            if key in self.slider_widgets:
                # Access the slider widget and set its value
                self.slider_widgets[key]["slider"].set(value)
        
        # Set the mode dropdown value
        self.mode_dropdown.set(user_data.get("mode", "AOO"))
        
    def monitor_connection(self):
        try:
            self.serPacemaker.receive_packet()  # Attempt to communicate
            messagebox.showinfo("status","Pacemaker Connection: ✓")
        except Exception:
            messagebox.showinfo("status","Pacemaker Connection: X")

    def save_settings(self):
        # Get the selected mode
        mode = self.mode_dropdown.get()

        # Get the list of sliders for the selected mode
        visible_parameters = self.param_for_modes.get(mode, [])

        # Collect the current slider values
        parameters = {}
        for key in visible_parameters:
            # Check if the key exists in the widget dictionary
            if key in self.slider_widgets:
                slider = self.slider_widgets[key]["slider"]
                parameters[key] = slider.get()  # Get the value from the slider

        # Save user settings
        if self.username in self.user_manager.users:
            self.user_manager.users[self.username]["mode"] = mode
            self.user_manager.users[self.username]["parameters"] = parameters

        # Save the data to persistent storage
        self.user_manager.save_users()

        # Display success message
        messagebox.showinfo("Success", "Your settings have been saved!")

    def show_info(self):
    
        # Create a new top-level window for the custom info box
        info_window = tk.Toplevel()
        info_window.title("Information")

        # Set the window size and make it resizable
        info_window.geometry("600x400")
        info_window.resizable(True, True)

        # Add a label with the information text
        info_message = (
            "Welcome to the Pacemaker DCM Interface!\n\n"
            "Here’s how to use the app:\n\n"
            "1. Adjust pacemaker parameters using the sliders\n" 
            "   (e.g., lower/upper rate limit, ect.)\n\n"
            "2. Select your preferred Pacemaker Mode from the dropdown (default is AOO).\n\n"
            "3. Click 'Save User Settings' to save these configurations\n"
            "   for your user profile.\n\n"
            "4. To visualize real-time EGM data, click 'Apply to HeartView'.\n"
            "   This will open a new window that will display EGM graphs.\n"
        )

        label = tk.Label(info_window, text=info_message, padx=10, pady=10, justify="left", anchor="w")
        label.pack(fill="both", expand=True)
