from app import db

class Review(db.Model):
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    
    # Unique constraint: one review per user per product per order
    __table_args__ = (db.UniqueConstraint('user_id', 'product_id', 'order_id', name='unique_user_product_order_review'),)
    
    def __repr__(self):
        return f'<Review {self.id} - User {self.user_id} - Product {self.product_id} - Rating {self.rating}>'

