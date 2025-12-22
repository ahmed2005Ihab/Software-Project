from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    address = db.Column(db.String(200))
    phone_number = db.Column(db.String(20))
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    # Relationships
    carts = db.relationship('Cart', backref='user', lazy=True, cascade='all, delete-orphan')
    orders = db.relationship('Order', backref='user', lazy=True)
    wishlists = db.relationship('Wishlist', backref='user', lazy=True, cascade='all, delete-orphan')
    reviews = db.relationship('Review', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password): # Hash and set the password
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password): # Check if the provided password matches the hash
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.email}>'

