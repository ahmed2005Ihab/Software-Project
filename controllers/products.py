from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user
from repositories.factory import RepositoryFactory
from models.product import Product
from models.category import Category
from models.wishlist import Wishlist, WishlistItem
from models.review import Review
from models.cart import Cart, CartItem

products_bp = Blueprint('products', __name__)

@products_bp.route('/', strict_slashes=False)
@products_bp.route('/home', strict_slashes=False)
def home():
    """Home page"""
    return render_template('home.html')

@products_bp.route('/products', strict_slashes=False)
def products(): # Products listing page
    # Get repositories
    product_repo = RepositoryFactory.get_product_repository()
    category_repo = RepositoryFactory.get_category_repository()
    wishlist_repo = RepositoryFactory.get_wishlist_repository()
    cart_repo = RepositoryFactory.get_cart_repository()
    
    # Get filter parameters
    categories_filter = request.args.getlist('categories')  # Multiple categories
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    min_rating = request.args.get('min_rating', type=float)
    search_query = request.args.get('search', '')
    
    # Query products
    query = product_repo.query()
    
    # Filter by categories (multiple selection)
    if categories_filter:
        category_ids = []
        for cat_name in categories_filter:
            category = category_repo.get_by_name(cat_name)
            if category:
                category_ids.append(category.id)
        if category_ids:
            query = query.filter(Product.category_id.in_(category_ids))
    
    # Filter by price range
    if min_price is not None or max_price is not None:
        query = product_repo.filter_by_price_range(min_price, max_price)
    
    # Filter by search query
    if search_query:
        products_list = product_repo.search_products(search_query)
        # Apply other filters if needed
        if categories_filter or min_price is not None or max_price is not None:
            filtered_list = []
            for p in products_list:
                if categories_filter:
                    if p.category_id not in category_ids:
                        continue
                if min_price is not None and float(p.price) < min_price:
                    continue
                if max_price is not None and float(p.price) > max_price:
                    continue
                filtered_list.append(p)
            products_list = filtered_list
    else:
        products_list = query.all()

    # Filter by rating based on customer reviews / stored average rating
    if min_rating is not None:
        products_list = [p for p in products_list if (p.rating or 0) >= min_rating]
    
    categories = category_repo.get_all_categories()
    
    # Get wishlist items for current user if authenticated
    wishlist_product_ids = []
    wishlist_item_map = {}  # product_id -> wishlist_item_id
    cart_quantity_map = {}  # product_id -> cart_quantity
    if current_user.is_authenticated:
        wishlist = wishlist_repo.get_by_user_id(current_user.id)
        if wishlist:
            wishlist_items = wishlist_repo.get_wishlist_items(wishlist.id)
            for item in wishlist_items:
                wishlist_product_ids.append(item.product_id)
                wishlist_item_map[item.product_id] = item.id
        
        # Get cart quantities for each product
        cart = cart_repo.get_by_user_id(current_user.id)
        if cart:
            cart_items = cart_repo.get_cart_items(cart.id)
            for cart_item in cart_items:
                cart_quantity_map[cart_item.product_id] = cart_item.quantity
    
    # Get current filter values for maintaining form state
    current_filters = {
        'categories': categories_filter,
        'min_price': min_price,
        'max_price': max_price,
        'min_rating': min_rating,
        'search': search_query
    }
    
    return render_template('products.html', 
                         products=products_list, 
                         categories=categories,
                         current_filters=current_filters,
                         wishlist_product_ids=wishlist_product_ids,
                         wishlist_item_map=wishlist_item_map,
                         cart_quantity_map=cart_quantity_map)

@products_bp.route('/product/<int:product_id>', strict_slashes=False)
def product_detail(product_id): # Product detail page
    product_repo = RepositoryFactory.get_product_repository()
    wishlist_repo = RepositoryFactory.get_wishlist_repository()
    wishlist_item_repo = RepositoryFactory.get_wishlist_item_repository()
    cart_repo = RepositoryFactory.get_cart_repository()
    cart_item_repo = RepositoryFactory.get_cart_item_repository()
    review_repo = RepositoryFactory.get_review_repository()
    
    product = product_repo.get_by_id(product_id)
    if not product:
        flash('Product not found.', 'error')
        return redirect(url_for('products.products'))
    
    # Check if product is in wishlist
    in_wishlist = False
    wishlist_item_id = None
    cart_quantity = 0
    if current_user.is_authenticated:
        wishlist = wishlist_repo.get_by_user_id(current_user.id)
        if wishlist:
            wishlist_item = wishlist_item_repo.get_by_wishlist_and_product(wishlist.id, product_id)
            if wishlist_item:
                in_wishlist = True
                wishlist_item_id = wishlist_item.id
        
        # Get cart quantity for this product
        cart = cart_repo.get_by_user_id(current_user.id)
        if cart:
            cart_item = cart_item_repo.get_by_cart_and_product(cart.id, product_id)
            if cart_item:
                cart_quantity = cart_item.quantity
    
    # Get reviews for this product
    reviews = review_repo.get_product_reviews_ordered(product_id, order_by='created_at', desc=True)
    
    # Calculate average rating from reviews
    average_rating = product.get_average_rating()
    review_count = len(reviews)
    
    return render_template('product_detail.html', 
                         product=product, 
                         in_wishlist=in_wishlist,
                         wishlist_item_id=wishlist_item_id,
                         reviews=reviews,
                         average_rating=average_rating,
                         review_count=review_count,
                         cart_quantity=cart_quantity)

