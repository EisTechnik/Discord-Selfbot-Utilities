import json
from asyncio import create_task
from datetime import datetime
from pathlib import Path
from re import compile as regex_compile
from traceback import format_exc
from typing import Dict, List, Set

from discord import Embed, Message

from utils import BotClass, do_log, slugify


class SaveMessagesTwitchRelay:
    def __init__(self, bot: BotClass):
        self.bot = bot

        self.cfg = self.bot.CFG.get("save_messages_twitch_relay", {})
        if not self.cfg.get("run", None):
            do_log(
                "'run' variable for 'save_messages_twitch_relay' in config not true. Skipping 'Save Messages Twitch "
                "Relay' module."
            )
            return
        self.debug = self.bot.CFG.get("debug", False)
        self.data_folder = self.bot.data_folder
        self.filter_guilds = True
        self.filter_authors = True
        self.filter_channels = True
        self.url_regex = regex_compile(
            r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
        )
        self.messages: Dict[str, List] = {}
        self.word_list: Set[str] = set()
        create_task(self.async_init())

    async def async_init(self):
        do_log("Initalizing 'Save Twitch Relay' module.")

        guild_ids = self.cfg.get("guild_ids", [])
        self.guilds = {}
        if not guild_ids:
            self.filter_guilds = False
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

        author_ids = self.cfg.get("author_ids", [])
        self.authors = {}
        if not author_ids:
            self.filter_authors = False
        else:
            for author_id in author_ids:
                for guild in self.guilds.values():
                    try:
                        author = guild.get_member(author_id)
                        if author is None:
                            continue
                        author.display_name = slugify(author.display_name)
                        if author_id not in self.authors:
                            self.authors[author_id] = {}
                        self.authors[author_id][guild.id] = author
                        do_log(
                            f"Found member id {author_id} ({author.display_name}) in '{guild.name}' guild."
                        )
                    except Exception:
                        if self.debug:
                            print(format_exc())
                        continue
                if author_id not in self.authors:
                    do_log(f"Failed to find member '{author_id}' in any guilds.")

            if not self.authors:
                do_log("Failed to find any specified authors. Terminating.")
                return

        channel_ids = self.cfg.get("channel_ids", [])
        self.channels = {}
        if not channel_ids:
            self.filter_channels = False
        else:
            for channel_id in channel_ids:
                for guild in self.guilds.values():
                    try:
                        channel = guild.get_channel(channel_id)
                        if channel is None:
                            continue
                        channel.name = slugify(channel.name)
                        self.channels[channel_id] = channel
                        do_log(
                            f"Found channel id {channel_id} ({channel.name}) in '{guild.name}' guild."
                        )
                        break  # Channel ids unique across guilds
                    except Exception:
                        if self.debug:
                            print(format_exc())
                        continue
                if channel_id not in self.channels:
                    do_log(f"Failed to find channel '{channel_id}' in any guilds.")

            if not self.channels:
                do_log("Failed to find any specified channels. Terminating.")
                return

        await self.run_process()

    async def run_process(self):
        await self.save_by_channels()

    async def save_by_channels(self):
        for channel in self.channels.values():
            guild = self.guilds[channel.guild.id]
            channel_name = slugify(channel.name)

            do_log(f"Saving messages from '{channel.name}' in '{guild.name}'")
            folder = self.data_folder / guild.name / channel_name
            Path(folder).mkdir(parents=True, exist_ok=True)
            async for message in channel.history(limit=None):
                await self.save_from_message(message, folder)

        with open("messages.json", "w") as f:
            f.write(json.dumps(self.messages, indent=4, sort_keys=True))

        with open("twitch_wordlist.json", "w") as f:
            f.write(json.dumps(list(self.word_list), indent=4, sort_keys=True))

        with open("authors.json", "w") as f:
            f.write(json.dumps(list(self.messages.keys()), indent=4, sort_keys=True))

        print("\n\n\n")
        do_log("Complete.")

    async def update_word_list(self, twitch_message: str):
        word_list = []

        for word in twitch_message.split():
            clean_word = "".join(char for char in word if char.isalpha())
            if len(word) <= 1 and word != "i":
                continue
            word_list.append(clean_word.lower())

        self.word_list |= set(word_list)

    async def save_from_message(self, message: Message, folder, member=None):
        if member is not None and message.author.id != member.id:
            return

        date_time = datetime.fromtimestamp(message.created_at.timestamp())
        dt_str = date_time.strftime("%Y-%m-%d_%H-%M-%S-%f")
        if len(message.embeds) > 0:
            embed: Embed = message.embeds[0]

            # Strip command from message
            # try:
            #     if not embed.description.startswith("!m "):
            #         return
            # except AttributeError:
            #     return

            # .replace("!m ", "")
            twitch_message = embed.description.encode("ascii", "ignore").decode("ascii")

            if twitch_message.startswith("/e"):
                return

            twitch_author = "ERROR"
            author_embed = embed.author
            if author_embed is not None:
                twitch_author = embed.author.name

            twitch_message_obj = {"date": dt_str, "message": twitch_message}

            if twitch_author not in self.messages:
                self.messages[twitch_author] = []

            self.messages[twitch_author].append(twitch_message_obj)

            await self.update_word_list(twitch_message)
