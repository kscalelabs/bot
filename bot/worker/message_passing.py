"""Functions for configuring the worker."""

import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable

import boto3
from pika.adapters.blocking_connection import BlockingChannel, BlockingConnection
from pika.connection import ConnectionParameters
from pika.credentials import PlainCredentials
from pika.spec import Basic, BasicProperties
from typing import Awaitable
import functools
from uuid import UUID

from bot.settings import load_settings
from typing import ParamSpec
import logging

logger = logging.getLogger(__name__)

P = ParamSpec("P")


def sync(f: Callable[P, Awaitable[None]]) -> Callable[P, None]:
    @functools.wraps(f)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> None:
        return asyncio.get_event_loop().run_until_complete(f(*args, **kwargs))
    return wrapper


def handle_errors(f: Callable[P, Awaitable[None]]) -> Callable[P, Awaitable[None]]:
    @functools.wraps(f)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> None:
        try:
            await f(*args, **kwargs)
        except Exception:
            logger.exception("An exception occurred.")
    return wrapper


@dataclass(frozen=True)
class Message:
    generation_uuid: UUID


class BaseQueue(ABC):
    @abstractmethod
    def initialize(self) -> None:
        """Initializes the queue."""

    @abstractmethod
    async def send(self, message: Message) -> None:
        """Sends a message to the queue.

        Args:
            message: The message to send.
        """

    @abstractmethod
    async def receive(self, callback: Callable[[Message],Awaitable[None]]) -> None:
        """Receives messages from the queue.

        Args:
            callback: The callback function to call when a message is received.
        """


class RabbitMessageQueue(BaseQueue):
    queue_name: str
    connection: BlockingConnection
    channel: BlockingChannel

    def initialize(self) -> None:
        settings = load_settings().worker.rabbit

        self.connection = BlockingConnection(
            ConnectionParameters(
                host=settings.host,
                port=settings.port,
                virtual_host=settings.virtual_host,
                credentials=PlainCredentials(
                    username=settings.username,
                    password=settings.password,
                ),
            )
        )

        self.queue_name = settings.queue_name
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue_name)

    async def send(self, message: Message) -> None:
        self.channel.basic_publish(
            exchange="",
            routing_key="generation",
            body=str(message.generation_uuid),
        )

    async def receive(self, callback: Callable[[Message], Awaitable[None]]) -> None:
        logger.info("Starting RabbitMQ worker...")

        callback = handle_errors(callback)

        @sync
        async def callback_wrapper(
            ch: BlockingChannel,
            method: Basic.Deliver,
            properties: BasicProperties,
            body: bytes,
        ) -> None:
            message = Message(generation_uuid=UUID(body.decode("utf-8")))
            callback(message)

        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            queue=self.queue_name,
            on_message_callback=callback_wrapper,
            auto_ack=True,
        )
        self.channel.start_consuming()


class SqsMessageQueue(BaseQueue):
    connection: Any
    queue_url: str

    def initialize(self) -> None:
        settings = load_settings().worker.sqs

        self.connection = boto3.client(
            "sqs",
            aws_access_key_id=settings.access_key_id,
            aws_secret_access_key=settings.secret_access_key,
            region_name=settings.region,
        )

        self.queue_url = self.connection.get_queue_url(QueueName=settings.queue_name)["QueueUrl"]

    async def send(self, message: Message) -> None:
        self.connection.send_message(
            QueueUrl=self.queue_url,
            MessageBody=message.generation_uuid,
        )

    async def receive(self, callback: Callable[[Message], Awaitable[None]]) -> None:
        logger.info("Starting SQS worker...")
        callback = handle_errors(callback)

        while True:
            response = self.connection.receive_message(
                QueueUrl=self.queue_url,
                MaxNumberOfMessages=1,
                WaitTimeSeconds=20,
            )
            for message in response["Messages"]:
                generation_uuid = message["Body"]
                message = Message(generation_uuid=generation_uuid)
                await callback(message)
                self.connection.delete_message(
                    QueueUrl=self.queue_url,
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
