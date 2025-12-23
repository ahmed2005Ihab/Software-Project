from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_required, current_user
from repositories.factory import RepositoryFactory
from models.cart import Cart, CartItem
from models.product import Product
from models.order import Order, OrderItem
from models.wishlist import Wishlist, WishlistItem
from models.review import Review
from datetime import datetime
import random
import string

cart_bp = Blueprint('cart', __name__)

def get_or_create_cart(user_id): # Get user's cart or create one if it doesn't exist
    cart_repo = RepositoryFactory.get_cart_repository()
    return cart_repo.get_or_create_cart(user_id)

def get_or_create_wishlist(user_id): # Get user's wishlist or create one if it doesn't exist
    wishlist_repo = RepositoryFactory.get_wishlist_repository()
    return wishlist_repo.get_or_create_wishlist(user_id)

@cart_bp.route('/')
@login_required
def view_cart(): # View shopping cart
    cart = get_or_create_cart(current_user.id)
    
    # Calculate totals
    subtotal = cart.get_total()
    shipping = 0.00 if subtotal >= 500 else 50.00
    tax = subtotal * 0.08
    total = subtotal + shipping + tax
    
    return render_template('cart.html', 
                         cart=cart, 
                         subtotal=subtotal,
                         shipping=shipping,
                         tax=tax,
                         total=total)

@cart_bp.route('/add/<int:product_id>', methods=['POST'])
def add_to_cart(product_id): # Add product to cart
    # Check if user is authenticated
    if not current_user.is_authenticated:
        # For AJAX requests, return JSON response indicating login is required
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': False,
                'message': 'Please login to add items to cart.',
                'requires_login': True,
                'login_url': url_for('auth.login', shopping='true')
            }), 401
        # For regular requests, redirect to login page with shopping parameter
        return redirect(url_for('auth.login', shopping='true'))
    
    product_repo = RepositoryFactory.get_product_repository()
    product = product_repo.get_by_id(product_id)
    if not product:
        flash('Product not found.', 'error')
        return redirect(url_for('products.products'))
    
    quantity = int(request.form.get('quantity', 1))
    
    # Check if product is in stock
    if product.stock_quantity <= 0:
        error_message = f'{product.name} is out of stock.'
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': False,
                'message': error_message
            }), 400
        flash(error_message, 'error')
        if request.referrer and 'product' in request.referrer:
            return redirect(url_for('products.product_detail', product_id=product_id))
        return redirect(url_for('products.products'))
    
    cart = get_or_create_cart(current_user.id)
    
    # Check if item already in cart
    cart_item_repo = RepositoryFactory.get_cart_item_repository()
    cart_item = cart_item_repo.get_by_cart_and_product(cart.id, product_id)
    
    # Calculate total quantity that will be in cart after this operation
    if cart_item:
        new_quantity = cart_item.quantity + quantity
    else:
        new_quantity = quantity
    
    # Validate stock availability
    if new_quantity > product.stock_quantity:
        available = product.stock_quantity
        error_message = f'Only {available} unit(s) of {product.name} available in stock. You tried to add {new_quantity} unit(s).'
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': False,
                'message': error_message,
                'available_stock': available
            }), 400
        flash(error_message, 'error')
        if request.referrer and 'product' in request.referrer:
            return redirect(url_for('products.product_detail', product_id=product_id))
        return redirect(url_for('products.products'))
    
    if cart_item:
        cart_item.quantity = new_quantity
        cart_item_repo.update_cart_item(cart_item)
        message = f'{product.name} added to cart successfully!'
    else:
        cart_item = CartItem(cart_id=cart.id, product_id=product_id, quantity=quantity)
        cart_item = cart_item_repo.create_cart_item(cart_item)
        message = f'{product.name} added to cart successfully!'
    
    # Check if this is an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            return jsonify({
                'success': True,
                'message': message,
                'cart_item_id': cart_item.id,
                'cart_quantity': cart_item.quantity
            }), 200
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Error adding to cart: {str(e)}'
            }), 500
    
    # Non-AJAX request handling (for backward compatibility)
    try:
        flash(message, 'success')
    except Exception as e:
        flash(f'Error adding to cart: {str(e)}', 'error')
    
    # Redirect based on where the request came from
    if request.referrer and 'product' in request.referrer:
        return redirect(url_for('products.product_detail', product_id=product_id))
    return redirect(url_for('products.products'))

