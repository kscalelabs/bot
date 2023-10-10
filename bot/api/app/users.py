"""Defines the API endpoint for creating, deleting and updating user information."""

from email.utils import parseaddr as parse_email_address

from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.security.utils import get_authorization_scheme_param
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token
from pydantic.main import BaseModel

from bot.api.email import OneTimePassPayload, send_delete_email, send_otp_email
from bot.api.model import Token, User
from bot.api.token import create_token, load_token
from bot.settings import load_settings

users_router = APIRouter()

security = HTTPBearer()

TOKEN_COOKIE_KEY = "__DPSH_TOKEN"


class UserTokenData(BaseModel):
    user_id: int

    async def encode(self) -> str:
        return await create_token({}, user=await User.get(id=self.user_id))

    @classmethod
    async def encode_from_user(cls, user: User) -> str:
        return await create_token({}, user=user)

    @classmethod
    async def decode(cls, payload: str) -> "UserTokenData":
        token, _ = await load_token(payload)
        return cls(user_id=token.user_id)


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


async def get_login_response(user_obj: User) -> UserLoginResponse:
    return UserLoginResponse(
        token=await UserTokenData.encode_from_user(user_obj),
        token_type="bearer",
    )


@users_router.post("/otp", response_model=UserLoginResponse)
async def otp(data: OneTimePass, response: Response) -> UserLoginResponse:
    payload = await OneTimePassPayload.decode(data.payload)
    user_obj = await create_or_get(payload.email)
    login_response = await get_login_response(user_obj)
    is_prod = load_settings().is_prod
    response.set_cookie(
        key=TOKEN_COOKIE_KEY,
        value=login_response.token,
        httponly=True,
        secure=is_prod,
        # samesite="Strict",
        samesite="None",
    )
    return login_response


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


async def get_current_user_http_auth(authorization: HTTPAuthorizationCredentials = Depends(security)) -> UserTokenData:
    token = authorization.credentials
    return await UserTokenData.decode(token)


async def get_current_user(request: Request) -> UserTokenData:
    # Tries Cookie.
    cookie_token = request.cookies.get(TOKEN_COOKIE_KEY)
    if cookie_token:
        return await UserTokenData.decode(cookie_token)

    # Tries Authorization header.
    authorization = request.headers.get("Authorization")
    if authorization:
        scheme, credentials = get_authorization_scheme_param(authorization)
        if not (scheme and credentials):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
        return await UserTokenData.decode(credentials)

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")


class UserInfoResponse(BaseModel):
    email: str


@users_router.get("/me", response_model=UserInfoResponse)
async def get_user_info(data: UserTokenData = Depends(get_current_user)) -> UserInfoResponse:
    user_obj = await User.get_or_none(id=data.user_id)
    if not user_obj:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")
    return UserInfoResponse(email=user_obj.email)


@users_router.delete("/myself")
async def delete_user(data: UserTokenData = Depends(get_current_user)) -> bool:
    user_obj = await User.get_or_none(id=data.user_id)
    if not user_obj:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")
    await user_obj.delete()
    await send_delete_email(user_obj.email)
    return True


@users_router.delete("/logout")
async def logout_user(response: Response) -> bool:
    response.delete_cookie(key=TOKEN_COOKIE_KEY)
    return True


@users_router.delete("/logout/all")
async def logout_all_users(data: UserTokenData = Depends(get_current_user)) -> bool:
    user_obj = await User.get_or_none(id=data.user_id)
    if not user_obj:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")
    await Token.filter(user=user_obj).delete()
    return True
