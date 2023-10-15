"""Functions for configuring the worker."""

import asyncio
import functools
import logging
from abc import ABC, abstractmethod
from typing import Awaitable, Callable, ParamSpec
from uuid import UUID

import aioboto3
from aio_pika import IncomingMessage, Message, connect_robust
from aio_pika.robust_connection import AbstractRobustConnection

from bot.settings import load_settings

logger = logging.getLogger(__name__)

P = ParamSpec("P")


def handle_errors(f: Callable[P, Awaitable[None]]) -> Callable[P, Awaitable[None]]:
    @functools.wraps(f)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> None:
        try:
            await f(*args, **kwargs)

        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received. Exiting...")
            raise

        except Exception:
            logger.exception("An exception occurred.")

    return wrapper


class BaseQueue(ABC):
    @abstractmethod
    def initialize(self) -> None:
        """Initializes the queue."""

    @abstractmethod
    async def send(self, generation_uuid: UUID) -> None:
        """Sends a message to the queue.

        Args:
            generation_uuid: The UUID of the generation to run.
        """

    @abstractmethod
    async def receive(self, callback: Callable[[UUID], Awaitable[None]]) -> None:
        """Receives messages from the queue.

        Args:
            callback: The callback function to call when a message is received.
        """


class RabbitMessageQueue(BaseQueue):
    queue_name: str
    connection: AbstractRobustConnection

    async def initialize(self) -> None:
        settings = load_settings().worker.rabbit
        self.queue_name = settings.queue_name
        self.connection = await connect_robust(
            host=settings.host,
            port=settings.port,
            virtualhost=settings.virtual_host,
            login=settings.username,
            password=settings.password,
        )
        self.channel = await self.connection.channel()
        await self.channel.declare_queue(name=self.queue_name)

    async def send(self, generation_uuid: UUID) -> None:
        await self.channel.default_exchange.publish(
            Message(body=generation_uuid.hex.encode("utf-8")),
            routing_key=self.queue_name,
        )

    async def receive(self, callback: Callable[[UUID], Awaitable[None]]) -> None:
        logger.info("Starting RabbitMQ worker...")
        callback = handle_errors(callback)

        async def callback_wrapper(message: IncomingMessage) -> None:
            async with message.process():
                generation_uuid = UUID(message.body.decode("utf-8"))
                await callback(generation_uuid)

        await self.channel.set_qos(prefetch_count=1)
        queue = await self.channel.get_queue(self.queue_name)

        try:
            await queue.consume(callback_wrapper)
            while True:
                logger.info("Waiting for messages...")
                await asyncio.sleep(60)
        finally:
            await self.connection.close()


class SqsMessageQueue(BaseQueue):
    def initialize(self) -> None:
        settings = load_settings().worker.sqs

        self.connection = aioboto3.client(
            "sqs",
            aws_access_key_id=settings.access_key_id,
            aws_secret_access_key=settings.secret_access_key,
            region_name=settings.region,
        )

        self.queue_name = settings.queue_name

    async def send(self, generation_uuid: UUID) -> None:
        await self.connection.send_message(
            QueueUrl=self.queue_name,
            MessageBody=generation_uuid.hex,
        )

    async def receive(self, callback: Callable[[UUID], Awaitable[None]]) -> None:
        logger.info("Starting SQS worker...")
        callback = handle_errors(callback)

        while True:
            logger.info("Waiting for messages...")

            # Long polling for new messages.
            response = await self.connection.receive_message(
                QueueUrl=self.queue_name,
                MaxNumberOfMessages=1,
                WaitTimeSeconds=20,
            )

            if "Messages" not in response:
                continue

            for message in response["Messages"]:
                generation_uuid = UUID(message["Body"])
                await callback(generation_uuid)

                await self.connection.delete_message(
                    QueueUrl=self.queue_name,
                    ReceiptHandle=message["ReceiptHandle"],
                )


def get_message_queue() -> BaseQueue:
    settings = load_settings().worker

    match settings.queue_type:
        case "rabbit":
            return RabbitMessageQueue()
        case "sqs":
            return SqsMessageQueue()
        case _:
            raise ValueError(f"Invalid queue type {settings.queue_type}")
