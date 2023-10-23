"""Defines the FastAPI application entrypoint.

Usage:

.. code-block:: bash

    $ uvicorn bot.api.app.main:app --reload --host
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from tortoise import Tortoise
from tortoise.contrib.fastapi import register_tortoise

from bot.api.app.admin import admin_router
from bot.api.app.audio import audio_router
from bot.api.app.generation import generation_router
from bot.api.app.infer import infer_router
from bot.api.app.users import users_router
from bot.api.db import get_config
from bot.settings import settings

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    await Tortoise.init(config=get_config())
    if settings.database.generate_schemas:
        logger.info("Generating schemas...")
        await Tortoise.generate_schemas()
    try:
        yield
    finally:
        await Tortoise.close_connections()


app = FastAPI(lifespan=lifespan)

# Just link to the official terms of service.
app.terms_of_service = "https://dpsh.dev/tos"

# Adds CORS middleware.
app.add_middleware(
    CORSMiddleware,
    # allow_origins=[settings.site.homepage],
    allow_origins=["*"],
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)


@app.get("/")
async def read_index() -> bool:
    return True


@app.exception_handler(ValueError)
async def value_error_exception_handler(request: Request, exc: ValueError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"message": "The request was invalid.", "detail": str(exc)},
    )


app.include_router(admin_router, prefix="/admin", tags=["admin"])
app.include_router(audio_router, prefix="/audio", tags=["audio"])
app.include_router(generation_router, prefix="/generation", tags=["generation"])
app.include_router(infer_router, prefix="/infer", tags=["infer"])
app.include_router(users_router, prefix="/users", tags=["users"])

# Registers the database, generating schemas if not in production.
register_tortoise(app, config=get_config(), generate_schemas=not settings.database.generate_schemas)
