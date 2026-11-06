from beanie import Document, PydanticObjectId
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class User(Document):
    email: str
    password_hash: str
    events: list[PydanticObjectId] = Field(default_factory=list)

    class Settings:
        name = "users"


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserSignIn(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    email: EmailStr