import tkinter as tk
from tkinter import messagebox
import tkinter.font as tkFont

from user_manager import UserManager
from pacemaker_interface import PacemakerInterface

class LoginScreen:
    def __init__(self, root=None):
        if root is None:
            self.root = tk.Tk()  # Create a new Tkinter window if none is passed
        else:
            self.root = root  # Use the passed window (e.g., from UserManager)

        self.user_manager = UserManager(self.root)  # Pass root to UserManager
        self.root.title("Pacemaker DCM Login")
        self.root.geometry("500x500")

        # Set up the window close handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.create_widgets()
        self.root.mainloop()

    def create_widgets(self):
        # Fonts
        label_font = ("Helvetica", 22, "bold")

        # Name Entry
        tk.Label(self.root, text="Name", font=label_font).pack(pady=5)
        self.entry_name = tk.Entry(self.root, font=label_font, width=30)
        self.entry_name.pack(pady=5)

        # Password Entry
        tk.Label(self.root, text="Password", font=label_font).pack(pady=5)
        self.entry_password = tk.Entry(self.root, show="*", font=label_font, width=30)
        self.entry_password.pack(pady=5)

        # Buttons
        tk.Button(self.root, text="Register", command=self.register_user, font=label_font, width=15, height=2).pack(pady=5)
        tk.Button(self.root, text="Login", command=self.login_user, font=label_font, width=15, height=2).pack(pady=5)

    def register_user(self):
        # Register user
        name = self.entry_name.get()
        password = self.entry_password.get()
        success, message = self.user_manager.register(name, password)
        messagebox.showinfo("Register", message)
        if success:
            self.clear_entries()

    def login_user(self):
        # Login user
        name = self.entry_name.get()
        password = self.entry_password.get()
        success, message = self.user_manager.login(name, password)
        if success:
            messagebox.showinfo("Login", message)
            self.clear_entries()
            self.open_pacemaker_interface(name)
        else:
            messagebox.showerror("Login", message)

    def clear_entries(self):
        # Clear entry fields
        self.entry_name.delete(0, tk.END)
        self.entry_password.delete(0, tk.END)

    def open_pacemaker_interface(self, name):
        # Create and open pacemaker interface
        self.root.withdraw()  # Hide the login window

        # Create the pacemaker interface (this will create its own window)
        PacemakerInterface(self.root, name, self.user_manager)

    def on_close(self):
        # When the main window is closed, quit the app
        self.root.quit()  # This will stop the Tkinter event loop and close the app
