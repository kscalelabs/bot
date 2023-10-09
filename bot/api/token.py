"""Defines functions for controlling access tokens."""

import datetime
import logging

import jwt
from fastapi import HTTPException, status

from bot.api.model import Token, User
from bot.settings import load_settings

logger = logging.getLogger(__name__)

TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def _server_time() -> datetime.datetime:
    return datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)


async def create_token(data: dict, user: User | None = None, expire_minutes: int | None = None) -> str:
    """Creates a token from a dictionary.

    The "exp" and "id" keys are reserved for internal use.

    Args:
        data: The data to encode.
        user: The user to associate with the token.
        expire_minutes: The number of minutes until the token expires. If not
            provided, will default to the internal settings.

    Returns:
        The encoded JWT.
    """
    if "exp" in data:
        raise ValueError("The payload should not contain an expiration time")
    if "id" in data:
        raise ValueError("The payload should not contain a token ID")
    if "uid" in data:
        raise ValueError("The payload should not contain a user ID")
    settings = load_settings().crypto
    to_encode = data.copy()

    # JWT exp claim expects a timestamp in seconds. This will automatically be
    # used to determine if the token is expired.
    expires: datetime.datetime | None = None
    if expire_minutes is not None:
        expires = _server_time() + datetime.timedelta(minutes=expire_minutes)
        to_encode.update({"exp": expires})

    # Creates a token in the database.
    token = await Token.create(user=user, expires=expires)
    uuid_str = str(token.uuid)
    to_encode.update({"id": uuid_str})

    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.algorithm)
    return encoded_jwt


async def load_token(payload: str, only_once: bool = False) -> tuple[Token, dict]:
    """Loads the token payload.

    Args:
        payload: The JWT-encoded payload.
        only_once: If ``True``, the token will be marked as used.

    Returns:
        The decoded payload.
    """
    settings = load_settings().crypto

    # Decodes the JWT.
    try:
        data: dict = jwt.decode(payload, settings.jwt_secret, algorithms=[settings.algorithm])
        token_uuid = data["id"]
    except Exception:
        logger.exception("Invalid token")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    # Checks the token against the database, and deletes it if necessary.
    token = await Token.get_or_none(uuid=token_uuid)
    if token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is disabled")
    if token.disabled:
        await token.delete()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is disabled")
    if token.expires is not None and token.expires < _server_time():
        await token.delete()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    if only_once:
        await token.delete()

    return token, data
