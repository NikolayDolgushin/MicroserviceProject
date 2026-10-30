from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from database.connection import get_session
from models.db import EventDB
from models.events import Event, EventCreate, EventUpdate
from models.users import UserMessage

event_router = APIRouter()

SessionDep = Annotated[Session, Depends(get_session)]


@event_router.get("/", response_model=list[Event])
async def retrieve_all_events(session: SessionDep) -> list[EventDB]:
    events = session.exec(select(EventDB)).all()
    return events


@event_router.get("/{event_id}", response_model=Event)
async def retrieve_event(event_id: int, session: SessionDep) -> EventDB:
    event = session.get(EventDB, event_id)
    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event with supplied ID does not exist",
        )
    return event


@event_router.post("/new", response_model=UserMessage, status_code=status.HTTP_201_CREATED)
async def create_event(body: EventCreate, session: SessionDep) -> UserMessage:
    if body.id is not None:
        existing = session.get(EventDB, body.id)
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Event with supplied ID already exists",
            )

    event = EventDB(**body.model_dump(exclude={"id"}))
    if body.id is not None:
        event.id = body.id

    session.add(event)
    session.commit()
    session.refresh(event)
    return UserMessage(message="Event created successfully")


@event_router.patch("/{event_id}", response_model=Event)
async def update_event(event_id: int, body: EventUpdate, session: SessionDep) -> EventDB:
    event = session.get(EventDB, event_id)
    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event with supplied ID does not exist",
        )

    update_data = body.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(event, key, value)

    session.add(event)
    session.commit()
    session.refresh(event)
    return event


@event_router.delete("/{event_id}", response_model=UserMessage)
async def delete_event(event_id: int, session: SessionDep) -> UserMessage:
    event = session.get(EventDB, event_id)
    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event with supplied ID does not exist",
        )
    session.delete(event)
    session.commit()
    return UserMessage(message="Event deleted successfully")