@cart_bp.route('/update/<int:item_id>', methods=['POST'])
@login_required
def update_quantity(item_id): # Update cart item quantity
    cart_item_repo = RepositoryFactory.get_cart_item_repository()
    cart_repo = RepositoryFactory.get_cart_repository()
    product_repo = RepositoryFactory.get_product_repository()
    
    cart_item = cart_item_repo.get_by_id(item_id)
    if not cart_item:
        flash('Cart item not found.', 'error')
        return redirect(url_for('cart.view_cart'))
    
    cart = cart_repo.get_by_id(cart_item.cart_id)
    if not cart:
        flash('Cart not found.', 'error')
        return redirect(url_for('cart.view_cart'))
    
    # Verify cart belongs to current user
    if cart.user_id != current_user.id:
        flash('Unauthorized access.', 'error')
        return redirect(url_for('cart.view_cart'))
    
    quantity = int(request.form.get('quantity', 1))
    
    if quantity <= 0:
        cart_item_repo.delete_cart_item(cart_item)
        flash('Item removed from cart!', 'success')
        return redirect(url_for('cart.view_cart'))
    
    # Check stock availability
    product = product_repo.get_by_id(cart_item.product_id)
    if not product:
        flash('Product not found.', 'error')
        return redirect(url_for('cart.view_cart'))
    
    if product.stock_quantity <= 0:
        flash(f'{product.name} is out of stock. Please remove it from your cart.', 'error')
        return redirect(url_for('cart.view_cart'))
    
    if quantity > product.stock_quantity:
        flash(f'Only {product.stock_quantity} unit(s) of {product.name} available in stock. Quantity updated to available stock.', 'error')
        quantity = product.stock_quantity
    
    cart_item.quantity = quantity
    cart_item_repo.update_cart_item(cart_item)
    flash('Cart updated!', 'success')
    return redirect(url_for('cart.view_cart'))

@cart_bp.route('/remove/<int:item_id>', methods=['POST'])
@login_required
def remove_from_cart(item_id): # Remove item from cart
    cart_item_repo = RepositoryFactory.get_cart_item_repository()
    cart_repo = RepositoryFactory.get_cart_repository()
    
    cart_item = cart_item_repo.get_by_id(item_id)
    if not cart_item:
        flash('Cart item not found.', 'error')
        return redirect(url_for('cart.view_cart'))
    
    cart = cart_repo.get_by_id(cart_item.cart_id)
    if not cart:
        flash('Cart not found.', 'error')
        return redirect(url_for('cart.view_cart'))
    
    # Verify cart belongs to current user
    if cart.user_id != current_user.id:
        flash('Unauthorized access.', 'error')
        return redirect(url_for('cart.view_cart'))
    
    cart_item_repo.delete_cart_item(cart_item)
    flash('Item removed from cart!', 'success')
    return redirect(url_for('cart.view_cart'))

@cart_bp.route('/checkout')
@login_required
def checkout(): # Checkout page
    cart = get_or_create_cart(current_user.id)
    
    # Check if cart is empty
    if not cart.items:
        flash('Your cart is empty. Add items before checkout.', 'error')
        return redirect(url_for('cart.view_cart'))
    
    # Validate stock availability for all cart items
    stock_errors = []
    items_to_remove = []
    items_adjusted = False
    
    product_repo = RepositoryFactory.get_product_repository()
    cart_item_repo = RepositoryFactory.get_cart_item_repository()
    
    for cart_item in cart.items:
        product = product_repo.get_by_id(cart_item.product_id)
        if not product:
            items_to_remove.append(cart_item)
            stock_errors.append(f'{cart_item.product.name if cart_item.product else "Product"} is no longer available.')
            continue
        
        if product.stock_quantity <= 0:
            items_to_remove.append(cart_item)
            stock_errors.append(f'{product.name} is out of stock.')
        elif cart_item.quantity > product.stock_quantity:
            cart_item.quantity = product.stock_quantity
            cart_item_repo.update_cart_item(cart_item)
            items_adjusted = True
            stock_errors.append(f'{product.name} quantity adjusted to available stock ({product.stock_quantity} unit(s)).')
    
    # Remove out-of-stock items from cart
    for cart_item in items_to_remove:
        cart_item_repo.delete_cart_item(cart_item)
    
    # Commit changes if any adjustments were made
    if stock_errors or items_adjusted:
        pass  # Changes already committed by repository methods
        # Reload cart to reflect changes
        cart = get_or_create_cart(current_user.id)
        for error in stock_errors:
            flash(error, 'error')
        # If cart is now empty, redirect to cart page
        if not cart.items:
            return redirect(url_for('cart.view_cart'))
    
    # Calculate totals
    subtotal = cart.get_total()
    shipping = 0.00 if subtotal >= 500 else 50.00
    tax = subtotal * 0.08
    total = subtotal + shipping + tax
    
    return render_template('checkout.html',
                         cart=cart,
                         subtotal=subtotal,
                         shipping=shipping,
                         tax=tax,
                         total=total)

