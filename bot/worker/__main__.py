"""Entrypoint for the worker service."""

import asyncio
from bot.worker.model import worker_fn


if __name__ == "__main__":
    # python -m bot.worker
    asyncio.run(worker_fn())
