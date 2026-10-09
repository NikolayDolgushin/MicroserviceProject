from fastapi import FastAPI, APIRouter
from pydantic import BaseModel

app = FastAPI()
router = APIRouter()
user_list=[]

app.include_router(router, prefix="/user", tags=["user"])

class Lesson(BaseModel):
    item: str
    status: str
class User(BaseModel):
    id: int
    lesson: Lesson
class UserUpdate(BaseModel):
    lesson: Lesson



@router.get("/user/{id}")
async def get_user(id: int):
    for user in user_list:
        if user.id == id:
            return user
    return {"message": "user not found"}

@router.post("/user")
async def create_user(user: User):
    user_list.append(user)
    return user

@router.get("/user")
async def get_user():
    return user_list

@router.delete("/user/{id}")
async def delete_user(id: int):
    for user in user_list:
        if user.id == id:
            user_list.remove(user)
            return {"message": "user deleted"}
        return {"message": "user not found"}
    return None

@router.patch("/user/{id}")
async def update_user(id: int, update_data: UserUpdate):
    for user in user_list:
        if user.id == id:
            user.lesson = update_data.lesson
            return user
        return {"message": "user not found"}
    return None



