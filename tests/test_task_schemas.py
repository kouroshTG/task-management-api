
import pytest
from pydantic import ValidationError

from app.schemas.task import (
    TaskCreate,
    TaskPriority,
    TaskStatus,
    TaskUpdate,
)


def test_task_create_with_valid_data():
    task = TaskCreate(
        title="Learn FastAPI",
        description="Build a REST API",
        priority="high",
    )

    assert task.title == "Learn FastAPI"
    assert task.priority == TaskPriority.HIGH


def test_task_create_uses_default_priority():
    task = TaskCreate(title="Learn SQLAlchemy")

    assert task.priority == TaskPriority.MEDIUM


def test_task_create_rejects_invalid_priority():
    with pytest.raises(ValidationError):
        TaskCreate(
            title="Learn FastAPI",
            priority="urgent",
        )


def test_task_create_rejects_owner_id():
    with pytest.raises(ValidationError):
        TaskCreate(
            title="Learn FastAPI",
            owner_id=25,
        )


def test_task_update_accepts_valid_status():
    task = TaskUpdate(status="completed")

    assert task.status == TaskStatus.COMPLETED


def test_task_update_rejects_invalid_status():
    with pytest.raises(ValidationError):
        TaskUpdate(status="doing")


def test_task_update_exclude_unset():
    task = TaskUpdate(status="completed")

    assert task.model_dump(exclude_unset=True) == {
        "status": TaskStatus.COMPLETED
    }

def test_task_update_rejects_null_title():
    with pytest.raises(ValidationError):
        TaskUpdate(title=None)


def test_task_update_rejects_null_status():
    with pytest.raises(ValidationError):
        TaskUpdate(status=None)
