from core.database import DatabaseSingleton


def test_singleton_instance():
    db1 = DatabaseSingleton()
    db2 = DatabaseSingleton()
    assert db1 is db2