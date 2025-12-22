# Wishlist Repository - Handles all data access for Wishlist and WishlistItem entities

from .base_repository import BaseRepository
from models.wishlist import Wishlist, WishlistItem

class WishlistRepository(BaseRepository): # Repository for Wishlist entity
    
    def __init__(self):
        super().__init__(Wishlist)
    
    def get_by_user_id(self, user_id): # Get wishlist by user ID

        return self.filter_by(user_id=user_id).first()
    
    def get_or_create_wishlist(self, user_id): # Get user's wishlist or create one if it doesn't exist
        wishlist = self.get_by_user_id(user_id)
        if not wishlist:
            wishlist = Wishlist(user_id=user_id)
            wishlist = self.create(wishlist)
        return wishlist
    
    def get_wishlist_items(self, wishlist_id): # Get all items in a wishlist
        return WishlistItemRepository().filter_by(wishlist_id=wishlist_id).all()


class WishlistItemRepository(BaseRepository): # Repository for WishlistItem entity
    
    def __init__(self):
        super().__init__(WishlistItem)
    
    def get_by_wishlist_and_product(self, wishlist_id, product_id): # Get wishlist item by wishlist ID and product ID
        return self.filter_by(wishlist_id=wishlist_id, product_id=product_id).first()
    
    def get_by_wishlist_id(self, wishlist_id): # Get all wishlist items for a wishlist
        return self.filter_by(wishlist_id=wishlist_id).all()
    
    def create_wishlist_item(self, wishlist_item): # Create a new wishlist item
        return self.create(wishlist_item)
    
    def delete_wishlist_item(self, wishlist_item): # Delete a wishlist item
        self.delete(wishlist_item)



