# TODO: remake
# Old code from ~2017
import os
from mimetypes import guess_type
from re import findall
from shutil import move

import imagehash

try:
    from PIL import Image
except:
    import Image

import asyncio
import io
import re
from traceback import format_exc as tracebackformat

import aiofiles
import aiohttp
import discord

client = discord.Client()
from datetime import datetime
from time import time


@client.event
async def on_ready():
    print(
        "Loaded {}".format(
            client.user.name.encode("ascii", "replace").decode("ascii", "replace")
        )
    )
    serverid = "123456789012345678"

    channels = ["123456789012345678"]
    authors = ["123456789012345678"]
    server = client.get_server(serverid)
    directory = (
        "Images_"
        + server.name.encode("ascii", "replace").decode("ascii", "replace")
        + "_"
        + server.id
    )
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except:
        directory = "Images_" + server.id
        if not os.path.exists(directory):
            os.makedirs(directory)

    for channel in server.channels:
        if channels != []:
            if channel.id not in channels:
                continue
        channeldirectory = channel.name.encode("ascii", "replace").decode(
            "ascii", "replace"
        )
        try:
            if not os.path.exists(os.path.join(directory, channeldirectory)):
                os.makedirs(os.path.join(directory, channeldirectory))
        except:
            channeldirectory = channel.id
            if not os.path.exists(os.path.join(directory, channeldirectory)):
                os.makedirs(os.path.join(directory, channeldirectory))

        print(
            "Downloading images from {} channel".format(
                channel.name.encode("ascii", "replace").decode("ascii", "replace")
            )
        )
        async for msg in client.logs_from(channel, limit=500000):
            if authors != []:
                if msg.author.id not in authors:
                    continue
            urls = findall(
                "http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
                msg.content,
            )
            for attachment in msg.attachments:
                urls.append(attachment["url"])
            for url in urls:
                mimetype, encoding = guess_type(url)
                if not (mimetype) or not (mimetype.startswith("image")):
                    urls.remove(url)
            for image in urls:
                try:
                    async with aiohttp.ClientSession() as cs:
                        async with cs.get(image) as r:
                            try:
                                imagename = image.split("/")[-1]
                                if os.path.isfile(
                                    os.path.join(directory, channeldirectory, imagename)
                                ):
                                    imagename = (
                                        imagename.rsplit(".", 1)[0]
                                        + str(time()).replace(".", "")
                                        + "."
                                        + imagename.rsplit(".", 1)[1]
                                    )
                                print("Saving {}".format(imagename))
                                f = await aiofiles.open(
                                    os.path.join(
                                        directory, channeldirectory, imagename
                                    ),
                                    mode="wb",
                                )
                                await f.write(await r.read())
                                await f.close()

                            except:
                                print("Failure")
                                print(tracebackformat())
                                input("Press enter to continue")
                                continue
                except:
                    print(tracebackformat())
                    input("Critical failure, press enter to continue")


token = "SDFGSDFBSDFBDSGFHDSGHSDFGSDF"
client.run(token, bot=False)
