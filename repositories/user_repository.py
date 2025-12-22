# User Repository - Handles all data access for User entity

from .base_repository import BaseRepository
from models.user import User

class UserRepository(BaseRepository): # Repository for User entity
    
    def __init__(self):
        super().__init__(User)
    
    def get_by_email(self, email): # Get user by email
        return self.filter_by(email=email).first()
    
    def get_all_users(self): # Get all users
        return self.get_all()
    
    def create_user(self, user): # Create a new user
        return self.create(user)
    
    def update_user(self, user): # Update an existing user
        return self.update(user)
    
    def delete_user(self, user): # Delete a user
        self.delete(user)
    
    def get_admins(self): # Get all admin users
        return self.filter_by(is_admin=True).all()
    
    def get_customers(self): # Get all customer users
        return self.filter_by(is_admin=False).all()
    
    def search_users(self, search_query): # Search users by name or email
        from core.database import database
        db = database.db
        return self.query().filter(
            db.or_(
                User.name.contains(search_query),
                User.email.contains(search_query)
            )
        ).all()



