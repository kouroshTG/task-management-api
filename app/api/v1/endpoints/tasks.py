from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

from app.api.dependencies import CurrentUser, TaskServiceDep
from app.schemas.task import (
    TaskCreate,
    TaskPriority,
    TaskResponse,
    TaskStatus,
    TaskUpdate,
)

router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"],
)


@router.post(
    "/",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_task(
    task_data: TaskCreate,
    current_user: CurrentUser,
    task_service: TaskServiceDep,
) -> TaskResponse:
    task = task_service.create(
        task_data=task_data,
        owner_id=current_user.id,
    )

    return TaskResponse.model_validate(task)




@router.get(
    "/",
    response_model=list[TaskResponse],
)
def get_tasks(
    current_user: CurrentUser,
    task_service: TaskServiceDep,
    task_status: Annotated[
        TaskStatus | None,
        Query(alias="status"),
    ] = None,
    priority: Annotated[
        TaskPriority | None,
        Query(),
    ] = None,
    search: Annotated[
        str | None,
        Query(min_length=1, max_length=200),
    ] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[TaskResponse]:
    tasks = task_service.get_all_for_owner(
        owner_id=current_user.id,
        status=task_status,
        priority=priority,
        search=search,
        limit=limit,
        offset=offset,
    )

    return [
        TaskResponse.model_validate(task)
        for task in tasks
    ]




@router.get(
    "/{task_id}",
    response_model=TaskResponse,
)
def get_task(
    task_id: int,
    current_user: CurrentUser,
    task_service: TaskServiceDep,
) -> TaskResponse:
    task = task_service.get_by_id_for_owner(
        task_id=task_id,
        owner_id=current_user.id,
    )

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return TaskResponse.model_validate(task)


@router.patch(
    "/{task_id}",
    response_model=TaskResponse,
)
def update_task(
    task_id: int,
    task_data: TaskUpdate,
    current_user: CurrentUser,
    task_service: TaskServiceDep,
) -> TaskResponse:
    task = task_service.update(
        task_id=task_id,
        owner_id=current_user.id,
        task_data=task_data,
    )

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return TaskResponse.model_validate(task)


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_task(
    task_id: int,
    current_user: CurrentUser,
    task_service: TaskServiceDep,
) -> None:
    deleted = task_service.delete(
        task_id=task_id,
        owner_id=current_user.id,
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
