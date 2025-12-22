# Product Repository - Handles all data access for Product entity

from .base_repository import BaseRepository
from models.product import Product

class ProductRepository(BaseRepository): # Repository for Product entity
    
    def __init__(self):
        super().__init__(Product)
    
    def get_by_category(self, category_id): # Get products by category
        return self.filter_by(category_id=category_id).all()
    
    def search_products(self, search_query): # Search products by name
        return self.query().filter(Product.name.contains(search_query)).all()
    
    def filter_by_price_range(self, min_price=None, max_price=None): # Filter products by price range
        query = self.query()
        if min_price is not None:
            query = query.filter(Product.price >= min_price)
        if max_price is not None:
            query = query.filter(Product.price <= max_price)
        return query
    
    def filter_by_rating(self, min_rating): # Filter products by minimum rating

        return self.query().filter(Product.rating >= min_rating)

    def filter_by_stock(self, in_stock=True): # Filter products by stock availability
        if in_stock:
            return self.query().filter(Product.stock_quantity > 0)
        else:
            return self.query().filter(Product.stock_quantity == 0)
    
    def get_in_stock_products(self):

        return self.filter_by_stock(in_stock=True).all()
    
    def get_out_of_stock_products(self):

        return self.filter_by_stock(in_stock=False).all()
    
    def update_stock(self, product_id, quantity):

        product = self.get_by_id(product_id)
        if product:
            product.stock_quantity += quantity
            return self.update(product)
        return None



