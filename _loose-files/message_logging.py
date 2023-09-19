from asyncio import sleep as async_sleep
from traceback import format_exc

from discord import Forbidden, HTTPException, Message, NotFound, Profile, Status
from discord.ext.commands import Bot

from message_logging_cog import MessageLogging
from utils import log_with_time

client = Bot(
    command_prefix="/",  # Needs a prefix for some reason, not used
    self_bot=True,
    status=Status.invisible,
)


@client.event
async def on_error(event, args="", kwargs=""):
    """Automatically catch discord.py errors and continue after logging them, instead of crashing"""
    error_trace = format_exc()

    if "KeyboardInterrupt" in error_trace:
        # We actually do want to halt the program on this, or Control+C won't work
        raise KeyboardInterrupt

    log_with_time(f"[Uncaught Error]\n{error_trace}")


async def init(guild_id: int):
    client.add_cog(MessageLogging(client, guild_id))


@client.event
async def on_ready():
    try:
        log_with_time(f"Your name: {client.user.name}")
        log_with_time(f"Your ID: {client.user.id}")
        # CHANGE THIS v
        guild_id = 123456789012345678
        # CHANGE THIS ^

        await init(guild_id)
    except Exception:
        error_trace = format_exc()
        log_with_time(f"[Critical Error]\n{error_trace}")
        # Regardless of success or exception, execute this code next
        try:
            await client.close()
        except Exception:
            pass


# CHANGE THIS v
your_token = "ABCdEFg1HiJkLMN2OPQ3RST4.UVwX5y.-zabCD6eFgHiJK7lMnop8qr9S0t"
# CHANGE THIS ^

client.run(your_token)
