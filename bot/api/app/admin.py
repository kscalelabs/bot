"""Defines the API endpoint for taking admin actions."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic.main import BaseModel

from bot.api.app.users import SessionTokenData, get_session_token
from bot.api.model import Audio, Generation, User
from bot.settings import load_settings

admin_router = APIRouter()


async def is_admin(user_obj: User) -> bool:
    email = user_obj.email
    settings = load_settings().user
    return email in settings.admin_emails


async def assert_is_admin(token_data: SessionTokenData = Depends(get_session_token)) -> SessionTokenData:
    admin_user_obj = await User.get(id=token_data.user_id)

    # Validates that the logged in user can take admin actions.
    if not admin_user_obj:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Admin user not found")
    if not await is_admin(admin_user_obj):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized")

    return token_data


@admin_router.get("/check")
async def admin_check(token_data: SessionTokenData = Depends(get_session_token)) -> bool:
    user_obj = await User.get(id=token_data.user_id)
    return await is_admin(user_obj)


class AdminUserRequest(BaseModel):
    email: str
    banned: bool | None = None
    deleted: bool | None = None


class AdminUserResponse(BaseModel):
    banned: bool
    deleted: bool


@admin_router.post("/act/user")
async def admin_act_user(
    data: AdminUserRequest,
    token_data: SessionTokenData = Depends(assert_is_admin),
) -> AdminUserResponse:
    user_obj = await User.get_or_none(email=data.email)
    if user_obj is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")
    changed = False
    if data.banned is not None and user_obj.banned != data.banned:
        user_obj.banned = data.banned
        changed = True
    if data.deleted is not None and user_obj.deleted != data.deleted:
        user_obj.deleted = data.deleted
        changed = True
    if changed:
        await user_obj.save()
    return AdminUserResponse(banned=user_obj.banned, deleted=user_obj.deleted)


class AdminContentRequest(BaseModel):
    uuid: UUID
    public: bool | None = None


class AdminContentResponse(BaseModel):
    public: bool


@admin_router.post("/act/content")
async def admin_act_content(
    data: AdminContentRequest,
    token_data: SessionTokenData = Depends(assert_is_admin),
) -> AdminContentResponse:
    audio_obj = await Audio.get_or_none(uuid=data.uuid)
    if audio_obj is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Audio not found")
    changed = False
    if data.public is not None and audio_obj.public != data.public:
        audio_obj.public = data.public
        changed = True
    if changed:
        await audio_obj.save()
    return AdminContentResponse(public=audio_obj.public)


class AdminGenerationRequest(BaseModel):
    output_id: UUID
    public: bool | None = None


class AdminGenerationResponse(BaseModel):
    public: bool


@admin_router.post("/act/generation")
async def admin_act_generation(
    data: AdminGenerationRequest,
    token_data: SessionTokenData = Depends(assert_is_admin),
) -> AdminGenerationResponse:
    generation_obj = await Generation.filter(output_id=data.output_id).get_or_none()
    if generation_obj is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Generation not found")
    changed = False
    if data.public is not None and generation_obj.public != data.public:
        generation_obj.public = data.public
        if data.public:
            # When making a generation public, we also make the source,
            # reference and output audio files public.
            audio_ids = [generation_obj.source_id, generation_obj.reference_id, generation_obj.output_id]
            await Audio.filter(uuid__in=audio_ids).update(public=True)
        changed = True
    if changed:
        await generation_obj.save()
    return AdminGenerationResponse(public=generation_obj.public)