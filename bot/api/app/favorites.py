"""Defines the API endpoint for managing favorites."""

from typing import cast
from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic.main import BaseModel

from bot.api.app.users import SessionTokenData, get_session_token
from bot.api.model import AudioSource, Favorites

MAX_UUIDS_PER_QUERY = 100

favorites_router = APIRouter()


class AddFavoriteRequest(BaseModel):
    uuid: UUID


@favorites_router.post("/add")
async def add_favorite(data: AddFavoriteRequest, user_data: SessionTokenData = Depends(get_session_token)) -> bool:
    await Favorites.create(user_id=user_data.user_id, audio_id=data.uuid)
    return True


@favorites_router.delete("/remove")
async def remove_favorite(uuid: UUID, user_data: SessionTokenData = Depends(get_session_token)) -> bool:
    await Favorites.filter(user_id=user_data.user_id, audio_id=uuid).delete()
    return True


class QueryMyFavoritesResponse(BaseModel):
    uuids: list[UUID]


@favorites_router.get("/query/me", response_model=QueryMyFavoritesResponse)
async def query_my_favorites(
    start: int,
    limit: int,
    source: AudioSource | None = None,
    user_data: SessionTokenData = Depends(get_session_token),
) -> QueryMyFavoritesResponse:
    assert start >= 0, "Start must be non-negative"
    assert limit <= MAX_UUIDS_PER_QUERY, "Can only return 100 samples at a time"
    query = Favorites.filter(user_id=user_data.user_id)
    if source is not None:
        query = query.filter(source=source)
    uuids = cast(
        list[UUID], await query.order_by("-created").offset(start).limit(limit).values_list("audio_id", flat=True)
    )
    return QueryMyFavoritesResponse(uuids=uuids)
