from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from repositories.factory import RepositoryFactory
from models.user import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Check if user was redirected from shopping/cart
    shopping_redirect = request.args.get('shopping', 'false') == 'true'
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user_type = request.form.get('user_type', 'customer')
        
        user_repo = RepositoryFactory.get_user_repository()
        user = user_repo.get_by_email(email)
        
        if user and user.check_password(password):
            # Check if user type matches
            if user_type == 'admin' and not user.is_admin:
                flash('Access denied. Admin login required.', 'error')
                return render_template('login.html', shopping_redirect=shopping_redirect)
            elif user_type == 'customer' and user.is_admin:
                flash('Please use admin login for admin accounts.', 'error')
                return render_template('login.html', shopping_redirect=shopping_redirect)
            
            login_user(user)
            flash('Login successful!', 'success')
            
            if user.is_admin:
                return redirect(url_for('admin.dashboard'))
            else:
                # If redirected from shopping, go back to products page
                if shopping_redirect:
                    return redirect(url_for('products.products'))
                return redirect(url_for('products.home'))
        else:
            flash('Invalid email or password.', 'error')
    
    return render_template('login.html', shopping_redirect=shopping_redirect)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        address = request.form.get('Address', '')
        phone_number = request.form.get('phone', '')
        
        # Check if user already exists
        user_repo = RepositoryFactory.get_user_repository()
        if user_repo.get_by_email(email):
            flash('Email already registered. Please login.', 'error')
            return render_template('register.html')
        
        # Create new user
        user = User(
            name=name,
            email=email,
            address=address,
            phone_number=phone_number,
            is_admin=False
        )
        user.set_password(password)
        
        try:
            user_repo.create_user(user)
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            flash('Registration failed. Please try again.', 'error')
    
    return render_template('register.html')

@auth_bp.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('products.home'))

@auth_bp.route('/profile')
@login_required
def profile(): # View user profile
    return render_template('profile.html', user=current_user)

@auth_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile(): # Edit user profile
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        address = request.form.get('address', '').strip()
        phone_number = request.form.get('phone_number', '').strip()
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validate required fields
        if not name:
            flash('Name is required.', 'error')
            return render_template('profile.html', user=current_user, editing=True)
        
        if not email:
            flash('Email is required.', 'error')
            return render_template('profile.html', user=current_user, editing=True)
        
        # Check if email is being changed and if it's already taken
        user_repo = RepositoryFactory.get_user_repository()
        if email != current_user.email:
            existing_user = user_repo.get_by_email(email)
            if existing_user:
                flash('Email already registered. Please use a different email.', 'error')
                return render_template('profile.html', user=current_user, editing=True)
        
        # Update user information
        current_user.name = name
        current_user.email = email
        current_user.address = address if address else None
        current_user.phone_number = phone_number if phone_number else None
        
        # Handle password change if provided
        if new_password:
            if not current_password:
                flash('Current password is required to change password.', 'error')
                return render_template('profile.html', user=current_user, editing=True)
            
            if not current_user.check_password(current_password):
                flash('Current password is incorrect.', 'error')
                return render_template('profile.html', user=current_user, editing=True)
            
            if new_password != confirm_password:
                flash('New passwords do not match.', 'error')
                return render_template('profile.html', user=current_user, editing=True)
            
            if len(new_password) < 6:
                flash('New password must be at least 6 characters long.', 'error')
                return render_template('profile.html', user=current_user, editing=True)
            
            current_user.set_password(new_password)
        
        try:
            user_repo.update_user(current_user)
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('auth.profile'))
        except Exception as e:
            flash(f'Error updating profile: {str(e)}. Please try again.', 'error')
            return render_template('profile.html', user=current_user, editing=True)
    
    return render_template('profile.html', user=current_user, editing=True)

