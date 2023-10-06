"""Defines request and response models for the API."""

from fastapi import UploadFile
from pydantic import BaseModel


class UploadRequest(BaseModel):
    file: UploadFile


class UploadResponse(BaseModel):
    key: str


class InfoResponse(BaseModel):
    app_name: str
    version: str
