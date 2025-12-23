from unittest.mock import patch, MagicMock

@patch("controllers.users.RepositoryFactory")
def test_user_not_found_page(mock_factory, client):
    mock_repo = MagicMock()
    mock_repo.get_all.return_value = []
    mock_factory.get_user_repository.return_value = mock_repo

    response = client.get("/users")
    assert response.status_code == 404
    assert b"No users found" in response.data