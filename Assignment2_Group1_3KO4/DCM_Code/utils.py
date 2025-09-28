import json
import bcrypt
import tkinter.messagebox as messagebox
import tkinter as tk

USERS_FILE = 'users.json'

class Utils:


#TBH IDK if we need this cuz like maybe it makes more sense to just have the functions in their respective classes
#first 4 functions here are alreday in the user_manager.


    def load_users():
        try:
            with open(USERS_FILE, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_users(users):
        with open(USERS_FILE, 'w') as f:
            json.dump(users, f, indent=4)

    def hash_password(password):
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def check_password(hashed_password, password):
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
