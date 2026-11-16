
import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import get_db
from app.main import app


@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.pop(get_db, None)


def test_register_user_successfully(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "http-test@example.com",
            "password": "StrongPassword123!",
            "full_name": "HTTP Test",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["email"] == "http-test@example.com"
    assert data["full_name"] == "HTTP Test"
    assert data["is_active"] is True

    assert "password" not in data
    assert "password_hash" not in data


def test_register_user_with_duplicate_email(client):
    payload = {
        "email": "duplicate-http@example.com",
        "password": "StrongPassword123!",
    }

    first_response = client.post(
        "/api/v1/auth/register",
        json=payload,
    )

    second_response = client.post(
        "/api/v1/auth/register",
        json=payload,
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json()["detail"] == (
        "Email is already registered"
    )


def test_register_user_with_invalid_email(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "not-an-email",
            "password": "StrongPassword123!",
        },
    )

    assert response.status_code == 422


def test_get_current_user_profile_successfully(client):
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "profile-test@example.com",
            "password": "StrongPassword123!",
            "full_name": "Profile Test",
        },
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "profile-test@example.com",
            "password": "StrongPassword123!",
        },
    )

    assert login_response.status_code == 200

    access_token = login_response.json()["access_token"]

    profile_response = client.get(
        "/api/v1/users/me",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
    )

    assert profile_response.status_code == 200

    profile_data = profile_response.json()

    assert profile_data["email"] == "profile-test@example.com"
    assert profile_data["full_name"] == "Profile Test"
    assert "password" not in profile_data
    assert "password_hash" not in profile_data


def test_get_current_user_profile_without_token(client):
    response = client.get("/api/v1/users/me")

    assert response.status_code == 401


def test_get_current_user_profile_with_invalid_token(client):
    response = client.get(
        "/api/v1/users/me",
        headers={
            "Authorization": "Bearer invalid-token",
        },
    )

    assert response.status_code == 401
