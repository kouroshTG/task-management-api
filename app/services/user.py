
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate


class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repository = UserRepository(db)

    def get_by_id(self, user_id: int) -> User | None:
        return self.user_repository.get_by_id(user_id)

    def register(self, user_data: UserCreate) -> User:
        existing_user = self.user_repository.get_by_email(
            user_data.email
        )

        if existing_user is not None:
            raise ValueError("Email is already registered")

        password_hash = hash_password(user_data.password)

        try:
            user = self.user_repository.create(
                user_data=user_data,
                password_hash=password_hash,
            )

            self.db.commit()
            self.db.refresh(user)

            return user

        except IntegrityError:
            self.db.rollback()

            existing_user = self.user_repository.get_by_email(
                user_data.email
            )

            if existing_user is not None:
                raise ValueError(
                    "Email is already registered"
                ) from None

            raise

    def authenticate(
        self,
        email: str,
        password: str,
    ) -> User:
        user = self.user_repository.get_by_email(email)

        if user is None:
            raise ValueError("Invalid email or password")

        if not verify_password(password, user.password_hash):
            raise ValueError("Invalid email or password")

        if not user.is_active:
            raise ValueError("Account is inactive")

        return user
