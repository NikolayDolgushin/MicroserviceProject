
from beanie import PydanticObjectId
from fastapi import APIRouter, HTTPException, status
from pwdlib import PasswordHash

from models.users import User, UserCreate, UserResponse
from models.events import Event, EventResponse, EventParticipant


router = APIRouter(
    prefix="/users",
    tags=["Users"],
)

password_hash = PasswordHash.recommended()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_user(data: UserCreate):
    existing_user = await User.find_one(
        User.email == data.email
    )

    if existing_user is not None:
        raise HTTPException(409, "User already exists")

    user = User(
        email=data.email,
        password_hash=password_hash.hash(data.password),
    )

    await user.insert()

    return UserResponse(
        id=str(user.id),
        email=user.email,
    )


# Получение мероприятий пользователя

@router.get(
    "/{user_id}/events",
    response_model=list[EventResponse],
)
async def get_user_events(user_id: PydanticObjectId):
    user = await User.get(user_id)

    if user is None:
        raise HTTPException(404, "User not found")

    participations = await EventParticipant.find(
        EventParticipant.user_id == user_id
    ).to_list()

    events = []

    for participation in participations:
        event = await Event.get(participation.event_id)

        if event is not None:
            events.append(
                EventResponse(
                    id=str(event.id),
                    **event.model_dump(exclude={"id"}),
                )
            )

    return events


# Удаление пользователя вместе со связями

@router.delete("/{user_id}")
async def delete_user(user_id: PydanticObjectId):
    user = await User.get(user_id)

    if user is None:
        raise HTTPException(404, "User not found")

    await EventParticipant.find(
        EventParticipant.user_id == user_id
    ).delete()

    await user.delete()

    return {"message": "User deleted"}

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    try:
        user_object_id = PydanticObjectId(user_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID",
        )

    user = await User.get(user_object_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    participations = await EventParticipant.find(
        EventParticipant.user_id == user.id
    ).to_list()

    events = []

    for participation in participations:
        event = await Event.get(participation.event_id)

        if event is not None:
            events.append(
                EventResponse(
                    id=str(event.id),
                    **event.model_dump(exclude={"id"}),
                )
            )

    return UserResponse(
        id=str(user.id),
        email=user.email,
        events=events,
    )