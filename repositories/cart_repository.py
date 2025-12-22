# Cart Repository - Handles all data access for Cart and CartItem entities

from .base_repository import BaseRepository
from models.cart import Cart, CartItem

class CartRepository(BaseRepository):
    
    def __init__(self):
        super().__init__(Cart)
    
    def get_by_user_id(self, user_id): # Get cart by user ID
        return self.filter_by(user_id=user_id).first()
    
    def get_or_create_cart(self, user_id): # Get user's cart or create one if it doesn't exist
        cart = self.get_by_user_id(user_id)
        if not cart:
            cart = Cart(user_id=user_id)
            cart = self.create(cart)
        return cart
    
    def get_cart_items(self, cart_id): # Get all items in a cart
        return CartItemRepository().filter_by(cart_id=cart_id).all()
    
    def clear_cart(self, cart_id): # Clear all items from a cart
        cart_items = self.get_cart_items(cart_id)
        cart_item_repo = CartItemRepository()
        for item in cart_items:
            cart_item_repo.delete(item)


class CartItemRepository(BaseRepository): # Repository for CartItem entity
    
    def __init__(self):
        super().__init__(CartItem)
    
    def get_by_cart_and_product(self, cart_id, product_id): # Get cart item by cart ID and product ID
        return self.filter_by(cart_id=cart_id, product_id=product_id).first()
    
    def get_by_cart_id(self, cart_id): # Get all cart items for a cart
        return self.filter_by(cart_id=cart_id).all()
    
    def create_cart_item(self, cart_item): # Create a new cart item
        return self.create(cart_item)
    
    def update_cart_item(self, cart_item): # Update a cart item
        return self.update(cart_item)
    
    def delete_cart_item(self, cart_item): # Delete a cart item
        self.delete(cart_item)
    
    def delete_by_cart_id(self, cart_id): # Delete all cart items for a cart
        from core.database import database
        db = database.db
        db.session.query(CartItem).filter_by(cart_id=cart_id).delete()
        db.session.commit()