@cart_bp.route('/payment', methods=['GET', 'POST'])
@login_required
def payment(): # Payment page
    if request.method == 'POST':
        # This is coming from checkout page - validate and show payment form
        shipping_address = request.form.get('shipping_address', '').strip()
        
        if not shipping_address:
            flash('Please provide a shipping address.', 'error')
            return redirect(url_for('cart.checkout'))
        
        cart = get_or_create_cart(current_user.id)
        
        # Check if cart is empty
        if not cart.items:
            flash('Your cart is empty.', 'error')
            return redirect(url_for('cart.view_cart'))
        
        # Validate stock availability for all cart items before proceeding to payment
        product_repo = RepositoryFactory.get_product_repository()
        cart_item_repo = RepositoryFactory.get_cart_item_repository()
        
        stock_errors = []
        items_to_remove = []
        for cart_item in cart.items:
            product = product_repo.get_by_id(cart_item.product_id)
            if not product:
                items_to_remove.append(cart_item)
                stock_errors.append(f'{cart_item.product.name if cart_item.product else "Product"} is no longer available.')
                continue
            
            if product.stock_quantity <= 0:
                items_to_remove.append(cart_item)
                stock_errors.append(f'{product.name} is out of stock.')
            elif cart_item.quantity > product.stock_quantity:
                items_to_remove.append(cart_item)
                stock_errors.append(f'Only {product.stock_quantity} unit(s) of {product.name} available. You have {cart_item.quantity} in cart.')
        
        # Remove problematic items from cart
        for cart_item in items_to_remove:
            cart_item_repo.delete_cart_item(cart_item)
        
        if stock_errors:
            for error in stock_errors:
                flash(error, 'error')
            return redirect(url_for('cart.view_cart'))
        
        # Re-check if cart is empty after removing items
        cart = get_or_create_cart(current_user.id)  # Reload cart
        if not cart.items:
            flash('Your cart is empty after removing out-of-stock items.', 'error')
            return redirect(url_for('cart.view_cart'))
        
        # Calculate totals
        subtotal = cart.get_total()
        shipping = 0.00 if subtotal >= 500 else 50.00
        tax = subtotal * 0.08
        total = subtotal + shipping + tax
        
        # Store shipping address in session temporarily
        session['pending_shipping_address'] = shipping_address
        
        return render_template('payment.html',
                             cart=cart,
                             subtotal=subtotal,
                             shipping=shipping,
                             tax=tax,
                             total=total,
                             shipping_address=shipping_address)
    
    # GET request - redirect to checkout if no pending order
    flash('Please complete checkout first.', 'error')
    return redirect(url_for('cart.checkout'))

