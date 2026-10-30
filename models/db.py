from sqlalchemy import Column, JSON
from sqlmodel import Field, Relationship, SQLModel


class UserEventLink(SQLModel, table=True):
    __tablename__ = "user_event_link"

    user_id: int | None = Field(default=None, foreign_key="users.id", primary_key=True)
    event_id: int | None = Field(default=None, foreign_key="events.id", primary_key=True)


class EventDB(SQLModel, table=True):
    __tablename__ = "events"

    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(min_length=1, max_length=200)
    image: str = Field(min_length=1, max_length=2048)
    description: str
    location: str = Field(min_length=1, max_length=300)
    tags: list[str] = Field(default_factory=list, sa_column=Column(JSON))

    users: list["UserDB"] = Relationship(back_populates="events", link_model=UserEventLink)


class UserDB(SQLModel, table=True):
    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=320)
    password: str = Field(min_length=8, max_length=128)  # было password_hash

    events: list[EventDB] = Relationship(back_populates="users", link_model=UserEventLink)