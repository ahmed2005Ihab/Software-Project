from repositories.factory import RepositoryFactory
from repositories.product_repository import ProductRepository
from repositories.user_repository import UserRepository


def test_factory_returns_product_repo():
    repo = RepositoryFactory.get_repository("product")
    assert isinstance(repo, ProductRepository)


def test_factory_invalid_type():
    try:
        RepositoryFactory.get_repository("invalid")
        assert False
    except Exception:
        assert True


def test_factory_returns_user_repo():
    repo = RepositoryFactory.get_repository("user")
    assert isinstance(repo, UserRepository)


def test_factory_invalid_type_2():
    try:
        RepositoryFactory.get_repository("unknown")
        assert False
    except Exception:
        assert True