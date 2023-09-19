# TODO: remake
# Old code from ~2017
import asyncio
import io
import os
import re
from winsound import Beep

import aiohttp
import discord
from discord.ext import commands
from PIL import Image

client = discord.Client()
from datetime import datetime


async def SaveMessages(servers, author=None, channellist=None):
    print("\n\n\n--MESSAGE LOGS--\n\n\n")
    for server in servers:
        server = client.get_server(server)
        directory = (
            server.name.encode("ascii", "replace").decode("ascii", "replace")
            + "_"
            + server.id
        )
        try:
            if not os.path.exists(directory):
                os.makedirs(directory)
        except:
            if not os.path.exists(server.id):
                os.makedirs(server.id)
            directory = server.id
        for channel in server.channels:
            if channellist != None:
                if channel.id not in channellist:
                    continue
            print(
                channel.name.encode("ascii", errors="ignore").decode(
                    "ascii", errors="ignore"
                )
            )
            try:
                msgs = []
                async for msg in client.logs_from(channel, limit=500000):
                    msgl = ""
                    if author == None or msg.author.id == author:
                        msgl = (
                            msg.timestamp.strftime("[%Y-%b-%d_%Hh%Mm%Ss] ")
                            + msg.author.name
                            + ": "
                        )
                        try:
                            msg.attachments[0]
                            for i in msg.attachments:
                                msgl += i["url"]
                                if i != msg.attachments[-1]:
                                    msgl += "\n"
                        except:
                            msgl += msg.content
                        msgl = msgl.encode("ascii", errors="ignore").decode(
                            "ascii", errors="ignore"
                        )
                        msgl += "\n\n"
                        msgs.insert(0, msgl)
                        # print(msgl)
                with open(
                    os.path.join(
                        directory,
                        channel.name.encode("ascii", errors="ignore").decode(
                            "ascii", errors="ignore"
                        )
                        + ".txt",
                    ),
                    "a",
                ) as inputfile:
                    for i in msgs:
                        try:
                            inputfile.write(i)
                        except:
                            print("Error in write")
            except Exception as e:
                print(str(e))


async def SaveMessagesWithIDs(servers, author=None, channellist=None):
    print("\n\n\n--MESSAGE LOGS--\n\n\n")
    for server in servers:
        server = client.get_server(server)
        directory = (
            server.name.encode("ascii", "replace").decode("ascii", "replace")
            + "_"
            + server.id
        )
        try:
            if not os.path.exists(directory):
                os.makedirs(directory)
        except:
            if not os.path.exists(server.id):
                os.makedirs(server.id)
            directory = server.id
        for channel in server.channels:
            if channellist != None:
                if channel.id not in channellist:
                    continue
            print(
                channel.name.encode("ascii", errors="ignore").decode(
                    "ascii", errors="ignore"
                )
            )
            try:
                msgs = []
                async for msg in client.logs_from(channel, limit=500000):
                    msgl = ""
                    if author == None or msg.author.id == author:
                        msgl = "{" + msg.id + "} "
                        msgl += (
                            msg.timestamp.strftime("[%Y-%b-%d_%Hh%Mm%Ss] ")
                            + msg.author.name
                            + ": "
                        )
                        try:
                            msg.attachments[0]
                            for i in msg.attachments:
                                msgl += i["url"]
                                if i != msg.attachments[-1]:
                                    msgl += "\n"
                        except:
                            msgl += msg.content
                        msgl = msgl.encode("ascii", errors="ignore").decode(
                            "ascii", errors="ignore"
                        )
                        msgl += "\n\n"
                        msgs.insert(0, msgl)
                        # print(msgl)
                with open(
                    os.path.join(
                        directory,
                        channel.name.encode("ascii", errors="ignore").decode(
                            "ascii", errors="ignore"
                        )
                        + ".txt",
                    ),
                    "a",
                ) as inputfile:
                    for i in msgs:
                        try:
                            inputfile.write(i)
                        except:
                            print("Error in write")
            except Exception as e:
                print(str(e))


