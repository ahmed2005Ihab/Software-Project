from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from repositories.factory import RepositoryFactory
from core.database import database
from models.product import Product
from models.category import Category
from models.order import Order, OrderItem
from models.user import User
from models.cart import CartItem
from models.wishlist import WishlistItem
from models.review import Review
from functools import wraps
import os
from datetime import datetime, timedelta

admin_bp = Blueprint('admin', __name__)

def admin_required(f): # Decorator to require admin access
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('products.home'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@admin_required
def dashboard(): # Admin dashboard
    
    # Get today's date range
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Get statistics for today only
    order_repo = RepositoryFactory.get_order_repository()
    db = database.db
    
    # Total revenue excluding cancelled orders (today only)
    total_revenue = order_repo.get_total_revenue(start_date=today_start, exclude_cancelled=True)
    
    # Get orders for today
    today_orders = order_repo.get_orders_by_date_range(today_start).all()
    new_orders = len([o for o in today_orders if o.status == 'pending'])
    pending_returns = len([o for o in today_orders if o.status == 'cancelled'])
    
    # Get recent orders (today only, including cancelled orders)
    recent_orders = sorted(today_orders, key=lambda x: x.created_at, reverse=True)[:10]
    
    return render_template('admin_dashboard.html', 
                         total_revenue=float(total_revenue),
                         new_orders=new_orders,
                         pending_returns=pending_returns,
                         recent_orders=recent_orders)

@admin_bp.route('/products')
@admin_required
def manage_products(): # Manage all products (admin)

    # Get filter parameters
    search_query = request.args.get('search', '')
    category_filter = request.args.get('category', 'all')
    stock_filter = request.args.get('stock', 'all')  # all, in_stock, out_of_stock
    min_rating = request.args.get('min_rating', type=float)
    
    # Query products using repository
    product_repo = RepositoryFactory.get_product_repository()
    category_repo = RepositoryFactory.get_category_repository()
    
    # Get all products first
    if search_query:
        products = product_repo.search_products(search_query)
    else:
        products = product_repo.get_all()
    
    # Filter by category
    if category_filter != 'all':
        category = category_repo.get_by_name(category_filter)
        if category:
            products = [p for p in products if p.category_id == category.id]
    
    # Filter by stock status
    if stock_filter == 'in_stock':
        products = [p for p in products if p.stock_quantity > 0]
    elif stock_filter == 'out_of_stock':
        products = [p for p in products if p.stock_quantity == 0]
    
    # Filter by minimum rating (based on stored average rating)
    if min_rating is not None:
        products = [p for p in products if (p.rating or 0) >= min_rating]
    
    # Order by most recent first
    products = sorted(products, key=lambda x: x.created_at, reverse=True)
    
    # Get all categories for filter dropdown
    categories = category_repo.get_all_categories()
    
    return render_template('admin_manage_products.html', 
                         products=products,
                         search_query=search_query,
                         category_filter=category_filter,
                         stock_filter=stock_filter,
                         min_rating=min_rating,
                         categories=categories)

@admin_bp.route('/add-product', methods=['GET', 'POST'])
@admin_required
def add_product():
    """Add new product"""
    if request.method == 'POST':
        name = request.form.get('product-name')
        price = float(request.form.get('price', 0))
        category_name = request.form.get('category')
        description = request.form.get('description', '')
        
        # Handle image upload
        image_url = ''
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '':
                try:
                    # Use Flask's static folder path
                    static_folder = current_app.static_folder
                    images_dir = os.path.join(static_folder, 'images')
                    
                    # Ensure the directory exists
                    os.makedirs(images_dir, exist_ok=True)
                    
                    # Generate a unique filename
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = secure_filename(file.filename)
                    if not filename:
                        # If secure_filename returns empty, use a default
                        filename = 'uploaded_image'
                    name_part, ext = os.path.splitext(filename)
                    if not ext:
                        ext = '.jpg'  # Default extension if none provided
                    unique_filename = f"{name_part}_{timestamp}{ext}"
                    
                    # Save the file
                    file_path = os.path.join(images_dir, unique_filename)
                    file.save(file_path)
                    
                    # Verify file was saved
                    if os.path.exists(file_path):
                        # Store only the filename (not the full path)
                        image_url = unique_filename
                    else:
                        flash('Warning: Image file was not saved correctly.', 'error')
                except Exception as e:
                    flash(f'Error saving image: {str(e)}', 'error')
        
        # Get or create category
        category_repo = RepositoryFactory.get_category_repository()
        product_repo = RepositoryFactory.get_product_repository()
        
        category = category_repo.get_by_name(category_name)
        if not category:
            category = Category(name=category_name)
            category = category_repo.create_category(category)
        
        # Get stock quantity
        stock_quantity = int(request.form.get('stock_quantity', 0))
        
        # Create product
        product = Product(
            name=name,
            price=price,
            description=description,
            category_id=category.id,
            image_url=image_url,
            stock_quantity=stock_quantity,
            rating=5.0
        )
        
        try:
            product_repo.create(product)
            flash(f'Product "{name}" added successfully!', 'success')
            return redirect(url_for('admin.manage_products'))
        except Exception as e:
            flash(f'Error adding product: {str(e)}. Please try again.', 'error')
    
    category_repo = RepositoryFactory.get_category_repository()
    categories = category_repo.get_all_categories()
    return render_template('admin_add.html', categories=categories, product=None)

@admin_bp.route('/products/<int:product_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_product(product_id): # Edit existing product
    
    product_repo = RepositoryFactory.get_product_repository()
    product = product_repo.get_by_id(product_id)
    
    if not product:
        flash('Product not found.', 'error')
        return redirect(url_for('admin.manage_products'))
    
    if request.method == 'POST':
        product.name = request.form.get('product-name')
        product.price = float(request.form.get('price', 0))
        category_name = request.form.get('category')
        product.description = request.form.get('description', '')
        product.stock_quantity = int(request.form.get('stock_quantity', 0))
        
        # Handle image upload 
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '':
                try:
                    # Use Flask's static folder path
                    static_folder = current_app.static_folder
                    images_dir = os.path.join(static_folder, 'images')
                    
                    # Ensure the directory exists
                    os.makedirs(images_dir, exist_ok=True)
                    
                    # Generate a unique filename
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = secure_filename(file.filename)
                    if not filename:
                        filename = 'uploaded_image'
                    name_part, ext = os.path.splitext(filename)
                    if not ext:
                        ext = '.jpg'
                    unique_filename = f"{name_part}_{timestamp}{ext}"
                    
                    # Save the file
                    file_path = os.path.join(images_dir, unique_filename)
                    file.save(file_path)
                    
                    # Verify file was saved
                    if os.path.exists(file_path):
                        
                        old_image_path = os.path.join(images_dir, product.image_url)
                        if product.image_url and os.path.exists(old_image_path):
                             os.remove(old_image_path)
                        
                        # Store only the filename
                        product.image_url = unique_filename
                    else:
                        flash('Warning: Image file was not saved correctly.', 'error')
                except Exception as e:
                    flash(f'Error saving image: {str(e)}', 'error')
        
        # Get or create category
        category_repo = RepositoryFactory.get_category_repository()
        
        category = category_repo.get_by_name(category_name)
        if not category:
            category = Category(name=category_name)
            category = category_repo.create_category(category)
        
        product.category_id = category.id
        
        try:
            product_repo.update(product)
            flash(f'Product "{product.name}" updated successfully!', 'success')
            return redirect(url_for('admin.manage_products'))
        except Exception as e:
            flash(f'Error updating product: {str(e)}. Please try again.', 'error')
    
    category_repo = RepositoryFactory.get_category_repository()
    categories = category_repo.get_all_categories()
    return render_template('admin_add.html', categories=categories, product=product)

@admin_bp.route('/products/<int:product_id>/delete', methods=['POST'])
@admin_required
def delete_product(product_id): # Delete a product
    product_repo = RepositoryFactory.get_product_repository()
    order_item_repo = RepositoryFactory.get_order_item_repository()
    cart_item_repo = RepositoryFactory.get_cart_item_repository()
    wishlist_item_repo = RepositoryFactory.get_wishlist_item_repository()
    review_repo = RepositoryFactory.get_review_repository()
    
    product = product_repo.get_by_id(product_id)
    if not product:
        flash('Product not found.', 'error')
        return redirect(url_for('admin.manage_products'))
    
    product_name = product.name
    
    # Check if product has been ordered 
    order_items = order_item_repo.filter_by(product_id=product_id).all()
    order_items_count = len(order_items)
    
    if order_items_count > 0:
        flash(f'Cannot delete product "{product_name}" because it has been ordered {order_items_count} time(s). Products with order history cannot be deleted to maintain data integrity.', 'error')
        return redirect(url_for('admin.manage_products'))
    
    try:
        # Delete related cart items, wishlist items, and reviews
        cart_items = cart_item_repo.filter_by(product_id=product_id).all()
        for item in cart_items:
            cart_item_repo.delete_cart_item(item)
        
        wishlist_items = wishlist_item_repo.filter_by(product_id=product_id).all()
        for item in wishlist_items:
            wishlist_item_repo.delete_wishlist_item(item)
        
        reviews = review_repo.get_by_product_id(product_id)
        for review in reviews:
            review_repo.delete_review(review)
        
        # Now delete the product
        product_repo.delete(product)
        flash(f'Product "{product_name}" has been deleted.', 'success')
    except Exception as e:
        flash(f'Error deleting product: {str(e)}', 'error')
    
    return redirect(url_for('admin.manage_products'))

@admin_bp.route('/orders')
@admin_required
def view_orders(): # View all orders
    # Get filter parameters
    status_filter = request.args.get('status', 'all')
    search_query = request.args.get('search', '')
    
    # Query orders using repository
    order_repo = RepositoryFactory.get_order_repository()
    
    # Get all orders
    if status_filter != 'all':
        orders = order_repo.get_by_status(status_filter)
    else:
        orders = order_repo.get_all()
    
    # Filter by search (order number or customer name/email)
    if search_query:
        orders = [o for o in orders if (
            search_query.lower() in (o.order_number or '').lower() or
            search_query.lower() in (o.user.name or '').lower() or
            search_query.lower() in (o.user.email or '').lower()
        )]
    
    # Order by most recent first
    orders = sorted(orders, key=lambda x: x.created_at, reverse=True)
    
    # Get counts for status filter tabs
    all_orders = order_repo.get_all()
    all_count = len(all_orders)
    pending_count = len(order_repo.get_by_status('pending'))
    processing_count = len(order_repo.get_by_status('processing'))
    completed_count = len(order_repo.get_by_status('completed'))
    cancelled_count = len(order_repo.get_by_status('cancelled'))
    
    return render_template('admin_view_orders.html',
                         orders=orders,
                         status_filter=status_filter,
                         search_query=search_query,
                         all_count=all_count,
                         pending_count=pending_count,
                         processing_count=processing_count,
                         completed_count=completed_count,
                         cancelled_count=cancelled_count)

@admin_bp.route('/orders/<int:order_id>')
@admin_required
def order_details(order_id):
    """View order details"""
    order_repo = RepositoryFactory.get_order_repository()
    order = order_repo.get_by_id(order_id)
    
    if not order:
        flash('Order not found.', 'error')
        return redirect(url_for('admin.view_orders'))
    
    # Calculate breakdown
    order_items = order_repo.get_order_items(order.id)
    subtotal = sum(float(item.price) * item.quantity for item in order_items)
    tax = subtotal * 0.08
    shipping = float(order.total_amount) - subtotal - tax
    
    return render_template('admin_order_details.html', order=order, subtotal=subtotal, shipping=shipping, tax=tax, order_items=order_items)

@admin_bp.route('/orders/<int:order_id>/update-status', methods=['POST'])
@admin_required
def update_order_status(order_id):
    """Update order status"""
    order_repo = RepositoryFactory.get_order_repository()
    order = order_repo.get_by_id(order_id)
    
    if not order:
        flash('Order not found.', 'error')
        return redirect(url_for('admin.view_orders'))
    
    new_status = request.form.get('status')
    
    if new_status in ['pending', 'processing', 'completed', 'cancelled']:
        order.status = new_status
        try:
            order_repo.update_order(order)
            flash(f'Order {order.order_number} status updated to {new_status}.', 'success')
        except Exception as e:
            flash('Error updating order status.', 'error')
    
    # Check if request came from order details page or orders list
    if request.referrer and str(order_id) in request.referrer:
        return redirect(url_for('admin.order_details', order_id=order_id))
    return redirect(url_for('admin.view_orders'))

@admin_bp.route('/users')
@admin_required
def manage_users(): # Manage users
    # Get filter parameters
    user_type = request.args.get('type', 'all')  # all, admin, customer
    search_query = request.args.get('search', '')
    
    # Query users using repository
    user_repo = RepositoryFactory.get_user_repository()
    
    # Get users based on type
    if user_type == 'admin':
        users = user_repo.get_admins()
    elif user_type == 'customer':
        users = user_repo.get_customers()
    else:
        users = user_repo.get_all_users()
    
    # Filter by search
    if search_query:
        users = user_repo.search_users(search_query)
        # Apply type filter after search
        if user_type == 'admin':
            users = [u for u in users if u.is_admin]
        elif user_type == 'customer':
            users = [u for u in users if not u.is_admin]
    
    # Order by most recent first
    users = sorted(users, key=lambda x: x.created_at, reverse=True)
    
    # Get counts
    all_users = user_repo.get_all_users()
    all_count = len(all_users)
    admin_count = len(user_repo.get_admins())
    customer_count = len(user_repo.get_customers())
    
    return render_template('admin_manage_users.html',
                         users=users,
                         user_type=user_type,
                         search_query=search_query,
                         all_count=all_count,
                         admin_count=admin_count,
                         customer_count=customer_count)

@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id): # Delete a user
    user_repo = RepositoryFactory.get_user_repository()
    user = user_repo.get_by_id(user_id)
    
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('admin.manage_users'))
    
    # Prevent deleting yourself
    if user.id == current_user.id:
        flash('You cannot delete your own account.', 'error')
        return redirect(url_for('admin.manage_users'))
    
    # Prevent deleting the last admin
    if user.is_admin:
        admin_count = len(user_repo.get_admins())
        if admin_count <= 1:
            flash('Cannot delete the last admin user.', 'error')
            return redirect(url_for('admin.manage_users'))
    
    try:
        user_repo.delete_user(user)
        flash(f'User {user.email} has been deleted.', 'success')
    except Exception as e:
        flash('Error deleting user.', 'error')
    
    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/sales-reports')
