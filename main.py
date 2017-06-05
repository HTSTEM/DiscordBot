import traceback
import discord
import asyncio
import random
import datetime
import os
import urllib.request
import json
import feedparser


client = discord.Client()

PREFIX = "sb?"
OWNER_ID = "140564059417346049"  # "161508165672763392" <- Bottersnike's ID for testing
HTSTEM_ID = "282219466589208576"  # "290573725366091787" <- Bottersnike's ID for tesing
YT_ROLE_ID = "289942717419749377"  # "320939806530076673" <- Bottersnike's ID for testing
BOTE_SPAM = ["282500390891683841", "290757101914030080", "229595785346416640"]  # I can't remember which is which, but this is:
# HTSTEM #bote-spam
# Bottersnike Bot Testing #bot-testing
# Noah's chill lounge #bot-spam
CARY_YT_URL = "https://www.youtube.com/feeds/videos.xml?user=carykh"
VIDEO_ANNOUNCE_CHANNEL = "282225245761306624"  # "290757101914030080" <- Bottersnike's ID for testing


def clear_formatting(inp):
    if not inp.isspace():
        op = inp.replace("`", "​`").replace("*", "​*").replace("_", "​_")  # .replace("", " ")
    else:
        op = "[empty string]"

    return op


def get_json(urlstring):
    with urllib.request.urlopen(urlstring) as url:
        data = json.loads(url.read().decode())
        return data


async def cary_video_checker():
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
            channel = client.get_channel(VIDEO_ANNOUNCE_CHANNEL)
            await client.send_message(channel, "@here `carykh` has uploaded a new YouTube video!\n\"%s\" - %s" % (title, href))
            urls.append(href)

    f = open("videoURLS.txt", "w")
    f.write("\n".join(urls))
    f.close()


