"""Defines the API endpoint for querying images."""

import datetime
from typing import Any, cast
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse, RedirectResponse
from pydantic.main import BaseModel
from tortoise.contrib.postgres.functions import Random

from bot.api.app.users import SessionTokenData, get_session_token
from bot.api.audio import get_audio_url
from bot.api.model import Audio, AudioSource
from bot.settings import load_settings

MAX_UUIDS_PER_QUERY = 100

settings = load_settings()

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
    assert limit <= MAX_UUIDS_PER_QUERY, f"Can only return {MAX_UUIDS_PER_QUERY} samples at a time"
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


class SingleIdResponse(BaseModel):
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
    def from_dict(cls, data: dict) -> "SingleIdResponse":
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
    infos: list[SingleIdResponse]


@audio_router.post("/query/ids", response_model=QueryIdsResponse)
async def query_ids(
    data: QueryIdsRequest,
    user_data: SessionTokenData = Depends(get_session_token),
) -> QueryIdsResponse:
    values = SingleIdResponse.keys()
    query = await Audio.filter(user_id=user_data.user_id, uuid__in=data.uuids).values(*values)
    infos = [SingleIdResponse.from_dict(info) for info in query]
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


@audio_router.get(f"/media/{{uuid}}.{settings.file.audio_file_ext}")
async def get_media(uuid: UUID) -> FileResponse:
    audio = await Audio.get_or_none(uuid=uuid)
    if audio is None or not audio.available:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Audio with UUID {uuid} not found")
    audio_url, is_url = await get_audio_url(audio)
    if is_url:
        return RedirectResponse(audio_url)  # type: ignore[return-value]
    return FileResponse(audio_url)


class PublicIdsRequest(BaseModel):
    count: int
    source: AudioSource | None = None


class PublicIdsResponse(BaseModel):
    infos: list[SingleIdResponse]


@audio_router.post("/public", response_model=PublicIdsResponse)
async def public_ids(data: PublicIdsRequest) -> PublicIdsResponse:
    assert data.count <= MAX_UUIDS_PER_QUERY, f"Can only return {MAX_UUIDS_PER_QUERY} samples at a time"

    values = SingleIdResponse.keys()
    query = Audio.filter(public=True)
    if data.source is not None:
        query = query.filter(source=data.source)

    # Note that RANDOM is shared between PostgreSQL and SQLite, but not MySQL.
    query = query.annotate(order=Random()).order_by("order")
    query = query.limit(data.count)
    infos = [SingleIdResponse.from_dict(info) for info in await query.values(*values)]
    return PublicIdsResponse(infos=infos)
