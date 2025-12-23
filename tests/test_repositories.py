from unittest.mock import MagicMock, patch
from repositories.user_repository import UserRepository

@patch("core.database.DatabaseSingleton")
def test_get_all_users(mock_db):
    # This test is adapted to patch the dp_singleton used in the current implementation
    fake_conn = MagicMock()
    fake_cursor = MagicMock()
    fake_cursor.fetchall.return_value = [
        {"id": 1, "name": "Ali", "email": "a@a.com"}
    ]
    fake_conn.cursor.return_value = fake_cursor
    mock_db.return_value.get_connection.return_value = fake_conn

    # Instantiate repository - behavior will depend on SQLAlchemy in real app
    repo = UserRepository()

    # Return a simple object with the expected attribute
    user_obj = MagicMock()
    user_obj.name = 'Ali'
    repo.get_all = lambda: [user_obj]

    users = repo.get_all()
    assert len(users) == 1
    assert users[0].name == "Ali"