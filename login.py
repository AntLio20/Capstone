# Description: This file handles user authentication and account creation using SQLite

import sqlite3
import os
import hashlib
import re
from PyQt5.QtWidgets import QMessageBox


class LoginSystem:
    def __init__(self):
        try:
            # Create database directory if it doesn't exist
            if not os.path.exists("database"):
                os.makedirs("database")

            # Connect to SQLite database (will create it if it doesn't exist)
            self.conn = sqlite3.connect("database/users.db")
            self.cursor = self.conn.cursor()

            # Create users table if it doesn't exist
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            self.conn.commit()
        except Exception as e:
            print(f"Database initialization error: {e}")
            # Create a default connection to prevent errors
            self.conn = None
            self.cursor = None

    def __del__(self):
        # Ensure connection is closed when object is destroyed
        if hasattr(self, 'conn') and self.conn:
            try:
                self.conn.close()
            except:
                pass

    def _hash_password(self, password):
        """Hash the password using SHA-256"""
        try:
            return hashlib.sha256(password.encode()).hexdigest()
        except Exception as e:
            print(f"Password hashing error: {e}")
            return ""

    def validate_username(self, username):
        """Check if username is valid"""
        try:
            # Username must be between 3 and 20 characters
            if not (3 <= len(username) <= 20):
                return False, "Username must be between 3 and 20 characters"

            # Username must contain only alphanumeric characters and underscores
            if not re.match(r'^[a-zA-Z0-9_]+$', username):
                return False, "Username can only contain letters, numbers, and underscores"

            return True, ""
        except Exception as e:
            print(f"Username validation error: {e}")
            return False, "Validation error"

    def validate_password(self, password):
        """Check if password is strong enough"""
        try:
            # Password must be at least 8 characters
            if len(password) < 8:
                return False, "Password must be at least 8 characters long"

            # Password should contain at least one digit
            if not any(char.isdigit() for char in password):
                return False, "Password must contain at least one number"

            # Password should contain at least one uppercase letter
            if not any(char.isupper() for char in password):
                return False, "Password must contain at least one uppercase letter"

            return True, ""
        except Exception as e:
            print(f"Password validation error: {e}")
            return False, "Validation error"

    def register_user(self, username, password, email=""):
        """Register a new user"""
        try:
            if not self.conn or not self.cursor:
                return False, "Database connection error"

            # Validate username
            username_valid, username_msg = self.validate_username(username)
            if not username_valid:
                return False, username_msg

            # Validate password
            password_valid, password_msg = self.validate_password(password)
            if not password_valid:
                return False, password_msg

            # Check if username already exists
            self.cursor.execute("SELECT username FROM users WHERE username=?", (username,))
            if self.cursor.fetchone():
                return False, "Username already exists"

            # Hash the password
            password_hash = self._hash_password(password)
            if not password_hash:
                return False, "Error processing password"

            # Insert the new user
            self.cursor.execute(
                "INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)",
                (username, password_hash, email)
            )
            self.conn.commit()
            return True, "User created successfully"
        except sqlite3.Error as e:
            print(f"Database error during registration: {e}")
            return False, f"Database error: {str(e)}"
        except Exception as e:
            print(f"Registration error: {e}")
            return False, "Registration failed"

    def authenticate_user(self, username, password):
        """Authenticate a user"""
        try:
            if not self.conn or not self.cursor:
                return False, "Database connection error"

            # Hash the password
            password_hash = self._hash_password(password)
            if not password_hash:
                return False, "Error processing password"

            # Check if username and password match
            self.cursor.execute(
                "SELECT id FROM users WHERE username=? AND password_hash=?",
                (username, password_hash)
            )
            user = self.cursor.fetchone()

            if user:
                return True, "Login successful"
            else:
                return False, "Invalid username or password"
        except sqlite3.Error as e:
            print(f"Database error during authentication: {e}")
            return False, "Database error"
        except Exception as e:
            print(f"Authentication error: {e}")
            return False, "Authentication failed"

    def show_message(self, parent, title, message, icon=QMessageBox.Information):
        """Show a message dialog"""
        try:
            msg_box = QMessageBox(parent)
            msg_box.setIcon(icon)
            msg_box.setWindowTitle(title)
            msg_box.setText(message)
            msg_box.exec_()
        except Exception as e:
            print(f"Error displaying message: {e}")
