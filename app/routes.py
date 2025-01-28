from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from .models import db, User
from flask_login import login_user, logout_user, login_required, current_user
import time
# API routes
api = Blueprint('api', __name__)

@api.route('/')
def index():
    return render_template('landing.html')  # Your landing page

@api.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        if user and user.verify_password(password):  # Use the verify_password method
            login_user(user)  # Create a user session
            flash('Login successful!', 'success')  # Flash success message
            time.sleep(1)
            return redirect(url_for('main_routes.home'))  # Redirect to home.html on successful login
        else:
            flash('Login failed. Check your username and password.', 'danger')  # Flash error message
            return redirect(url_for('api.login'))  # Redirect back to login page on failure

    return render_template('login.html')  # Render the login form for GET requests

@api.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # Check if all fields are filled
        if not username or not email or not password:
            flash('All fields are required.', 'danger')
            return redirect(url_for('api.register'))  # Redirect back to registration page

        # Check if the user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists. Please choose a different one.', 'danger')
            return redirect(url_for('api.register'))  # Redirect back to registration page

        if User.query.filter_by(email=email).first():
            flash('Email already registered. Please use a different email.', 'danger')
            return redirect(url_for('api.register'))  # Redirect back to registration page

        # Create a new user
        new_user = User(username=username, email=email)
        new_user.password = password  # This will use the password setter to hash the password
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('api.login'))  # Redirect to login page

    return render_template('login.html')  # Render the registration form for GET requests

@api.route('/about')
def about():
    return render_template('about.html')

main_routes = Blueprint('main_routes', __name__)

@main_routes.route('/home')
@login_required  # Protect this route
def home():
    return render_template('home.html')  # Render the home page for logged-in users

@api.route('/privacy')
def privacy():
    return render_template('terms_privacy.html')
