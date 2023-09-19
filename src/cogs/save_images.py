from asyncio import create_task
from datetime import datetime
from mimetypes import guess_type
from os.path import isfile
from pathlib import Path
from re import compile as regex_compile
from traceback import format_exc

from aiofiles import open as aio_open
from aiohttp import ClientSession as AioClientSession

from utils import BotClass, do_log, ntfs_compress_snowflake, slugify


class SaveImages:
    def __init__(self, bot: BotClass):
        self.bot = bot

        self.cfg = self.bot.CFG.get("save_images", {})
        if not self.cfg.get("run", None):
            do_log(
                "'run' variable for 'save_images' in config not true. Skipping 'Save Images' module."
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
        create_task(self.async_init())

    async def async_init(self):
        do_log("Initalizing 'Save Images' module.")

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
        if self.filter_authors:
            await self.save_by_author()
        elif self.filter_channels:
            await self.save_by_channels()
        else:
            await self.save_by_guilds()

    async def save_by_author(self):
        for memberships in self.authors.values():
            for guild_id, membership in memberships.items():
                guild = self.guilds[guild_id]
                do_log(
                    f"Saving images from '{membership.display_name}' in '{guild.name}'"
                )

                author_folder = self.data_folder / guild.name / membership.display_name
                channel_list = guild.channels
                if self.filter_channels:
                    channel_list = [
                        channel
                        for channel in self.channels.values()
                        if channel.guild.id == guild.id
                    ]
                for channel in channel_list:
                    channel_name = slugify(channel.name)
                    do_log(f"Scanning '{channel_name}' channel")
                    folder = author_folder / channel_name
                    Path(folder).mkdir(parents=True, exist_ok=True)
                    async for message in channel.history(limit=None):
                        await self.save_from_message(message, folder, membership)
        print("\n\n\n")
        do_log("Complete.")

    async def save_by_channels(self):
        for channel in self.channels.values():
            guild = self.guilds[channel.guild.id]
            channel_name = slugify(channel.name)

            do_log(f"Saving images from '{channel.name}' in '{guild.name}'")
            folder = self.data_folder / guild.name / channel_name
            Path(folder).mkdir(parents=True, exist_ok=True)
            async for message in channel.history(limit=None):
                await self.save_from_message(message, folder)
        print("\n\n\n")
        do_log("Complete.")

    async def save_from_message(self, message, folder, member=None):
        if member is not None and message.author.id != member.id:
            return

        # Find URLs in message
        image_urls = self.url_regex.findall(message.content)

        # Get URLs for embedded attachments
        for attachment in message.attachments:
            image_urls.append(attachment.url)

        for url in image_urls:
            mime_type, _ = guess_type(url)
            if not (mime_type) or not (mime_type.startswith("image")):
                continue

            file_name = url.rsplit("/", 1)[-1]  # Last part of URL

            date_time = datetime.fromtimestamp(message.created_at.timestamp())
            dt_str = date_time.strftime("%Y-%m-%d_%H-%M-%S-%f")
            image_name, extension = file_name.rsplit(".", 1)
            file_name = f"{dt_str}.{extension}"
            if isfile(folder / file_name):
                continue
            # if isfile(folder / file_name):
            #     image_name, extension = file_name.rsplit(".", 1)
            #     snowflake = int(str(message.created_at.timestamp()).replace(".", ""))
            #     file_name = (
            #        f"{image_name}_{ntfs_compress_snowflake(snowflake)}.{extension}"
            #     )
            try:
                async with AioClientSession() as session:
                    async with session.get(url) as response:
                        try:
                            print("Saving {}".format(file_name))
                            file_manager = await aio_open(
                                folder / file_name,
                                mode="wb",
                            )
                            await file_manager.write(await response.read())
                            await file_manager.close()

                        except Exception:
                            do_log(f"ERROR\n{format_exc()}\n\n")
                            input("Press enter to continue")
                            continue
            except Exception:
                do_log(f"ERROR\n{format_exc()}\n\n")
                input("Critical failure, press enter to continue")
