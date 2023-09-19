import os
from traceback import format_exc

from dotenv import load_dotenv

import utils
from cogs.save_emojis import SaveEmojis as SaveEmojisCog
from cogs.save_images import SaveImages as SaveImagesCog
from cogs.save_messages_twitch_relay import (
    SaveMessagesTwitchRelay as SaveMessagesTwitchRelayCog,
)

global bot
bot = utils.BotClass()


@bot.client.event
async def on_error(event, args="", kwargs=""):
    error = format_exc()
    utils.log_error("[Uncaught Error] " + error)


async def cog_init():
    bot.save_images_cog = SaveImagesCog(bot)
    bot.save_emojis_cog = SaveEmojisCog(bot)
    bot.save_messages_twitch_relay_cog = SaveMessagesTwitchRelayCog(bot)


@bot.client.event
async def on_ready():
    try:
        utils.do_log(f"Discord name: {bot.client.user.name}")
        utils.do_log(f"Discord ID: {bot.client.user.id}")

        utils.do_log("Ready\n\n")

        bot.ready = True
        await cog_init()
    except Exception:
        await utils.log_error(
            f"\n\n\nCRITICAL ERROR: FAILURE TO INITIALIZE{format_exc()}"
        )
        await bot.client.close()
        await bot.client.logout()
        raise Exception("CRITICAL ERROR: FAILURE TO INITIALIZE")


def main():
    global bot
    bot.ready = False
    utils.do_log("Loading Config")

    bot = utils.load_config_to_bot(bot)  # Load a json to the bot class
    load_dotenv(verbose=True)

    # Merge any env vars with config vars, and make variables easily accessible
    utils.do_log(f"Discord token: {utils.censor_text(os.getenv('DISCORD_TOKEN'))}")

    # DiscordPy tasks
    utils.do_log("Loaded Config")
    utils.do_log("Logging in")
    bot.client.run(os.getenv("DISCORD_TOKEN"), bot=False)
    utils.do_log("Logging out")


if __name__ == "__main__":
    main()
