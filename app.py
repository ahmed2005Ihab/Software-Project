from flask import Flask
from flask_login import LoginManager
import os

# Import singleton database
from core.database import database


db = database.db
login_manager = LoginManager()


def create_app():
    
    root_dir = os.path.dirname(os.path.abspath(__file__))
    template_dir = os.path.join(root_dir, 'Templates')
    static_dir = os.path.join(root_dir, 'static')
    
    app = Flask(__name__, template_folder = template_dir, static_folder = static_dir)
    
    # Configuration
    app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///homecraft.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize singleton database with Flask app
    database.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    
    
    @login_manager.user_loader
    def load_user(user_id):
        from repositories.factory import RepositoryFactory
        user_repo = RepositoryFactory.get_user_repository()
        return user_repo.get_by_id(int(user_id))
    

    from models.user import User
    from models.product import Product
    from models.category import Category
    from models.cart import Cart, CartItem
    from models.order import Order, OrderItem
    from models.wishlist import Wishlist, WishlistItem
    from models.review import Review
    from models.feedback import Feedback
    

    from controllers.auth import auth_bp
    from controllers.products import products_bp
    from controllers.cart import cart_bp
    from controllers.admin import admin_bp
    from controllers.feedback import feedback_bp
    from controllers.users import users_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(products_bp)
    app.register_blueprint(cart_bp, url_prefix='/cart')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(feedback_bp)
    app.register_blueprint(users_bp)

    
    @app.errorhandler(404)
    def page_not_found(e):
        return 'Page Not Found', 404
    
    
    with app.app_context():
        db.create_all()
        
        
        from repositories.factory import RepositoryFactory
        category_repo = RepositoryFactory.get_category_repository()
        default_categories = ['Sofas & Chairs', 'Tables', 'Beds', 'Storage', 'Lighting']
        for cat_name in default_categories:
            if not category_repo.get_by_name(cat_name):
                category = Category(name=cat_name)
                category_repo.create_category(category)
        
        
        user_repo = RepositoryFactory.get_user_repository()
        if not user_repo.get_by_email('admin@homecraft.com'):
            admin = User(
                name='Admin',
                email='admin@homecraft.com',
                address='Admin Address',
                phone_number='',
                is_admin=True
            )
            admin.set_password('admin123')
            user_repo.create_user(admin)
    
    return app
