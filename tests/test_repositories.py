from unittest.mock import MagicMock, patch
from repositories.user_repository import UserRepository

@patch("repositories.base_repository.BaseRepository.get_all")
def test_get_all_users(mock_get_all):
    fake_user = MagicMock()
    fake_user.name = "Ali"

    mock_get_all.return_value = [fake_user]

    repo = UserRepository()
    users = repo.get_all_users()

    assert len(users) == 1
    assert users[0].name == "Ali"
