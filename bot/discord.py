"""Defines the Discord bot structure."""

import logging
import os

import discord
import ml.api as ml
from discord.ext.commands import Bot, Context
from discord.voice_client import VoiceClient

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
    bot = Bot(command_prefix="!", intents=intents)

    connections: dict[int, VoiceClient] = {}

    @bot.event
    async def on_ready() -> None:
        logger.info("Logged in as %s", bot.user)

    @bot.command(name="record")
    async def record(ctx: Context) -> None:
        voice = ctx.author.voice
        if not voice:
            await ctx.send("You aren't in a voice channel!")
            return

        vc = await voice.channel.connect()
        connections.update({ctx.guild.id: vc})

        # Start recording
        # vc.start_recording(discord.WavSink("output.wav"))
        vc.stop()

        await ctx.send("Recording started. Use !stop to stop recording.")

    @bot.command(name="stop")
    async def stop(ctx: Context) -> None:
        vc = connections.get(ctx.guild.id)
        if not vc:
            await ctx.send("Not recording.")
            return

        # Stop recording and disconnect
        vc.stop()
        await vc.disconnect()

        await ctx.send("Recording stopped.")

    bot.run(token)
