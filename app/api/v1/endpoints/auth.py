
from fastapi import APIRouter, HTTPException, status

from app.api.dependencies import UserServiceDep
from app.core.security import create_access_token
from app.schemas.user import (
    TokenResponse,
    UserCreate,
    UserLogin,
    UserResponse,
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_user(
    user_data: UserCreate,
    user_service: UserServiceDep,
) -> UserResponse:
    try:
        user = user_service.register(user_data)
        return UserResponse.model_validate(user)

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login_user(
    user_data: UserLogin,
    user_service: UserServiceDep,
) -> TokenResponse:
    try:
        user = user_service.authenticate(
            email=user_data.email,
            password=user_data.password,
        )

        access_token = create_access_token(
            subject=str(user.id),
        )

        return TokenResponse(
            access_token=access_token,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(error),
            headers={"WWW-Authenticate": "Bearer"},
        ) from error
