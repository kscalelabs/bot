# mypy: disable-error-code="var-annotated"
"""Defines the table models for the API."""

import enum

from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.models import Model


class User(Model):
    id = fields.IntField(pk=True)
    email = fields.CharField(max_length=255, unique=True)
    banned = fields.BooleanField(default=False)


class Token(Model):
    id = fields.IntField(pk=True)
    user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "models.User",
        related_name="tokens",
        on_delete=fields.CASCADE,
        index=True,
        null=False,
    )
    issued = fields.DatetimeField(auto_now_add=True)
    disabled = fields.BooleanField(default=False)


class AudioSource(enum.Enum):
    uploaded = "uploaded"
    recorded = "recorded"
    generated = "generated"


def cast_audio_source(s: str) -> AudioSource:
    match s:
        case "uploaded":
            return AudioSource.uploaded
        case "recorded":
            return AudioSource.recorded
        case "generated":
            return AudioSource.generated
        case _:
            raise ValueError(f"Invalid audio source {s}")


class Audio(Model):
    uuid = fields.UUIDField(pk=True)
    user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "models.User",
        related_name="audios",
        on_delete=fields.CASCADE,
        index=True,
        null=False,
    )
    source = fields.CharEnumField(enum_type=AudioSource, index=True)
    created = fields.DatetimeField(auto_now_add=True)


# Pydantic models for FastAPI
User_Pydantic = pydantic_model_creator(User, name="User")
Audio_Pydantic = pydantic_model_creator(Audio, name="Audio")
