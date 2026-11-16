
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate


def test_create_and_get_user(db_session):
    repository = UserRepository(db_session)

    user_data = UserCreate(
        email="repository-test@example.com",
        password="password123",
        full_name="Repository Test",
    )

    user = repository.create(
        user_data=user_data,
        password_hash="test-password-hash",
    )

    assert user.id is not None
    assert user.email == "repository-test@example.com"
    assert user.password_hash == "test-password-hash"

    found_user = repository.get_by_email(
        "repository-test@example.com"
    )

    assert found_user is not None
    assert found_user.id == user.id


def test_get_user_by_email_returns_none(db_session):
    repository = UserRepository(db_session)

    user = repository.get_by_email(
        "not-existing-user@example.com"
    )

    assert user is None
