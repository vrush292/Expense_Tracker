from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import db  # Adjust the import based on your project structure
from datetime import datetime

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    bio = db.Column(db.Text, nullable=True) 
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
        
    def __repr__(self):
        return f'<User  {self.username}>'

    
class Income(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    description = db.Column(db.String(200))

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    description = db.Column(db.String(200))

    def __repr__(self):
        return f'<Expense {self.amount} on {self.date}>'

class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    month = db.Column(db.String(20), nullable=False)  # Month as a string (e.g., "March 2025")
    limit = db.Column(db.Float, nullable=False)
    spent = db.Column(db.Float, default=0.0)  # New column to track total spent
    saving = db.Column(db.Float, default=0.0)  # Saving amount, default to 0.0
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __repr__(self):
        return f'<Budget {self.month} - Limit: {self.limit}, Spent: {self.spent}>'

class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    goal_name = db.Column(db.String(150), nullable=False)
    target_amount = db.Column(db.Float, nullable=False)
    current_amount = db.Column(db.Float, default=0.0)
    deadline = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
