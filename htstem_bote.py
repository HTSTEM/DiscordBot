import asyncio
import datetime
import json
import os
import random
import traceback
import urllib.request

import discord
import feedparser

from globals import *


class HTSTEM_Bote:
    def __init__(self, client, reload_func):
        self.client = client
        self.reload_func = reload_func

    async def on_ready(self):
        print("Logged in as:")
        print(self.client.user.name)
        print(self.client.user.id)
        print("======")

    async def on_message(self, message):
        try:
            is_command = False
            if message.content.startswith(PREFIX) and not message.content.startswith(PREFIX * 2):
                is_command = True

            command = message.content[len(PREFIX):].split(" ")[0]
            raw_arguments = " ".join(message.content[len(PREFIX):].split(" ")[1:])
            is_developer = message.author.id in DEVELOPERS
            arguments = raw_arguments.split(" ")
            while "" in arguments:
                arguments.remove("")

            if is_command:
                if command == "help":
                    commands = {
                        "help": "`%shelp` - lists the bot commands" % PREFIX,
                        "usercount": "`%susercount` - lists the users on the server" % PREFIX,
                        "userinfo": "`%suserinfo` - displays info about yourself or a mentioned user" % PREFIX,
                        "serverinfo": "`%sserverinfo` - displays info about the server" % PREFIX,
                        "roll": "`%sroll [# of sides] [# of dice to roll]` - rolls some dice" % PREFIX,
                        "cat": "`%scat` - gimme some o' dem cute cat pix" % PREFIX,
                        "dog": "`%sdog` - gimme dem cute dogs" % PREFIX,
                        "randomuser": "`%srandomuser` - selects a random user on the server" % PREFIX,
                        "credits": "`%scredits` - lists the users who have worked on the bot" % PREFIX,

                        "yt": "`%syt [on/off]` - turn YT video notifications on/off" % PREFIX,
                    }
                    aliases = {
                        "adam": "dog"
                    }

                    if len(arguments) == 0:
                        commands_message = "\n".join([i[1] for i in commands.items()])
                        help_message = """Hi! I'm the STEM part of the HTC-Bote, a super-exclusive part only for the HTwins STEM server.
I have a couple commands you can try out, which include:
{0}""".format(commands_message)

                        await self.client.send_message(message.channel, help_message)
                    else:
                        help_message = []
                        done = []
                        for cmd in arguments:
                            if cmd not in done:
                                if cmd in commands:
                                    help_message.append(commands[cmd])
                                elif cmd in aliases:
                                    help_message.append(
                                        "`{0}{1}`: Alias for `{0}{2}`".format(PREFIX, cmd, aliases[cmd]))
                                else:
                                    help_message.append("`{0}{1}`: Command not found".format(PREFIX, cmd))
                                done.append(cmd)
                        await self.client.send_message(message.channel, "\n".join(help_message))
                elif command == "usercount":
                    await self.client.send_message(message.channel, "`{0}` currently has {1} users.".format(
                        message.server.name, message.server.member_count))
                elif command == "userinfo":
                    await self.client.request_offline_members(message.server)

                    if len(message.mentions) > 0:
                        usr = message.mentions[0]
                    elif len(arguments) == 0:
                        usr = message.author
                    else:
                        usr = message.author
                        closest = -1
                        for m in message.server.members:
                            d = self.levenshtein(raw_arguments.lower(), m.name.lower())
                            if raw_arguments.lower() in m.name.lower() and (closest == -1 or d < closest):
                                closest = d
                                usr = m

                    # Get user info

                    username = clear_formatting(usr.name)
                    discrim = "#" + usr.discriminator

                    nickname = "[none]"
                    if usr.nick is not None:
                        nickname = clear_formatting(usr.nick)

                    if usr.game is None:
                        game = "[none]"
                    else:
                        game = clear_formatting(usr.game.name)

                    joined = usr.joined_at
                    joined_days = datetime.datetime.utcnow() - joined
                    created = usr.created_at
                    created_days = datetime.datetime.utcnow() - created
                    avatar = usr.avatar_url

                    # Send message

                    await self.client.send_message(message.channel, """```ini
[ID]            %s
[Username]      %s
[Discriminator] %s
[Nickname]      %s
[Current game]  %s
[Joined]        %s (%d days ago)
[Created]       %s (%d days ago)
[Avatar] %s```""" % (usr.id,
                     username,
                     discrim,
                     nickname,
                     game,
                     joined.strftime("%m/%d/%Y %I:%M:%S %p"),
                     max(0, joined_days.days),
                     created.strftime("%m/%d/%Y %I:%M:%S %p"),
                     max(0, created_days.days),
                     avatar))
                elif command == "serverinfo":
                    roles = [role.name for role in message.server.roles]

                    created = message.server.created_at
                    created_days = datetime.datetime.utcnow() - created
                    roles_string = ", ".join(roles)
                    region = message.server.region.name

                    await self.client.send_message(message.channel, """```ini
[Name]            %s
[ID]              %s
[User Count]      %s
[Channel Count]   %d
[Default Channel] #%s
[Role Count]      %d
[Roles]           %s
[Owner]           @%s
[Created]         %s (%d days ago)
[Icon] %s
```""" % (clear_formatting(message.server.name),
          message.server.id,
          message.server.member_count,
          len(message.server.channels),
          message.server.default_channel.name,
          len(roles),
          clear_formatting(roles_string),
          clear_formatting(str(message.server.owner)),
          created.strftime("%m/%d/%Y %I:%M:%S %p"),
          created_days.days,
          message.server.icon_url))
                elif command == "roll":
                    success = False
                    try:
                        map(int, arguments)
                        success = True
                    except ValueError:
                        await self.client.send_message(message.channel, "Please only enter integers. Thanks.")

                    if success:
                        output = "The 6-sided die rolled a %d." % random.randint(1, 6)

                        if len(arguments) == 2:
                            if arguments[1]:
                                sides = int(arguments[0])  # Set die sides
                                dice = int(arguments[1])  # Set # of dice to roll

                                if (dice < 1) or (sides < 1):  # check if # of dice/die sides is under 1
                                    output = "Yeah, sorry, but you can't roll something that doesn't exist."
                                elif sides == 1:
                                    output = "All %d of the 1-sided dice shockingly rolled a 1." % dice
                                elif dice <= 30:
                                    if sides <= 100:
                                        rolled_dice = ", ".join(
                                            [str(random.randint(1, sides)) for i in range(dice)])

                                        output = "The %d %d-sided dice rolled %s." % (dice, sides, rolled_dice)
                                    else:
                                        output = "Woahh, that's a lot of sides. Try lowering it below 100?"
                                else:
                                    output = "Woahh, that's a lot of dice to roll. Try lowering it below 30?"
                        elif len(arguments) == 1:
                            if arguments[0]:
                                sides = int(arguments[0])
                                if sides < 1:
                                    output = "Yeahh, sorry, but you can't roll something that doesn't exist."
                                elif sides == 1:
                                    output = "The 1-sided die shockingly rolled a 1."
                                else:
                                    output = "The %d-sided die rolled a %d." % (sides, random.randint(1, sides))

                                    # hey, you! yes, you, reading this! don't you dare tell people about these easter eggs! i will be watching...
                                    # What was that Noah? Did you say something?
                                    # No? I guess I just add these to the help menu...

                                    if sides == 666:
                                        output = "Satan rolled a nice %d for you." % random.randint(1, sides)
                                    elif sides == 1337:
                                        output = "Th3 %d-51d3d d13 r0ll3d 4 %d." % (sides, random.randint(1, sides))
                                    elif sides == message.server.member_count:
                                        await self.client.request_offline_members(message.server)

                                        members = list(message.server.members)
                                        members.sort(key=lambda x: x.joined_at)

                                        rnd_number = random.randint(0, len(members) - 1)
                                        rnd_user = members[rnd_number]
                                        output = "%d? That's how many users are on the server! Well, your die rolled a %d, and according to the cache, that member is `%s`." % (
                                            sides, rnd_number + 1, rnd_user.name)

                        await self.client.send_message(message.channel, output)
                elif command == "randomuser":
                    await self.client.request_offline_members(message.server)

                    members = list(message.server.members)
                    members.sort(key=lambda x: x.joined_at)

                    rnd_number = random.randint(0, message.server.member_count - 1)

                    try:
                        rnd_user = members[rnd_number]
                        rnd_number_str = str(rnd_number + 1)
                        if rnd_number_str[-1] == "1":
                            rnd_number_str += "ˢᵗ"
                        elif rnd_number_str[-1] == "2":
                            rnd_number_str += "ⁿᵈ"
                        elif rnd_number_str[-1] == "3":
                            rnd_number_str += "ʳᵈ"
                        else:
                            rnd_number_str += "ᵗʰ"

                        await self.client.send_message(message.channel,
                                                       "Your random user of the day is `%s`, who was the %s member to join the server." % (
                                                           rnd_user.name, rnd_number_str))
                    except Exception as error:
                        print("[ERROR] Something happened while running %s%s:" % (PREFIX, command))
                        traceback.print_exc()
                        if rnd_number > message.server.member_count:
                            await self.client.send_message(message.channel,
                                                           "Something happened while trying to grab information about user #%d, which seems to be bigger than the current user count (%d) - good job <@140564059417346049> (or maybe <@161508165672763392>?) \ud83d\udc4f" % (
                                                               rnd_number, message.server.member_count))
                        else:
                            await self.client.send_message(message.channel,
                                                           "Something happened while trying to grab information about user #%d." % rnd_number)
                            raise error

                elif command == "cat":
                    cat = self.get_json("http://random.cat/meow")
                    while cat["file"].split(".")[-1].lower() not in IMAGE_FORMATS:
                        cat = self.get_json("http://random.cat/meow")

                    await self.client.send_message(message.channel, cat["file"])
                elif command in ["dog", "adam"]:
                    dog = self.get_json("https://random.dog/woof.json")
                    while dog["url"].split(".")[-1].lower() not in IMAGE_FORMATS:
                        dog = self.get_json("https://random.dog/woof.json")
                    await self.client.send_message(message.channel, dog["url"])
                elif command in ["credits", "contributers"]:
                    await self.client.send_message(message.channel, "Original C# dev: Noahkiq#2928 \nPorted bot to python: Bottersnike#3605 (🍷) \nAlso trying to make Noah use python: hanss314#0128")

                # Debugging and development commands:
                elif command == "die" and is_developer:
                    raise ValueError("Test error.")
                elif command == "reload" and is_developer:
                    await self.client.send_message(message.channel, ":wave:")
                    self.reload_func()
                elif command == "debug" and is_developer:
                    roles = message.server.roles
                    roles.sort(key=lambda x: x.name)
                    rolestring = "Sever roles: "
                    rolestring += " | ".join([role.name for role in roles])
                    print(rolestring)

            is_HSTEM = False
            if message.server is not None:
                if message.server.id == HTSTEM_ID:
                    is_HSTEM = True

            if command == "yt" and (is_HSTEM or message.channel.is_private):
                if self.client.get_server(HTSTEM_ID).get_member(message.author.id) is None:
                    await self.client.send_message(message.channel,
                                              "You must be on HTwins STEM to use this command. " +
                                              "You can join it here: https://discord.gg/4Gn4GAC")

                elif len(arguments) == 1:
                    htstem = self.client.get_server(HTSTEM_ID)
                    member = htstem.get_member(message.author.id)
                    roles = htstem.roles
                    role = None
                    for r in roles:
                        if r.id == YT_ROLE_ID:
                            role = r

                    if arguments[0].lower() == "on":
                        await self.client.add_roles(member, role)
                        await self.client.send_message(message.channel,
                                                       "You have been given the YouTube notification role on HTwins STEM.")
                    elif arguments[0].lower() == "off":
                        await self.client.remove_roles(member, role)
                        await self.client.send_message(message.channel,
                                                       "You have been removed from the YouTube notification role on HTwins STEM.")
                    else:
                        await self.client.send_message(message.channel, "Proper usage: `%syt [on/off]`" % PREFIX)
                else:
                    await self.client.send_message(message.channel, "Proper usage: `%syt [on/off]`" % PREFIX)

        except Exception:
            trace_back = traceback.format_exc()
            print(trace_back)
            for user in DEVELOPERS_ERROR_PINGS:
                channel = await self.client.get_user_info(user)
                await self.client.send_message(channel,
                                               "The bot borked at {0}:\nCommand:\n```\n{1}```\nError:\n```py\n{2}```".format(datetime.datetime.now(),
                                                                                                         message.content,
                                                                                                         clear_formatting(
                                                                                                         trace_back)))
            print("Error message DMs sent!")

    def levenshtein(self, s1, s2):
        if len(s1) < len(s2):
            return self.levenshtein(s2, s1)

        # len(s1) >= len(s2)
        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[
                                 j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]

    @staticmethod
    def get_json(urlstring):
        with urllib.request.urlopen(urlstring) as url:
            data = json.loads(url.read().decode())
            return data

    async def cary_video_checker(self):
        await asyncio.sleep(10)

        if not os.path.exists("videoURLS.txt"):
            open("videoURLS.txt", "w").close()

        feed = feedparser.parse(CARY_YT_URL)
        videos = feed["entries"]

        urls = open("videoURLS.txt").read().split("\n")

        for v in videos:
            href = v["link"]
            if href not in urls:
                title = v["title"]
                print("New video: %s - %s" % (title, href))
                channel = self.client.get_channel(VIDEO_ANNOUNCE_CHANNEL)
                await self.client.send_message(channel,
                                               "@here `carykh` has uploaded a new YouTube video!\n\"%s\" - %s" % (
                                                   title, href))
                urls.append(href)

        f = open("videoURLS.txt", "w")
        f.write("\n".join(urls))
        f.close()

