"""Defines the API endpoint for running the ML model."""

import logging

from fastapi import APIRouter, Depends
from pydantic.main import BaseModel

from bot.api.app.users import SessionTokenData, get_session_token
from bot.api.model import Generation
from bot.worker.message_passing import get_message_queue

logger = logging.getLogger(__name__)

infer_router = APIRouter()

mq = get_message_queue()


@infer_router.on_event("startup")
async def startup_event() -> None:
    await mq.initialize()


@infer_router.on_event("shutdown")
async def shutdown_event() -> None:
    await mq.close()


async def generate(source_id: int, reference_id: int, user_id: int) -> Generation:
    """Generates a new audio file from a source and a reference.

    Args:
        source_id: The ID of the source audio.
        reference_id: The ID of the reference audio.
        user_id: The ID of the user who requested the generation.

    Returns:
        The row in generation table containing the generation ID.
    """
    generation = await Generation.create(
        user_id=user_id,
        source_id=source_id,
        reference_id=reference_id,
    )

    # Sends the generation ID to the queue, deleting it if the send fails.
    try:
        await mq.send(generation.id)
    except Exception:
        logger.exception("Error sending generation to queue")
        await generation.delete()
        raise

    return generation


class RunRequest(BaseModel):
    source_id: int
    reference_id: int


class RunResponse(BaseModel):
    id: int


@infer_router.post("/run", response_model=RunResponse)
async def run(data: RunRequest, user_data: SessionTokenData = Depends(get_session_token)) -> RunResponse:
    generation = await generate(data.source_id, data.reference_id, user_data.user_id)
    return RunResponse(id=generation.id)