@client.event
async def on_message(message):
    is_cmd = False
    if message.content.lower().startswith(PREFIX + PREFIX):
        is_cmd = False
    elif message.content.lower().startswith(PREFIX):
        is_cmd = True

    is_owner = message.author.id == OWNER_ID
    msg = message.content
    msgarray = msg[len(PREFIX):].split(" ")

    if len(msgarray) == 0:
        cmd = ""
    else:
        cmd = msgarray[0].lower()
    args = msgarray[1:]
    argtext = msg[len(PREFIX) + len(cmd):]
    while argtext.startswith(" "):
        argtext = argtext[1:]

    if not message.channel.is_private:
        if is_cmd and message.channel.id in BOTE_SPAM:
            if cmd == "help":
                help = "`%shelp` - lists the bot commands" % PREFIX
                usercount = "`%susercount` - lists the users on the server" % PREFIX  # note: this command won't work unless joinbot is running
                userinfo = "`%suserinfo` - displays info about yourself or a mentioned user" % PREFIX
                serverinfo = "`%sserverinfo` - displays info about the server" % PREFIX
                roll = "`%sroll [# of sides] [# of dice to roll]` - rolls some dice" % PREFIX
                cat = "`%scat` - gimme some o' dem cute cat pix" % PREFIX
                dog = "`%sdog` - gimme dem cute dogs" % PREFIX
                randomuser = "`%srandomuser` - selects a random user on the server" % PREFIX
                creduts - "`%scredits` - lists the users who have worked on the bot" % PREFIX

                yt = "`%syt [on/off]` - turn YT video notifications on/off" % PREFIX

                cmds = "\n".join([help, usercount, userinfo, serverinfo, roll, randomuser, cat, dog])
                greet = "Hi! I'm the STEM part of the HTC-Bote, a super-exclusive part only for the HTwins STEM server. "
                avacmds = "I have a couple commands you can try out, which include: \n%s\nI also have some commands for use in private messages: \n%s" % (
                    cmds, yt)

                helpmsg = greet + avacmds
                await client.send_message(message.channel, helpmsg)

            elif cmd == "usercount":
                await client.send_message(message.channel, "`%s` currently has %d users." % (
                    message.server.name, message.server.member_count))
            elif cmd == "userinfo":
                # users = message.server.members.sort(key=lambda x:x.joined_at)

                # Find user

                if len(message.mentions) > 0:  # Is there a mention?
                    usr = message.mentions[0]
                else:  # No? Just use the message author
                    usr = message.author

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
                joined_days = datetime.datetime.now() - joined
                created = usr.created_at
                created_days = datetime.datetime.now() - created
                avatar = usr.avatar_url

                # Send message

                await client.send_message(message.channel, """```ini
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
                     joined_days.days,
                     created.strftime("%m/%d/%Y %I:%M:%S %p"),
                     created_days.days,
                     avatar)
                                          )

            elif cmd == "serverinfo":
                roles = [role.name for role in message.server.roles]

                created = message.server.created_at
                created_days = datetime.datetime.now() - created
                roles_string = ", ".join(roles)
                region = message.server.region.name

                await client.send_message(message.channel, """```ini
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

            elif cmd == "roll":
                try:
                    output = "The 6-sided die rolled a %d." % random.randint(1, 6)

                    if len(args) == 2:
                        if args[1]:
                            sides = int(args[0])  # Set die sides
                            dice = int(args[1])  # Set # of dice to roll
                            max_rolls = sides + 1  # Set max roll int

                            if (dice < 1) or (sides < 1):  # check if # of dice/die sides is under 1
                                output = "Yeah, sorry, but you can't roll something that doesn't exist."
                            elif sides == 1:
                                output = "All %d of the 1-sided dice shockingly rolled a 1." % dice
                            elif dice <= 30:
                                if sides <= 100:
                                    rolled_dice = ", ".join([str(random.randint(1, sides)) for i in range(dice)])

                                    output = "The %d %d-sided dice rolled %s." % (dice, sides, rolled_dice)
                                else:
                                    output = "Woahh, that's a lot of sides. Try lowering it below 100?"
                            else:
                                output = "Woahh, that's a lot of dice to roll. Try lowering it below 30?"
                    elif len(args) == 1:
                        if args[0]:
                            sides = int(args[0])
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
                                    await client.request_offline_members(message.server)

                                    members = list(message.server.members)
                                    members.sort(key=lambda x: x.joined_at)

                                    rnd_number = random.randint(0, len(members) - 1)
                                    rnd_user = members[rnd_number]
                                    output = "%d? That's how many users are on the server! Well, your die rolled a %d, and according to the cache, that member is `%s`." % (
                                        sides, rnd_number + 1, rnd_user.name)

                    await client.send_message(message.channel, output)
                except Exception as error:
                    print("[ERROR] Something happened while running %s%s:" % (PREFIX, cmd))
                    traceback.print_exc()
                    await client.send_message(message.channel,
                                              "An error occured while trying to roll the dice. You most likely entered non-integers.")

            elif cmd == "randomuser":
                await client.request_offline_members(message.server)

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

                    await client.send_message(message.channel, "Your random user of the day is `%s`, who was the %s member to join the server." % (rnd_user.name, rnd_number_str))
                except Exception as error:
                    print("[ERROR] Something happened while running %s%s:" % (PREFIX, cmd))
                    traceback.print_exc()
                    if rnd_number > message.server.member_count:
                        await client.send_message(message.channel, "Something happened while trying to grab information about user #%d, which seems to be bigger than the current user count (%d) - good job <@140564059417346049> (or maybe <@161508165672763392>?) \ud83d\udc4f" % (rnd_number, message.server.member_count));
                    else:
                        await client.send_message(message.channel, "Something happened while trying to grab information about user #%d." % rnd_number)

            elif cmd == "cat":
                cat = get_json("http://random.cat/meow")
                await client.send_message(message.channel, cat["file"])
            elif cmd in ["dog", "adam"]:
                dog = get_json("https://random.dog/woof.json")
                await client.send_message(message.channel, dog["url"])
            elif cmd in ["credits", "contributers"]:
                await client.send_message(message.channel, "Original C# dev: Noahkiq#2928 \nPorted bot to python: Bottersnike#3605 (🍷) \nAlso trying to make Noah use python: hanss314#0128")
            elif cmd == "debug" and is_owner:
                roles = message.server.roles
                roles.sort(key=lambda x:x.name)
                rolestring = "Sever roles: "
                rolestring += " | ".join([role.name for role in roles])
                print(rolestring)

    is_HSTEM = False
    if message.server is not None:
        if message.server.id == HTSTEM_ID:
            is_HSTEM = True

    if cmd == "yt" and (is_HSTEM or message.channel.is_private):
        if client.get_server(HTSTEM_ID).get_member(message.author.id) is None:
            await client.send_message(message.channel,
                                      "You must be on HTwins STEM to use this command. " +
                                      "You can join it here: https://discord.gg/4Gn4GAC")

        elif len(args) == 1:
            hstem = client.get_server(HTSTEM_ID)
            huser = hstem.get_member(message.author.id)
            roles = hstem.roles
            role = None
            for r in roles:
                if r.id == YT_ROLE_ID:
                    role = r

            if args[0].lower() == "on":
                await client.add_roles(huser, role)
                await client.send_message(message.channel,
                                          "You have been given the YouTube notification role on HTwins STEM.")
            elif args[0].lower() == "off":
                await client.remove_roles(huser, role)
                await client.send_message(message.channel,
                                          "You have been removed from the YouTube notification role on HTwins STEM.")
            else:
                await client.send_message(message.channel, "Proper usage: `{p}yt [on/off]`")
        else:
            await client.send_message(message.channel, "Proper usage: `{p}yt [on/off]`")


@client.event
async def on_ready():
    print("Logged in as:")
    print(client.user.name)
    print(client.user.id)
    print("======")


@client.event
async def on_member_join(member):
   pass


@client.event
async def on_member_remove(member):
    pass


client.loop.create_task(cary_video_checker())
client.run(open("bot-token.txt").read().split("\n")[0])
