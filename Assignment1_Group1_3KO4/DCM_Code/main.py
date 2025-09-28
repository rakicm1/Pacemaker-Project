import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import json
import tkinter.font as tkFont
import bcrypt

# Constants
MAX_USERS = 10
USERS_FILE = 'users.json'

class PacemakerApp:
    def __init__(self):
        self.users = self.load_users()
        self.root = tk.Tk()
        self.root.title("Pacemaker DCM Login")
        self.root.geometry("500x500")

        label_font = tkFont.Font(family="Helvetica", size=22, weight="bold")
        
        tk.Label(self.root, text="Name", font=label_font).pack(pady=5)
        self.entry_name = tk.Entry(self.root, font=label_font, width=30)
        self.entry_name.pack(pady=5)
        
        tk.Label(self.root, text="Password", font=label_font).pack(pady=5)
        self.entry_password = tk.Entry(self.root, show="*", font=label_font, width=30)
        self.entry_password.pack(pady=5)
        
        tk.Button(self.root, text="Register", command=self.register_user, font=label_font, width=15, height=2).pack(pady=5)
        tk.Button(self.root, text="Login", command=self.login_user, font=label_font, width=15, height=2).pack(pady=5)
        
        self.root.mainloop()

    def load_users(self):
        try:
            with open(USERS_FILE, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_users(self):
        with open(USERS_FILE, 'w') as f:
            json.dump(self.users, f, indent=4)

    def hash_password(self, password):
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    def check_password(self, hashed_password, password):
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

    def register_user(self):
        name = self.entry_name.get() 
        password = self.entry_password.get()
        
        if name in self.users:
            messagebox.showerror("Error", "User already exists!") #checking if the username has already been registed
            return
        
        if len(self.users) >= MAX_USERS:
            messagebox.showerror("Error", "Maximum user limit reached!") #checking if their is space for a user
            return
        
        if name and password:
            self.users[name] = {
                'password': self.hash_password(password),  #if both are valid, we peform the folowing
                'mode': 'AOO'
            }
            self.save_users()
            messagebox.showinfo("Success", "User registered successfully!") #appending the new user to the Json
            self.clear_entries() #clearing the registration fields
        else:
            messagebox.showerror("Error", "Please enter both name and password.") #otherwise error

    def login_user(self):
        name = self.entry_name.get()
        password = self.entry_password.get()
        
        if name in self.users and self.check_password(self.users[name]['password'], password):#using the unhashing function 
            messagebox.showinfo("Success", f"Welcome {name}!")                                  #the inputted passcode
            self.open_pacemaker_interface(name) #if valid open
        else:
            messagebox.showerror("Error", "Failed Login Attempt.") #otherwise error

    def clear_entries(self):
        self.entry_name.delete(0, tk.END)
        self.entry_password.delete(0, tk.END)

    def show_info(self):
        info_message = (
            "Welcome to the Pacemaker DCM Interface!\n\n"
            "Here’s how to use the app:\n\n"
            "1. Adjust pacemaker parameters using the sliders (e.g., lower/upper rate limit, "
            "atrial/ventricular amplitude, etc.).\n"
            "2. Select your preferred Pacemaker Mode from the dropdown (default is AOO).\n"
            "3. Click 'Save User Settings' to save these configurations for your user profile.\n"
            "4. To visualize real-time EGM data, click 'Apply to HeartView'. This will open a new "
            "window that will display EGM graphs.\n\n"
            "Please note: Currently, the EGM window is blank but will be updated soon to include live graphs."
        )
        messagebox.showinfo("Information", info_message)

    def check_rate_limits(self, *args):
        lower_limit = self.sliders["Lower Rate Limit"].get() #retrieving the lower limit value
        upper_limit = self.sliders["Upper Rate Limit"].get() #retrieving the upper limit value
        
        if upper_limit < lower_limit:                   #if upper less than lower, move upper to be one hgiher than lower
            self.sliders["Upper Rate Limit"].set(lower_limit + 1)

    def create_slider(self, frame, label_text, from_val, to_val, resolution=1, callback=None):
        tk.Label(frame, text=label_text).pack()
        slider = tk.Scale(frame, from_=from_val, to=to_val, resolution=resolution, orient='horizontal') #using a function to automatically
        slider.pack(pady=5)                                                                 #create sliders for each parameter 
        
        if callback:
            slider.config(command=callback)
        
        return slider

    def save_mode(self, name, selected_mode):
        self.users[name]['mode'] = selected_mode                               #to save the mode selected by the user to their profile
        self.users[name]['parameters'] = {key: self.sliders[key].get() for key in self.sliders} #saving the parameters as well
        self.save_users()
        messagebox.showinfo("Success", "Mode and parameters saved successfully!")

    def show_heartview(self):
        heartview_window = tk.Toplevel(self.root)
        heartview_window.title("HeartView EGM Display") #to display the Egram screen
        heartview_window.geometry("800x600")
        
        tk.Label(                           #using basic text, this will be updated in assignment to display the graphs and data
            heartview_window, text="HeartView EGM Display", font=("Helvetica", 16, "bold") 
        ).pack(pady=20)
        
        tk.Label(
            heartview_window, text="Real-time EGM graphs will appear here.", font=("Helvetica", 12)
        ).pack(pady=10)

    def open_pacemaker_interface(self, name):   
        self.root.withdraw()   #removing the welcome screen
        pacemaker_window = tk.Toplevel(self.root)
        pacemaker_window.title("Pacemaker Interface")
        pacemaker_window.geometry("800x700")

        def on_close():
            self.root.destroy() 
            pacemaker_window.destroy()  # Close the pacemaker window

        pacemaker_window.protocol("WM_DELETE_WINDOW", on_close) #bindin gthe exit button on the screen to closing the application

        
        title_font = tkFont.Font(family="Helvetica", size=16, weight="bold") #creating the title font and title
        tk.Label(pacemaker_window, text="Pacemaker Interface", font=title_font).pack(pady=10)
        
        slider_frame = tk.Frame(pacemaker_window)   #creating the frame where alll the sliders will go
        slider_frame.pack(pady=10, anchor="center")

        self.sliders = {}                           #creating sliders for all the paramters using the create_slider function
        self.sliders["Lower Rate Limit"] = self.create_slider(slider_frame, "Lower Rate Limit (ppm):", 30, 175, callback=self.check_rate_limits)
        self.sliders["Upper Rate Limit"] = self.create_slider(slider_frame, "Upper Rate Limit (ppm):", 60, 180, callback=self.check_rate_limits)
        
        self.sliders["Atrial Amplitude"] = self.create_slider(slider_frame, "Atrial Amplitude (V):", 0.5, 7.0, resolution=0.1)
        self.sliders["Atrial Pulse Width"] = self.create_slider(slider_frame, "Atrial Pulse Width (ms):", 0.1, 2.0, resolution=0.1)
        self.sliders["Ventricular Amplitude"] = self.create_slider(slider_frame, "Ventricular Amplitude (V):", 0.5, 7.0, resolution=0.1)
        self.sliders["Ventricular Pulse Width"] = self.create_slider(slider_frame, "Ventricular Pulse Width (ms):", 0.1, 2.0, resolution=0.1)
        self.sliders["VRP"] = self.create_slider(slider_frame, "VRP (ms):", 150, 500)
        self.sliders["ARP"] = self.create_slider(slider_frame, "ARP (ms):", 150, 500)

        tk.Label(pacemaker_window, text="Select PM Mode:").place(relx=0.95, rely=0.02, anchor='ne')  #dropdown for slecting the mode
        mode_options = ["AOO", "VOO", "AAI", "VVI"]
        mode_dropdown = ttk.Combobox(pacemaker_window, values=mode_options, state="readonly")
        
        if name in self.users:                                                  #if name is in users we set their parameters as saved
            saved_parameters = self.users[name].get('parameters', {})
            for key in self.sliders:
                if key in saved_parameters:
                    self.sliders[key].set(saved_parameters[key])
            mode_dropdown.set(self.users[name]['mode'])
        else:
            mode_dropdown.set("AOO")
        
        mode_dropdown.place(relx=0.95, rely=0.06, anchor='ne')
                                                                            #buttons for all the functions previouslt defined
        tk.Button(pacemaker_window, text="Info", command=self.show_info, font=title_font, width=6, height=1).place(x=10, y=10)
        tk.Button(pacemaker_window, text="Save User Settings", command=lambda: self.save_mode(name, mode_dropdown.get())).place(x=10, y=650)
        tk.Label(pacemaker_window, text="The Pacemaker is not communicating with the DCM").place(x=240, y=650)
        tk.Button(pacemaker_window, text="Apply to HeartView", command=self.show_heartview).place(x=620, y=650)

# Initialize and run the application
PacemakerApp()

