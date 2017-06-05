import traceback
import discord
import asyncio
import datetime
import os

# Good enough
BOTE_SPAM = ["282500390891683841", "290757101914030080"]

# Real
HTC_ID = "184755239952318464"  # "290573725366091787"
HTSTEM_ID = "290573725366091787"  # "2282219466589208576"
HTC_LOG = "207659596167249920"  # "319830765842071563"
HTC_BACKUP = "303374467336241152"  # "319830765842071563"
HTSTEM_LOG = "282477076454309888"  # "319830765842071563"
HTSTEM_BACKUP = "303374407420608513"  # "319830765842071563"

SOME_SERVER = "303365979444871169"  # "290573725366091787"
SOME_SERVER_LOG = "303530104339038209"  # "319830765842071563"

OWNER_ID = "140564059417346049"  # "161508165672763392"

PREFIX = "!"
CLIENTS = []


def clear_formatting(inp):
    if not inp.isspace():
        op = inp.replace("`", "​`").replace("*", "​*").replace("_", "​_")  # .replace("", " ")
    else:
        op = "[empty string]"

    return op


def message_increment(botnum, user, sid):
    botstring = "bot-" + str(botnum)
    path = os.path.join(os.getcwd(), botstring, str(sid), str(datetime.datetime.now().month))
    datafile = os.path.join(path, str(user.id) + ".txt")

    if not os.path.exists(path):
        os.makedirs(path)

    if os.path.exists(datafile):
        d = open(datafile).read()

        if d:
            line = d.split("\n")[0]
            try:
                messages = int(line)
            except ValueError:
                messages = 0

            messages += 1
            f = open(datafile, "wb")
            f.write(("%d\n%s" % (messages, clear_formatting(user.name))).encode("utf-8"))
            f.close()
        else:
            f = open(datafile, "wb")
            f.write(("1\n%s" % clear_formatting(user.name)).encode("utf-8"))
            f.close()
    else:
        f = open(datafile, "wb")
        f.write(("1\n%s" % clear_formatting(user.name)).encode("utf-8"))
        f.close()


def message_decrement(botnum, user, sid):
    botstring = "bot-" + str(botnum)
    path = os.path.join(os.getcwd(), botstring, str(sid), str(datetime.datetime.now().month))
    datafile = os.path.join(path, str(user.id) + ".txt")

    if not os.path.exists(path):
        os.makedirs(path)

    if os.path.exists(datafile):
        d = open(datafile).read()

        if not d:
            line = d.split("\n")[0]
            try:
                messages = int(line)
            except ValueError:
                messages = 0

            messages -= 1
            f = open(datafile, "wb")
            f.write(("%d\n%s" % (messages, clear_formatting(user.name))).encode("utf-8"))
            f.close()
        else:
            f = open(datafile, "wb")
            f.write(("1\n%s" % clear_formatting(user.name)).encode("utf-8"))
            f.close()
    else:
        f = open(datafile, "wb")
        f.write(("1\n%s" % clear_formatting(user.name)).encode("utf-8"))
        f.close()


def message_top(botnum, sid, number_of_users):
    botstring = "bot-" + str(botnum)
    path = os.path.join(os.getcwd(), botstring, str(sid), str(datetime.datetime.now().month))

    if not os.path.exists(path):
        os.makedirs(path)

    files = os.listdir(path)
    message_counts = []
    for filename in files:
        try:
            filepath = filename
            if botstring not in filename:
                filepath = os.path.join(path, filename)

            messages_string = open(filepath).read().split("\n")[0]
            username = open(filepath).read().split("\n")[1]

            try:
                activecount = int(messages_string)
                message_counts.append((str(username), activecount))
            except ValueError:
                pass

        except:
            print("something bad happened while trying to grab/write info about a user during messagetop:")
            traceback.print_exc()

    filtered = message_counts
    filtered.sort(key=lambda x: x[1], reverse=True)
    filtered = filtered[:number_of_users]
    topusers = ""
    for i in filtered:
        topusers += "%s: %s\n" % i

    return topusers


