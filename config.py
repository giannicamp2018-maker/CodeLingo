"""
Configuration file for the Flask application.
Contains all application settings including database configuration and secret keys.
"""
import os
from dotenv import load_dotenv
from pathlib import Path

# Get the directory where this config.py file is located (project root)
basedir = Path(__file__).resolve().parent

# Load environment variables from .env file in the project root
# Explicitly specify the path to ensure it's loaded correctly
env_path = basedir / '.env'
# Load with explicit encoding to handle BOM if present
# python-dotenv handles UTF-8 BOM automatically, but we'll be explicit
# Use override=True to ensure .env file values override system environment variables
load_dotenv(dotenv_path=env_path, override=True)


class Config:
    """
    Main configuration class for the Flask application.
    All application settings are defined here.
    """
    # Secret key for Flask sessions - used to encrypt session data
    # In production, this should be a long, random string stored in environment variables
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Session configuration - make sessions permanent so they persist
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours in seconds
    
    # Database configuration
    # Check if we're on Vercel (serverless environment)
    # Vercel has a read-only filesystem except for /tmp
    if os.environ.get('VERCEL'):
        # On Vercel, use /tmp for database (note: data won't persist between invocations)
        # For production, you should use a proper database service like PostgreSQL
        database_uri = 'sqlite:////tmp/database.db'
    else:
        # Local development: SQLite database in instance folder
        instance_path = basedir / 'instance'
        # Ensure instance directory exists
        instance_path.mkdir(exist_ok=True)
        database_path = instance_path / 'database.db'
        # Convert Windows path to SQLite format (forward slashes)
        database_uri = 'sqlite:///' + str(database_path).replace('\\', '/')
    
    # Allow DATABASE_URL environment variable to override
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or database_uri
    
    # Disable SQLAlchemy event system to save resources
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # OpenAI API key - loaded from environment variables for security
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY') or ''

# this is a one liner