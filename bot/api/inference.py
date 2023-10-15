# mypy: disable-error-code="no-untyped-def"
"""Defines the inference backend glue code."""

import asyncio
import time
from typing import Callable, ParamSpec

from fastapi import Request, Response
from fastapi.routing import APIRoute

P = ParamSpec("P")


class InferenceRoute(APIRoute):
    """Defines an inference route that locks the inference backend per request.

    This is done to ensure that the GPU only processes one request at a time.
    This is not particularly efficient, so it should probably be reworked in
    the future.
    """

    def __init__(self, *args, **kwargs) -> None:  # noqa: ANN002, ANN003
        super().__init__(*args, **kwargs)

        self.lock = asyncio.Lock()

    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def inference_route_handler(request: Request) -> Response:
            await self.lock.acquire()
            start_time = time.time()
            response: Response = await original_route_handler(request)
            elapsed_time = time.time() - start_time
            response.headers["X-Response-Time"] = str(elapsed_time)
            self.lock.release()
            return response

        return inference_route_handler
