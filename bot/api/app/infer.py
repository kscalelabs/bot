"""Defines the API endpoint for running the ML model."""

from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic.main import BaseModel

from bot.api.app.users import SessionTokenData, get_session_token
from bot.api.model import Audio, AudioSource, Generation

infer_router = APIRouter()


async def generate(
    source_uuid: UUID,
    reference_uuid: UUID,
    user_id: int,
) -> Generation:
    """Generates a new audio file from a source and a reference.

    Args:
        source_uuid: The UUID of the source audio.
        reference_uuid: The UUID of the reference audio.
        user_id: The ID of the user who requested the generation.

    Returns:
        The row in generation table containing the generation ID.
    """
    gen_audio = await Audio.create(
        user_id=user_id,
        source=AudioSource.generated,
        available=False,
    )
    generation = await Generation.create(
        user_id=user_id,
        source_id=source_uuid,
        reference_id=reference_uuid,
        output_id=gen_audio.uuid,
    )
    return generation


class RunRequest(BaseModel):
    orig_uuid: UUID
    ref_uuid: UUID


class RunResponse(BaseModel):
    gen_uuid: UUID


@infer_router.post("/run", response_model=RunResponse)
async def run(data: RunRequest, user_data: SessionTokenData = Depends(get_session_token)) -> RunResponse:
    generation = await generate(data.orig_uuid, data.ref_uuid, user_data.user_id)
    return RunResponse(gen_uuid=generation.output_id)
