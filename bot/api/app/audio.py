"""Defines the API endpoint for querying images."""

import datetime
import re
from typing import Any, cast

from fastapi import (
    APIRouter,
    Depends,
    Form,
    HTTPException,
    Request,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse, RedirectResponse
from pydantic.main import BaseModel
from tortoise.contrib.postgres.functions import Random
from tortoise.expressions import Q

from bot.api.app.users import SessionTokenData, get_session_token
from bot.api.audio import get_audio_url, save_audio_file
from bot.api.model import Audio, AudioSource, cast_audio_source
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
    ids: list[int]


@audio_router.get("/query/me", response_model=QueryMeResponse)
async def query_me(
    start: int,
    limit: int,
    q: str | None = None,
    source: AudioSource | None = None,
    user_data: SessionTokenData = Depends(get_session_token),
) -> QueryMeResponse:
    start = max(start, 0)
    limit = min(limit, MAX_UUIDS_PER_QUERY)
    query = Audio.filter(user_id=user_data.user_id)
    if q is not None:
        query = query.filter(name__icontains=q)
    if source is not None:
        query = query.filter(source=source)
    ids = cast(list[int], await query.order_by("-created").offset(start).limit(limit).values_list("id", flat=True))
    return QueryMeResponse(ids=ids)


class SingleIdResponse(BaseModel):
    id: int
    name: str
    source: AudioSource
    created: datetime.datetime
    num_frames: int
    num_channels: int
    sample_rate: int
    duration: float

    @staticmethod
    def keys() -> tuple[str, ...]:
        return ("id", "name", "source", "created", "num_frames", "num_channels", "sample_rate", "duration")


class QueryIdsRequest(BaseModel):
    ids: list[int]


class QueryIdsResponse(BaseModel):
    infos: list[SingleIdResponse]


@audio_router.post("/query/ids", response_model=QueryIdsResponse)
async def query_ids(
    data: QueryIdsRequest,
    user_data: SessionTokenData = Depends(get_session_token),
) -> QueryIdsResponse:
    values = SingleIdResponse.keys()
    query = Q(id__in=data.ids) & (Q(user_id=user_data.user_id) | Q(public=True))
    audios = await Audio.filter(query).values(*values)
    infos = [SingleIdResponse(**info) for info in audios]
    return QueryIdsResponse(infos=infos)


@audio_router.delete("/delete")
async def delete_audio(id: int, user_data: SessionTokenData = Depends(get_session_token)) -> bool:
    await Audio.filter(id=id, user_id=user_data.user_id).delete()
    return True


class UpdateRequest(BaseModel):
    id: int
    name: str | None = None


@audio_router.post("/update")
async def update_name(data: UpdateRequest, user_data: SessionTokenData = Depends(get_session_token)) -> bool:
    kwargs: dict[str, Any] = {}
    if data.name is not None:
        kwargs["name"] = data.name
    if not kwargs:
        return True
    await Audio.filter(id=data.id, user_id=user_data.user_id).update(**kwargs)
    return True


def get_media_filename(name: str) -> str:
    name = "".join(name.split(".")[:-1])  # Remove file extension.
    name = "".join(re.findall(r"[\w\d\_]+", name))  # Remove non-alphanumeric characters.
    name = f"{name}.{settings.file.audio.file_ext}"  # Add file extension.
    return name


@audio_router.get(f"/media/{{media_id}}.{settings.file.audio.file_ext}")
async def get_media(media_id: int, access_token: str | None = None) -> FileResponse:
    if access_token is None:
        audio = await Audio.get_or_none(Q(id=media_id) & Q(public=True))
    else:
        user_id = SessionTokenData.decode(access_token).user_id
        audio = await Audio.get_or_none(Q(id=media_id) & (Q(user_id=user_id) | Q(public=True)))
    if audio is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audio not found")
    name = get_media_filename(audio.name)
    audio_url, is_url = await get_audio_url(audio)
    headers = {"Content-Disposition": f"attachment; filename={name}"}
    if is_url:
        return RedirectResponse(audio_url, headers=headers)  # type: ignore[return-value]
    return FileResponse(audio_url, headers=headers)


class UploadResponse(BaseModel):
    id: int


async def verify_file_size(request: Request) -> int:
    content_length = request.headers.get("Content-Length")
    if not content_length:
        raise HTTPException(
            status_code=status.HTTP_411_LENGTH_REQUIRED,
            detail="Content-Length header required",
        )
    bytes_int = int(content_length)
    max_size = load_settings().file.audio.max_mb * 1024 * 1024
    if bytes_int > max_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File must be less than {load_settings().file.audio.max_mb} megabytes",
        )
    return bytes_int


@audio_router.post("/upload", response_model=UploadResponse)
async def upload(
    file: UploadFile,
    source: str = Form(...),
    user_data: SessionTokenData = Depends(get_session_token),
    file_size_verified: int = Depends(verify_file_size),
) -> UploadResponse:
    source_enum = cast_audio_source(source)
    if source_enum not in (AudioSource.uploaded, AudioSource.recorded):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Source must be one of {AudioSource.uploaded}, {AudioSource.recorded}",
        )
    audio_entry = await save_audio_file(user_data.user_id, source_enum, file.file, file.filename)
    return UploadResponse(id=audio_entry.id)


class PublicIdsRequest(BaseModel):
    count: int
    source: AudioSource | None = None


class PublicIdsResponse(BaseModel):
    infos: list[SingleIdResponse]


@audio_router.post("/public", response_model=PublicIdsResponse)
async def public_ids(data: PublicIdsRequest) -> PublicIdsResponse:
    count = min(data.count, MAX_UUIDS_PER_QUERY)
    values = SingleIdResponse.keys()
    query = Audio.filter(public=True)
    if data.source is not None:
        query = query.filter(source=data.source)
    # Note that RANDOM is shared between PostgreSQL and SQLite, but not MySQL.
    query = query.annotate(order=Random()).order_by("order")
    query = query.limit(count)
    infos = [SingleIdResponse(**info) for info in await query.values(*values)]
    return PublicIdsResponse(infos=infos)
