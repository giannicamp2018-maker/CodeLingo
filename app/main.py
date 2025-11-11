"""
Main application routes.
Handles the home page, code generation, and code explanation functionality.
"""
from flask import Blueprint, render_template, request, jsonify, session
from app import db
from app.models import User, Project, SavedPrompt
from app.auth import login_required
from app.openai_service import generate_code_from_description, explain_code

# Create main blueprint
# This blueprint handles the main application functionality
bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    """
    Home page route.
    Displays the main interface with language tabs and code generation/explanation tools.
    """
    # Check if user is logged in
    user_id = session.get('user_id')
    projects = []
    
    if user_id:
        # If user is logged in, get their projects
        # This allows them to select a project to save prompts to
        user = User.query.get(user_id)
        if user:
            projects = Project.query.filter_by(user_id=user_id).order_by(Project.created_at.desc()).all()
    
    # Render the main page with projects (if user is logged in)
    return render_template('index.html', projects=projects, user_logged_in=bool(user_id))


@bp.route('/generate-code', methods=['POST'])
def generate_code():
    """
    Code generation route.
    Receives English description, generates code using OpenAI, and saves to database.
    
    Expected JSON data:
    {
        "language": "python" | "javascript" | "html",
        "description": "English description of what the code should do",
        "project_id": integer (optional, if user wants to save to a project)
    }
    
    Returns:
        JSON response with generated code and explanation
    """
    try:
        # Get JSON data from request
        data = request.get_json()
        
        # Extract parameters
        language = data.get('language', '').lower()
        description = data.get('description', '').strip()
        project_id = data.get('project_id')
        
        # Validate input
        if not language or language not in ['python', 'javascript', 'html']:
            return jsonify({
                'success': False,
                'error': 'Invalid language. Please select Python, JavaScript, or HTML/CSS.'
            }), 400
        
        if not description:
            return jsonify({
                'success': False,
                'error': 'Description is required.'
            }), 400
        
        # Generate code using OpenAI service
        result = generate_code_from_description(language, description)
        
        # Check if generation was successful
        if not result.get('success'):
            return jsonify({
                'success': False,
                'error': result.get('explanation', 'Failed to generate code.')
            }), 500
        
        # Get user ID from session (if logged in)
        user_id = session.get('user_id')
        
        # Save to database if user is logged in and project_id is provided
        if user_id and project_id:
            try:
                # Verify that the project belongs to the user
                project = Project.query.filter_by(id=project_id, user_id=user_id).first()
                
                if project:
                    # Create new SavedPrompt entry
                    saved_prompt = SavedPrompt(
                        project_id=project_id,
                        language=language,
                        input_type='description',
                        input_text=description,
                        output_code=result.get('code', ''),
                        explanation=result.get('explanation', '')
                    )
                    
                    # Add to database
                    db.session.add(saved_prompt)
                    db.session.commit()
            
            except Exception as e:
                # If saving fails, log error but don't fail the request
                # The user still gets their code, it just won't be saved
                print(f"Error saving prompt to database: {str(e)}")
                db.session.rollback()
        
        # Return successful response with code and explanation
        return jsonify({
            'success': True,
            'code': result.get('code', ''),
            'explanation': result.get('explanation', '')
        })
    
    except Exception as e:
        # Handle any unexpected errors
        print(f"Error in generate_code route: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'An unexpected error occurred. Please try again.'
        }), 500


@bp.route('/explain-code', methods=['POST'])
def explain_code_route():
    """
    Code explanation route.
    Receives code, explains it using OpenAI, and saves to database.
    
    Expected JSON data:
    {
        "language": "python" | "javascript" | "html",
        "code": "The code to explain",
        "project_id": integer (optional, if user wants to save to a project)
    }
    
    Returns:
        JSON response with explanation
    """
    try:
        # Get JSON data from request
        data = request.get_json()
        
        # Extract parameters
        language = data.get('language', '').lower()
        code = data.get('code', '').strip()
        project_id = data.get('project_id')
        
        # Validate input
        if not language or language not in ['python', 'javascript', 'html']:
            return jsonify({
                'success': False,
                'error': 'Invalid language. Please select Python, JavaScript, or HTML/CSS.'
            }), 400
        
        if not code:
            return jsonify({
                'success': False,
                'error': 'Code is required.'
            }), 400
        
        # Explain code using OpenAI service
        result = explain_code(language, code)
        
        # Check if explanation was successful
        if not result.get('success'):
            return jsonify({
                'success': False,
                'error': result.get('explanation', 'Failed to explain code.')
            }), 500
        
        # Get user ID from session (if logged in)
        user_id = session.get('user_id')
        
        # Save to database if user is logged in and project_id is provided
        if user_id and project_id:
            try:
                # Verify that the project belongs to the user
                project = Project.query.filter_by(id=project_id, user_id=user_id).first()
                
                if project:
                    # Create new SavedPrompt entry
                    saved_prompt = SavedPrompt(
                        project_id=project_id,
                        language=language,
                        input_type='code',
                        input_text=code,
                        output_code=None,  # No output code for explanations
                        explanation=result.get('explanation', '')
                    )
                    
                    # Add to database
                    db.session.add(saved_prompt)
                    db.session.commit()
            
            except Exception as e:
                # If saving fails, log error but don't fail the request
                print(f"Error saving explanation to database: {str(e)}")
                db.session.rollback()
        
        # Return successful response with explanation
        return jsonify({
            'success': True,
            'explanation': result.get('explanation', '')
        })
    
    except Exception as e:
        # Handle any unexpected errors
        print(f"Error in explain_code_route: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'An unexpected error occurred. Please try again.'
        }), 500

