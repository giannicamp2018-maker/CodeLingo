"""
Project management routes.
Handles creation, viewing, and deletion of user projects/folders.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from app import db
from app.models import User, Project, SavedPrompt
from app.auth import login_required
from datetime import datetime

# Create projects blueprint
# This blueprint handles all project-related functionality
bp = Blueprint('projects', __name__)


@bp.route('/')
@login_required
def list_projects():
    """
    List all projects for the current user.
    Displays a page with all user's projects and option to create new ones.
    """
    # Get user ID from session
    user_id = session.get('user_id')
    
    # Get all projects for this user, ordered by most recent first
    projects = Project.query.filter_by(user_id=user_id).order_by(Project.created_at.desc()).all()
    
    # Render projects page with list of projects
    return render_template('projects.html', projects=projects)


@bp.route('/create', methods=['POST'])
@login_required
def create_project():
    """
    Create a new project/folder.
    Receives project name and creates a new project for the current user.
    """
    # Get user ID from session
    user_id = session.get('user_id')
    
    # Get project name from form
    project_name = request.form.get('name', '').strip()
    
    # Validate input
    if not project_name:
        flash('Project name is required.', 'error')
        return redirect(url_for('projects.list_projects'))
    
    # Check if project name is too long
    if len(project_name) > 100:
        flash('Project name must be less than 100 characters.', 'error')
        return redirect(url_for('projects.list_projects'))
    
    try:
        # Create new project
        project = Project(name=project_name, user_id=user_id)
        
        # Add to database
        db.session.add(project)
        db.session.commit()
        
        # Get the project ID after commit
        project_id = project.id
        
        # Verify the project was actually saved by querying it back
        # This helps catch any database transaction issues
        verified_project = Project.query.filter_by(id=project_id, user_id=user_id).first()
        
        if verified_project:
            # Flash success message
            flash(f'Project "{project_name}" created successfully!', 'success')
            print(f"✓ Project '{project_name}' (ID: {project_id}) created and verified for user {user_id}")
        else:
            # This should never happen, but if it does, we need to know
            flash(f'Project "{project_name}" may not have been saved properly. Please refresh the page.', 'error')
            print(f"⚠ WARNING: Project '{project_name}' (ID: {project_id}) was created but could not be verified for user {user_id}")
    
    except Exception as e:
        # Handle errors
        db.session.rollback()
        flash('An error occurred while creating the project. Please try again.', 'error')
        print(f"✗ Error creating project: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # Redirect to home page so user can immediately use the new project
    return redirect(url_for('main.index'))


@bp.route('/<int:project_id>')
@login_required
def project_detail(project_id):
    """
    View details of a specific project.
    Displays all saved prompts in the project.
    
    Args:
        project_id: ID of the project to view
    """
    # Get user ID from session
    user_id = session.get('user_id')
    
    # Get project and verify it belongs to the user
    project = Project.query.filter_by(id=project_id, user_id=user_id).first()
    
    # Check if project exists and belongs to user
    if not project:
        flash('Project not found or you do not have permission to view it.', 'error')
        return redirect(url_for('projects.list_projects'))
    
    # Get all saved prompts for this project, ordered by most recent first
    saved_prompts = SavedPrompt.query.filter_by(project_id=project_id).order_by(SavedPrompt.created_at.desc()).all()
    
    # Render project detail page
    return render_template('project_detail.html', project=project, saved_prompts=saved_prompts)


@bp.route('/<int:project_id>/delete', methods=['POST'])
@login_required
def delete_project(project_id):
    """
    Delete a project and all its saved prompts.
    
    Args:
        project_id: ID of the project to delete
    """
    # Get user ID from session
    user_id = session.get('user_id')
    
    # Get project and verify it belongs to the user
    project = Project.query.filter_by(id=project_id, user_id=user_id).first()
    
    # Check if project exists and belongs to user
    if not project:
        flash('Project not found or you do not have permission to delete it.', 'error')
        return redirect(url_for('projects.list_projects'))
    
    try:
        # Store project name for flash message
        project_name = project.name
        
        # Delete project (cascade will delete all saved prompts automatically)
        db.session.delete(project)
        db.session.commit()
        
        # Flash success message
        flash(f'Project "{project_name}" deleted successfully!', 'success')
    
    except Exception as e:
        # Handle errors
        db.session.rollback()
        flash('An error occurred while deleting the project. Please try again.', 'error')
        print(f"Error deleting project: {str(e)}")
    
    # Redirect back to projects list
    return redirect(url_for('projects.list_projects'))


@bp.route('/<int:project_id>/set-active', methods=['POST'])
@login_required
def set_active_project(project_id):
    """
    Set a project as the active project in the session.
    This allows the user to automatically save prompts to this project.
    
    Args:
        project_id: ID of the project to set as active
    
    Returns:
        JSON response with success status
    """
    # Get user ID from session
    user_id = session.get('user_id')
    
    # Get project and verify it belongs to the user
    project = Project.query.filter_by(id=project_id, user_id=user_id).first()
    
    # Check if project exists and belongs to user
    if not project:
        return jsonify({
            'success': False,
            'error': 'Project not found or you do not have permission to access it.'
        }), 404
    
    # Set active project in session
    session['active_project_id'] = project_id
    
    # Return success response
    return jsonify({
        'success': True,
        'message': f'Active project set to "{project.name}"'
    })