@cart_bp.route('/place-order', methods=['POST'])
@login_required
def place_order(): # Place order from payment page
    cart = get_or_create_cart(current_user.id)
    
    # Check if cart is empty
    if not cart.items:
        flash('Your cart is empty.', 'error')
        return redirect(url_for('cart.view_cart'))
    
    # Get shipping address from session or form
    shipping_address = session.get('pending_shipping_address', '').strip()
    if not shipping_address:
        shipping_address = request.form.get('shipping_address', '').strip()
    
    if not shipping_address:
        flash('Please provide a shipping address.', 'error')
        return redirect(url_for('cart.checkout'))
    
    # Get payment method
    payment_method = request.form.get('payment_method', '').strip()
    if not payment_method:
        flash('Please select a payment method.', 'error')
        return redirect(url_for('cart.payment'))
    
    # Validate stock availability for all cart items before placing order
    product_repo = RepositoryFactory.get_product_repository()
    order_repo = RepositoryFactory.get_order_repository()
    order_item_repo = RepositoryFactory.get_order_item_repository()
    cart_item_repo = RepositoryFactory.get_cart_item_repository()
    
    stock_errors = []
    for cart_item in cart.items:
        product = product_repo.get_by_id(cart_item.product_id)
        if not product:
            stock_errors.append(f'{cart_item.product.name if cart_item.product else "Product"} is no longer available.')
            continue
        
        if product.stock_quantity <= 0:
            stock_errors.append(f'{product.name} is out of stock.')
        elif cart_item.quantity > product.stock_quantity:
            stock_errors.append(f'Only {product.stock_quantity} unit(s) of {product.name} available. You have {cart_item.quantity} in cart.')
    
    if stock_errors:
        error_message = 'Cannot place order: ' + ' '.join(stock_errors)
        flash(error_message, 'error')
        return redirect(url_for('cart.view_cart'))
    
    # Calculate totals
    subtotal = cart.get_total()
    shipping = 0.00 if subtotal >= 500 else 50.00
    tax = subtotal * 0.08
    total = subtotal + shipping + tax
    
    # Generate unique order number
    order_number = 'ORD-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    
    # Create order
    order = Order(
        user_id=current_user.id,
        order_number=order_number,
        status='pending',
        total_amount=total,
        shipping_address=shipping_address
    )
    
    try:
        order = order_repo.create_order(order)
        
        # Create order items from cart items and update stock
        for cart_item in cart.items:
            product = product_repo.get_by_id(cart_item.product_id)
            
            # Double-check stock before creating order item
            if product.stock_quantity < cart_item.quantity:
                flash(f'Insufficient stock for {product.name}. Only {product.stock_quantity} unit(s) available.', 'error')
                return redirect(url_for('cart.view_cart'))
            
            order_item = OrderItem(
                order_id=order.id,
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
                price=cart_item.product.price  # Store price at time of order
            )
            order_item_repo.create_order_item(order_item)
            
            # Update product stock
            product_repo.update_stock(product.id, -cart_item.quantity)
        
        # Clear cart after order is placed
        cart_item_repo.delete_by_cart_id(cart.id)
        
        # Clear session data
        session.pop('pending_shipping_address', None)
        
        flash(f'Order placed successfully! Order number: {order_number}', 'success')
        return redirect(url_for('cart.order_history'))
    except Exception as e:
        flash(f'Error placing order: {str(e)}', 'error')
        return redirect(url_for('cart.payment'))

@cart_bp.route('/orders')
@login_required
def order_history(): # View customer order history
    # Get filter parameters
    status_filter = request.args.get('status', 'all')
    
    # Query orders for current user
    order_repo = RepositoryFactory.get_order_repository()
    
    # Filter by status
    if status_filter != 'all':
        orders = order_repo.get_user_orders_by_status(current_user.id, status_filter)
        # Order by most recent first
        orders = sorted(orders, key=lambda x: x.created_at, reverse=True)
    else:
        orders = order_repo.get_by_user_id(current_user.id)
        # Order by most recent first
        orders = sorted(orders, key=lambda x: x.created_at, reverse=True)
    
    # Get counts for status filter tabs
    all_orders = order_repo.get_by_user_id(current_user.id)
    all_count = len(all_orders)
    pending_count = len(order_repo.get_user_orders_by_status(current_user.id, 'pending'))
    processing_count = len(order_repo.get_user_orders_by_status(current_user.id, 'processing'))
    completed_count = len(order_repo.get_user_orders_by_status(current_user.id, 'completed'))
    cancelled_count = len(order_repo.get_user_orders_by_status(current_user.id, 'cancelled'))
    
    return render_template('order_history.html',
                         orders=orders,
                         status_filter=status_filter,
                         all_count=all_count,
                         pending_count=pending_count,
                         processing_count=processing_count,
                         completed_count=completed_count,
                         cancelled_count=cancelled_count)

@cart_bp.route('/orders/<int:order_id>')
@login_required
def order_details(order_id): # View order details for customer
    order_repo = RepositoryFactory.get_order_repository()
    review_repo = RepositoryFactory.get_review_repository()
    
    order = order_repo.get_by_id(order_id)
    if not order:
        flash('Order not found.', 'error')
        return redirect(url_for('cart.order_history'))
    
    # Verify order belongs to current user
    if order.user_id != current_user.id:
        flash('Unauthorized access.', 'error')
        return redirect(url_for('cart.order_history'))
    
    # Calculate breakdown
    order_items = order_repo.get_order_items(order.id)
    subtotal = sum(float(item.price) * item.quantity for item in order_items)
    tax = subtotal * 0.08
    shipping = float(order.total_amount) - subtotal - tax
    
    # Get existing reviews for products in this order
    existing_reviews = {}
    if order.status == 'completed':
        for item in order_items:
            review = review_repo.get_by_user_product_order(
                current_user.id,
                item.product_id,
                order.id
            )
            if review:
                existing_reviews[item.product_id] = review
    
    return render_template('order_details.html', 
                         order=order, 
                         subtotal=subtotal, 
                         shipping=shipping, 
                         tax=tax,
                         existing_reviews=existing_reviews,
                         order_items=order_items)

