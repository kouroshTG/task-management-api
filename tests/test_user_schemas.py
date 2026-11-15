
from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from app.models.task import Task  # noqa: F401
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserUpdate


def test_user_create_with_valid_data():
    user = UserCreate(
        email="test@example.com",
        password="password123",
        full_name="Test User",
    )

    assert user.email == "test@example.com"
    assert user.full_name == "Test User"


def test_user_create_rejects_invalid_email():
    with pytest.raises(ValidationError):
        UserCreate(
            email="not-an-email",
            password="password123",
        )


def test_user_create_rejects_short_password():
    with pytest.raises(ValidationError):
        UserCreate(
            email="test@example.com",
            password="123",
        )


def test_user_update_exclude_unset():
    update = UserUpdate(full_name="New Name")

    assert update.model_dump(exclude_unset=True) == {
        "full_name": "New Name"
    }


def test_user_response_does_not_expose_password_hash():
    now = datetime.now(UTC)

    user = User(
        id=1,
        email="test@example.com",
        password_hash="this-is-a-secret-hash",
        full_name="Test User",
        is_active=True,
        created_at=now,
        updated_at=now,
    )

    response = UserResponse.model_validate(user)
    response_data = response.model_dump()

    assert response_data["email"] == "test@example.com"
    assert "password_hash" not in response_data
    assert "password" not in response_data
