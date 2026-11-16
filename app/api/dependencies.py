
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.user import User
from app.services.task import TaskService
from app.services.user import UserService

bearer_scheme = HTTPBearer(auto_error=False)


def get_user_service(
    db: Annotated[Session, Depends(get_db)],
) -> UserService:
    return UserService(db)



def get_task_service(
    db: Annotated[Session, Depends(get_db)],
) -> TaskService:
    return TaskService(db)


TaskServiceDep = Annotated[
    TaskService,
    Depends(get_task_service),
]

UserServiceDep = Annotated[
    UserService,
    Depends(get_user_service),
]


def get_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(bearer_scheme),
    ],
    user_service: UserServiceDep,
) -> User:
    unauthorized_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if credentials is None:
        raise unauthorized_exception

    payload = decode_access_token(credentials.credentials)

    if payload is None:
        raise unauthorized_exception

    subject = payload.get("sub")

    if not isinstance(subject, str) or not subject.isdecimal():
        raise unauthorized_exception

    user = user_service.get_by_id(int(subject))

    if user is None or not user.is_active:
        raise unauthorized_exception

    return user


CurrentUser = Annotated[
    User,
    Depends(get_current_user),
]