@cart_bp.route('/orders/<int:order_id>/cancel', methods=['POST'])
@login_required
def cancel_order(order_id): # Cancel an order
    order_repo = RepositoryFactory.get_order_repository()
    product_repo = RepositoryFactory.get_product_repository()
    
    order = order_repo.get_by_id(order_id)
    if not order:
        flash('Order not found.', 'error')
        return redirect(url_for('cart.order_history'))
    
    # Verify order belongs to current user
    if order.user_id != current_user.id:
        flash('Unauthorized access.', 'error')
        return redirect(url_for('cart.order_history'))
    
    # Check if order can be cancelled (only pending or processing orders)
    if order.status not in ['pending', 'processing']:
        if order.status == 'cancelled':
            flash('This order has already been cancelled.', 'error')
        elif order.status == 'completed':
            flash('Completed orders cannot be cancelled.', 'error')
        else:
            flash('This order cannot be cancelled.', 'error')
        return redirect(url_for('cart.order_details', order_id=order_id))
    
    try:
        # Restore stock quantities for all items in the order
        order_items = order_repo.get_order_items(order.id)
        for order_item in order_items:
            product = product_repo.get_by_id(order_item.product_id)
            if product:
                product_repo.update_stock(product.id, order_item.quantity)
        
        # Update order status to cancelled
        order.status = 'cancelled'
        order_repo.update_order(order)
        
        flash(f'Order #{order.order_number} has been cancelled successfully. Stock quantities have been restored.', 'success')
        return redirect(url_for('cart.order_history'))
    except Exception as e:
        flash(f'Error cancelling order: {str(e)}', 'error')
        return redirect(url_for('cart.order_details', order_id=order_id))

@cart_bp.route('/wishlist')
@login_required
def view_wishlist(): # View wishlist
    wishlist = get_or_create_wishlist(current_user.id)
    
    # Get cart quantities for each product in wishlist
    cart_repo = RepositoryFactory.get_cart_repository()
    cart_quantity_map = {}  # product_id -> cart_quantity
    cart = cart_repo.get_by_user_id(current_user.id)
    if cart:
        cart_items = cart_repo.get_cart_items(cart.id)
        for cart_item in cart_items:
            cart_quantity_map[cart_item.product_id] = cart_item.quantity
    
    return render_template('wishlist.html', wishlist=wishlist, cart_quantity_map=cart_quantity_map)

@cart_bp.route('/wishlist/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_wishlist(product_id): # Add product to wishlist
    product_repo = RepositoryFactory.get_product_repository()
    wishlist_repo = RepositoryFactory.get_wishlist_repository()
    wishlist_item_repo = RepositoryFactory.get_wishlist_item_repository()
    
    product = product_repo.get_by_id(product_id)
    if not product:
        flash('Product not found.', 'error')
        return redirect(url_for('products.products'))
    
    wishlist = get_or_create_wishlist(current_user.id)
    
    # Check if item already in wishlist
    wishlist_item = wishlist_item_repo.get_by_wishlist_and_product(wishlist.id, product_id)
    
    # Check if this is an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if wishlist_item:
            return jsonify({
                'success': False,
                'message': f'{product.name} is already in your wishlist!',
                'already_in_wishlist': True
            }), 200
        else:
            wishlist_item = WishlistItem(wishlist_id=wishlist.id, product_id=product_id)
            wishlist_item = wishlist_item_repo.create_wishlist_item(wishlist_item)
            return jsonify({
                'success': True,
                'message': f'{product.name} added to the wish list successfully!',
                'item_id': wishlist_item.id
            }), 200
    
    # Non-AJAX request handling (for backward compatibility)
    if wishlist_item:
        flash(f'{product.name} is already in your wishlist!', 'info')
    else:
        wishlist_item = WishlistItem(wishlist_id=wishlist.id, product_id=product_id)
        wishlist_item_repo.create_wishlist_item(wishlist_item)
        flash(f'{product.name} added to wishlist!', 'success')
    
    # Redirect based on where the request came from
    if request.referrer and 'product' in request.referrer:
        return redirect(url_for('products.product_detail', product_id=product_id))
    elif request.referrer and 'wishlist' in request.referrer:
        return redirect(url_for('cart.view_wishlist'))
    return redirect(url_for('products.products'))

@cart_bp.route('/wishlist/remove/<int:item_id>', methods=['POST'])
@login_required
def remove_from_wishlist(item_id): # Remove item from wishlist
    wishlist_item_repo = RepositoryFactory.get_wishlist_item_repository()
    wishlist_repo = RepositoryFactory.get_wishlist_repository()
    
    wishlist_item = wishlist_item_repo.get_by_id(item_id)
    if not wishlist_item:
        flash('Wishlist item not found.', 'error')
        return redirect(url_for('cart.view_wishlist'))
    
    wishlist = wishlist_repo.get_by_id(wishlist_item.wishlist_id)
    if not wishlist:
        flash('Wishlist not found.', 'error')
        return redirect(url_for('cart.view_wishlist'))
    
    # Verify wishlist belongs to current user
    if wishlist.user_id != current_user.id:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': False,
                'message': 'Unauthorized access.'
            }), 403
        flash('Unauthorized access.', 'error')
        return redirect(url_for('cart.view_wishlist'))
    
    product_name = wishlist_item.product.name if wishlist_item.product else 'Product'
    product_id = wishlist_item.product_id
    
    # Check if this is an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        wishlist_item_repo.delete_wishlist_item(wishlist_item)
        return jsonify({
            'success': True,
            'message': f'{product_name} removed from wishlist!',
            'product_id': product_id
        }), 200
    
    # Non-AJAX request handling
    wishlist_item_repo.delete_wishlist_item(wishlist_item)
    flash(f'{product_name} removed from wishlist!', 'success')
    return redirect(url_for('cart.view_wishlist'))

