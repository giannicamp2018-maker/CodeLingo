"""
Application entry point.
Run this file to start the Flask development server.
"""
from app import create_app, db
from app.models import User, Project, SavedPrompt

# Create Flask application instance
app = create_app()

# Create database tables if they don't exist
# This will create all tables defined in models.py
with app.app_context():
    db.create_all()
    print("Database initialized successfully!")

if __name__ == '__main__':
    # Run the Flask development server
    # debug=True enables auto-reload on code changes and detailed error pages
    # In production, set debug=False and use a proper WSGI server
    app.run(debug=True, host='0.0.0.0', port=5000)

