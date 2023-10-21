"""Defines a CLI for calling the model runner."""

import argparse
import asyncio
import logging

from aiohttp.client import ClientSession
from ml.utils.logging import configure_logging
from yarl import URL

logger = logging.getLogger(__name__)


async def call_server_once(endpoint: URL) -> None:
    add_endpoint = endpoint.with_path("/")
    async with ClientSession() as session:
        async with session.get(add_endpoint) as response:
            if response.status != 200:
                logger.error("Request failed with status %s", response.status)
                return
            text = await response.text()
            logger.info("Response: %s", text)


async def log_queue_size(endpoint: URL) -> None:
    queue_size_endpoint = endpoint.with_path("/queue")
    async with ClientSession() as session:
        while True:
            try:
                async with session.get(queue_size_endpoint) as response:
                    if response.status != 200:
                        logger.error("Request failed with status %s", response.status)
                        return
                    text = await response.text()
                    logger.info("Response: %s", text)
            finally:
                await asyncio.sleep(1)


async def call_server(num_times: int, endpoint: URL) -> None:
    task = asyncio.create_task(log_queue_size(endpoint))
    await asyncio.gather(*(call_server_once(endpoint) for _ in range(num_times)))
    task.cancel()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the HTTP server.")
    parser.add_argument("num_times", type=int, help="Number of times to call the server")
    parser.add_argument("-t", "--host", type=str, default="localhost", help="The host to run the server on")
    parser.add_argument("-p", "--port", type=int, default=8080, help="The port to run the server on")
    parser.add_argument("-s", "--scheme", type=str, default="http", help="The scheme to use")
    args = parser.parse_args()

    configure_logging()

    endpoint = URL.build(scheme=args.scheme, host=args.host, port=args.port)
    num_times = args.num_times
    asyncio.run(call_server(num_times, endpoint))


if __name__ == "__main__":
    # python -m bot.worker.cli
    main()
