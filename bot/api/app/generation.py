"""Defines the API for querying generations."""

import datetime
from typing import cast
from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic.main import BaseModel

from bot.api.app.users import SessionTokenData, get_session_token
from bot.api.model import Generation

MAX_GENERATIONS_PER_QUERY = 100

generation_router = APIRouter()


class InfoMeResponse(BaseModel):
    count: int


@generation_router.get("/info/me", response_model=InfoMeResponse)
async def info_me(
    user_data: SessionTokenData = Depends(get_session_token),
) -> InfoMeResponse:
    query = Generation.filter(user_id=user_data.user_id)
    count = await query.count()
    return InfoMeResponse(count=count)


class SingleGenerationResponse(BaseModel):
    output_id: UUID
    reference_id: UUID
    source_id: UUID
    created: datetime.datetime


class QueryMeResponse(BaseModel):
    generations: list[SingleGenerationResponse]


@generation_router.get("/query/me", response_model=QueryMeResponse)
async def query_me(
    start: int,
    limit: int,
    user_data: SessionTokenData = Depends(get_session_token),
) -> QueryMeResponse:
    assert start >= 0, "Start must be non-negative"
    assert limit <= MAX_GENERATIONS_PER_QUERY, "Can only return 100 samples at a time"
    query = Generation.filter(user_id=user_data.user_id)
    generations = cast(
        list[SingleGenerationResponse],
        await query.order_by("-created")
        .offset(start)
        .limit(limit)
        .values(
            "output_id",
            "reference_id",
            "source_id",
            "created",
        ),
    )
    return QueryMeResponse(generations=generations)
