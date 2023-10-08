"""Defines functions for controlling access tokens."""

import datetime
import logging

import jwt
from fastapi import HTTPException, status

from bot.settings import load_settings

logger = logging.getLogger(__name__)

TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def create_access_token(data: dict) -> str:
    if "exp" in data:
        raise ValueError("The payload should not contain an expiration time")
    settings = load_settings().crypto
    to_encode = data.copy()

    # JWT exp claim expects a timestamp in seconds. This will automatically be
    # used to determine if the token is expired.
    expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=settings.expire_token_minutes)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.algorithm)
    return encoded_jwt


def load_access_token(payload: str) -> dict:
    settings = load_settings().crypto
    try:
        return jwt.decode(payload, settings.jwt_secret, algorithms=[settings.algorithm])
    except Exception:
        logger.exception("Invalid token")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
