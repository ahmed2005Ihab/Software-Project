from unittest.mock import patch, MagicMock
from models.product import Product
from models.user import User

@patch("controllers.products.RepositoryFactory")
def test_products_page(mock_factory, client):
    mock_repo = MagicMock()
    # Return simple objects compatible with rendering
    prod = MagicMock()
    prod.name = "Desk"
    prod.price = 3000
    prod.get_average_rating.return_value = 4.0
    prod.category = None
    prod.image_url = None
    prod.stock_quantity = 10
    prod.id = 1
    # Configure query().all() used by the controller
    mock_query = MagicMock()
    mock_query.all.return_value = [prod]
    mock_repo.query.return_value = mock_query

    # Ensure the mocked RepositoryFactory returns the product repo via get_product_repository
    mock_factory.get_product_repository.return_value = mock_repo

    response = client.get("/products")
    assert response.status_code == 200
    assert b"Desk" in response.data
    assert b"3000" in response.data

@patch("controllers.users.RepositoryFactory")
def test_users_page(mock_factory, client):
    mock_repo = MagicMock()
    user = MagicMock()
    user.name = "John"
    mock_repo.get_all.return_value = [user]
    mock_factory.get_user_repository.return_value = mock_repo

    response = client.get("/users")
    assert response.status_code == 200
    assert b"John" in response.data