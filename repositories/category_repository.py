# Category Repository - Handles all data access for Category entity

from .base_repository import BaseRepository
from models.category import Category

class CategoryRepository(BaseRepository): # Repository for Category entity
    
    def __init__(self):
        super().__init__(Category)
    
    def get_by_name(self, name): # Get category by name
        return self.filter_by(name=name).first()
    
    def search_categories(self, search_query): # Search categories by name
        return self.query().filter(Category.name.contains(search_query)).all()
    
    def get_all_categories(self): # Get all categories
        return self.get_all()
    
    def create_category(self, category): # Create a new category
        return self.create(category)
    
    def delete_category(self, category): # Delete a category
        self.delete(category)



