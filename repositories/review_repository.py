# Review Repository - Handles all data access for Review entity

from .base_repository import BaseRepository
from models.review import Review

class ReviewRepository(BaseRepository): # Repository for Review entity
    
    def __init__(self):
        super().__init__(Review)
    
    def get_by_product_id(self, product_id): # Get all reviews for a product
        return self.filter_by(product_id=product_id).all()
    
    def get_by_user_id(self, user_id): # Get all reviews by a user
        return self.filter_by(user_id=user_id).all()
    
    def get_by_order_id(self, order_id): # Get all reviews for an order
        return self.filter_by(order_id=order_id).all()
    
    def get_by_user_product_order(self, user_id, product_id, order_id): # Get review by user, product, and order
        return self.query().filter(
            Review.user_id == user_id,
            Review.product_id == product_id,
            Review.order_id == order_id
        ).first()
    
    def create_review(self, review): # Create a new review
        return self.create(review)
    
    def update_review(self, review): # Update an existing review
        return self.update(review)
    
    def delete_review(self, review): # Delete a review
        self.delete(review)
    
    def get_product_reviews_ordered(self, product_id, order_by='created_at', desc=True): # Get product reviews ordered by a field
        query = self.filter_by(product_id=product_id)
        order_field = getattr(Review, order_by, Review.created_at)
        if desc:
            query = query.order_by(order_field.desc())
        else:
            query = query.order_by(order_field.asc())
        return query.all()



