
from beanie import init_beanie
from pydantic_settings import BaseSettings, SettingsConfigDict
from pymongo import AsyncMongoClient

from models.events import Event, EventParticipant
from models.users import User


class Settings(BaseSettings):
    mongo_url: str = "mongodb://localhost:27017"
    database_name: str = "microservice_project"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()

client: AsyncMongoClient | None = None


async def connect_to_mongodb() -> None:
    global client

    client = AsyncMongoClient(settings.mongo_url)

    await init_beanie(
        database=client[settings.database_name],
        document_models=[
            Event,
            User,
            EventParticipant,
        ],
    )


async def close_mongodb_connection() -> None:
    global client

    if client is not None:
        await client.close()
        client = None
