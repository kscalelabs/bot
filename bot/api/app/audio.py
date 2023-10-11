"""Defines the API endpoint for querying images."""

from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic.main import BaseModel

from bot.api.app.users import SessionTokenData, get_session_token
from bot.api.model import Audio, AudioSource

audio_router = APIRouter()


class AudioInfoResponse(BaseModel):
    count: int


@audio_router.post("/me", response_model=AudioInfoResponse)
async def get(
    user_data: SessionTokenData = Depends(get_session_token),
) -> AudioInfoResponse:
    count = await Audio.filter(user_id=user_data.user_id).count()
    return AudioInfoResponse(count=count)


class AudioQueryResponse(BaseModel):
    uuids: list[UUID]


@audio_router.get("/query", response_model=AudioQueryResponse)
async def query(
    start: int,
    limit: int,
    source: AudioSource | None = None,
    user_data: SessionTokenData = Depends(get_session_token),
) -> AudioQueryResponse:
    assert start >= 0, "Start must be non-negative"
    assert limit <= 100, "Can only return 100 samples at a time"
    query = Audio.filter(user_id=user_data.user_id)
    if source is not None:
        query = query.filter(source=source)
    uuids = await query.order_by("-created").offset(start).limit(limit).values_list("uuid", flat=True)
    return AudioQueryResponse(uuids=uuids)
