"""Defines the FastAPI application backend."""

import asyncio

from fastapi import FastAPI, UploadFile
from fastapi.responses import FileResponse

from bot import __version__ as bot_version
from bot.api.models import InfoResponse, UploadRequest, UploadResponse

from concurrent import futures

app = FastAPI()


async def process_audio(file: UploadFile) -> str:
    # Stub for audio processing
    await asyncio.sleep(10)  # Simulate long processing time
    return "processed_audio_file_path.wav"


@app.post("/upload/", response_model=UploadResponse)
async def upload_audio(request: UploadRequest) -> UploadResponse:
    audio_key = await process_audio(request.file)
    return {"key": audio_key}


@app.get("/download/", response_class=FileResponse)
async def download_audio(key: str) -> FileResponse:
    file_path = get_file_path(key)
    return FileResponse(file_path)


@app.get("/info", response_model=InfoResponse)
async def info() -> InfoResponse:
    return InfoResponse(
        app_name=settings.app_name,
        version=settings.version,
    )

futures.ProcessPoolExecutor(max_workers=10)
