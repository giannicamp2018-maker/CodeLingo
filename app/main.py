"""
Main application routes.
Handles the home page, code generation, and code explanation functionality.
"""
from flask import Blueprint, render_template, request, jsonify, session
from app import db
from app.models import User, Project, SavedPrompt, PromptLog
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
        
        # Get user ID from session (if logged in) for logging
        user_id = session.get('user_id')
        
        # Generate code using OpenAI service
        result = generate_code_from_description(language, description, user_id=user_id)
        
        # Check if generation was successful
        if not result.get('success'):
            # Return error message (could be in 'explanation' field from service)
            error_msg = result.get('error') or result.get('explanation', 'Failed to generate code.')
            return jsonify({
                'success': False,
                'error': error_msg
            }), 500
        
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


@bp.route('/test-api-key', methods=['GET'])
@login_required
def test_api_key():
    """
    Test endpoint to verify OpenAI API key configuration.
    Only accessible to logged-in users for security.
    """
    try:
        from app.openai_service import get_client, reset_client
        from config import Config
        
        # Reset client to ensure fresh API key is used
        reset_client()
        
        # Get API key info (without exposing the full key)
        api_key = Config.OPENAI_API_KEY
        if not api_key:
            return jsonify({
                'success': False,
                'error': 'API key not configured',
                'details': 'OPENAI_API_KEY is not set in .env file'
            }), 400
        
        # Show partial key for verification (first 7 and last 4 characters)
        key_preview = f"{api_key[:7]}...{api_key[-4:]}" if len(api_key) > 11 else "***"
        
        # Try to make a simple API call to test the key
        try:
            client = get_client()
            # Make a minimal test request
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": "Say 'test'"}
                ],
                max_tokens=5
            )
            
            return jsonify({
                'success': True,
                'message': 'API key is valid and working',
                'key_preview': key_preview,
                'test_response': response.choices[0].message.content
            })
        except Exception as e:
            error_details = str(e)
            error_type = type(e).__name__
            
            # Try to extract more error information
            status_code = None
            error_body = None
            if hasattr(e, 'response'):
                try:
                    if hasattr(e.response, 'status_code'):
                        status_code = e.response.status_code
                    if hasattr(e.response, 'json'):
                        error_body = e.response.json()
                except:
                    pass
            
            return jsonify({
                'success': False,
                'error': 'API key test failed',
                'key_preview': key_preview,
                'error_type': error_type,
                'error_details': error_details,
                'status_code': status_code,
                'error_body': error_body,
                'suggestions': [
                    'Verify the API key is correct',
                    'Check if the API key belongs to an account with credits',
                    'Ensure the API key has not been revoked',
                    'Check your account billing and usage limits',
                    'Verify there are no spending limits blocking usage'
                ]
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Test failed: {str(e)}'
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
        
        # Get user ID from session (if logged in) for logging
        user_id = session.get('user_id')
        
        # Explain code using OpenAI service
        result = explain_code(language, code, user_id=user_id)
        
        # Check if explanation was successful
        if not result.get('success'):
            # Return error message (could be in 'explanation' field from service)
            error_msg = result.get('error') or result.get('explanation', 'Failed to explain code.')
            return jsonify({
                'success': False,
                'error': error_msg
            }), 500
        
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


@bp.route('/monitor', methods=['GET'])
@login_required
def monitor():
    """
    Monitoring page to view all prompts and responses.
    Shows all prompts sent to OpenAI, including successful and failed requests.
    Only accessible to logged-in users.
    """
    try:
        # Get filter parameters
        operation_type = request.args.get('operation_type', '')
        language = request.args.get('language', '')
        success_only = request.args.get('success_only', 'false').lower() == 'true'
        limit = int(request.args.get('limit', 50))
        
        # Build query
        query = PromptLog.query
        
        # Filter by user (show only current user's prompts, or all if admin)
        user_id = session.get('user_id')
        if user_id:
            query = query.filter(PromptLog.user_id == user_id)
        
        # Apply filters
        if operation_type:
            query = query.filter(PromptLog.operation_type == operation_type)
        if language:
            query = query.filter(PromptLog.language == language)
        if success_only:
            query = query.filter(PromptLog.success == True)
        
        # Order by most recent first
        query = query.order_by(PromptLog.created_at.desc())
        
        # Limit results
        logs = query.limit(limit).all()
        
        # Get statistics
        total_logs = PromptLog.query.filter(PromptLog.user_id == user_id).count() if user_id else PromptLog.query.count()
        successful_logs = PromptLog.query.filter(PromptLog.success == True)
        if user_id:
            successful_logs = successful_logs.filter(PromptLog.user_id == user_id)
        successful_logs = successful_logs.count()
        
        # Render monitoring page
        return render_template('monitor.html', 
                             logs=logs,
                             total_logs=total_logs,
                             successful_logs=successful_logs,
                             operation_type=operation_type,
                             language=language,
                             success_only=success_only,
                             limit=limit)
    
    except Exception as e:
        print(f"Error in monitor route: {str(e)}")
        return render_template('monitor.html', 
                             logs=[],
                             total_logs=0,
                             successful_logs=0,
                             error=f"Error loading logs: {str(e)}")

