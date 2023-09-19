from asyncio import create_task
from pathlib import Path
from re import compile as regex_compile
from traceback import format_exc

from utils import BotClass, do_log, slugify


class SaveEmojis:
    def __init__(self, bot: BotClass):
        self.bot = bot

        self.cfg = self.bot.CFG.get("save_emojis", {})
        if not self.cfg.get("run", None):
            do_log(
                "'run' variable for 'save_emojis' in config not true. Skipping 'Save Emojis' module."
            )
            return
        self.debug = self.bot.CFG.get("debug", False)
        self.data_folder = self.bot.data_folder
        self.url_regex = regex_compile(
            r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
        )
        create_task(self.async_init())

    async def async_init(self):
        do_log("Initalizing 'Save Emojis' module.")

        guild_ids = self.cfg.get("guild_ids", [])
        self.guilds = {}
        if not guild_ids:
            self.guilds = self.bot.client.guilds
        else:
            for guild_id in guild_ids:
                try:
                    guild = self.bot.client.get_guild(guild_id)
                    if guild is None:
                        continue
                    guild.name = slugify(guild.name)
                    self.guilds[guild_id] = guild
                    do_log(f"Found guild id {guild_id} ({guild.name}).")
                except Exception:
                    do_log(f"Failed to find guild '{guild_id}', skipping")
                    if self.debug:
                        print(format_exc())

            if not self.guilds:
                do_log("Failed to find any specified guilds. Terminating.")
                return

        await self.run_process()

    async def run_process(self):
        await self.save_by_guild()

    async def save_by_guild(self):
        for guild in self.guilds.values():
            folder = self.data_folder / guild.name / "_emojis"
            Path(folder).mkdir(parents=True, exist_ok=True)
            do_log(f"Saving emojis from '{guild.name}'")
            for emoji in guild.emojis:
                emoji.name = slugify(emoji.name)
                await self.save_emoji(emoji, folder)
        print("\n\n\n")
        do_log("Complete.")

    async def save_emoji(self, emoji, folder):
        emoji_url = str(emoji.url)
        emoji_asset = emoji.url
        file_extension = emoji_url.rsplit(".", 1)[-1]
        file_name = f"{emoji.name}.{file_extension}"

        try:
            print("Saving {}".format(file_name))
            await emoji_asset.save(folder / file_name)
        except Exception:
            do_log(f"ERROR\n{format_exc()}\n\n")
            input("Critical failure, press enter to continue")
