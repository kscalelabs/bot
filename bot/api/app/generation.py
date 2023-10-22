"""Defines the API for querying generations."""

import datetime
from typing import cast

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic.main import BaseModel
from tortoise.contrib.postgres.functions import Random

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
    id: int
    output_id: int | None
    reference_id: int
    source_id: int
    task_finished: datetime.datetime

    @staticmethod
    def keys() -> tuple[str, ...]:
        return ("id", "output_id", "reference_id", "source_id", "task_finished")


class QueryMeResponse(BaseModel):
    generations: list[SingleGenerationResponse]


@generation_router.get("/query/me", response_model=QueryMeResponse)
async def query_me(
    start: int,
    limit: int,
    user_data: SessionTokenData = Depends(get_session_token),
) -> QueryMeResponse:
    start = max(start, 0)
    limit = min(limit, MAX_GENERATIONS_PER_QUERY)
    query = Generation.filter(user_id=user_data.user_id)
    generations = cast(
        list[SingleGenerationResponse],
        await query.order_by("-task_finished").offset(start).limit(limit).values(*SingleGenerationResponse.keys()),
    )
    return QueryMeResponse(generations=generations)


@generation_router.get("/id", response_model=SingleGenerationResponse)
async def query_from_id(id: int, user_data: SessionTokenData = Depends(get_session_token)) -> SingleGenerationResponse:
    generation = await Generation.filter(id=id, user_id=user_data.user_id).get_or_none()
    if generation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Generation not found")
    return SingleGenerationResponse(
        id=generation.id,
        output_id=generation.output_id,
        reference_id=generation.reference_id,
        source_id=generation.source_id,
        task_finished=generation.task_finished,
    )


class PublicIdsRequest(BaseModel):
    count: int


class PublicIdsResponse(BaseModel):
    infos: list[SingleGenerationResponse]


@generation_router.post("/public", response_model=PublicIdsResponse)
async def public_ids(data: PublicIdsRequest) -> PublicIdsResponse:
    count = min(data.count, MAX_GENERATIONS_PER_QUERY)
    query = Generation.filter(public=True)
    generations = cast(
        list[SingleGenerationResponse],
        await query.annotate(order=Random()).order_by("order").limit(count).values(*SingleGenerationResponse.keys()),
    )
    return PublicIdsResponse(infos=generations)
