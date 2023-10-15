"""Defines functions for controlling access tokens."""

import datetime
import logging

import jwt
from fastapi import HTTPException, status

from bot.api.model import Token, User
from bot.utils import server_time
from bot.settings import load_settings

logger = logging.getLogger(__name__)

TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def create_token(data: dict, expire_minutes: int | None = None) -> str:
    """Creates a token from a dictionary.

    The "exp" key is reserved for internal use.

    Args:
        data: The data to encode.
        expire_minutes: The number of minutes until the token expires. If not
            provided, will default to the internal settings.

    Returns:
        The encoded JWT.
    """
    if "exp" in data:
        raise ValueError("The payload should not contain an expiration time")
    settings = load_settings().crypto
    to_encode = data.copy()

    # JWT exp claim expects a timestamp in seconds. This will automatically be
    # used to determine if the token is expired.
    expires: datetime.datetime | None = None
    if expire_minutes is not None:
        expires = server_time() + datetime.timedelta(minutes=expire_minutes)
        to_encode.update({"exp": expires})

    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.algorithm)
    return encoded_jwt


def load_token(payload: str) -> dict:
    """Loads the token payload.

    Args:
        payload: The JWT-encoded payload.
        only_once: If ``True``, the token will be marked as used.

    Returns:
        The decoded payload.
    """
    settings = load_settings().crypto
    try:
        data: dict = jwt.decode(payload, settings.jwt_secret, algorithms=[settings.algorithm])
    except Exception:
        logger.exception("Invalid token")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return data


async def create_refresh_token(user: User) -> str:
    """Creates a refresh token for a user.

    Refresh tokens never expire. They are used to generate short-lived session
    tokens which are used for authentication.

    Args:
        user: The user to create the token for.

    Returns:
        The encoded JWT.
    """
    token = await Token.create(user=user)
    return create_token({"uid": user.id, "tid": token.id})


def load_refresh_token(payload: str) -> tuple[int, int]:
    """Loads the refresh token payload.

    Args:
        payload: The JWT-encoded payload.

    Returns:
        The user ID and token ID.
    """
    data = load_token(payload)
    return data["uid"], data["tid"]
