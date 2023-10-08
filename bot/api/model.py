# mypy: disable-error-code="var-annotated"
"""Defines the table models for the API."""

from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.models import Model


class User(Model):
    id = fields.IntField(pk=True)
    email = fields.CharField(max_length=255)
    password = fields.CharField(max_length=255)
    google_id = fields.CharField(max_length=255, null=True)
    email_verified = fields.BooleanField(default=False)


class Images(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="images")
    image_size = fields.CharField(max_length=255)
    upload_time = fields.DatetimeField(auto_now_add=True)
    shared_publicly = fields.BooleanField(default=False)


class Gallery(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="galleries")
    name = fields.CharField(max_length=255)


class GalleryItems(Model):
    id = fields.IntField(pk=True)
    gallery = fields.ForeignKeyField("models.Gallery", related_name="items")
    image = fields.ForeignKeyField("models.Images", related_name="gallery_items")


# Pydantic models for FastAPI
User_Pydantic = pydantic_model_creator(User, name="User")
Images_Pydantic = pydantic_model_creator(Images, name="Images")
Gallery_Pydantic = pydantic_model_creator(Gallery, name="Gallery")
GalleryItems_Pydantic = pydantic_model_creator(GalleryItems, name="GalleryItems")
