"""Defines the API endpoint for creating, deleting and updating user information."""

import re
from email.utils import parseaddr as parse_email_address

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic.main import BaseModel

from bot.api.auth import check_password, hash_password
from bot.api.email import OneTimePassPayload, send_otp_email, send_verification_email, verify_email
from bot.api.model import User
from bot.api.token import create_access_token, load_access_token

users_router = APIRouter()

security = HTTPBearer()


class TokenData(BaseModel):
    user_id: int
    is_verified: bool

    def encode(self) -> str:
        return create_access_token(
            {
                "id": self.user_id,
                "verified": self.is_verified,
            },
        )

    @classmethod
    def decode(cls, payload: str) -> "TokenData":
        token_data = load_access_token(payload)
        return cls(
            user_id=token_data["id"],
            is_verified=token_data["verified"],
        )


class UserSignup(BaseModel):
    email: str
    password: str
    login_url: str


class UserSignupResponse(BaseModel):
    token: str
    token_type: str


def validate_email(email: str) -> str:
    try:
        email = parse_email_address(email)[1]
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid email")
    return email


def validate_password(password: str) -> str:
    if len(password) < 8:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password must be at least 8 characters")
    if len(password) > 128:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password must be at most 128 characters")
    if not re.search(r"[a-z]", password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password must contain a lowercase letter")
    if not re.search(r"[A-Z]", password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password must contain an uppercase letter")
    if not re.search(r"[0-9]", password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password must contain a number")
    return password


@users_router.post("/signup")
async def sign_up_user(data: UserSignup, request: Request) -> UserSignupResponse:
    email = validate_email(data.email)
    password = validate_password(data.password)
    user_obj = await User.get_or_none(email=email)
    if user_obj is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    hashed_password = hash_password(password)
    user_obj = await User.create(email=data.email, hashed_password=hashed_password)
    request_url = str(request.base_url)
    await send_verification_email(data.email, request_url, data.login_url)
    return UserSignupResponse(
        token=TokenData(
            user_id=user_obj.id,
            is_verified=user_obj.email_verified,
        ).encode(),
        token_type="bearer",
    )


class UserReverify(BaseModel):
    email: str
    login_url: str


@users_router.post("/reverify")
async def resend_verification(data: UserReverify, request: Request) -> bool:
    user_obj = await User.get_or_none(email=data.email)
    if user_obj is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email not registered")
    if user_obj.email_verified:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already verified")
    request_url = str(request.base_url)
    await send_verification_email(data.email, request_url, data.login_url)
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
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid username or password")
    if not check_password(data.password, user_obj.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid username or password")
    return UserLoginResponse(
        token=TokenData(
            user_id=user_obj.id,
            is_verified=user_obj.email_verified,
        ).encode(),
        token_type="bearer",
    )


class OneTimePass(BaseModel):
    payload: str


@users_router.post("/otp", response_model=UserLoginResponse)
async def otp(data: OneTimePass) -> UserLoginResponse:
    try:
        data = OneTimePassPayload.decode(data.payload)
        user_obj = await User.get(email=data.email)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid one-time passcode")
    return UserLoginResponse(
        token=TokenData(
            user_id=user_obj.id,
            is_verified=user_obj.email_verified,
        ).encode(),
        token_type="bearer",
    )


async def get_current_user(authorization: HTTPAuthorizationCredentials = Depends(security)) -> TokenData:
    token = authorization.credentials
    return TokenData.decode(token)


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


@users_router.delete("/myself")
async def delete_user(data: TokenData = Depends(get_current_user)) -> bool:
    user_obj = await User.get_or_none(id=data.user_id)
    if not user_obj:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")
    await user_obj.delete()
    return True


class UpdateEmail(BaseModel):
    new_email: str
    login_url: str


@users_router.put("/email/update")
async def update_email(data: UpdateEmail, request: Request, user_data: TokenData = Depends(get_current_user)) -> bool:
    user_obj = await User.get_or_none(id=user_data.user_id)
    if not user_obj:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")
    new_email = validate_email(data.new_email)
    if new_email == user_obj.email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="New email cannot be the same as old email")
    user_obj.email = new_email
    user_obj.email_verified = False
    await user_obj.save()
    request_url = str(request.base_url)
    await send_verification_email(new_email, request_url, data.login_url)
    return True


class UpdatePassword(BaseModel):
    new_password: str


@users_router.put("/password/update")
async def update_password(data: UpdatePassword, user_data: TokenData = Depends(get_current_user)) -> bool:
    user_obj = await User.get_or_none(id=user_data.user_id)
    if not user_obj:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")
    user_obj.hashed_password = hash_password(validate_password(data.new_password))
    await user_obj.save()
    return True


class ForgotPassword(BaseModel):
    email: str
    login_url: str


@users_router.post("/password/forgot")
async def forgot_password(data: ForgotPassword) -> bool:
    user_obj = await User.get_or_none(email=data.email)
    if not user_obj:
        # raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email not registered")
        # Don't leak whether the email is registered or not.
        return True
    await send_otp_email(data.email, data.login_url)
    return True