async def SaveChannels(servers):
    print("\n\n\n--CHANNEL LIST--\n\n\n")
    for server in servers:
        server = client.get_server(server)
        directory = (
            server.name.encode("ascii", "replace").decode("ascii", "replace")
            + "_"
            + server.id
        )
        try:
            if not os.path.exists(directory):
                os.makedirs(directory)
        except:
            if not os.path.exists(server.id):
                os.makedirs(server.id)
            directory = server.id
        with open(os.path.join(directory, "___channels___.txt"), "w") as inputfile:
            for channel in server.channels:
                channelname = (
                    "#"
                    + channel.name.encode("ascii", errors="ignore").decode(
                        "ascii", errors="ignore"
                    )
                    + " ("
                    + channel.id
                    + ")"
                )
                try:
                    if (
                        channel.topic.encode("ascii", errors="ignore").decode(
                            "ascii", errors="ignore"
                        )
                        != ""
                    ):
                        channelname += "\n" + channel.topic.encode(
                            "ascii", errors="ignore"
                        ).decode("ascii", errors="ignore")
                    channelname += "\n" + channel.created_at.strftime(
                        "[%Y-%b-%d_%Hh%Mm%Ss] "
                    )
                    async for msg in client.logs_from(channel, limit=1):
                        msg.content
                except:
                    channelname += "\n<Private>"
                print(channelname)
                inputfile.write(channelname + "\n\n\n\n")


async def SaveSelf_ChannelPerms(servers):
    print("\n\n\n--SELF CHANNEL PERMS--\n\n\n")
    for server in servers:
        server = client.get_server(server)
        directory = (
            server.name.encode("ascii", "replace").decode("ascii", "replace")
            + "_"
            + server.id
        )
        try:
            if not os.path.exists(directory):
                os.makedirs(directory)
        except:
            if not os.path.exists(server.id):
                os.makedirs(server.id)
            directory = server.id
        with open(
            os.path.join(directory, "___self_channelpermissions___.txt"), "w"
        ) as inputfile:
            for channel in server.channels:
                channelname = (
                    "#"
                    + channel.name.encode("ascii", errors="ignore").decode(
                        "ascii", errors="ignore"
                    )
                    + " ("
                    + channel.id
                    + ")"
                )
                print(channelname)
                inputfile.write("----" + channelname + "----\n")
                cp = channel.permissions_for(server.get_member(client.user.id))
                cp = (
                    [cp.create_instant_invite, "Create Instant Invite"],
                    [cp.manage_channels, "Manage Channel"],
                    [cp.manage_roles, "Manage Permissions"],
                    [cp.manage_webhooks, "Manage Webhooks"],
                    [cp.read_messages, "Read Messages"],
                    [cp.send_messages, "Send Messages"],
                    [cp.send_tts_messages, "Send TTS Messages"],
                    [cp.manage_messages, "Manages Messages"],
                    [cp.embed_links, "Embed Links"],
                    [cp.attach_files, "Attach Files"],
                    [cp.read_message_history, "Read Message History"],
                    [cp.mention_everyone, "Mention Everyone"],
                    [cp.external_emojis, "Use External Emojis"],
                    [cp.add_reactions, "Add Reactions"],
                )
                chanperms = ""
                for permobj in cp:
                    chanperms += permobj[1] + ": "
                    if permobj[0]:
                        chanperms += "Y"
                    else:
                        chanperms += "N"
                    chanperms += "\n"
                inputfile.write(chanperms + "\n\n")


