"""Defines the API endpoint for creating, deleting and updating user information."""

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import RedirectResponse

from bot.api.email import send_verification_email, verify_email
from bot.api.model import User, User_Pydantic
from bot.settings import load_settings

users_router = APIRouter()


@users_router.post("/create", response_model=User_Pydantic)
async def create_user(email: str, password: str) -> User_Pydantic:
    user_obj = await User.get_or_none(email=email)
    if user_obj:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    user_obj = await User.create(email=email, password=password)
    await send_verification_email(email)
    return await User_Pydantic.from_tortoise_orm(user_obj)


@users_router.get("/verify/{payload}")
async def verify(payload: str) -> RedirectResponse:
    try:
        await verify_email(payload)
        homepage = load_settings().site.homepage
        return RedirectResponse(url=homepage)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid payload")


@users_router.post("/delete")
async def delete(email: str) -> None:
    user_obj = await User.get_or_none(email=email)
    if user_obj is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")
    await user_obj.delete()
