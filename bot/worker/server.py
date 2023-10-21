"""A simple HTTP server for serving responses from the model."""

import argparse
import asyncio
import logging
from dataclasses import dataclass

from aiohttp import web
from aiohttp.web_request import Request
from aiohttp.web_response import Response, json_response
from ml.utils.logging import configure_logging
from torch import Tensor

from bot.api.db import close_db, init_db
from bot.api.model import Audio
from bot.worker.model import ModelRunner

logger = logging.getLogger(__name__)

SOURCE_ID_KEY = "source_id"
REFERENCE_ID_KEY = "reference_id"
OUTPUT_ID_KEY = "output_id"
GENERATION_ID_KEY = "generation_id"


@dataclass(frozen=True)
class RequestData:
    request: Request
    response_future: asyncio.Future[Response]

    async def wait(self) -> Response:
        return await self.response_future


@dataclass(frozen=True)
class LoadedRequestData:
    data: RequestData
    src: Audio
    ref: Audio
    src_array: Tensor
    ref_array: Tensor


@dataclass(frozen=True)
class ProcessedRequestData:
    data: RequestData
    src: Audio
    ref: Audio
    output_array: Tensor
    elapsed_time: float


class Server:
    def __init__(self, host: str, port: int, max_loaded_requests: int = 2) -> None:
        super().__init__()

        self.host = host
        self.port = port
        self.max_loaded_requests = max_loaded_requests

        self.request_queue: "asyncio.Queue[RequestData]" = asyncio.Queue()
        self.loaded_request_queue: "asyncio.Queue[LoadedRequestData]" = asyncio.Queue(maxsize=max_loaded_requests)
        self.processed_request_queue: "asyncio.Queue[ProcessedRequestData]" = asyncio.Queue()
        self.runner_lock: asyncio.Lock = asyncio.Lock()

        self.model_runner = ModelRunner()

    async def get_queue_size(self, request: Request) -> Response:
        return web.Response(text=str(self.request_queue.qsize()))

    async def handle_request(self, request: Request) -> Response:
        data = RequestData(request, asyncio.Future())
        await self.request_queue.put(data)
        return await data.wait()

    async def request_loader(self) -> None:
        logger.info("Starting request loader...")

        def get_param(request: Request, key: str) -> int | None:
            if key not in request.query:
                return None
            try:
                return int(request.query[key])
            except ValueError:
                return None

        while True:
            data = await self.request_queue.get()

            try:
                if (src_id := get_param(data.request, SOURCE_ID_KEY)) is None:
                    data.response_future.set_result(web.Response(text=f"Malformed {SOURCE_ID_KEY}", status=400))
                    continue
                if (ref_id := get_param(data.request, REFERENCE_ID_KEY)) is None:
                    data.response_future.set_result(web.Response(text=f"Malformed {REFERENCE_ID_KEY}", status=400))
                    continue

                # Queries the database to get both of the audio objects together.
                audios: list[Audio] = await Audio.filter(id__in=[src_id, ref_id]).all()
                assert len(audios) == 2
                src, ref = (audios[0], audios[1]) if audios[0].id == src_id else (audios[1], audios[0])

                # Loads the audio samples into memory.
                src_array, ref_array = await self.model_runner.load_samples(src=src, ref=ref)
                output_data = LoadedRequestData(
                    data=data,
                    src=src,
                    ref=ref,
                    src_array=src_array,
                    ref_array=ref_array,
                )
                await self.loaded_request_queue.put(output_data)

            except KeyboardInterrupt:
                raise

            except Exception:
                logger.exception("Error loading request")
                data.response_future.set_result(web.Response(text="Error loading request", status=500))

    async def request_processor(self) -> None:
        logger.info("Starting request processor...")

        while True:
            data = await self.loaded_request_queue.get()

            try:
                output_array, elapsed_time = await self.model_runner.run_model(
                    src_audio=data.src_array,
                    ref_audio=data.ref_array,
                )
                output_data = ProcessedRequestData(
                    data=data.data,
                    src=data.src,
                    ref=data.ref,
                    output_array=output_array,
                    elapsed_time=elapsed_time,
                )
                await self.processed_request_queue.put(output_data)

            except KeyboardInterrupt:
                raise

            except Exception:
                logger.exception("Error processing request")
                data.data.response_future.set_result(web.Response(text="Error processing request", status=500))

    async def request_saver(self) -> None:
        logger.info("Starting request saver...")

        while True:
            data = await self.processed_request_queue.get()

            try:
                output, generation = await self.model_runner.process_output(
                    src=data.src,
                    ref=data.ref,
                    output_audio=data.output_array,
                    elapsed_time=data.elapsed_time,
                )
                response = json_response({OUTPUT_ID_KEY: output.id, GENERATION_ID_KEY: generation.id})
                data.data.response_future.set_result(response)

            except KeyboardInterrupt:
                raise

            except Exception:
                logger.exception("Error saving request")
                data.data.response_future.set_result(web.Response(text="Error saving request", status=500))

    async def start(self) -> None:
        """Starts the server.

        The server will run until the process is killed. It has two endpoints:

        - ``GET /``: Takes a source ID and a reference ID and processes them.
            It returns a 200 response with the output audio ID.
        - ``GET /queue``: Returns the number of requests currently in the queue,
            which can be used for load balancing.
        """

        async def get_lock() -> None:
            if self.runner_lock.locked():
                raise RuntimeError("Server is already running")
            await self.runner_lock.acquire()

        async def open_db_conn() -> None:
            logger.info("Opening database connection...")
            await init_db()

        async def start_web_server() -> web.AppRunner:
            app = web.Application()
            app.router.add_get("/", self.handle_request)
            app.router.add_get("/queue", self.get_queue_size)
            runner = web.AppRunner(app)
            await runner.setup()
            logger.info("Started app runner")

            site = web.TCPSite(runner, self.host, self.port)
            await site.start()
            logger.info("Started TCP site on %s:%s", self.host, self.port)

            return runner

        logger.info("Starting server...")
        _, _, runner = await asyncio.gather(get_lock(), open_db_conn(), start_web_server())

        tasks: list[asyncio.Task] = []
        tasks.append(asyncio.create_task(self.request_loader()))
        tasks.append(asyncio.create_task(self.request_processor()))
        tasks.append(asyncio.create_task(self.request_saver()))
        await asyncio.gather(*tasks)

        logger.info("Shutting down server...")
        await asyncio.gather(runner.cleanup(), close_db())
        self.runner_lock.release()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the HTTP server.")
    parser.add_argument("-t", "--host", type=str, default="localhost", help="The host to run the server on")
    parser.add_argument("-p", "--port", type=int, default=8080, help="The port to run the server on")
    parser.add_argument("-d", "--debug", action="store_true", help="If set, turn on debug mode for asyncio.run")
    args = parser.parse_args()

    configure_logging()
    logging.getLogger("aiohttp").setLevel(logging.WARNING)

    server = Server(args.host, args.port)
    asyncio.run(server.start())


if __name__ == "__main__":
    main()