class Bot:
    def __init__(self, token, botnum):
        self.client = discord.Client()
        self.botnum = botnum
        self.banneduser = ""

        @self.client.event
        async def on_ready():
            print("Logged in as:")
            print(self.client.user.name)
            print(self.client.user.id)
            print("======")

        @self.client.event
        async def on_message(message):
            try:
                if not (self.botnum == 2 and message.server.id == HTSTEM_ID):
                    msg = message.content
                    cmd = msg.replace(PREFIX, "").split(' ')
                    if len(cmd) == 0:
                        cmd = ""
                    else:
                        cmd = cmd[0].lower()
                    args = msg.replace(PREFIX, "").split(' ')[1:]
                    rawargs = msg[len(PREFIX) + len(cmd):]
                    is_cmd = msg.startswith(PREFIX)
                    is_bot = message.author.bot
                    is_self = message.author.id == self.client.user.id
                    is_bot_spam = message.channel.id in BOTE_SPAM
                    is_music = "music" in message.channel.name
                    is_joinbot = "joinbot" in message.channel.name

                    shouldnt_log = is_cmd or is_bot_spam or is_bot or is_self or is_music or is_joinbot

                    if not shouldnt_log:
                        message_increment(self.botnum, message.author, message.server.id)

                    htc = self.client.get_server(HTC_ID)
                    user = message.author

                    if not message.channel.is_private:
                        serv = message.server
                        bot = serv.get_member(self.client.user.id)
                        owner = serv.get_member(OWNER_ID)

                        is_owner = False
                        if owner is not None:
                            if message.author == owner:
                                is_owner = True
                        if (is_owner or "joinbot" in message.channel.name) and cmd == "userinfo":
                            await self.client.request_offline_members(message.server)

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
                     joined_days.days,
                     created.strftime("%m/%d/%Y %I:%M:%S %p"),
                     created_days.days,
                     avatar)
                                                           )

                        elif cmd == "topusers" and is_owner:
                            if len(args) == 0:
                                if message_top(self.botnum, message.server.id, 10):
                                    await self.client.send_message(message.channel,
                                                                   message_top(self.botnum, message.server.id, 10))
                            else:
                                try:
                                    users = int(args[0])
                                except ValueError:
                                    users = 10

                                topusers = "idk something borked"

                                if users > 20 and not is_owner:
                                    await self.client.send_message(message.channel, "woah, keep it under 20 will ya?")
                                else:
                                    topusers = message_top(self.botnum, message.server.id, users)

                                await self.client.send_message(message.channel, topusers)

                        elif is_owner and "music" not in message.channel.name and (
                                cmd == "restart" or cmd == "shutdown"):
                            await self.client.send_message(message.channel, "Restarting bot...")
                            print("Restarting bot...")

                            await self.client.close()
                            await self.client.logout()
                            quit()

                        # semi-public commands

                        if message.content == "!gameupdate":
                            await self.client.change_presence(game=discord.Game(name="for " + str(htc.member_count) + " users"))

                        if (is_owner or message.author.server_permissions.manage_roles) and (
                            message.content == "!usercount"):
                            await self.client.send_message(message.channel, "%s currently has %s users." % (
                            message.server.name, message.server.member_count))

            except:
                print("[ERROR] An issue occured while trying to send out a message.")
                traceback.print_exc()

        @self.client.event
        async def on_message_delete(message):
            if not (self.botnum == 2 and message.server.id == HTSTEM_ID):
                msg = message.content
                cmd = msg.replace(PREFIX, "").split(' ')
                if len(cmd) == 0:
                    cmd = ""
                else:
                    cmd = cmd[0].lower()
                args = msg.replace(PREFIX, "").split(' ')[1:]
                rawargs = msg[len(PREFIX) + len(cmd):]
                is_cmd = msg.startswith(PREFIX)
                is_bot = message.author.bot
                is_self = message.author.id == self.client.user.id
                is_bot_spam = message.channel.id in BOTE_SPAM
                is_music = "music" in message.channel.name
                is_joinbot = "joinbot" in message.channel.name

                shouldnt_log = is_cmd or is_bot_spam or is_bot or is_self or is_music or is_joinbot

                if not shouldnt_log:
                    message_decrement(self.botnum, message.author, message.server.id)

        @self.client.event
        async def on_member_join(member):
            if member.server.id == HTC_ID:
                self.client.change_presence(game=discord.Game(name="for %d users" % member.server.member_count))

            time_now = datetime.datetime.now()

            print("[%s - Bot #%d] A user joined %s: %s#%s (%s)" % (
                time_now.strftime("%m/%d - %H:%M:%S"), self.botnum, member.server.name, member.name,
                member.discriminator,
                member.id))

            log_channel = None
            backup_channel = None
            valid_channel = False

            if not (self.botnum == 2 and member.server.id == HTSTEM_ID):
                log_channel = None
                for channel in member.server.channels:
                    if channel.name == "joinbot":
                        log_channel = channel

            if log_channel is not None:
                valid_channel = True

            if member.server.id == HTC_ID:
                log_channel = self.client.get_channel(HTC_LOG)
                backup_channel = self.client.get_channel(HTC_BACKUP)
            elif member.server.id == HTSTEM_ID and self.botnum != 2:
                log_channel = self.client.get_channel(HTSTEM_LOG)
                backup_channel = self.client.get_channel(HTSTEM_BACKUP)

            discrim = str(member.discriminator).zfill(4)

            if len(discrim) == 0:
                discrim = " [Something has gone horribly wrong and the user doesn't have a discriminator. " + \
                          "Please inform Noahkiq of this, thanks!]"

            msg = "✅ %s (`%s#%s` User #%s) user joined the server." % (
                member.mention, member.name, discrim, member.server.member_count)
            if member.avatar_url.isspace():
                msg += "\n😶 User doesn't have an avatar."

            try:
                creation_time = member.created_at
                time_diff = time_now - creation_time

                if time_diff.total_seconds() / 3600 <= 24:
                    msg += "\n🕐 User's account was created at " + creation_time.strftime("%m/%d/%Y %I:%M:%S %p")
                else:
                    msg += "\nUser's account was created at " + creation_time.strftime("%m/%d/%Y %I:%M:%S %p")
            except Exception:
                print("[NoahError(tm)] something happened while tryin to do the timestamp grabby thing:")
                traceback.print_exc()

            try:
                if valid_channel:
                    await self.client.send_message(log_channel, msg)
                if backup_channel is not None:
                    await self.client.send_message(backup_channel, msg)
                if member.server.id == SOME_SERVER:
                    await self.client.send_message(member.server.get_channel(SOME_SERVER_LOG), msg)
            except Exception:
                print("[ERROR] An issue occured while trying to send out a message.")
                traceback.print_exc()

        @self.client.event
        async def on_member_remove(member):
            if member.server.id == HTC_ID:
                self.client.change_status(game="for %d users" % member.server.member_count)
            await asyncio.sleep(0.25)
            is_banned = member.id == self.banneduser

            if not is_banned:
                time_now = datetime.datetime.now()
                print("[%s - Bot #%d] A user left %s: %s#%s (%s)" % (
                    time_now.strftime("%m/%d - %H:%M:%S"), self.botnum, member.server.name, member.name,
                    member.discriminator, member.id))

                log_channel = None
                backup_channel = None
                valid_channel = False

                if not (self.botnum == 2 and member.server.id == HTSTEM_ID):
                    log_channel = None
                    for channel in member.server.channels:
                        if channel.name == "joinbot":
                            log_channel = channel

                if log_channel is not None:
                    valid_channel = True

                if member.server.id == HTC_ID:
                    log_channel = self.client.get_channel(HTC_LOG)
                    backup_channel = self.client.get_channel(HTC_BACKUP)
                elif member.server.id == HTSTEM_ID and self.botnum != 2:
                    log_channel = self.client.get_channel(HTSTEM_LOG)
                    backup_channel = self.client.get_channel(HTSTEM_BACKUP)

                discrim = str(member.discriminator).zfill(4)

                if len(discrim) == 0:
                    discrim = " [Something has gone horribly wrong and the user doesn't have a discriminator. " + \
                              "Please inform Noahkiq of this, thanks!]"

                try:
                    msg = "❌ %s (`%s#%s`) left the server." % (member.mention, member.name, discrim)

                    if valid_channel:
                        await self.client.send_message(log_channel, msg)
                    if backup_channel is not None:
                        await self.client.send_message(backup_channel, msg)
                    if member.server.id == SOME_SERVER:
                        await self.client.send_message(member.server.get_channel(SOME_SERVER_LOG), msg)
                except Exception:
                    print("[ERROR] An issue occured while trying to send out a message.")
                    traceback.print_exc()

        @self.client.event
        async def on_member_ban(member):
            self.banneduser = member.id

            time_now = datetime.datetime.now()
            print("[%s - Bot #%d]  A user was banned from %s: %s#%s (%s)" % (
                time_now.strftime("%m/%d - %H:%M:%S"), self.botnum, member.server.name, member.name,
                member.discriminator, member.id))

            log_channel = None
            backup_channel = None
            valid_channel = False

            if not (self.botnum == 2 and member.server.id == HTSTEM_ID):
                log_channel = None
                for channel in member.server.channels:
                    if channel.name == "joinbot":
                        log_channel = channel

            if log_channel is not None:
                valid_channel = True

            if member.server.id == HTC_ID:
                log_channel = self.client.get_channel(HTC_LOG)
                backup_channel = self.client.get_channel(HTC_BACKUP)
            elif member.server.id == HTSTEM_ID and self.botnum != 2:
                log_channel = self.client.get_channel(HTSTEM_LOG)
                backup_channel = self.client.get_channel(HTSTEM_BACKUP)

            discrim = str(member.discriminator).zfill(4)

            if len(discrim) == 0:
                discrim = " [Something has gone horribly wrong and the user doesn't have a discriminator. " + \
                          "Please inform Noahkiq of this, thanks!]"

            try:
                msg = "🔨 %s (`%s#%s`) was banned from the server." % (member.mention, member.name, discrim)

                if valid_channel:
                    await self.client.send_message(log_channel, msg)
                if backup_channel is not None:
                    await self.client.send_message(backup_channel, msg)
                if member.server.id == SOME_SERVER:
                    await self.client.send_message(member.server.get_channel(SOME_SERVER_LOG), msg)
            except Exception:
                print("[ERROR] An issue occured while trying to send out a message.")
                traceback.print_exc()

        @self.client.event
        async def on_member_unban(server, member):
            time_now = datetime.datetime.now()
            print("[%s - Bot #%d]  A user was unbanned from %s: %s#%s (%s)" % (
                time_now.strftime("%m/%d - %H:%M:%S"), self.botnum, server.name, member.name,
                member.discriminator, member.id))

            log_channel = None
            backup_channel = None
            valid_channel = False

            if not (self.botnum == 2 and server.id == HTSTEM_ID):
                log_channel = None
                for channel in server.channels:
                    if channel.name == "joinbot":
                        log_channel = channel

            if server.id == HTC_ID:
                log_channel = self.client.get_channel(HTC_LOG)
                backup_channel = self.client.get_channel(HTC_BACKUP)
            elif server.id == HTSTEM_ID and self.botnum != 2:
                log_channel = self.client.get_channel(HTSTEM_LOG)
                backup_channel = self.client.get_channel(HTSTEM_BACKUP)

            if log_channel is not None:
                valid_channel = True

            discrim = str(member.discriminator).zfill(4)

            if len(discrim) == 0:
                discrim = " [Something has gone horribly wrong and the user doesn't have a discriminator. " + \
                          "Please inform Noahkiq of this, thanks!]"

            try:
                msg = "🔓 %s (`%s#%s`) was unbanned from the server." % (member.mention, member.name, discrim)

                if valid_channel:
                    await self.client.send_message(log_channel, msg)
                if backup_channel is not None:
                    await self.client.send_message(backup_channel, msg)
                if server.id == SOME_SERVER:
                    await self.client.send_message(member.server.get_channel(SOME_SERVER_LOG), msg)
            except Exception:
                print("[ERROR] An issue occured while trying to send out a message.")
                traceback.print_exc()

        @self.client.event
        async def on_member_update(before, after):
            if before.name != after.name:
                time_now = datetime.datetime.now()
                print("[%s - Bot #%d] A user (%s) changed their name from %s#%s to %s#%s" % (
                    time_now.strftime("%m/%d - %H:%M:%S"), self.botnum, before.id, before.name,
                    before.discriminator, after.name, after.discriminator))

                log_channel = None
                backup_channel = None
                valid_channel = False

                if not (self.botnum == 2 and before.server.id == HTSTEM_ID):
                    log_channel = None
                    for channel in before.server.channels:
                        if channel.name == "joinbot":
                            log_channel = channel

                if log_channel is not None:
                    valid_channel = True

                if before.server.id == HTC_ID:
                    log_channel = self.client.get_channel(HTC_LOG)
                    backup_channel = self.client.get_channel(HTC_BACKUP)
                elif before.server.id == HTSTEM_ID and self.botnum != 2:
                    log_channel = self.client.get_channel(HTSTEM_LOG)
                    backup_channel = self.client.get_channel(HTSTEM_BACKUP)

                old_discrim = str(before.discriminator).zfill(4)

                if len(old_discrim) == 0:
                    old_discrim = " [Something has gone horribly wrong and the user doesn't have a discriminator. " + \
                                  "Please inform Noahkiq of this, thanks!]"

                new_discrim = str(after.discriminator).zfill(4)

                if len(new_discrim) == 0:
                    new_discrim = " [Something has gone horribly wrong and the user doesn't have a discriminator. " + \
                                  "Please inform Noahkiq of this, thanks!]"

                msg = "User **%s#%s** changed their name to **%s#%s** (%s)" % (before.name, old_discrim,
                                                                               after.name, new_discrim, after.mention)
                if old_discrim != new_discrim:
                    msg += "\n🔁 *User's discriminator changed!*"

                try:
                    if valid_channel:
                        await self.client.send_message(log_channel, msg)
                    if backup_channel is not None:
                        await self.client.send_message(backup_channel, msg)
                except Exception:
                    print("[ERROR] An issue occured while trying to send out a message.")
                    traceback.print_exc()
            elif (before.avatar_url != after.avatar_url) and (
                    before.server.id == HTC_ID or before.server.id == HTSTEM_ID):
                time_now = datetime.datetime.now()
                print("[%s - Bot #%d] %s#%s (%s) changed their avatar from %s to %s" % (
                    time_now.strftime("%m/%d - %H:%M:%S"), self.botnum, after.name, after.discriminator,
                    after.id, before.avatar_url, after.avatar_url))

                log_channel = None
                valid_channel = False

                if not (self.botnum == 2 and before.server.id == HTSTEM_ID):
                    log_channel = None
                    for channel in before.server.channels:
                        if channel.name == "joinbot":
                            log_channel = channel

                if log_channel is not None:
                    valid_channel = True

                if before.server.id == HTC_ID:
                    log_channel = self.client.get_channel("305337536157450240")
                else:
                    log_channel = self.client.get_channel("305337565513515008")

                discrim = str(after.discriminator).zfill(4)

                if len(discrim) == 0:
                    discrim = " [Something has gone horribly wrong and the user doesn't have a discriminator. " + \
                              "Please inform Noahkiq of this, thanks!]"

                msg = "<:bookFace:310922953791504384> User **%s#%s** changed their avatar from %s to %s (%s)" % (
                    after.name, discrim, before.avatar_url, after.avatar_url, after.mention
                )

                try:
                    await self.client.send_message(log_channel, msg)
                except Exception:
                    print("[ERROR] An issue occured while trying to send out a message.")
                    traceback.print_exc()

        if botnum == 1:
            c = self.client.start(token)
            CLIENTS.append(c)
        else:
            for c in CLIENTS:
                self.client.loop.create_task(c)
            self.client.run(token)


Bot(open("bot-token.txt").read().split("\n")[0], 1)
Bot(open("bot-token.txt").read().split("\n")[1], 2)
