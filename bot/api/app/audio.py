"""Defines the API endpoint for querying images."""

import datetime
from typing import Any, cast
from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic.main import BaseModel

from bot.api.app.users import SessionTokenData, get_session_token
from bot.api.model import Audio, AudioSource

MAX_UUIDS_PER_QUERY = 100

audio_router = APIRouter()


class InfoMeResponse(BaseModel):
    count: int


@audio_router.get("/info/me", response_model=InfoMeResponse)
async def info_me(
    q: str | None = None,
    source: AudioSource | None = None,
    user_data: SessionTokenData = Depends(get_session_token),
) -> InfoMeResponse:
    query = Audio.filter(user_id=user_data.user_id)
    if q is not None:
        query = query.filter(name__icontains=q)
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
    q: str | None = None,
    source: AudioSource | None = None,
    user_data: SessionTokenData = Depends(get_session_token),
) -> QueryMeResponse:
    assert start >= 0, "Start must be non-negative"
    assert limit <= MAX_UUIDS_PER_QUERY, "Can only return 100 samples at a time"
    query = Audio.filter(user_id=user_data.user_id)
    if q is not None:
        query = query.filter(name__icontains=q)
    if source is not None:
        query = query.filter(source=source)
    uuids = cast(list[UUID], await query.order_by("-created").offset(start).limit(limit).values_list("uuid", flat=True))
    return QueryMeResponse(uuids=uuids)


class AudioDataResponse(BaseModel):
    num_frames: int
    num_channels: int
    sample_rate: int
    duration: float


class QueryIdResponse(BaseModel):
    uuid: UUID
    name: str
    source: AudioSource
    created: datetime.datetime
    available: bool
    data: AudioDataResponse | None

    @staticmethod
    def keys() -> tuple[str, ...]:
        return (
            "uuid",
            "name",
            "source",
            "created",
            "available",
            "num_frames",
            "num_channels",
            "sample_rate",
            "duration",
        )

    @classmethod
    def from_dict(cls, data: dict) -> "QueryIdResponse":
        return cls(
            uuid=data["uuid"],
            name=data["name"],
            source=AudioSource(data["source"]),
            created=data["created"],
            available=data["available"],
            data=AudioDataResponse(**data) if data["available"] else None,
        )


class QueryIdsRequest(BaseModel):
    uuids: list[UUID]


class QueryIdsResponse(BaseModel):
    infos: list[QueryIdResponse]


@audio_router.post("/query/ids", response_model=QueryIdsResponse)
async def query_ids(
    data: QueryIdsRequest,
    user_data: SessionTokenData = Depends(get_session_token),
) -> QueryIdsResponse:
    values = QueryIdResponse.keys()
    query = await Audio.filter(user_id=user_data.user_id, uuid__in=data.uuids).values(*values)
    infos = [QueryIdResponse.from_dict(info) for info in query]
    return QueryIdsResponse(infos=infos)


@audio_router.delete("/delete")
async def delete_audio(uuid: UUID, user_data: SessionTokenData = Depends(get_session_token)) -> bool:
    await Audio.filter(user_id=user_data.user_id, uuid=uuid).delete()
    return True


class UpdateRequest(BaseModel):
    uuid: UUID
    name: str | None = None


@audio_router.post("/update")
async def update_name(data: UpdateRequest, user_data: SessionTokenData = Depends(get_session_token)) -> bool:
    kwargs: dict[str, Any] = {}
    if data.name is not None:
        kwargs["name"] = data.name
    if not kwargs:
        return True
    await Audio.filter(user_id=user_data.user_id, uuid=data.uuid).update(**kwargs)
    return True
