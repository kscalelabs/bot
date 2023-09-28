"""Defines the Discord bot structure."""

import logging
import os

import discord
import ml.api as ml

logger = logging.getLogger(__name__)


def handle_response(message: str) -> str:
    return f"Hello, {message}!"


async def send_message(message: discord.Message, user_message: str, is_private: bool) -> None:
    try:
        response = handle_response(user_message)
        await message.author.send(response) if is_private else await message.channel.send(response)
    except Exception:
        logger.exception("Error sending message.")


def run_discord_bot() -> None:
    ml.configure_logging()

    token = os.environ["DISCORD_TOKEN"]
    intents = discord.Intents.all()
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready() -> None:
        logger.info(f"Logged in as {client.user}.")

    @client.event
    async def on_message(message: discord.Message) -> None:
        if message.author == client.user:
            return

        is_private = isinstance(message.channel, discord.DMChannel)

        username = str(message.author)
        user_message = message.content
        channel = str(message.channel)
        logger.info(f"Received message from {username} in {channel}: {user_message}")

        await send_message(message, user_message, is_private)

    client.run(token)