@admin_required
def sales_reports(): # Sales reports and statistics
    # Get time period filter
    period = request.args.get('period', 'all')  # all, today, week, month, year
    
    # Calculate date range
    now = datetime.now()
    if period == 'today':
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == 'week':
        start_date = now - timedelta(days=7)
    elif period == 'month':
        start_date = now - timedelta(days=30)
    elif period == 'year':
        start_date = now - timedelta(days=365)
    else:
        start_date = None
    
    # Get statistics using repository
    order_repo = RepositoryFactory.get_order_repository()
    order_item_repo = RepositoryFactory.get_order_item_repository()
    
    # Calculate total revenue
    total_revenue = order_repo.get_total_revenue(start_date=start_date, exclude_cancelled=True)
    
    # Get orders for the period
    if start_date:
        period_orders = order_repo.get_orders_by_date_range(start_date).all()
    else:
        period_orders = order_repo.get_all()
    
    # Filter out cancelled orders for counts
    non_cancelled_orders = [o for o in period_orders if o.status != 'cancelled']
    total_orders = len(non_cancelled_orders)
    completed_orders = len([o for o in non_cancelled_orders if o.status == 'completed'])
    pending_orders = len([o for o in non_cancelled_orders if o.status == 'pending'])
    processing_orders = len([o for o in non_cancelled_orders if o.status == 'processing'])
    
    # Get cancelled orders count (for display, not included in revenue)
    cancelled_orders = len([o for o in period_orders if o.status == 'cancelled'])
    
    # Average order value
    avg_order_value = float(total_revenue) / total_orders if total_orders > 0 else 0
    
    # Recent orders for the period (including cancelled orders for display)
    recent_orders = sorted(period_orders, key=lambda x: x.created_at, reverse=True)[:20]
    
    # Top products (by quantity sold)
    top_products = order_item_repo.get_top_products(start_date=start_date, limit=10)
    
    return render_template('admin_sales_reports.html',
                         period=period,
                         total_revenue=float(total_revenue),
                         total_orders=total_orders,
                         completed_orders=completed_orders,
                         pending_orders=pending_orders,
                         processing_orders=processing_orders,
                         cancelled_orders=cancelled_orders,
                         avg_order_value=avg_order_value,
                         recent_orders=recent_orders,
                         top_products=top_products)

