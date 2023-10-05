"""Defines request and response models for the API."""

from pydantic import BaseModel
from fastapi import UploadFile
from fastapi.responses import FileResponse


class UploadRequest(BaseModel):
    file: UploadFile


class UploadResponse(BaseModel):
    key: str


class InfoResponse(BaseModel):
    app_name: str
    version: str
