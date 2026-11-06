
from beanie import PydanticObjectId
from fastapi import APIRouter, HTTPException, status

from models.events import (
    Event,
    EventCreate,
    EventUpdate,
    EventResponse,
    EventParticipant,
)
from models.users import User, UserResponse


router = APIRouter(
    prefix="/events",
    tags=["Events"],
)


@router.post(
    "/",
    response_model=EventResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_event(data: EventCreate):
    event = Event(**data.model_dump())
    await event.insert()

    return EventResponse(
        id=str(event.id),
        **event.model_dump(exclude={"id"}),
    )

@router.get("/", response_model=list[EventResponse])
async def get_events():
    events = await Event.find_all().to_list()

    return [
        EventResponse(id=str(event.id), **event.model_dump(exclude={"id"}))
        for event in events
    ]


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(event_id: PydanticObjectId):
    event = await Event.get(event_id)

    if event is None:
        raise HTTPException(404, "Event not found")

    return EventResponse(
        id=str(event.id),
        **event.model_dump(exclude={"id"}),
    )


@router.patch("/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: PydanticObjectId,
    data: EventUpdate,
):
    event = await Event.get(event_id)

    if event is None:
        raise HTTPException(404, "Event not found")

    update_data = data.model_dump(
        exclude_unset=True,
        exclude_none=True,
    )

    for field, value in update_data.items():
        setattr(event, field, value)

    await event.save()

    return EventResponse(
        id=str(event.id),
        **event.model_dump(exclude={"id"}),
    )


# Добавление пользователя на мероприятие

@router.post(
    "/{event_id}/participants/{user_id}",
    status_code=status.HTTP_201_CREATED,
)
async def add_participant(
    event_id: PydanticObjectId,
    user_id: PydanticObjectId,
):
    event = await Event.get(event_id)
    user = await User.get(user_id)

    if event is None:
        raise HTTPException(404, "Event not found")

    if user is None:
        raise HTTPException(404, "User not found")

    existing = await EventParticipant.find_one(
        EventParticipant.event_id == event_id,
        EventParticipant.user_id == user_id,
    )

    if existing is not None:
        raise HTTPException(409, "User already participates in this event")

    await EventParticipant(
        event_id=event_id,
        user_id=user_id,
    ).insert()

    return {"message": "User successfully added to event"}


# Получение участников мероприятия

@router.get(
    "/{event_id}/participants",
    response_model=list[UserResponse],
)
async def get_event_participants(event_id: PydanticObjectId):
    event = await Event.get(event_id)

    if event is None:
        raise HTTPException(404, "Event not found")

    participations = await EventParticipant.find(
        EventParticipant.event_id == event_id
    ).to_list()

    users = []

    for participation in participations:
        user = await User.get(participation.user_id)

        if user is not None:
            users.append(
                UserResponse(
                    id=str(user.id),
                    email=user.email,
                )
            )

    return users


# Удаление пользователя из мероприятия

@router.delete("/{event_id}/participants/{user_id}")
async def remove_participant(
    event_id: PydanticObjectId,
    user_id: PydanticObjectId,
):
    participation = await EventParticipant.find_one(
        EventParticipant.event_id == event_id,
        EventParticipant.user_id == user_id,
    )

    if participation is None:
        raise HTTPException(404, "Participation not found")

    await participation.delete()

    return {"message": "User removed from event"}


# Удаление мероприятия вместе со связями

@router.delete(
    "/{event_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_event(event_id: PydanticObjectId):
    event = await Event.get(event_id)

    if event is None:
        raise HTTPException(404, "Event not found")

    await EventParticipant.find(
        EventParticipant.event_id == event_id
    ).delete()

    await event.delete()
