# mypy: disable-error-code="var-annotated"
"""Defines the table models for the API."""

import enum

from tortoise import fields
from tortoise.models import Model


class User(Model):
    id = fields.IntField(pk=True)
    email = fields.CharField(max_length=255, unique=True, index=True)
    banned = fields.BooleanField(default=False, index=True)


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
    name = fields.CharField(max_length=255, default="Untitled", index=True)
    user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "models.User",
        related_name="audios",
        on_delete=fields.CASCADE,
        index=True,
        null=False,
    )
    source = fields.CharEnumField(enum_type=AudioSource, index=True)
    created = fields.DatetimeField(auto_now_add=True)
    available = fields.BooleanField(default=False)
    num_frames = fields.IntField(null=True)
    num_channels = fields.IntField(null=True)
    sample_rate = fields.IntField(null=True)
    duration = fields.FloatField(null=True)


class Generation(Model):
    id = fields.IntField(pk=True)
    user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "models.User",
        related_name="generations",
        on_delete=fields.CASCADE,
        index=True,
        null=False,
    )
    source: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "models.Audio",
        related_name="generations_as_source",
        on_delete=fields.CASCADE,
        index=True,
        null=False,
    )
    reference: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "models.Audio",
        related_name="generations_as_reference",
        on_delete=fields.CASCADE,
        index=True,
        null=False,
    )
    output: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "models.Audio",
        related_name="generations_as_output",
        on_delete=fields.CASCADE,
        index=True,
        null=False,
    )
    model = fields.CharField(max_length=255, index=True, null=True)
    created = fields.DatetimeField(auto_now_add=True)
