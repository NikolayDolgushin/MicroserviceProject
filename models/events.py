
from datetime import datetime, timezone

from beanie import Document, PydanticObjectId
from pydantic import BaseModel, ConfigDict, Field
from pymongo import ASCENDING, IndexModel


class Event(Document):
    title: str = Field(min_length=1, max_length=200)
    image: str = Field(min_length=1, max_length=2048)
    description: str = Field(min_length=1)
    tags: list[str] = Field(default_factory=list)
    location: str = Field(min_length=1, max_length=300)

    class Settings:
        name = "events"


class EventParticipant(Document):
    user_id: PydanticObjectId
    event_id: PydanticObjectId
    registered_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    class Settings:
        name = "event_participants"

        indexes = [
            IndexModel(
                [
                    ("user_id", ASCENDING),
                    ("event_id", ASCENDING),
                ],
                unique=True,
            ),
            IndexModel([("event_id", ASCENDING)]),
        ]


class EventCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    image: str = Field(min_length=1, max_length=2048)
    description: str = Field(min_length=1)
    tags: list[str] = Field(default_factory=list)
    location: str = Field(min_length=1, max_length=300)


class EventUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    image: str | None = Field(default=None, min_length=1, max_length=2048)
    description: str | None = Field(default=None, min_length=1)
    tags: list[str] | None = None
    location: str | None = Field(default=None, min_length=1, max_length=300)


class EventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    image: str
    description: str
    tags: list[str]
    location: str
