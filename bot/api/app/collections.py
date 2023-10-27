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


class QueryIdsRequest(BaseModel):
    name: str
    audio_ids: list[int]


class QueryIdsSingleResponse(BaseModel):
    audio_id: int
    in_collection: bool


class QueryIdsResponse(BaseModel):
    ids: list[QueryIdsSingleResponse]


@collections_router.post("/query/ids", response_model=QueryIdsResponse)
async def query_ids(
    data: QueryIdsRequest,
    user_data: SessionTokenData = Depends(get_session_token),
) -> QueryIdsResponse:
    audio_ids = cast(
        list[int],
        await Collection.filter(
            name=data.name,
            user_id=user_data.user_id,
            audio_id__in=data.audio_ids,
        ).values_list("audio_id", flat=True),
    )
    audio_id_set = set(audio_ids)
    return QueryIdsResponse(
        ids=[
            QueryIdsSingleResponse(audio_id=audio_id, in_collection=audio_id in audio_id_set)
            for audio_id in data.audio_ids
        ]
    )
