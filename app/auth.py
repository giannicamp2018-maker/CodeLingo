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
            
            # Debug: Log user creation
            print(f"User '{username}' (ID: {user.id}) registered successfully")
            
            # Automatically log the user in after registration
            # Store user ID in session to identify logged-in user
            session['user_id'] = user.id
            session['username'] = user.username
            session.permanent = True  # Make session permanent
            
            # Flash success message
            flash(f'Registration successful! Welcome, {username}! You are now logged in.', 'success')
            
            # Redirect to home page (user is already logged in)
            return redirect(url_for('main.index'))
        
        except Exception as e:
            # If there's an error, rollback database transaction
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'error')
            print(f"Registration error: {str(e)}")
            import traceback
            traceback.print_exc()
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
        # Query for the user with a fresh query
        user = User.query.filter_by(username=username).first()
        
        # Check if user exists
        if not user:
            # User doesn't exist - don't reveal this for security
            print(f"Login attempt: User '{username}' not found")
            flash('Invalid username or password.', 'error')
            return render_template('login.html')
        
        # Force a database query to ensure password_hash is loaded
        # This ensures we have the latest data from the database
        # Access the attribute to trigger lazy loading if needed
        _ = user.password_hash
        
        # Refresh the object from database to ensure we have the absolute latest data
        try:
            db.session.refresh(user)
        except Exception as refresh_error:
            # If refresh fails (object detached), re-query
            print(f"Refresh failed, re-querying user: {refresh_error}")
            user = User.query.filter_by(username=username).first()
            if not user:
                flash('Invalid username or password.', 'error')
                return render_template('login.html')
        
        # Debug: Log user found
        print(f"Login attempt: User '{username}' (ID: {user.id}) found")
        
        # Explicitly access password_hash to ensure it's loaded from database
        # This forces SQLAlchemy to fetch the attribute if it hasn't been loaded yet
        password_hash_value = user.password_hash
        
        # Check if user has a valid password hash
        if not password_hash_value:
            print(f"Login error: User '{username}' has no password hash")
            flash('Account error: Password not set. Please contact support or reset your password.', 'error')
            return render_template('login.html')
        
        # Debug: Log password hash status  
        print(f"Login attempt: User '{username}' has password hash: {bool(password_hash_value)}, length: {len(password_hash_value) if password_hash_value else 0}")
        
        # Check if password is correct
        try:
            password_valid = user.check_password(password)
            print(f"Login attempt: Password validation result for user '{username}': {password_valid}")
        except Exception as e:
            # Log the error for debugging (in production, use proper logging)
            print(f"Password check error for user {username}: {str(e)}")
            import traceback
            traceback.print_exc()
            flash('An error occurred during login. Please try again.', 'error')
            return render_template('login.html')
        
        if password_valid:
            # Create session for logged-in user
            # Store user ID in session to identify logged-in user
            session['user_id'] = user.id
            session['username'] = user.username
            
            # Make session permanent so it persists across browser restarts
            session.permanent = True
            
            # Debug: Log successful login
            print(f"Login successful: User '{username}' (ID: {user.id}) logged in, session permanent: {session.permanent}")
            
            # Flash success message
            flash(f'Welcome back, {user.username}!', 'success')
            
            # Redirect to home page
            return redirect(url_for('main.index'))
        else:
            # Invalid password
            print(f"Login failed: Invalid password for user '{username}'")
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

