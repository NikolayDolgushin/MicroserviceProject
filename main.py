from fastapi import APIRouter, FastAPI, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

app = FastAPI()
router = APIRouter()
templates = Jinja2Templates(directory="templates")
user_list = []

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


@router.get("/page", response_class=HTMLResponse)
async def users_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="users_list.html",
        context={"users": user_list},
    )


@router.get("/page/create", response_class=HTMLResponse)
async def create_user_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="create_user.html",
        context={"form": {}},
    )


@router.post("/page/create", response_class=HTMLResponse)
async def create_user_form(
    request: Request,
    id: int = Form(...),
    item: str = Form(...),
    status_: str = Form(..., alias="status"),
):
    for u in user_list:
        if u.id == id:
            return templates.TemplateResponse(
                request=request,
                name="create_user.html",
                context={
                    "form": {"id": id, "item": item, "status": status_},
                    "message": f"Пользователь с id={id} уже существует",
                    "error": True,
                },
                status_code=400,
            )

    user_list.append(User(id=id, lesson=Lesson(item=item, status=status_)))
    return RedirectResponse(url="/user/page", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/page/{id}", response_class=HTMLResponse)
async def user_page(request: Request, id: int):
    for user in user_list:
        if user.id == id:
            return templates.TemplateResponse(
                request=request,
                name="user_detail.html",
                context={"user": user},
            )
    return templates.TemplateResponse(
        request=request,
        name="users_list.html",
        context={
            "users": user_list,
            "message": f"Пользователь с id={id} не найден",
            "error": True,
        },
        status_code=404,
    )


@router.get("/page/{id}/edit", response_class=HTMLResponse)
async def edit_user_page(request: Request, id: int):
    for user in user_list:
        if user.id == id:
            return templates.TemplateResponse(
                request=request,
                name="update_user.html",
                context={
                    "user_id": id,
                    "form": {"item": user.lesson.item, "status": user.lesson.status},
                },
            )
    return RedirectResponse(url="/user/page", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/page/{id}/edit", response_class=HTMLResponse)
async def edit_user_form(
    request: Request,
    id: int,
    item: str = Form(...),
    status_: str = Form(..., alias="status"),
):
    for user in user_list:
        if user.id == id:
            user.lesson = Lesson(item=item, status=status_)
            return RedirectResponse(
                url=f"/user/page/{id}", status_code=status.HTTP_303_SEE_OTHER
            )

    return templates.TemplateResponse(
        request=request,
        name="update_user.html",
        context={
            "user_id": id,
            "form": {"item": item, "status": status_},
            "message": f"Пользователь с id={id} не найден",
            "error": True,
        },
        status_code=404,
    )

@router.get("/page/{id}/delete", response_class=HTMLResponse)
async def delete_user_form(id: int):
    for user in user_list:
        if user.id == id:
            user_list.remove(user)
            break
    return RedirectResponse(url="/user/page", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/", include_in_schema=False)
async def root_redirect():
    return RedirectResponse(url="/user/page", status_code=status.HTTP_303_SEE_OTHER)
