"""Defines the API for managing collections."""


from typing import cast

from fastapi import APIRouter, Depends
from pydantic.main import BaseModel

from bot.api.app.users import SessionTokenData, get_session_token
from bot.api.model import Collection

collections_router = APIRouter()


class SingleCollectionResponse(BaseModel):
    audio_ids: list[int]


@collections_router.get("/query/collection", response_model=SingleCollectionResponse)
async def query_collection(
    name: str,
    user_data: SessionTokenData = Depends(get_session_token),
) -> SingleCollectionResponse:
    audio_ids = cast(
        list[int],
        await Collection.filter(name=name, user_id=user_data.user_id).values_list("audio_id", flat=True),
    )
    return SingleCollectionResponse(audio_ids=audio_ids)


class MyCollectionsResponse(BaseModel):
    names: list[str]


@collections_router.get("/query/me")
async def query_my_collections(user_data: SessionTokenData = Depends(get_session_token)) -> MyCollectionsResponse:
    names = cast(
        list[str],
        await Collection.filter(user_id=user_data.user_id).distinct().order_by("name").values_list("name", flat=True),
    )
    return MyCollectionsResponse(names=names)


class AddToCollectionRequest(BaseModel):
    name: str
    audio_id: int


@collections_router.post("/add")
async def add_to_collection(
    data: AddToCollectionRequest,
    user_data: SessionTokenData = Depends(get_session_token),
) -> bool:
    await Collection.create(name=data.name, audio_id=data.audio_id, user_id=user_data.user_id)
    return True


class RemoveFromCollectionRequest(BaseModel):
    name: str
    audio_id: int


@collections_router.delete("/remove")
async def remove_from_collection(
    name: str,
    audio_id: int,
    user_data: SessionTokenData = Depends(get_session_token),
) -> bool:
    await Collection.filter(name=name, audio_id=audio_id, user_id=user_data.user_id).delete()
    return True
