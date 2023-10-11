"""Defines the API endpoint for running the ML model."""

from uuid import UUID

from fastapi import APIRouter, Depends, Form, HTTPException, Request, UploadFile, status
from pydantic.main import BaseModel

from bot.api.app.users import SessionTokenData, get_session_token
from bot.api.audio import queue_for_generation, save_uuid
from bot.api.model import Audio, AudioSource, Generation, cast_audio_source
from bot.settings import load_settings

make_router = APIRouter()


class UploadResponse(BaseModel):
    uuid: UUID


async def verify_file_size(request: Request) -> int:
    content_length = request.headers.get("Content-Length")
    if not content_length:
        raise HTTPException(
            status_code=status.HTTP_411_LENGTH_REQUIRED,
            detail="Content-Length header required",
        )
    bytes_int = int(content_length)
    max_size = load_settings().file.audio_max_mb * 1024 * 1024
    if bytes_int > max_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File must be less than {max_size} bytes",
        )
    return bytes_int


@make_router.post("/upload", response_model=UploadResponse)
async def upload(
    file: UploadFile,
    source: str = Form(...),
    user_data: SessionTokenData = Depends(get_session_token),
    file_size_verified: int = Depends(verify_file_size),
) -> UploadResponse:
    source_enum = cast_audio_source(source)
    assert source_enum in (AudioSource.uploaded, AudioSource.recorded), "Invalid audio source"
    audio_entry = await Audio.create(user_id=user_data.user_id, source=source_enum)

    try:
        uuid = audio_entry.uuid
        await save_uuid(uuid, file.file, file.filename)
    except Exception:
        await audio_entry.delete()
        raise
    return UploadResponse(uuid=uuid)


class RunRequest(BaseModel):
    orig_uuid: UUID
    ref_uuid: UUID


class RunResponse(BaseModel):
    gen_uuid: UUID


@make_router.post("/run", response_model=RunResponse)
async def run(data: RunRequest, user_data: SessionTokenData = Depends(get_session_token)) -> RunResponse:
    gen_audio = await Audio.create(user_id=user_data.user_id, source=cast_audio_source("generated"))
    generation = await Generation.create(
        user_id=user_data.user_id,
        source_id=data.orig_uuid,
        reference_id=data.ref_uuid,
        output_id=gen_audio.uuid,
    )
    await queue_for_generation(generation)
    return RunResponse(gen_uuid=gen_audio.uuid)
