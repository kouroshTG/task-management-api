
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


def register_and_login(
    client,
    email="task-test@example.com",
    ):
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "StrongPassword123!",
        },
    )

    user_id = register_response.json()["id"]

    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": "StrongPassword123!",
        },
    )

    access_token = login_response.json()["access_token"]

    return access_token, user_id


def test_create_task_successfully(client):
    access_token, user_id = register_and_login(client)

    response = client.post(
        "/api/v1/tasks/",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
        json={
            "title": "Learn FastAPI",
            "description": "Build a task management API",
            "priority": "high",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["title"] == "Learn FastAPI"
    assert data["description"] == "Build a task management API"
    assert data["priority"] == "high"
    assert data["status"] == "pending"
    assert data["owner_id"] == user_id


def test_create_task_without_authentication(client):
    response = client.post(
        "/api/v1/tasks/",
        json={
            "title": "Unauthorized task",
        },
    )

    assert response.status_code == 401


def test_create_task_with_owner_id_in_payload(client):
    access_token, _ = register_and_login(client)

    response = client.post(
        "/api/v1/tasks/",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
        json={
            "title": "Task with forged owner",
            "owner_id": 999,
        },
    )

    assert response.status_code == 422


def test_get_tasks_successfully(client):
    access_token, user_id = register_and_login(client)

    client.post(
        "/api/v1/tasks/",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
        json={
            "title": "First task",
        },
    )

    response = client.get(
        "/api/v1/tasks/",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["title"] == "First task"
    assert data[0]["owner_id"] == user_id


def test_get_tasks_without_authentication(client):
    response = client.get("/api/v1/tasks/")

    assert response.status_code == 401


def test_get_task_successfully(client):
    access_token, _ = register_and_login(client)

    create_response = client.post(
        "/api/v1/tasks/",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
        json={
            "title": "Task to retrieve",
        },
    )

    task_id = create_response.json()["id"]

    response = client.get(
        f"/api/v1/tasks/{task_id}",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
    )

    assert response.status_code == 200
    assert response.json()["id"] == task_id
    assert response.json()["title"] == "Task to retrieve"


def test_get_task_not_found(client):
    access_token, _ = register_and_login(client)

    response = client.get(
        "/api/v1/tasks/999999",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


def test_user_cannot_access_another_users_task(client):
    # Create two independent users.
    user_a_token, _ = register_and_login(
        client,
        email="user-a@example.com",
    )

    user_b_token, _ = register_and_login(
        client,
        email="user-b@example.com",
    )

    # User B creates a task.
    create_response = client.post(
        "/api/v1/tasks/",
        headers={
            "Authorization": f"Bearer {user_b_token}",
        },
        json={
            "title": "Private task of user B",
        },
    )

    task_id = create_response.json()["id"]

    # User A tries to access User B's task.
    response = client.get(
        f"/api/v1/tasks/{task_id}",
        headers={
            "Authorization": f"Bearer {user_a_token}",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


def test_update_task_successfully(client):
    access_token, _ = register_and_login(client)

    create_response = client.post(
        "/api/v1/tasks/",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
        json={
            "title": "Learn FastAPI",
            "priority": "high",
        },
    )

    task_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/tasks/{task_id}",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
        json={
            "status": "completed",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "completed"
    assert data["title"] == "Learn FastAPI"
    assert data["priority"] == "high"


def test_update_task_not_found(client):
    access_token, _ = register_and_login(client)

    response = client.patch(
        "/api/v1/tasks/999999",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
        json={
            "title": "Updated task",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


def test_delete_task_successfully(client):
    access_token, _ = register_and_login(client)

    create_response = client.post(
        "/api/v1/tasks/",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
        json={
            "title": "Task to delete",
        },
    )

    task_id = create_response.json()["id"]

    response = client.delete(
        f"/api/v1/tasks/{task_id}",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
    )

    assert response.status_code == 204
    assert response.content == b""

    get_response = client.get(
        f"/api/v1/tasks/{task_id}",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
    )

    assert get_response.status_code == 404


def test_delete_task_not_found(client):
    access_token, _ = register_and_login(client)

    response = client.delete(
        "/api/v1/tasks/999999",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


def test_user_cannot_delete_another_users_task(client):
    access_token_a, _ = register_and_login(
        client,
        email="user-a@example.com",
    )

    access_token_b, _ = register_and_login(
        client,
        email="user-b@example.com",
    )

    create_response = client.post(
        "/api/v1/tasks/",
        headers={
            "Authorization": f"Bearer {access_token_b}",
        },
        json={
            "title": "User B task",
        },
    )

    task_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/api/v1/tasks/{task_id}",
        headers={
            "Authorization": f"Bearer {access_token_a}",
        },
    )

    assert delete_response.status_code == 404

    get_response = client.get(
        f"/api/v1/tasks/{task_id}",
        headers={
            "Authorization": f"Bearer {access_token_b}",
        },
    )

    assert get_response.status_code == 200
    assert get_response.json()["title"] == "User B task"


def test_user_cannot_update_another_users_task(client):
    access_token_a, _ = register_and_login(
        client,
        email="user-a-update@example.com",
    )

    access_token_b, _ = register_and_login(
        client,
        email="user-b-update@example.com",
    )

    create_response = client.post(
        "/api/v1/tasks/",
        headers={
            "Authorization": f"Bearer {access_token_b}",
        },
        json={
            "title": "Original task",
        },
    )

    task_id = create_response.json()["id"]

    update_response = client.patch(
        f"/api/v1/tasks/{task_id}",
        headers={
            "Authorization": f"Bearer {access_token_a}",
        },
        json={
            "title": "Modified by user A",
        },
    )

    assert update_response.status_code == 404

    get_response = client.get(
        f"/api/v1/tasks/{task_id}",
        headers={
            "Authorization": f"Bearer {access_token_b}",
        },
    )

    assert get_response.status_code == 200
    assert get_response.json()["title"] == "Original task"


def test_filter_tasks_by_status_and_priority(client):
    access_token, _ = register_and_login(client)

    headers = {
        "Authorization": f"Bearer {access_token}",
    }

    tasks = [
        {"title": "High completed", "priority": "high"},
        {"title": "High pending", "priority": "high"},
        {"title": "Low completed", "priority": "low"},
    ]

    for task_data in tasks:
        create_response = client.post(
            "/api/v1/tasks/",
            headers=headers,
            json=task_data,
        )
        assert create_response.status_code == 201

    task_id = create_response.json()["id"]

    update_response = client.patch(
        f"/api/v1/tasks/{task_id}",
        headers=headers,
        json={"status": "completed"},
    )
    assert update_response.status_code == 200

    response = client.get(
        "/api/v1/tasks/?status=completed&priority=low",
        headers=headers,
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Low completed"

def test_filter_tasks_with_invalid_status(client):
    access_token, _ = register_and_login(client)

    response = client.get(
        "/api/v1/tasks/?status=invalid",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
    )

    assert response.status_code == 422


def test_search_tasks_by_title_and_description(client):
    access_token, _ = register_and_login(client)
    headers = {"Authorization": f"Bearer {access_token}"}

    client.post(
        "/api/v1/tasks/",
        headers=headers,
        json={
            "title": "Learn Python",
            "description": "Backend development",
        },
    )

    client.post(
        "/api/v1/tasks/",
        headers=headers,
        json={
            "title": "Learn FastAPI",
            "description": "Python REST API",
        },
    )

    title_response = client.get(
        "/api/v1/tasks/?search=python",
        headers=headers,
    )

    description_response = client.get(
        "/api/v1/tasks/?search=backend",
        headers=headers,
    )

    assert title_response.status_code == 200
    assert len(title_response.json()) == 2

    assert description_response.status_code == 200
    assert len(description_response.json()) == 1
    assert description_response.json()[0]["title"] == "Learn Python"


def test_tasks_pagination(client):
    access_token, _ = register_and_login(client)
    headers = {"Authorization": f"Bearer {access_token}"}

    created_ids = []

    for number in range(3):
        response = client.post(
            "/api/v1/tasks/",
            headers=headers,
            json={"title": f"Task {number}"},
        )
        created_ids.append(response.json()["id"])

    response = client.get(
        "/api/v1/tasks/?limit=2&offset=1",
        headers=headers,
    )

    assert response.status_code == 200
    assert len(response.json()) == 2

    returned_ids = [task["id"] for task in response.json()]

    assert returned_ids == [
        created_ids[1],
        created_ids[0],
    ]


def test_tasks_pagination_rejects_invalid_values(client):
    access_token, _ = register_and_login(client)
    headers = {"Authorization": f"Bearer {access_token}"}

    invalid_urls = [
        "/api/v1/tasks/?limit=0",
        "/api/v1/tasks/?limit=101",
        "/api/v1/tasks/?offset=-1",
    ]

    for url in invalid_urls:
        response = client.get(url, headers=headers)
        assert response.status_code == 422
