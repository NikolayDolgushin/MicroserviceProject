from pydantic import BaseModel, ConfigDict, Field


class EventBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    image: str = Field(min_length=1, max_length=2048)
    description: str = Field(min_length=1)
    tags: list[str] = Field(default_factory=list)
    location: str = Field(min_length=1, max_length=300)


class EventCreate(EventBase):
    id: int = Field(gt=0)


class Event(EventCreate):
    model_config = ConfigDict(from_attributes=True)


class EventUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    image: str | None = Field(default=None, min_length=1, max_length=2048)
    description: str | None = Field(default=None, min_length=1)
    tags: list[str] | None = None
    location: str | None = Field(default=None, min_length=1, max_length=300)
