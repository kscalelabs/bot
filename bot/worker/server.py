"""A simple HTTP server for serving responses from the model."""

import asyncio
import logging
from dataclasses import dataclass
from types import TracebackType

from aiohttp import web
from aiohttp.web_request import Request
from aiohttp.web_response import Response, json_response
from ml.utils.logging import configure_logging
from torch import Tensor

from bot.api.db import close_db, init_db
from bot.api.model import Audio
from bot.settings import env_settings
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
    def __init__(self, max_loaded_requests: int = 2) -> None:
        super().__init__()

        self.max_loaded_requests = max_loaded_requests

        self.request_queue: "asyncio.Queue[RequestData]" = asyncio.Queue()
        self.loaded_request_queue: "asyncio.Queue[LoadedRequestData]" = asyncio.Queue(maxsize=max_loaded_requests)
        self.processed_request_queue: "asyncio.Queue[ProcessedRequestData]" = asyncio.Queue()

        self.model_runner = ModelRunner()

        self._tasks: list[asyncio.Task] = []
        self._app: web.Application | None = None

    @property
    def app(self) -> web.Application:
        assert self._app is not None, "Server not started"
        return self._app

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
            try:
                data = await self.request_queue.get()
            except asyncio.CancelledError:
                break

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
            try:
                data = await self.loaded_request_queue.get()
            except asyncio.CancelledError:
                break

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
            try:
                data = await self.processed_request_queue.get()
            except asyncio.CancelledError:
                break

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

    async def __aenter__(self) -> "Server":
        """Starts the server.

        The server will run until the process is killed. It has two endpoints:

        - ``GET /``: Takes a source ID and a reference ID and processes them.
            It returns a 200 response with the output audio ID.
        - ``GET /queue``: Returns the number of requests currently in the queue,
            which can be used for load balancing.
        """

        async def start_web_server() -> None:
            assert self._app is None, "Server already started"
            self._app = web.Application()
            self._app.router.add_get("/", self.handle_request)
            self._app.router.add_get("/queue", self.get_queue_size)

        async def start_tasks() -> None:
            assert len(self._tasks) == 0, "Tasks already started"
            self._tasks.append(asyncio.create_task(self.request_loader()))
            self._tasks.append(asyncio.create_task(self.request_processor()))
            self._tasks.append(asyncio.create_task(self.request_saver()))

        async def start_db() -> None:
            await init_db(generate_schemas=env_settings.database.generate_schemas)

        await asyncio.gather(start_web_server(), start_tasks(), start_db())

        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        async def stop_web_server() -> None:
            assert self._app is not None, "Server not started"
            await self._app.shutdown()
            await self._app.cleanup()

        async def stop_tasks() -> None:
            assert len(self._tasks) > 0, "Tasks not started"
            for task in self._tasks:
                task.cancel()
            await asyncio.gather(*self._tasks)

        await asyncio.gather(stop_web_server(), stop_tasks(), close_db())


class Runner:
    def __init__(self, server: Server) -> None:
        super().__init__()

        self.server = server

        self._runner: web.AppRunner | None = None
        self._site: web.TCPSite | None = None

    async def __aenter__(self) -> "Runner":
        await self.server.__aenter__()

        self._runner = web.AppRunner(self.server.app)
        await self._runner.setup()
        logger.info("Started app runner")

        host = env_settings.worker.host
        port = env_settings.worker.port
        self._site = web.TCPSite(self._runner, host, port)
        await self._site.start()
        logger.info("Started TCP site on %s:%s", host, port)

        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        assert self._site is not None, "Site not started"
        await self._site.stop()

        assert self._runner is not None, "Runner not started"
        await self._runner.shutdown()
        await self._runner.cleanup()

        await self.server.__aexit__(exc_type, exc_val, exc_tb)

    async def run_forever(self) -> None:
        async with self:
            await asyncio.Event().wait()


def main() -> None:
    configure_logging()
    logging.getLogger("aiohttp").setLevel(logging.WARNING)

    server = Server()
    runner = Runner(server)
    asyncio.run(runner.run_forever())


if __name__ == "__main__":
    # python -m bot.worker.server
    main()
