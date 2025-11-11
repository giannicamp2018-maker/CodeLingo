"""
Diagnostic script to check user accounts in the database.
This script helps diagnose login issues by checking user accounts and password hashes.
"""
from app import create_app, db
from app.models import User
from werkzeug.security import check_password_hash

app = create_app()

with app.app_context():
    print("=" * 60)
    print("User Account Diagnostic Tool")
    print("=" * 60)
    print()
    
    # Get all users
    users = User.query.all()
    
    if not users:
        print("No users found in the database.")
        print("You may need to register a new account.")
    else:
        print(f"Found {len(users)} user(s) in the database:\n")
        
        for user in users:
            print(f"User ID: {user.id}")
            print(f"Username: {user.username}")
            print(f"Email: {user.email}")
            print(f"Created: {user.created_at}")
            
            # Check password hash
            if user.password_hash:
                print(f"Password Hash: {user.password_hash[:50]}... (truncated)")
                print(f"Hash Length: {len(user.password_hash)} characters")
                
                # Test password verification (you can modify this to test a specific password)
                print("Password Hash Status: OK")
            else:
                print("Password Hash Status: MISSING - User cannot login!")
            
            print("-" * 60)
            print()
    
    # Test login for a specific user (modify username and password as needed)
    print("=" * 60)
    print("Password Verification Test")
    print("=" * 60)
    print()
    print("To test a specific username and password, modify this script.")
    print("Or use the following code in a Python shell:")
    print()
    print("  from app import create_app, db")
    print("  from app.models import User")
    print("  app = create_app()")
    print("  with app.app_context():")
    print("      user = User.query.filter_by(username='YOUR_USERNAME').first()")
    print("      if user:")
    print("          result = user.check_password('YOUR_PASSWORD')")
    print("          print(f'Password valid: {result}')")
    print("      else:")
    print("          print('User not found')")
    print()

