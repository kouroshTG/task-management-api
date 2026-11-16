
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.task import Task
from app.schemas.task import TaskCreate


class TaskRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        task_data: TaskCreate,
        owner_id: int,
    ) -> Task:
        task = Task(
            **task_data.model_dump(),
            owner_id=owner_id,
        )

        self.db.add(task)
        self.db.flush()

        return task

    def get_by_id_for_owner(
        self,
        task_id: int,
        owner_id: int,
    ) -> Task | None:
        statement = select(Task).where(
            Task.id == task_id,
            Task.owner_id == owner_id,
        )

        return self.db.execute(statement).scalar_one_or_none()



    def get_all_for_owner(
        self,
        owner_id: int,
        status: str | None = None,
        priority: str | None = None,
        search: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Task]:
        statement = select(Task).where(
            Task.owner_id == owner_id,
        )

        if status is not None:
            statement = statement.where(Task.status == status)

        if priority is not None:
            statement = statement.where(Task.priority == priority)

        if search is not None:
            search_term = f"%{search}%"

            statement = statement.where(
                or_(
                    Task.title.ilike(search_term),
                    Task.description.ilike(search_term),
                )
            )

        statement = (
            statement
            .order_by(Task.created_at.desc(), Task.id.desc())
            .offset(offset)
            .limit(limit)
        )

        return list(self.db.execute(statement).scalars().all())


    def update(
        self,
        task: Task,
        update_data: dict,
    ) -> Task:
        for field, value in update_data.items():
            setattr(task, field, value)

        self.db.flush()

        return task

    def delete(self, task: Task) -> None:
        self.db.delete(task)
        self.db.flush()
