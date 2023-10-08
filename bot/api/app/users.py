"""Defines the API endpoint for creating, deleting and updating user information."""

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import RedirectResponse
from pydantic.main import BaseModel

from bot.api.email import send_verification_email, verify_email
from bot.api.model import User

users_router = APIRouter()


class UserCreate(BaseModel):
    email: str
    password: str
    login_url: str


@users_router.post("/create")
async def create_user(data: UserCreate) -> bool:
    user_obj = await User.get_or_none(email=data.email)
    if user_obj:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    user_obj = await User.create(email=data.email, password=data.password)
    await send_verification_email(data.email, data.login_url)
    return True


@users_router.get("/verify/{payload}")
async def verify(payload: str) -> RedirectResponse:
    try:
        redirect_url = await verify_email(payload)
        return RedirectResponse(url=redirect_url, status_code=307)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid payload")
