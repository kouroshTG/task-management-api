
from sqlalchemy.orm import Session

from app.models.task import Task
from app.repositories.task import TaskRepository
from app.schemas.task import TaskCreate, TaskUpdate


class TaskService:
    def __init__(self, db: Session):
        self.db = db
        self.task_repository = TaskRepository(db)

    def create(
        self,
        task_data: TaskCreate,
        owner_id: int,
    ) -> Task:
        try:
            task = self.task_repository.create(
                task_data=task_data,
                owner_id=owner_id,
            )

            self.db.commit()
            self.db.refresh(task)

            return task

        except Exception:
            self.db.rollback()
            raise

    def get_by_id_for_owner(
        self,
        task_id: int,
        owner_id: int,
    ) -> Task | None:
        return self.task_repository.get_by_id_for_owner(
            task_id=task_id,
            owner_id=owner_id,
        )



    def get_all_for_owner(
        self,
        owner_id: int,
        status: str | None = None,
        priority: str | None = None,
        search: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Task]:
        return self.task_repository.get_all_for_owner(
            owner_id=owner_id,
            status=status,
            priority=priority,
            search=search,
            limit=limit,
            offset=offset,
        )




    def update(
        self,
        task_id: int,
        owner_id: int,
        task_data: TaskUpdate,
    ) -> Task | None:
        task = self.task_repository.get_by_id_for_owner(
            task_id=task_id,
            owner_id=owner_id,
        )

        if task is None:
            return None

        update_data = task_data.model_dump(
            exclude_unset=True,
        )

        try:
            self.task_repository.update(
                task=task,
                update_data=update_data,
            )

            self.db.commit()
            self.db.refresh(task)

            return task

        except Exception:
            self.db.rollback()
            raise


    def delete(
        self,
        task_id: int,
        owner_id: int,
    ) -> bool:
        task = self.task_repository.get_by_id_for_owner(
            task_id=task_id,
            owner_id=owner_id,
        )

        if task is None:
            return False

        try:
            self.task_repository.delete(task)
            self.db.commit()

            return True

        except Exception:
            self.db.rollback()
            raise
