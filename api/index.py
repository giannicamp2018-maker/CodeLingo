"""
Vercel serverless function entry point for Flask application.
This file wraps the Flask app to work with Vercel's serverless environment.
"""
import sys
import os

# Add the parent directory to the path so we can import the app
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from app import create_app

# Create the Flask application
app = create_app()

# Vercel Python runtime automatically detects WSGI apps
# The app variable will be used by Vercel's WSGI adapter
# Make sure the app is accessible
__all__ = ['app']

