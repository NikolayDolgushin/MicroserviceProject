from fastapi import APIRouter, HTTPException, status

from database.connection import users
from models.users import User, UserCreate, UserMessage, UserSignIn

user_router = APIRouter()


@user_router.post("/signup", response_model=UserMessage, status_code=status.HTTP_201_CREATED)
async def sign_up(data: UserCreate) -> UserMessage:
    email = str(data.email).lower()
    if email in users:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with supplied email already exists",
        )
    users[email] = data
    return UserMessage(message="User successfully registered!")


@user_router.post("/signin", response_model=UserMessage)
async def sign_in(data: UserSignIn) -> UserMessage:
    email = str(data.email).lower()
    stored_user = users.get(email)
    if stored_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not exist",
        )
    # Учебный пример: пароль хранится открытым текстом.
    # Для реального приложения нужен хеш пароля и полноценная аутентификация.
    if stored_user.password != data.password:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Wrong credentials passed",
        )
    return UserMessage(message="User signed in successfully")
