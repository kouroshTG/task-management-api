
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> User | None:
        statement = select(User).where(User.email == email)

        return self.db.execute(statement).scalar_one_or_none()

    def get_by_id(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)

    def create(self, user_data: UserCreate, password_hash: str) -> User:
        user = User(
            email=user_data.email,
            password_hash=password_hash,
            full_name=user_data.full_name,
        )

        self.db.add(user)
        self.db.flush()

        return user
