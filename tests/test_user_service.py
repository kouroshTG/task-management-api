
import pytest

from app.core.security import verify_password
from app.schemas.user import UserCreate
from app.services.user import UserService


def test_register_user_successfully(db_session):
    service = UserService(db_session)

    user_data = UserCreate(
        email="service-test@example.com",
        password="StrongPassword123!",
        full_name="Service Test",
    )

    user = service.register(user_data)

    assert user.id is not None
    assert user.email == user_data.email
    assert user.full_name == user_data.full_name

    assert user.password_hash != user_data.password
    assert verify_password(
        user_data.password,
        user.password_hash,
    )


def test_register_user_with_duplicate_email(db_session):
    service = UserService(db_session)

    user_data = UserCreate(
        email="duplicate-test@example.com",
        password="StrongPassword123!",
    )

    service.register(user_data)

    with pytest.raises(
        ValueError,
        match="Email is already registered",
    ):
        service.register(user_data)


def test_authenticate_user_successfully(db_session):
    service = UserService(db_session)

    user_data = UserCreate(
        email="login-test@example.com",
        password="StrongPassword123!",
        full_name="Login Test",
    )

    registered_user = service.register(user_data)

    authenticated_user = service.authenticate(
        email=user_data.email,
        password=user_data.password,
    )

    assert authenticated_user.id == registered_user.id
    assert authenticated_user.email == user_data.email


def test_authenticate_user_with_wrong_password(db_session):
    service = UserService(db_session)

    user_data = UserCreate(
        email="wrong-password@example.com",
        password="StrongPassword123!",
    )

    service.register(user_data)

    with pytest.raises(
        ValueError,
        match="Invalid email or password",
    ):
        service.authenticate(
            email=user_data.email,
            password="WrongPassword123!",
        )
