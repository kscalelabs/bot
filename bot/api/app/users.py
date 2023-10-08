"""Defines the API endpoint for creating, deleting and updating user information."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic.main import BaseModel

from bot.api.auth import check_password, hash_password
from bot.api.email import reset_password, send_reset_email, send_verification_email, verify_email
from bot.api.model import User
from bot.api.token import create_access_token, load_access_token

users_router = APIRouter()

security = HTTPBearer()


class UserCreate(BaseModel):
    email: str
    password: str
    login_url: str


@users_router.post("/create")
async def create_user(data: UserCreate) -> bool:
    user_obj = await User.get_or_none(email=data.email)
    if user_obj is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    hashed_password = hash_password(data.password)
    user_obj = await User.create(email=data.email, hashed_password=hashed_password)
    await send_verification_email(data.email, data.login_url)
    return True


class UserReverify(BaseModel):
    email: str
    login_url: str


@users_router.post("/reverify")
async def send_verification(data: UserReverify) -> bool:
    user_obj = await User.get_or_none(email=data.email)
    if user_obj is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email not registered")
    if user_obj.email_verified:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already verified")
    await send_verification_email(data.email, data.login_url)
    return True


@users_router.get("/verify/{payload}")
async def verify(payload: str) -> RedirectResponse:
    try:
        redirect_url = await verify_email(payload)
        return RedirectResponse(url=redirect_url, status_code=307)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid payload")


class UserLogin(BaseModel):
    email: str
    password: str


class UserLoginResponse(BaseModel):
    token: str
    token_type: str


@users_router.post("/login", response_model=UserLoginResponse)
async def login(data: UserLogin) -> UserLoginResponse:
    user_obj = await User.get_or_none(email=data.email)
    if not user_obj:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email not registered")
    if not check_password(data.password, user_obj.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect password")
    return UserLoginResponse(token=create_access_token({"id": user_obj.id}), token_type="bearer")


class TokenData(BaseModel):
    user_id: int


async def get_current_user(authorization: HTTPAuthorizationCredentials = Depends(security)) -> TokenData:
    token = authorization.credentials
    token_data = load_access_token(token)
    return TokenData(user_id=token_data["id"])


class UserInfoResponse(BaseModel):
    email: str
    email_verified: bool


@users_router.get("/me", response_model=UserInfoResponse)
async def get_user_info(data: TokenData = Depends(get_current_user)) -> UserInfoResponse:
    user_obj = await User.get_or_none(id=data.user_id)
    if not user_obj:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")
    return UserInfoResponse(
        email=user_obj.email,
        email_verified=user_obj.email_verified,
    )


@users_router.delete("/me")
async def delete_user(data: TokenData = Depends(get_current_user)) -> bool:
    user_obj = await User.get_or_none(id=data.user_id)
    if not user_obj:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")
    await user_obj.delete()
    return True


users_password_router = APIRouter()


class ForgotPassword(BaseModel):
    email: str
    login_url: str


@users_password_router.post("/forgot")
async def forgot_password(data: ForgotPassword) -> bool:
    user_obj = await User.get_or_none(email=data.email)
    if not user_obj:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email not registered")
    await send_reset_email(data.email, data.login_url)
    return True


class PasswordReset(BaseModel):
    payload: str
    new_password: str


@users_password_router.post("/reset")
async def password_reset(data: PasswordReset) -> bool:
    try:
        await reset_password(data.payload, data.new_password)
        return True
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid payload")


users_router.include_router(users_password_router, prefix="/password", tags=["password"])
