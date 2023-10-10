# mypy: disable-error-code="var-annotated"
"""Defines the table models for the API."""

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


class Audio(Model):
    uuid = fields.UUIDField(pk=True)
    user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "models.User",
        related_name="audios",
        on_delete=fields.CASCADE,
        index=True,
        null=False,
    )
    generated = fields.BooleanField(index=True)


# Pydantic models for FastAPI
User_Pydantic = pydantic_model_creator(User, name="User")
Audio_Pydantic = pydantic_model_creator(Audio, name="Audio")
