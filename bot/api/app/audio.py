"""Defines the API endpoint for querying images."""

from typing import cast
from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic.main import BaseModel

from bot.api.app.users import SessionTokenData, get_session_token
from bot.api.model import Audio, AudioSource

audio_router = APIRouter()


class InfoMeResponse(BaseModel):
    count: int


@audio_router.get("/info/me", response_model=InfoMeResponse)
async def info_me(
    source: AudioSource | None = None,
    user_data: SessionTokenData = Depends(get_session_token),
) -> InfoMeResponse:
    query = Audio.filter(user_id=user_data.user_id)
    if source is not None:
        query = query.filter(source=source)
    count = await query.count()
    return InfoMeResponse(count=count)


class QueryMeResponse(BaseModel):
    uuids: list[UUID]


@audio_router.get("/query/me", response_model=QueryMeResponse)
async def query_me(
    start: int,
    limit: int,
    source: AudioSource | None = None,
    user_data: SessionTokenData = Depends(get_session_token),
) -> QueryMeResponse:
    assert start >= 0, "Start must be non-negative"
    assert limit <= 100, "Can only return 100 samples at a time"
    query = Audio.filter(user_id=user_data.user_id)
    if source is not None:
        query = query.filter(source=source)
    uuids = cast(list[UUID], await query.order_by("-created").offset(start).limit(limit).values_list("uuid", flat=True))
    return QueryMeResponse(uuids=uuids)
