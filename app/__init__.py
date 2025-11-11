"""
Flask application initialization file.
Sets up the Flask app, database, and registers all blueprints.
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

# Initialize SQLAlchemy database object
# This will be used to interact with the database throughout the application
db = SQLAlchemy()


def create_app(config_class=Config):
    """
    Application factory function.
    Creates and configures the Flask application instance.
    
    Args:
        config_class: Configuration class to use (defaults to Config)
    
    Returns:
        Flask application instance
    """
    # Create Flask app instance
    app = Flask(__name__)
    
    # Load configuration from config class
    app.config.from_object(config_class)
    
    # Initialize database with app
    db.init_app(app)
    
    # Import models here to avoid circular imports
    # Models need to be imported after db is created but before creating tables
    from app import models
    
    # Import blueprints (routes)
    from app.auth import bp as auth_bp
    from app.main import bp as main_bp
    from app.projects import bp as projects_bp
    
    # Register blueprints with the app
    # Blueprints organize routes into separate modules
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    app.register_blueprint(projects_bp, url_prefix='/projects')
    
    # Create database tables if they don't exist
    # This only creates tables, it doesn't modify existing ones
    with app.app_context():
        db.create_all()
    
    return app

