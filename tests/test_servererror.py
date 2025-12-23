from unittest.mock import patch, MagicMock
from repositories.user_repository import UserRepository

@patch("controllers.users.RepositoryFactory")
def test_repository_error_handling(mock_factory, client):
    mock_repo = MagicMock()
    mock_repo.get_all.side_effect = Exception("Database error")
    mock_factory.get_user_repository.return_value = mock_repo

    response = client.get("/users")
    assert response.status_code == 500
    assert b"Internal Server Error" in response.data