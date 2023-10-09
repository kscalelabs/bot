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
    used: fields.BooleanField = fields.BooleanField(default=False)


# Pydantic models for FastAPI
User_Pydantic = pydantic_model_creator(User, name="User")
