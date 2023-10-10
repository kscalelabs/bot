"""Defines the API endpoint for creating, deleting and updating user information."""

from email.utils import parseaddr as parse_email_address

from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response, status
from fastapi.security import HTTPBearer
from fastapi.security.utils import get_authorization_scheme_param
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token
from pydantic.main import BaseModel

from bot.api.email import OneTimePassPayload, send_delete_email, send_otp_email
from bot.api.model import Token, User
from bot.api.token import create_refresh_token, create_token, load_refresh_token, load_token
from bot.settings import load_settings

users_router = APIRouter()

security = HTTPBearer()

REFRESH_TOKEN_COOKIE_KEY = "__DPSH_REFRESH_TOKEN"
SESSION_TOKEN_COOKIE_KEY = "__DPSH_SESSION_TOKEN"

TOKEN_TYPE = "Bearer"


def set_token_cookie(response: Response, token: str, key: str) -> None:
    is_prod = load_settings().is_prod
    response.set_cookie(
        key=key,
        value=token,
        httponly=True,
        secure=is_prod,
        # samesite="strict",
        samesite="none",
    )


class RefreshTokenData(BaseModel):
    user_id: int
    token_id: int

    @classmethod
    async def encode(cls, user: User) -> str:
        return await create_refresh_token(user)

    @classmethod
    def decode(cls, payload: str) -> "RefreshTokenData":
        user_id, token_id = load_refresh_token(payload)
        return cls(user_id=user_id, token_id=token_id)


class SessionTokenData(BaseModel):
    user_id: int

    def encode(self) -> str:
        expire_minutes = load_settings().crypto.expire_token_minutes
        return create_token({"uid": self.user_id}, expire_minutes=expire_minutes)

    @classmethod
    def decode(cls, payload: str) -> "SessionTokenData":
        data = load_token(payload)
        return cls(user_id=data["uid"])


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


async def create_or_get(email: str) -> User:
    user_obj = await User.get_or_none(email=email)
    if user_obj is None:
        user_obj = await User.create(email=email)
    if not user_obj:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid one-time passcode")
    if user_obj.banned:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is banned")
    return user_obj


async def get_login_response(response: Response, user_obj: User) -> UserLoginResponse:
    refresh_token = await RefreshTokenData.encode(user_obj)
    set_token_cookie(response, refresh_token, REFRESH_TOKEN_COOKIE_KEY)
    return UserLoginResponse(token=refresh_token, token_type=TOKEN_TYPE)


@users_router.post("/otp", response_model=UserLoginResponse)
async def otp(data: OneTimePass, response: Response) -> UserLoginResponse:
    payload = OneTimePassPayload.decode(data.payload)
    user_obj = await create_or_get(payload.email)
    return await get_login_response(response, user_obj)


class GoogleLogin(BaseModel):
    token: str


@users_router.post("/google")
async def google_login(data: GoogleLogin) -> UserLoginResponse:
    try:
        idinfo = google_id_token.verify_oauth2_token(data.token, google_requests.Request())
        email = idinfo["email"]
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Google token")
    user_obj = await create_or_get(email)
    return await get_login_response(user_obj)


def get_token_from_cookie(token: str | None = Cookie(None)) -> str:
    if token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return token


async def get_refresh_token(request: Request) -> RefreshTokenData:
    # Tries Authorization header.
    authorization = request.headers.get("Authorization")
    if authorization:
        scheme, credentials = get_authorization_scheme_param(authorization)
        if not (scheme and credentials):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
        if scheme.lower() != TOKEN_TYPE.lower():
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
        return RefreshTokenData.decode(credentials)

    # Tries Cookie.
    cookie_token = request.cookies.get(REFRESH_TOKEN_COOKIE_KEY)
    if cookie_token:
        return RefreshTokenData.decode(cookie_token)

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")


async def get_session_token(request: Request) -> SessionTokenData:
    # Tries Authorization header.
    authorization = request.headers.get("Authorization")
    if authorization:
        scheme, credentials = get_authorization_scheme_param(authorization)
        if not (scheme and credentials):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
        if scheme.lower() != TOKEN_TYPE:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
        return SessionTokenData.decode(credentials)

    # Tries Cookie.
    cookie_token = request.cookies.get(SESSION_TOKEN_COOKIE_KEY)
    if cookie_token:
        return SessionTokenData.decode(cookie_token)

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")


class UserInfoResponse(BaseModel):
    email: str


@users_router.get("/me", response_model=UserInfoResponse)
async def get_user_info(data: SessionTokenData = Depends(get_session_token)) -> UserInfoResponse:
    user_obj = await User.get_or_none(id=data.user_id)
    if not user_obj:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")
    return UserInfoResponse(email=user_obj.email)


@users_router.delete("/myself")
async def delete_user(data: SessionTokenData = Depends(get_session_token)) -> bool:
    user_obj = await User.get_or_none(id=data.user_id)
    if not user_obj:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")
    await user_obj.delete()
    await send_delete_email(user_obj.email)
    return True


@users_router.delete("/logout")
async def logout_user(response: Response, data: SessionTokenData = Depends(get_session_token)) -> bool:
    response.delete_cookie(key=SESSION_TOKEN_COOKIE_KEY)
    response.delete_cookie(key=REFRESH_TOKEN_COOKIE_KEY)
    return True


class RefreshTokenResponse(BaseModel):
    token: str
    token_type: str


@users_router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh(response: Response, data: RefreshTokenData = Depends(get_refresh_token)) -> RefreshTokenResponse:
    token = await Token.get_or_none(id=data.token_id)
    if not token or token.disabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")
    session_token = SessionTokenData(user_id=data.user_id).encode()
    set_token_cookie(response, session_token, SESSION_TOKEN_COOKIE_KEY)
    return RefreshTokenResponse(token=session_token, token_type=TOKEN_TYPE)
