from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from database.connection import get_session
from models.db import EventDB, UserDB
from models.users import User, UserCreate, UserMessage, UserSignIn

user_router = APIRouter()

SessionDep = Annotated[Session, Depends(get_session)]


def _get_user_by_email(session: Session, email: str) -> UserDB | None:
    return session.exec(select(UserDB).where(UserDB.email == email)).first()


@user_router.post("/signup", response_model=User, status_code=status.HTTP_201_CREATED)
async def signup(body: UserCreate, session: SessionDep) -> UserDB:
    if _get_user_by_email(session, body.email) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists",
        )

    user = UserDB(email=body.email, password=body.password)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@user_router.post("/signin", response_model=User)
async def signin(body: UserSignIn, session: SessionDep) -> UserDB:
    user = _get_user_by_email(session, body.email)
    if user is None or user.password != body.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    return user


@user_router.get("/{email}", response_model=User)
async def retrieve_user(email: str, session: SessionDep) -> UserDB:
    user = _get_user_by_email(session, email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@user_router.post("/{email}/events/{event_id}", response_model=UserMessage)
async def register_for_event(email: str, event_id: int, session: SessionDep) -> UserMessage:
    user = _get_user_by_email(session, email)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    event = session.get(EventDB, event_id)
    if event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

    if event in user.events:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User is already registered for this event",
        )

    user.events.append(event)
    session.add(user)
    session.commit()
    return UserMessage(message="Successfully registered for event")


@user_router.delete("/{email}/events/{event_id}", response_model=UserMessage)
async def unregister_from_event(email: str, event_id: int, session: SessionDep) -> UserMessage:
    user = _get_user_by_email(session, email)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    event = session.get(EventDB, event_id)
    if event is None or event not in user.events:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User is not registered for this event",
        )

    user.events.remove(event)
    session.add(user)
    session.commit()
    return UserMessage(message="Successfully unregistered from event")