async def SaveSelf_ServerPerms(servers):
    print("\n\n\n--SELF SERVER PERMS--\n\n\n")
    for server in servers:
        server = client.get_server(server)
        directory = (
            server.name.encode("ascii", "replace").decode("ascii", "replace")
            + "_"
            + server.id
        )
        try:
            if not os.path.exists(directory):
                os.makedirs(directory)
        except:
            if not os.path.exists(server.id):
                os.makedirs(server.id)
            directory = server.id
        with open(
            os.path.join(directory, "___self_permissions___.txt"), "w"
        ) as inputfile:
            cp = server.get_member(client.user.id).server_permissions
            cp = (
                [cp.administrator, "Administrator"],
                [cp.kick_members, "Kick Members"],
                [cp.ban_members, "Ban Members"],
                [cp.create_instant_invite, "Create Instant Invite"],
                [cp.manage_channels, "Manage Channel"],
                [cp.manage_roles, "Manage Permissions"],
                [cp.manage_webhooks, "Manage Webhooks"],
                [cp.read_messages, "Read Messages"],
                [cp.send_messages, "Send Messages"],
                [cp.send_tts_messages, "Send TTS Messages"],
                [cp.manage_messages, "Manages Messages"],
                [cp.embed_links, "Embed Links"],
                [cp.attach_files, "Attach Files"],
                [cp.read_message_history, "Read Message History"],
                [cp.mention_everyone, "Mention Everyone"],
                [cp.external_emojis, "Use External Emojis"],
                [cp.add_reactions, "Add Reactions"],
            )
            chanperms = ""
            for permobj in cp:
                chanperms += permobj[1] + ": "
                if permobj[0]:
                    chanperms += "Y"
                else:
                    chanperms += "N"
                chanperms += "\n"
            inputfile.write(chanperms + "\n\n")


async def SaveRoles(servers):
    print("\n\n\n--ROLE LIST--\n\n\n")
    for server in servers:
        server = client.get_server(server)
        directory = (
            server.name.encode("ascii", "replace").decode("ascii", "replace")
            + "_"
            + server.id
        )
        try:
            if not os.path.exists(directory):
                os.makedirs(directory)
        except:
            if not os.path.exists(server.id):
                os.makedirs(server.id)
            directory = server.id
        roleslist = []
        for i in server.roles:
            roleslist.append(i)
        roleslist = sorted(roleslist, key=lambda mem: mem.position, reverse=True)

        with open(os.path.join(directory, "___roles___.txt"), "w") as inputfile:
            for role in roleslist:
                rolename = (
                    "@"
                    + role.name.encode("ascii", errors="ignore").decode(
                        "ascii", errors="ignore"
                    )
                    + " ("
                    + role.id
                    + ")"
                )
                print(rolename)
                inputfile.write(rolename + "\n\n\n\n")


async def SaveMembers(servers):
    print("\n\n\n--MEMBER LIST--\n\n\n")
    for server in servers:
        client.get_server(server).name
        server = client.get_server(server)
        print("Members: " + str(len(server.members)))
        try:
            if server.large:
                await client.request_offline_members(server)
        except:
            pass
        print("Members post-offline: " + str(len(server.members)))
        directory = (
            server.name.encode("ascii", "replace").decode("ascii", "replace")
            + "_"
            + server.id
        )
        try:
            if not os.path.exists(directory):
                os.makedirs(directory)
        except:
            if not os.path.exists(server.id):
                os.makedirs(server.id)
            directory = server.id
        memberslist = []
        for i in server.members:
            memberslist.append(i)
        memberslist = sorted(
            memberslist, key=lambda mem: mem.top_role.position, reverse=True
        )
        with open(os.path.join(directory, "___members___.txt"), "w") as inputfile:
            for i in memberslist:
                roles = ""
                for x in sorted(i.roles, key=lambda rle: rle.position, reverse=True):
                    roles += "[" + x.name + "," + str(x.position) + "]"
                    if x.name != i.roles[-1].name:
                        roles += ","
                if roles == "[@everyone,0]":
                    roles = ""
                elif "@everyone" in roles:
                    roles = roles.replace("[@everyone,0],", "")

                text = ""
                if i.display_name != i.name:
                    text += i.display_name + "\n"
                text += i.name + "#" + i.discriminator
                text += "\n" + i.id
                if i.avatar_url != "":
                    text += "\n" + i.avatar_url
                text += "\nJOIN: " + i.joined_at.strftime("%Y-%b-%d_%Hh%Mm%Ss")
                text += "\nCREATION: " + i.created_at.strftime("%Y-%b-%d_%Hh%Mm%Ss")
                text += "\n" + roles
                if i.bot:
                    text += "\n--BOT--"
                text = text.encode("ascii", "replace").decode("ascii", "replace")
                try:
                    print(text)
                except:
                    print("Print failure in write")
                inputfile.write(text + "\n\n\n\n")


