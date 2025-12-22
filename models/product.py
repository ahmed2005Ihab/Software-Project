from app import db

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    image_url = db.Column(db.String(500))
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    stock_quantity = db.Column(db.Integer, default=0)
    rating = db.Column(db.Numeric(2, 1), default=5.0)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    
    # Relationships
    cart_items = db.relationship('CartItem', backref='product', lazy=True, cascade='all, delete-orphan')
    order_items = db.relationship('OrderItem', backref='product', lazy=True)
    wishlist_items = db.relationship('WishlistItem', backref='product', lazy=True, cascade='all, delete-orphan')
    reviews = db.relationship('Review', backref='product', lazy=True, cascade='all, delete-orphan')
    
    def get_average_rating(self):
        if not self.reviews:
            return 0.0
        total_rating = sum(review.rating for review in self.reviews)
        return round(total_rating / len(self.reviews), 1)
    
    def __repr__(self):
        return f'<Product {self.name}>'

