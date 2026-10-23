from fastapi import APIRouter, HTTPException, status

from database.connection import events
from models.events import Event, EventCreate, EventUpdate
from models.users import UserMessage

event_router = APIRouter()


@event_router.get("/", response_model=list[Event])
async def retrieve_all_events() -> list[Event]:
    return list(events.values())


@event_router.get("/{event_id}", response_model=Event)
async def retrieve_event(event_id: int) -> Event:
    event = events.get(event_id)
    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event with supplied ID does not exist",
        )
    return event


@event_router.post("/new", response_model=UserMessage, status_code=status.HTTP_201_CREATED)
async def create_event(body: EventCreate) -> UserMessage:
    if body.id in events:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Event with supplied ID already exists",
        )
    events[body.id] = Event(**body.model_dump())
    return UserMessage(message="Event created successfully")


@event_router.patch("/{event_id}", response_model=Event)
async def update_event(event_id: int, body: EventUpdate) -> Event:
    event = events.get(event_id)
    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event with supplied ID does not exist",
        )
    updated_data = event.model_dump()
    updated_data.update(body.model_dump(exclude_unset=True))
    events[event_id] = Event(**updated_data)
    return events[event_id]


@event_router.delete("/{event_id}", response_model=UserMessage)
async def delete_event(event_id: int) -> UserMessage:
    if event_id not in events:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event with supplied ID does not exist",
        )
    del events[event_id]
    return UserMessage(message="Event deleted successfully")


