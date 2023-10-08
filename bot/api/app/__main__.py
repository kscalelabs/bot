"""Defines the FastAPI application entrypoint."""

from fastapi import FastAPI

from bot.api.app.users import users_router
from bot.api.db import init_db

app = FastAPI()


@app.on_event("startup")
async def startup_event() -> None:
    await init_db()


app.include_router(users_router, prefix="/users", tags=["users"])
