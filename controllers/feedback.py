from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from repositories.factory import RepositoryFactory
from models.feedback import Feedback
from functools import wraps
from core.database import database

feedback_bp = Blueprint('feedback', __name__)

def admin_required(f): # Decorator to require admin access
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('products.home'))
        return f(*args, **kwargs)
    return decorated_function

@feedback_bp.route('/contact', methods=['GET', 'POST'])
def contact(): # Contact Us / Feedback form (Login required)
    # Check authentication manually to avoid showing default login message
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        subject = request.form.get('subject', '').strip()
        message = request.form.get('message', '').strip()
        feedback_type = request.form.get('feedback_type', 'general').strip()
        
        # Validation
        if not name or not email or not subject or not message:
            flash('Please fill in all required fields.', 'error')
            return render_template('contact.html', 
                                 name=name, 
                                 email=email, 
                                 subject=subject, 
                                 message=message,
                                 feedback_type=feedback_type)
        
        # Create feedback entry
        feedback = Feedback(
            user_id=current_user.id,
            name=name,
            email=email,
            subject=subject,
            message=message,
            feedback_type=feedback_type,
            status='new'
        )
        
        try:
            feedback_repo = RepositoryFactory.get_feedback_repository()
            feedback_repo.create_feedback(feedback)
            flash('Thank you for your feedback! We will get back to you soon.', 'success')
            return redirect(url_for('feedback.contact'))
        except Exception as e:
            flash(f'Error submitting feedback: {str(e)}', 'error')
            return render_template('contact.html', 
                                 name=name, 
                                 email=email, 
                                 subject=subject, 
                                 message=message,
                                 feedback_type=feedback_type)
    
    # Pre-fill form with user's information
    name = current_user.name
    email = current_user.email
    
    return render_template('contact.html', name=name, email=email)

@feedback_bp.route('/admin/feedback')
@admin_required
def view_feedback(): # View all feedback
    
    # Get filter parameters
    status_filter = request.args.get('status', 'all')
    type_filter = request.args.get('type', 'all')
    search_query = request.args.get('search', '')
    
    # Query feedback using repository
    feedback_repo = RepositoryFactory.get_feedback_repository()
    db = database.db
    
    # Get all feedback first
    all_feedback = feedback_repo.get_all()
    
    # Filter by status
    if status_filter != 'all':
        all_feedback = [f for f in all_feedback if f.status == status_filter]
    
    # Filter by type
    if type_filter != 'all':
        all_feedback = [f for f in all_feedback if f.feedback_type == type_filter]
    
    # Filter by search
    if search_query:
        all_feedback = [f for f in all_feedback if (
            search_query.lower() in (f.subject or '').lower() or
            search_query.lower() in (f.message or '').lower() or
            search_query.lower() in (f.name or '').lower() or
            search_query.lower() in (f.email or '').lower()
        )]
    
    # Order by most recent first
    feedback_list = sorted(all_feedback, key=lambda x: x.created_at, reverse=True)
    
    # Get counts for filters
    all_feedback_all = feedback_repo.get_all()
    all_count = len(all_feedback_all)
    new_count = len(feedback_repo.get_by_status('new'))
    read_count = len(feedback_repo.get_by_status('read'))
    responded_count = len(feedback_repo.get_by_status('responded'))
    resolved_count = len(feedback_repo.get_by_status('resolved'))
    
    return render_template('admin_feedback.html',
                         feedback_list=feedback_list,
                         status_filter=status_filter,
                         type_filter=type_filter,
                         search_query=search_query,
                         all_count=all_count,
                         new_count=new_count,
                         read_count=read_count,
                         responded_count=responded_count,
                         resolved_count=resolved_count)

@feedback_bp.route('/admin/feedback/<int:feedback_id>')
@admin_required
def feedback_detail(feedback_id): # View feedback details
    feedback_repo = RepositoryFactory.get_feedback_repository()
    feedback = feedback_repo.get_by_id(feedback_id)
    
    if not feedback:
        flash('Feedback not found.', 'error')
        return redirect(url_for('feedback.view_feedback'))
    
    # Mark as read if it's new
    if feedback.status == 'new':
        feedback.status = 'read'
        feedback_repo.update_feedback(feedback)
    
    return render_template('admin_feedback_detail.html', feedback=feedback)

@feedback_bp.route('/admin/feedback/<int:feedback_id>/update-status', methods=['POST'])
@admin_required
def update_feedback_status(feedback_id): # Update feedback status
    feedback_repo = RepositoryFactory.get_feedback_repository()
    feedback = feedback_repo.get_by_id(feedback_id)
    
    if not feedback:
        flash('Feedback not found.', 'error')
        return redirect(url_for('feedback.view_feedback'))
    
    new_status = request.form.get('status')
    
    if new_status in ['new', 'read', 'responded', 'resolved']:
        feedback.status = new_status
        try:
            feedback_repo.update_feedback(feedback)
            flash(f'Feedback status updated to {new_status}.', 'success')
        except Exception as e:
            flash('Error updating feedback status.', 'error')
    
    return redirect(url_for('feedback.feedback_detail', feedback_id=feedback_id))

@feedback_bp.route('/admin/feedback/<int:feedback_id>/delete', methods=['POST'])
@admin_required
def delete_feedback(feedback_id): # Delete feedback
    feedback_repo = RepositoryFactory.get_feedback_repository()
    feedback = feedback_repo.get_by_id(feedback_id)
    
    if not feedback:
        flash('Feedback not found.', 'error')
        return redirect(url_for('feedback.view_feedback'))
    
    try:
        feedback_repo.delete_feedback(feedback)
        flash('Feedback deleted successfully.', 'success')
    except Exception as e:
        flash('Error deleting feedback.', 'error')
    
    return redirect(url_for('feedback.view_feedback'))

