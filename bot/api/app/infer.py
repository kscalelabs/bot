"""Defines the API endpoint for running the ML model."""

import logging

import aiohttp
from fastapi import APIRouter, Depends, HTTPException
from pydantic.main import BaseModel
from yarl import URL

from bot.api.app.users import SessionTokenData, get_session_token
from bot.settings import env_settings

logger = logging.getLogger(__name__)


infer_router = APIRouter()


class RunRequest(BaseModel):
    source_id: int
    reference_id: int


class RunResponse(BaseModel):
    output_id: int
    generation_id: int


@infer_router.post("/run", response_model=RunResponse)
async def run(data: RunRequest, user_data: SessionTokenData = Depends(get_session_token)) -> RunResponse:
    url = (
        URL(env_settings.worker.worker_url)
        .with_path("/")
        .with_query({"source_id": data.source_id, "reference_id": data.reference_id})
    )
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=response.reason)
            response_data = await response.json()
    return RunResponse(**response_data)
