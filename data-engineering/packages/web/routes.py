from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from web.client import execute
from web.graphql.user import UPDATE_USER_MUTATION, USER_QUERY, USERS_QUERY

STATIC_DIR = Path(__file__).parent / "static"

templates = Jinja2Templates(directory=Path(__file__).parent / "templates")

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def user_list(request: Request) -> HTMLResponse:
    data = await execute(USERS_QUERY)
    return templates.TemplateResponse(request, "user_list.html", {"users": data["users"]})


@router.get("/users/{id}", response_class=HTMLResponse)
async def user_edit(request: Request, id: str) -> HTMLResponse:
    data = await execute(USER_QUERY, {"id": id})
    if data["user"] is None:
        raise HTTPException(status_code=404, detail="User not found.")
    return templates.TemplateResponse(request, "user_edit.html", {"user": data["user"]})


@router.post("/users/{id}")
async def update_user(
    id: str,
    phoneNumber: Annotated[str, Form()] = "",
    availableDays: Annotated[list[str] | None, Form()] = None,
) -> RedirectResponse:
    await execute(
        UPDATE_USER_MUTATION,
        {
            "id": id,
            "input": {
                "phoneNumber": phoneNumber,
                "availability": {"availableDays": availableDays or []},
            },
        },
    )
    return RedirectResponse("/", status_code=303)
