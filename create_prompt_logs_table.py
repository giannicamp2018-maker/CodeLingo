"""
Script to create the prompt_logs table in the database.
Run this script once to add the new table for monitoring prompts.

Usage:
    python create_prompt_logs_table.py
"""
from app import create_app, db
from app.models import PromptLog

def create_prompt_logs_table():
    """Create the prompt_logs table if it doesn't exist."""
    app = create_app()
    
    with app.app_context():
        try:
            # Create all tables (this will only create tables that don't exist)
            db.create_all()
            print("✓ Database tables created/updated successfully!")
            print("✓ PromptLog table is ready for use.")
        except Exception as e:
            print(f"✗ Error creating tables: {str(e)}")
            raise

if __name__ == '__main__':
    create_prompt_logs_table()

