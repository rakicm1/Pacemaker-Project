import json
import bcrypt
USERS_FILE = 'users.json'
MAX_USERS = 10

class UserManager:
    def __init__(self, root):
        self.root = root
        self.users = self.load_users()

    def load_users(self):
        # Load users from file or return an empty dictionary
        try:
            with open(USERS_FILE, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_users(self):
        # Save users to file
        with open(USERS_FILE, 'w') as f:
            json.dump(self.users, f, indent=4)

    def hash_password(self, password):
        # Hash password
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def check_password(self, hashed_password, password):
        # Verify password
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

    def register(self, name, password):
        # Register a new user
        if name in self.users:
            return False, "User already exists!"
        if len(self.users) >= MAX_USERS:
            return False, "Maximum user limit reached!"
        if name and password:
            self.users[name] = {
                'password': self.hash_password(password),
                'mode': 'AOO',
                'parameters': {}
            }
            self.save_users()
            return True, "User registered successfully!"
        return False, "Please enter both name and password."

    def login(self, name, password):
        # Login a user
        if name in self.users and self.check_password(self.users[name]['password'], password):
            return True, "Login successful!"
        if name not in self.users:
            return False, "User does not exist."
        return False, "Incorrect password."


