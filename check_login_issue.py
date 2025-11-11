"""
Utility script to diagnose login issues.
Checks users in the database and verifies password hashes.
"""
from app import create_app, db
from app.models import User
from werkzeug.security import check_password_hash

app = create_app()

with app.app_context():
    print("=" * 60)
    print("USER DATABASE DIAGNOSTICS")
    print("=" * 60)
    
    # Get all users
    users = User.query.all()
    
    if not users:
        print("\nNo users found in database.")
        print("You may need to register a new account.")
    else:
        print(f"\nFound {len(users)} user(s) in database:\n")
        
        for user in users:
            print(f"User ID: {user.id}")
            print(f"Username: {user.username}")
            print(f"Email: {user.email}")
            print(f"Password Hash: {'Present' if user.password_hash else 'MISSING'}")
            if user.password_hash:
                print(f"Hash Length: {len(user.password_hash)} characters")
                print(f"Hash Preview: {user.password_hash[:20]}...")
            print(f"Created At: {user.created_at}")
            print("-" * 60)
    
    # Test password checking
    print("\n" + "=" * 60)
    print("PASSWORD CHECK TEST")
    print("=" * 60)
    print("\nEnter a username to test password checking:")
    username = input("Username: ").strip()
    
    if username:
        user = User.query.filter_by(username=username).first()
        if user:
            print(f"\nUser '{username}' found (ID: {user.id})")
            if user.password_hash:
                print("Password hash exists.")
                print("\nEnter password to test:")
                password = input("Password: ").strip()
                
                if password:
                    try:
                        result = user.check_password(password)
                        print(f"\nPassword check result: {'✓ CORRECT' if result else '✗ INCORRECT'}")
                    except Exception as e:
                        print(f"\n✗ Error checking password: {str(e)}")
                        import traceback
                        traceback.print_exc()
            else:
                print("✗ No password hash found for this user!")
                print("This user cannot log in. Password needs to be reset.")
        else:
            print(f"\n✗ User '{username}' not found in database.")

