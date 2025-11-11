"""
Utility script to reset a user's password.
Use this if you're locked out of your account.
"""
from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    print("=" * 60)
    print("PASSWORD RESET UTILITY")
    print("=" * 60)
    print()
    
    # List all users
    users = User.query.all()
    if not users:
        print("No users found in database.")
        exit(1)
    
    print("Available users:")
    for i, user in enumerate(users, 1):
        print(f"  {i}. {user.username} (ID: {user.id}, Email: {user.email})")
    print()
    
    # Get username
    username = input("Enter username to reset password: ").strip()
    
    if not username:
        print("No username provided. Exiting.")
        exit(1)
    
    user = User.query.filter_by(username=username).first()
    
    if not user:
        print(f"User '{username}' not found.")
        exit(1)
    
    print(f"\nUser found: {user.username} (ID: {user.id})")
    print(f"Email: {user.email}")
    
    # Get new password
    new_password = input("\nEnter new password: ").strip()
    
    if not new_password:
        print("No password provided. Exiting.")
        exit(1)
    
    if len(new_password) < 6:
        print("Password must be at least 6 characters long.")
        exit(1)
    
    # Confirm
    confirm = input(f"\nReset password for user '{user.username}'? (yes/no): ").strip().lower()
    
    if confirm != 'yes':
        print("Password reset cancelled.")
        exit(0)
    
    # Reset password
    try:
        user.set_password(new_password)
        db.session.commit()
        print(f"\n✓ Password reset successful for user '{user.username}'")
        print("You can now log in with the new password.")
    except Exception as e:
        db.session.rollback()
        print(f"\n✗ Error resetting password: {str(e)}")
        import traceback
        traceback.print_exc()
        exit(1)

