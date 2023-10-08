"""Defines the FastAPI application entrypoint.

Usage:

.. code-block:: bash

    $ uvicorn bot.api.app.main:app --reload --host
"""

from fastapi import FastAPI

from bot.api.app.users import users_router
from bot.api.db import close_db, init_db

app = FastAPI()

# Just link to the official terms of service.
app.terms_of_service = "https://dpsh.dev/tos"


@app.on_event("startup")
async def startup_event() -> None:
    await init_db()


@app.on_event("shutdown")
async def shutdown_event() -> None:
    await close_db()


@app.get("/")
async def read_index() -> bool:
    return True


app.include_router(users_router, prefix="/users", tags=["users"])
