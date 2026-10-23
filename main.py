from fastapi import FastAPI
import uvicorn

from routes.events import event_router
from routes.users import user_router

app = FastAPI(
    title="Event Planner API",
    version="1.0.0",
)

app.include_router(user_router, prefix="/user", tags=["User"])
app.include_router(event_router, prefix="/event", tags=["Events"])


@app.get("/", tags=["Root"])
async def root() -> dict[str, str]:
    return {"message": "Event Planner API is running", "docs": "/docs"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8080, reload=True)