async def SaveMemberNames(servers):
    print("\n\n\n--MEMBER NAME LIST--\n\n\n")
    for server in servers:
        client.get_server(server).name
        server = client.get_server(server)
        print("Members: " + str(len(server.members)))
        try:
            if server.large:
                await client.request_offline_members(server)
        except:
            pass
        print("Members post-offline: " + str(len(server.members)))
        directory = (
            server.name.encode("ascii", "replace").decode("ascii", "replace")
            + "_"
            + server.id
        )
        try:
            if not os.path.exists(directory):
                os.makedirs(directory)
        except:
            if not os.path.exists(server.id):
                os.makedirs(server.id)
            directory = server.id
        memberslist = []
        for i in server.members:
            memberslist.append(i)
        memberslist = sorted(
            memberslist, key=lambda mem: mem.top_role.position, reverse=True
        )
        with open(os.path.join(directory, "___members___.txt"), "w") as inputfile:
            for i in memberslist:
                text = ""
                if i.display_name != i.name:
                    text += i.display_name + "\n"
                text += i.name + "#" + i.discriminator
                text += "\n" + i.id
                if i.avatar_url != "":
                    text += "\n" + i.avatar_url
                text += "\nJOIN: " + i.joined_at.strftime("%Y-%b-%d_%Hh%Mm%Ss")
                text += "\nCREATION: " + i.created_at.strftime("%Y-%b-%d_%Hh%Mm%Ss")
                if i.bot:
                    text += "\n--BOT--"
                text = text.encode("ascii", "replace").decode("ascii", "replace")
                try:
                    print(text)
                except:
                    print("Print failure in write")
                inputfile.write(text + "\n\n\n\n")


async def SaveImages(servers):
    for server in servers:
        server = client.get_server(server)
        directory = (
            server.name.encode("ascii", "replace").decode("ascii", "replace")
            + "_"
            + server.id
        )
        try:
            if not os.path.exists(directory):
                os.makedirs(directory)
        except:
            if not os.path.exists(server.id):
                os.makedirs(server.id)
            directory = server.id
        for channel in server.channels:
            async for msg in client.logs_from(channel, limit=500000):
                try:
                    msg.attachments[0]
                except:
                    continue
                print(msg.attachments[0]["url"])


print("--Init--")
token = "FDGHDSFGHDVFSDFVAFDSVA"
print("Bot Token: " + token)


async def Reversefiles(dir):
    for root, dirs, files in os.walk(dir):
        for file in files:
            if file.endswith(".txt"):
                with open(os.path.join(root, file), "r") as f:
                    x = f.read()
                x = x.split("\n")
                x = reversed(x)
                with open(os.path.join(root, file), "w") as f:
                    for i in x:
                        f.write(i + "\n")


async def main():
    servers = ["123456789012345678"]
    # author = "123456789012345678"
    # await SaveMembers(servers)
    # await SaveMemberNames(servers)
    # await SaveChannels(servers)
    # await SaveRoles(servers)
    # await SaveSelf_ServerPerms(servers)
    # await SaveSelf_ChannelPerms(servers)
    # await SaveMessages(servers)
    await SaveMessagesWithIDs(
        servers, channellist=["123456789012345678", "123456789012345678"]
    )
    # await SaveImages(servers)
    # await Reversefiles("ABC/chatlogs")
    print("Done")
    # Beep(900,9999999)
    client.logout()


@client.event
async def on_ready():
    print("--Login--")
    print("Name: " + client.user.name)
    print("ID: " + client.user.id)
    print("------------READY------------")
    await main()


client.run(token)
print("Stopping")
