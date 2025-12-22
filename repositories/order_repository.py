# Order Repository - Handles all data access for Order and OrderItem entities

from .base_repository import BaseRepository
from models.order import Order, OrderItem

class OrderRepository(BaseRepository): # Repository for Order entity    
    def __init__(self):
        super().__init__(Order)
    
    def get_by_user_id(self, user_id): # Get all orders for a user
        return self.filter_by(user_id=user_id).all()
    
    def get_by_order_number(self, order_number): # Get order by order number
        return self.filter_by(order_number=order_number).first()
    
    def get_by_status(self, status): # Get orders by status
        return self.filter_by(status=status).all()
    
    def get_user_orders_by_status(self, user_id, status): # Get user orders by status
        return self.query().filter(
            Order.user_id == user_id,
            Order.status == status
        ).all()
    
    def search_orders(self, search_query): # Search orders by order number, customer name, or email
        from core.database import database
        from models.user import User
        db = database.db
        return self.query().join(User).filter(
            db.or_(
                Order.order_number.contains(search_query),
                User.name.contains(search_query),
                User.email.contains(search_query)
            )
        )
    
    def get_orders_by_date_range(self, start_date, end_date=None): # Get orders within a date range
        query = self.query().filter(Order.created_at >= start_date)
        if end_date:
            query = query.filter(Order.created_at <= end_date)
        return query
    
    def get_total_revenue(self, start_date=None, exclude_cancelled=True): # Get total revenue from orders
        from core.database import database
        db = database.db
        query = db.session.query(db.func.sum(Order.total_amount))
        
        if exclude_cancelled:
            query = query.filter(Order.status != 'cancelled')
        
        if start_date:
            query = query.filter(Order.created_at >= start_date)
        
        result = query.scalar()
        return float(result) if result else 0.0
    
    def create_order(self, order): # Create a new order
        return self.create(order)
    
    def update_order(self, order): # Update an existing order
        return self.update(order)
    
    def get_order_items(self, order_id): # Get all items in an order
        return OrderItemRepository().filter_by(order_id=order_id).all()


class OrderItemRepository(BaseRepository): # Repository for OrderItem entity
    
    def __init__(self):
        super().__init__(OrderItem)
    
    def get_by_order_id(self, order_id): # Get all order items for an order
        return self.filter_by(order_id=order_id).all()
    
    def get_by_order_and_product(self, order_id, product_id): # Get order item by order ID and product ID
        return self.filter_by(order_id=order_id, product_id=product_id).first()
    
    def create_order_item(self, order_item): # Create a new order item
        return self.create(order_item)
    
    def get_top_products(self, start_date=None, limit=10): # Get top products by quantity sold
        from core.database import database
        from models.product import Product
        db = database.db
        
        query = db.session.query(
            Product.name,
            db.func.sum(OrderItem.quantity).label('total_quantity'),
            db.func.sum(OrderItem.price * OrderItem.quantity).label('total_revenue')
        ).join(OrderItem, Product.id == OrderItem.product_id)\
         .join(Order, OrderItem.order_id == Order.id)\
         .filter(Order.status != 'cancelled')
        
        if start_date:
            query = query.filter(Order.created_at >= start_date)
        
        return query.group_by(Product.id, Product.name)\
                   .order_by(db.func.sum(OrderItem.quantity).desc())\
                   .limit(limit).all()



