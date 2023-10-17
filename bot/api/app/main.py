"""Defines the FastAPI application entrypoint.

Usage:

.. code-block:: bash

    $ uvicorn bot.api.app.main:app --reload --host
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

# from bot.api.app.admin import admin_router
# from bot.api.app.audio import audio_router
# from bot.api.app.generation import generation_router
# from bot.api.app.infer import infer_router
# from bot.api.app.users import users_router
from bot.api.db import close_db, init_db
from bot.settings import load_settings

app = FastAPI()
handler = Mangum(app)

# Site settings.
settings = load_settings()

# Just link to the official terms of service.
app.terms_of_service = "https://dpsh.dev/tos"

# Adds CORS middleware.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.site.homepage],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event() -> None:
    await init_db()


@app.on_event("shutdown")
async def shutdown_event() -> None:
    await close_db()


@app.get("/")
async def read_index() -> bool:
    return True


# app.include_router(admin_router, prefix="/admin", tags=["admin"])
# app.include_router(audio_router, prefix="/audio", tags=["audio"])
# app.include_router(generation_router, prefix="/generation", tags=["generation"])
# app.include_router(infer_router, prefix="/infer", tags=["infer"])
# app.include_router(users_router, prefix="/users", tags=["users"])
