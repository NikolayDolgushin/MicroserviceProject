from contextlib import asynccontextmanager

from fastapi import FastAPI

from database.connection import (
    connect_to_mongodb,
    close_mongodb_connection,
)

from routes import events, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongodb()
    yield
    await close_mongodb_connection()


app = FastAPI(
    title="Microservice Project",
    lifespan=lifespan,
)

app.include_router(events.router)
app.include_router(users.router)


@app.get("/")
async def root():
    return {"message": "Microservice Project API"}