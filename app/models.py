"""
Database models for the application.
Defines the structure of all database tables using SQLAlchemy ORM.
"""
from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    """
    User model representing a registered user in the system.
    
    Attributes:
        id: Primary key, unique identifier for each user
        username: Unique username for login
        email: Unique email address
        password_hash: Hashed password (never store plain text passwords)
        created_at: Timestamp when user account was created
        projects: Relationship to projects owned by this user
    """
    __tablename__ = 'users'
    
    # Primary key - unique identifier for each user
    id = db.Column(db.Integer, primary_key=True)
    
    # Username must be unique and cannot be null
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    
    # Email must be unique and cannot be null
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    
    # Password hash - stores the hashed password, not the plain text
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Timestamp when the user account was created
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship to projects - one user can have many projects
    # cascade='all, delete-orphan' means if user is deleted, their projects are also deleted
    projects = db.relationship('Project', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """
        Hash and set the user's password.
        
        Args:
            password: Plain text password to hash and store
        """
        # Generate password hash using Werkzeug's security function
        # This creates a secure hash that cannot be reversed
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """
        Check if the provided password matches the stored hash.
        
        Args:
            password: Plain text password to verify
        
        Returns:
            True if password matches, False otherwise
        """
        # Compare provided password with stored hash
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        """String representation of the User object for debugging."""
        return f'<User {self.username}>'


class Project(db.Model):
    """
    Project model representing a folder/project that contains saved prompts.
    Users can create multiple projects to organize their code examples.
    
    Attributes:
        id: Primary key, unique identifier for each project
        name: Name of the project/folder
        user_id: Foreign key to the user who owns this project
        created_at: Timestamp when project was created
        updated_at: Timestamp when project was last updated
        saved_prompts: Relationship to saved prompts in this project
    """
    __tablename__ = 'projects'
    
    # Primary key - unique identifier for each project
    id = db.Column(db.Integer, primary_key=True)
    
    # Project name - cannot be null
    name = db.Column(db.String(100), nullable=False)
    
    # Foreign key to users table - links project to its owner
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Timestamp when project was created
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Timestamp when project was last updated
    # Automatically updates when project is modified
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationship to saved prompts - one project can have many saved prompts
    # cascade='all, delete-orphan' means if project is deleted, its prompts are also deleted
    saved_prompts = db.relationship('SavedPrompt', backref='project', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        """String representation of the Project object for debugging."""
        return f'<Project {self.name}>'


class SavedPrompt(db.Model):
    """
    SavedPrompt model representing a saved code generation or explanation.
    Stores the input (description or code), output code, and explanation.
    
    Attributes:
        id: Primary key, unique identifier for each saved prompt
        project_id: Foreign key to the project this prompt belongs to
        language: Programming language (python, javascript, html)
        input_type: Type of input ('description' or 'code')
        input_text: The original input (description or code)
        output_code: The generated code (if input was description)
        explanation: Explanation of the code
        created_at: Timestamp when this prompt was saved
    """
    __tablename__ = 'saved_prompts'
    
    # Primary key - unique identifier for each saved prompt
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign key to projects table - links prompt to its project
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False, index=True)
    
    # Programming language - can be 'python', 'javascript', or 'html'
    language = db.Column(db.String(20), nullable=False)
    
    # Input type - either 'description' (English description) or 'code' (code to explain)
    input_type = db.Column(db.String(20), nullable=False)
    
    # The original input text (either description or code)
    input_text = db.Column(db.Text, nullable=False)
    
    # The generated code (only if input_type is 'description')
    # Can be null if this is an explanation of existing code
    output_code = db.Column(db.Text, nullable=True)
    
    # Explanation of the code
    explanation = db.Column(db.Text, nullable=False)
    
    # Timestamp when this prompt was saved
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        """String representation of the SavedPrompt object for debugging."""
        return f'<SavedPrompt {self.id} - {self.language}>'

