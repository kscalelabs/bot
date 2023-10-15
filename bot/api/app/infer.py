"""Defines the API endpoint for running the ML model."""

import asyncio
import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic.main import BaseModel

from bot.api.app.users import SessionTokenData, get_session_token
from bot.api.model import Audio, AudioSource, Generation
from bot.worker.message_passing import Message, get_message_queue

logger = logging.getLogger(__name__)

infer_router = APIRouter()

message_queue = get_message_queue()


@infer_router.on_event("startup")
async def startup_event() -> None:
    message_queue.initialize()


async def generate(source_uuid: UUID, reference_uuid: UUID, user_id: int) -> Generation:
    """Generates a new audio file from a source and a reference.

    Args:
        source_uuid: The UUID of the source audio.
        reference_uuid: The UUID of the reference audio.
        user_id: The ID of the user who requested the generation.

    Returns:
        The row in generation table containing the generation ID.
    """
    source, reference = await asyncio.gather(
        Audio.get_or_none(uuid=source_uuid),
        Audio.get_or_none(uuid=reference_uuid),
    )
    if source is None or reference is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Audio not found.")
    if not source.available or not reference.available:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Audio not available.")

    # Creates a new output audio.
    output = await Audio.create(
        user_id=user_id,
        source=AudioSource.generated,
        public=False,
        available=False,
    )
    generation = await Generation.create(
        user_id=user_id,
        source_id=source_uuid,
        output_id=output.uuid,
        reference_id=reference_uuid,
    )

    # Sends a new message to the message queue with the new generation.
    message = Message(generation_uuid=generation.uuid)
    await message_queue.send(message)

    return generation


class RunRequest(BaseModel):
    orig_uuid: UUID
    ref_uuid: UUID


class RunResponse(BaseModel):
    uuid: UUID


@infer_router.post("/run", response_model=RunResponse)
async def run(data: RunRequest, user_data: SessionTokenData = Depends(get_session_token)) -> RunResponse:
    generation = await generate(data.orig_uuid, data.ref_uuid, user_data.user_id)
    return RunResponse(uuid=generation.output_id)
