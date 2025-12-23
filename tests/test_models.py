from models.user import User
from models.product import Product

def test_user_model_fields():
    # Ensure the User model exposes expected columns/attributes
    assert hasattr(User, 'id')
    assert hasattr(User, 'name')
    assert hasattr(User, 'email')

def test_product_model_fields():
    # Ensure the Product model exposes expected columns/attributes
    assert hasattr(Product, 'id')
    assert hasattr(Product, 'name')
    assert hasattr(Product, 'price')
