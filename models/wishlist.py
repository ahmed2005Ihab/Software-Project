from app import db

class Wishlist(db.Model):
    __tablename__ = 'wishlists'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    
    # Relationships
    items = db.relationship('WishlistItem', backref='wishlist', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Wishlist {self.id} - User {self.user_id}>'

class WishlistItem(db.Model):
    __tablename__ = 'wishlist_items'
    
    id = db.Column(db.Integer, primary_key=True)
    wishlist_id = db.Column(db.Integer, db.ForeignKey('wishlists.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    # Unique constraint to prevent duplicate items
    __table_args__ = (db.UniqueConstraint('wishlist_id', 'product_id', name='unique_wishlist_product'),)
    
    def __repr__(self):
        return f'<WishlistItem {self.id} - Product {self.product_id}>'

