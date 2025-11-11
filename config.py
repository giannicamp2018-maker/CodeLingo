"""
Configuration file for the Flask application.
Contains all application settings including database configuration and secret keys.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """
    Main configuration class for the Flask application.
    All application settings are defined here.
    """
    # Secret key for Flask sessions - used to encrypt session data
    # In production, this should be a long, random string stored in environment variables
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database configuration
    # SQLite database will be stored in the instance folder
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///instance/database.db'
    
    # Disable SQLAlchemy event system to save resources
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # OpenAI API key - loaded from environment variables for security
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY') or ''

# this is a one liner