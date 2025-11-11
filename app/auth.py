"""
Authentication routes for user registration, login, and logout.
Handles user account creation and session management.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app import db
from app.models import User
from functools import wraps

# Create authentication blueprint
# Blueprints organize routes into separate modules
bp = Blueprint('auth', __name__)


def login_required(f):
    """
    Decorator to protect routes that require user authentication.
    If user is not logged in, redirects to login page.
    
    Args:
        f: The route function to protect
    
    Returns:
        Wrapped function that checks for authentication
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is logged in by checking session
        if 'user_id' not in session:
            # If not logged in, redirect to login page
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


@bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    User registration route.
    GET: Displays registration form 
    POST: Processes  registration form and creates new user account
    """
    if request.method == 'POST':
        # Get form data from request
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validate input data
        errors = []
        
        # Check if username is provided
        if not username:
            errors.append('Username is required.')
        
        # Check if email is provided
        if not email:
            errors.append('Email is required.')
        
        # Check if password is provided
        if not password:
            errors.append('Password is required.')
        
        # Check if passwords match
        if password != confirm_password:
            errors.append('Passwords do not match.')
        
        # Check if password is long enough
        if len(password) < 6:
            errors.append('Password must be at least 6 characters long.')
        
        # Check if username already exists
        if User.query.filter_by(username=username).first():
            errors.append('Username already exists. Please choose a different one.')
        
        # Check if email already exists
        if User.query.filter_by(email=email).first():
            errors.append('Email already registered. Please use a different email.')
        
        # If there are errors, display them and return to registration form
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('register.html')
        
        # Create new user
        try:
            user = User(username=username, email=email)
            # Set password (this will hash it automatically)
            user.set_password(password)
            
            # Add user to database
            db.session.add(user)
            db.session.commit()
            
            # Flash success message
            flash('Registration successful! Please log in.', 'success')
            
            # Redirect to login page
            return redirect(url_for('auth.login'))
        
        except Exception as e:
            # If there's an error, rollback database transaction
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'error')
            return render_template('register.html')
    
    # GET request - display registration form
    return render_template('register.html')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    User login route.
    GET: Displays login form
    POST: Processes login form and creates user session
    """
    if request.method == 'POST':
        # Get form data from request
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        # Validate input
        if not username or not password:
            flash('Please enter both username and password.', 'error')
            return render_template('login.html')
        
        # Find user by username
        user = User.query.filter_by(username=username).first()
        
        # Check if user exists and password is correct
        if user and user.check_password(password):
            # Create session for logged-in user
            # Store user ID in session to identify logged-in user
            session['user_id'] = user.id
            session['username'] = user.username
            
            # Flash success message
            flash(f'Welcome back, {user.username}!', 'success')
            
            # Redirect to home page
            return redirect(url_for('main.index'))
        else:
            # Invalid credentials
            flash('Invalid username or password.', 'error')
            return render_template('login.html')
    
    # GET request - display login form
    return render_template('login.html')


@bp.route('/logout')
def logout():
    """
    User logout route.
    Clears user session and redirects to home page.
    """
    # Clear session data
    session.clear()
    
    # Flash success message
    flash('You have been logged out successfully.', 'success')
    
    # Redirect to home page
    return redirect(url_for('main.index'))

