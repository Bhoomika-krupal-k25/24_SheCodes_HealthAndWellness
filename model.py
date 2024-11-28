# app/models.py

from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Unique ID for each user
    email = db.Column(db.String(100), unique=True, nullable=False)  # Email (unique and not null)
    password = db.Column(db.String(100), nullable=False)  # Password (not null)

    def set_password(self, password):
        """Hashes the password before storing it."""
        self.password = generate_password_hash(password)  # Hash the password before saving it

    def check_password(self, input_password):
        """Checks if the input password matches the stored hashed password."""
        return check_password_hash(self.password, input_password)  # Compare hashed password
