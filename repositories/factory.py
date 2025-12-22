# Repository Factory - Chooses the correct repository based on entity type

from .user_repository import UserRepository
from .product_repository import ProductRepository
from .category_repository import CategoryRepository
from .cart_repository import CartRepository, CartItemRepository
from .order_repository import OrderRepository, OrderItemRepository
from .wishlist_repository import WishlistRepository, WishlistItemRepository
from .review_repository import ReviewRepository
from .feedback_repository import FeedbackRepository

class RepositoryFactory: # Factory pattern to get the correct repository based on entity type
    
    
    _repositories = {
        'user': UserRepository,
        'product': ProductRepository,
        'category': CategoryRepository,
        'cart': CartRepository,
        'cart_item': CartItemRepository,
        'order': OrderRepository,
        'order_item': OrderItemRepository,
        'wishlist': WishlistRepository,
        'wishlist_item': WishlistItemRepository,
        'review': ReviewRepository,
        'feedback': FeedbackRepository,
    }
    
    _instances = {}
    
    @classmethod
    def get_repository(cls, entity_type): # Get repository instance for entity type (Singleton pattern for repositories)
        entity_type = entity_type.lower()
        
        if entity_type not in cls._repositories:
            raise ValueError(f"Unknown entity type: {entity_type}")
        
        # Singleton pattern: return same instance if already created
        if entity_type not in cls._instances:
            cls._instances[entity_type] = cls._repositories[entity_type]()
        
        return cls._instances[entity_type]
    
    @classmethod
    def get_user_repository(cls): # Get UserRepository instance
        return cls.get_repository('user')
    
    @classmethod
    def get_product_repository(cls): # Get ProductRepository instance
        return cls.get_repository('product')
    
    @classmethod
    def get_category_repository(cls): # Get CategoryRepository instance
        return cls.get_repository('category')
    
    @classmethod
    def get_cart_repository(cls): # Get CartRepository instance
        return cls.get_repository('cart')
    
    @classmethod
    def get_cart_item_repository(cls): # Get CartItemRepository instance
        return cls.get_repository('cart_item')
    
    @classmethod
    def get_order_repository(cls): # Get OrderRepository instance
        return cls.get_repository('order')
    
    @classmethod
    def get_order_item_repository(cls): # Get OrderItemRepository instance
        return cls.get_repository('order_item')
    
    @classmethod
    def get_wishlist_repository(cls): # Get WishlistRepository instance
        return cls.get_repository('wishlist')
    
    @classmethod
    def get_wishlist_item_repository(cls): # Get WishlistItemRepository instance
        return cls.get_repository('wishlist_item')
    
    @classmethod
    def get_review_repository(cls): # Get ReviewRepository instance
        return cls.get_repository('review')
    
    @classmethod
    def get_feedback_repository(cls): # Get FeedbackRepository instance
        return cls.get_repository('feedback')
