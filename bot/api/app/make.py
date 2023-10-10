"""Defines the API endpoint for running the ML model."""

from uuid import UUID

import soundfile as sf
from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, status
from pydantic.main import BaseModel

from bot.api.app.users import UserTokenData, get_current_user
from bot.api.audio import queue_for_generation, save_uuid
from bot.api.model import Audio
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
    user_data: UserTokenData = Depends(get_current_user),
    file_size_verified: int = Depends(verify_file_size),
) -> UploadResponse:
    audio_file = sf.SoundFile(file.file)
    audio_entry = await Audio.create(user_id=user_data.user_id, generated=False)
    uuid = audio_entry.uuid
    await save_uuid(uuid, audio_file)
    return UploadResponse(uuid=uuid)


class RunRequest(BaseModel):
    orig_uuid: UUID
    ref_uuid: UUID


class RunResponse(BaseModel):
    gen_uuid: UUID


@make_router.post("/run", response_model=RunResponse)
async def run(data: RunRequest, user_data: UserTokenData = Depends(get_current_user)) -> RunResponse:
    audio = await Audio.create(user_id=user_data.user_id, generated=True)
    gen_uuid = audio.uuid
    await queue_for_generation(data.orig_uuid, data.ref_uuid, gen_uuid)
    return RunResponse(gen_uuid=gen_uuid)