@cart_bp.route('/orders/<int:order_id>/review/<int:product_id>', methods=['GET', 'POST'])
@login_required
def create_review(order_id, product_id): # Create or update review for a product from a completed order
    order_repo = RepositoryFactory.get_order_repository()
    product_repo = RepositoryFactory.get_product_repository()
    order_item_repo = RepositoryFactory.get_order_item_repository()
    review_repo = RepositoryFactory.get_review_repository()
    
    order = order_repo.get_by_id(order_id)
    if not order:
        flash('Order not found.', 'error')
        return redirect(url_for('cart.order_history'))
    
    product = product_repo.get_by_id(product_id)
    if not product:
        flash('Product not found.', 'error')
        return redirect(url_for('cart.order_details', order_id=order_id))
    
    # Verify order belongs to current user
    if order.user_id != current_user.id:
        flash('Unauthorized access.', 'error')
        return redirect(url_for('cart.order_history'))
    
    # Verify order is completed
    if order.status != 'completed':
        flash('You can only review products from completed orders.', 'error')
        return redirect(url_for('cart.order_details', order_id=order_id))
    
    # Verify product is in the order
    order_item = order_item_repo.get_by_order_and_product(order_id, product_id)
    if not order_item:
        flash('This product is not in this order.', 'error')
        return redirect(url_for('cart.order_details', order_id=order_id))
    
    if request.method == 'POST':
        rating = int(request.form.get('rating', 0))
        comment = request.form.get('comment', '').strip()
        
        # Validate rating
        if rating < 1 or rating > 5:
            flash('Please select a valid rating (1-5 stars).', 'error')
            return redirect(url_for('cart.create_review', order_id=order_id, product_id=product_id))
        
        # Check if review already exists
        review = review_repo.get_by_user_product_order(
            current_user.id,
            product_id,
            order_id
        )
        
        if review:
            # Update existing review
            review.rating = rating
            review.comment = comment
            review_repo.update_review(review)
            flash('Review updated successfully!', 'success')
        else:
            # Create new review
            review = Review(
                user_id=current_user.id,
                product_id=product_id,
                order_id=order_id,
                rating=rating,
                comment=comment
            )
            review_repo.create_review(review)
            flash('Review submitted successfully!', 'success')
        
        try:
            # Update product average rating
            product.rating = product.get_average_rating()
            product_repo.update(product)
            
            return redirect(url_for('cart.order_details', order_id=order_id))
        except Exception as e:
            flash(f'Error saving review: {str(e)}', 'error')
            return redirect(url_for('cart.create_review', order_id=order_id, product_id=product_id))
    
    # GET request - show review form
    existing_review = review_repo.get_by_user_product_order(
        current_user.id,
        product_id,
        order_id
    )
    
    return render_template('review_form.html', 
                         order=order, 
                         product=product, 
                         existing_review=existing_review)

