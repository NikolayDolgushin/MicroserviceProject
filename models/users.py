from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserSignIn(BaseModel):
    email: EmailStr
    password: str


class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    email: EmailStr
    events: list[int] = Field(default_factory=list)

    @field_validator("events", mode="before")
    @classmethod
    def _events_to_ids(cls, v):
        # v может быть: None, list[int] (уже готовый), list[EventDB] (из ORM)
        if not v:
            return []
        if hasattr(v[0], "id"):
            return [e.id for e in v]
        return v


class UserMessage(BaseModel):
    message: str
