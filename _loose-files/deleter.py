from asyncio import sleep as async_sleep
from datetime import datetime
from traceback import format_exc

from discord import Forbidden, HTTPException, NotFound, Profile, Status
from discord.ext import commands

client = commands.Bot(
    command_prefix="/",  # Needs a prefix for some reason, not used
    self_bot=True,
    status=Status.invisible,
)


def log_with_time(message: str):
    """Prints a message with a date-time prefix, there are better ways to do this"""
    date_str: str = datetime.now().strftime("%Y-%b-%d %I:%M:%S %p")
    print(f"[{date_str}] {message}")


@client.event
async def on_error(event, args="", kwargs=""):
    """Automatically catch discord.py errors and continue after logging them, instead of crashing"""
    error_trace = format_exc()

    if "KeyboardInterrupt" in error_trace:
        # We actually do want to halt the program on this, or Control+C won't work
        raise KeyboardInterrupt

    log_with_time(f"[Uncaught Error]\n{error_trace}")


async def get_user_to_purge(target_id: int) -> Profile:
    try:
        user_profile = await client.fetch_user_profile(
            target_id, with_mutuals=False, fetch_note=False
        )
    except NotFound as e:
        raise ValueError(f"Could not find a user by id '{target_id}'.") from e
    except Forbidden as e:
        raise ValueError(
            f"Encountered some permission error fetching user by id '{target_id}'."
        ) from e
    except HTTPException as e:
        raise ValueError(
            f"Encountered some API error/ratelimit fetching user by id '{target_id}'."
        ) from e

    return user_profile


async def delete_own_messages_from_user(user_profile: Profile):
    processed_count = 0
    deleted_count = 0
    timeout_seconds = 20
    delete_padding_time = 1

    async for message in user_profile.user.history(limit=None):
        processed_count += 1
        if message.author == client.user:
            while True:
                # If successful, immediately break out, otherwise retry incrementally slower
                delay = timeout_seconds
                try:
                    await message.delete()
                    deleted_count += 1
                    log_with_time(
                        f"Deleted {deleted_count} messages ({processed_count} processed)"
                    )
                    # Wait after deleting so we don't spam and get rate limited
                    await async_sleep(delete_padding_time)
                    break
                except HTTPException as e:
                    if message.is_system():
                        break  # Skip system messages but don't check every delete, wasteful
                    content_indented = message.content.replace("\n", "\n ")
                    log_with_time(
                        f"\nPotential rate limit, waiting {delay}s\n Error details: {e}\n Processed: {processed_count}\n Deleted: {deleted_count}\n Failed message:\n '{content_indented}'\n"
                    )
                    await async_sleep(delay)
                    delay *= 2  # Double the delay until we succeed

        elif processed_count % 25 == 0 or processed_count == 0:
            log_with_time(
                f"Processed {processed_count} messages ({deleted_count} deleted)"
            )


async def init(target_id: int):
    log_with_time(f"Your name: {client.user.name}")
    log_with_time(f"Your ID: {client.user.id}")
    log_with_time(f"Target ID: {target_id}")
    log_with_time("Loaded\n\n")

    print(f"Starting deletion of direct messages. Is the above information correct?")
    print("Press Enter to proceed, or Control+C to terminate.")
    input()

    target_userobj = await get_user_to_purge(target_id)
    print(f"Found user '{target_userobj}'. Once more, double check this is correct.")
    print("Press Enter to proceed, or Control+C to terminate.")
    input()

    log_with_time("Beginning deletion sequence")
    await delete_own_messages_from_user(target_userobj)

    print("\n\n\n")
    log_with_time("Message deletion completed.")
    print("Press Enter to close.")
    input()
    exit()


@client.event
async def on_ready():
    try:
        # CHANGE THIS v
        user_id_to_delete_dms_in = 123456789012345678
        # CHANGE THIS ^

        await init(user_id_to_delete_dms_in)
    except (KeyboardInterrupt, SystemExit):
        pass
    except Exception:
        error_trace = format_exc()
        log_with_time(f"[Critical Error]\n{error_trace}")
    finally:
        # Regardless of success or exception, execute this code next
        try:
            await client.close()
        except Exception:
            pass


# CHANGE THIS v
your_token = "ABCdEFg1HiJkLMN2OPQ3RST4.UVwX5y.-zabCD6eFgHiJK7lMnop8qr9S0t"
# CHANGE THIS ^

client.run(your_token)