@admin_bp.route('/categories')
@admin_required
def manage_categories(): # Manage all categories (admin)
    # Get search parameter
    search_query = request.args.get('search', '')
    
    # Query categories using repository
    category_repo = RepositoryFactory.get_category_repository()
    product_repo = RepositoryFactory.get_product_repository()
    
    # Get categories
    if search_query:
        categories = category_repo.search_categories(search_query)
    else:
        categories = category_repo.get_all_categories()
    
    # Sort by name
    categories = sorted(categories, key=lambda x: x.name)
    
    # Get product count for each category
    category_data = []
    for category in categories:
        products = product_repo.get_by_category(category.id)
        product_count = len(products)
        category_data.append({
            'category': category,
            'product_count': product_count
        })
    
    return render_template('admin_manage_categories.html', 
                         category_data=category_data,
                         search_query=search_query)

@admin_bp.route('/categories/add', methods=['GET', 'POST'])
@admin_required
def add_category(): # Add new category
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        
        # Validate name
        if not name:
            flash('Category name is required.', 'error')
            return render_template('admin_add_category.html', name=name, description=description)
        
        # Check if category already exists
        category_repo = RepositoryFactory.get_category_repository()
        existing_category = category_repo.get_by_name(name)
        if existing_category:
            flash(f'Category "{name}" already exists!', 'error')
            return render_template('admin_add_category.html', name=name, description=description)
        
        # Create new category
        try:
            category = Category(name=name, description=description if description else None)
            category_repo.create_category(category)
            flash(f'Category "{name}" added successfully!', 'success')
            return redirect(url_for('admin.manage_categories'))
        except Exception as e:
            flash(f'Error adding category: {str(e)}. Please try again.', 'error')
            return render_template('admin_add_category.html', name=name, description=description)
    
    return render_template('admin_add_category.html')

@admin_bp.route('/categories/<int:category_id>/delete', methods=['POST'])
@admin_required
def delete_category(category_id): # Delete a category
    category_repo = RepositoryFactory.get_category_repository()
    product_repo = RepositoryFactory.get_product_repository()
    
    category = category_repo.get_by_id(category_id)
    if not category:
        flash('Category not found.', 'error')
        return redirect(url_for('admin.manage_categories'))
    
    category_name = category.name
    
    # Check if category has products
    products = product_repo.get_by_category(category_id)
    product_count = len(products)
    if product_count > 0:
        flash(f'Cannot delete category "{category_name}" because it has {product_count} product(s). Please remove or reassign products first.', 'error')
        return redirect(url_for('admin.manage_categories'))
    
    try:
        category_repo.delete_category(category)
        flash(f'Category "{category_name}" has been deleted.', 'success')
    except Exception as e:
        flash('Error deleting category.', 'error')
    
    return redirect(url_for('admin.manage_categories'))

