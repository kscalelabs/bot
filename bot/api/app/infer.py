"""Defines the API endpoint for running the ML model."""

import logging
from typing import Any

import aiohttp
from aiohttp.client import ClientSession
from fastapi import APIRouter, Depends, HTTPException
from pydantic.main import BaseModel
from yarl import URL

from bot.api.app.users import SessionTokenData, get_session_token
from bot.settings import settings

logger = logging.getLogger(__name__)


infer_router = APIRouter()


def get_client_session() -> ClientSession:
    worker_settings = settings.worker
    url = URL.build(
        scheme=worker_settings.scheme,
        host=worker_settings.host,
        port=worker_settings.port,
    )
    return aiohttp.ClientSession(base_url=url)


async def make_request(endpoint: URL) -> Any:  # noqa: ANN401
    async with get_client_session() as session:
        async with session.get(endpoint) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=response.reason)
            return await response.json()


class RunRequest(BaseModel):
    source_id: int
    reference_id: int


class RunResponse(BaseModel):
    output_id: int
    generation_id: int


@infer_router.post("/run", response_model=RunResponse)
async def run(data: RunRequest, user_data: SessionTokenData = Depends(get_session_token)) -> RunResponse:
    endpoint = URL.build(path="/", query={"source_id": data.source_id, "reference_id": data.reference_id})
    response_data = await make_request(endpoint)
    return RunResponse(**response_data)
