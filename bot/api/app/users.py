"""Defines the API endpoint for creating, deleting and updating user information."""

from email.utils import parseaddr as parse_email_address

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic.main import BaseModel

from bot.api.email import OneTimePassPayload, send_otp_email
from bot.api.model import User
from bot.api.token import create_access_token, load_access_token

users_router = APIRouter()

security = HTTPBearer()


class TokenData(BaseModel):
    user_id: int

    def encode(self) -> str:
        return create_access_token({"id": self.user_id})

    @classmethod
    def decode(cls, payload: str) -> "TokenData":
        token_data = load_access_token(payload)
        return cls(user_id=token_data["id"])


class UserSignup(BaseModel):
    email: str
    login_url: str


def validate_email(email: str) -> str:
    try:
        email = parse_email_address(email)[1]
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid email")
    return email


@users_router.post("/login")
async def login_user(data: UserSignup) -> bool:
    email = validate_email(data.email)
    payload = OneTimePassPayload(email)
    await send_otp_email(payload, data.login_url)
    return True


class OneTimePass(BaseModel):
    payload: str


class UserLoginResponse(BaseModel):
    token: str
    token_type: str


@users_router.post("/otp", response_model=UserLoginResponse)
async def otp(data: OneTimePass) -> UserLoginResponse:
    try:
        payload = OneTimePassPayload.decode(data.payload)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid one-time passcode")
    user_obj = await User.get_or_none(email=payload.email)
    if user_obj is None:
        user_obj = await User.create(email=payload.email)
    if not user_obj:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid one-time passcode")
    if user_obj.banned:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is banned")
    return UserLoginResponse(
        token=TokenData(user_id=user_obj.id).encode(),
        token_type="bearer",
    )


async def get_current_user(authorization: HTTPAuthorizationCredentials = Depends(security)) -> TokenData:
    token = authorization.credentials
    return TokenData.decode(token)


class UserInfoResponse(BaseModel):
    email: str


@users_router.get("/me", response_model=UserInfoResponse)
async def get_user_info(data: TokenData = Depends(get_current_user)) -> UserInfoResponse:
    user_obj = await User.get_or_none(id=data.user_id)
    if not user_obj:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")
    return UserInfoResponse(email=user_obj.email)


@users_router.delete("/myself")
async def delete_user(data: TokenData = Depends(get_current_user)) -> bool:
    user_obj = await User.get_or_none(id=data.user_id)
    if not user_obj:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")
    await user_obj.delete()
    return True
