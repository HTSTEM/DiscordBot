import discord
import random

prefix = "c!"

debug = False #set false for normal use

if debug:
    guild_id = 297811083308171264
    owner_id = [240995021208289280]

else:
    guild_id = 282219466589208576
    owner_id = [
        140564059417346049,
        161508165672763392,
        240995021208289280,
        210907256068374529,
        136374601788686336,
        136611352692129792,
        186553034439000064,
        164152700496379904,
        100764870617624576
    ]


class Colors:

    def __init__(self, bot):
        self.bot = bot

    async def on_message(self, message):
        if (not message.content.startswith(prefix)) or message.content.startswith(prefix+prefix):
            return

        command = message.content.split(' ')[0][len(prefix):].lower()

        htc = self.bot.get_guild(guild_id)
        bot = htc.me
        inHTC = (htc.get_member(message.author.id) != None)
        isOwner = message.author.id in owner_id
        roles = htc.roles
        teams = []

        for role in roles:
            if role.name.startswith("color_"):
                teams.append(role)

        if isOwner:
            if command == "permcheck":
                hasPerm = bot.guild_permissions.manage_roles
                if not hasPerm:
                    print("**Alert:** The bot does not have permission to manage roles.")
                else:
                    print("The bot currently has permission to manage roles.")

            if command == "colorstats":
                if htc.large: await self.bot.request_offline_members(htc)
                d = "--- FLAIR STATS ---\n"
                for role in teams:
                    d += '**{}**: {}\n'.format(role.name, self.get_role_count(role, htc))

                d += "--- END STATS ---"
                print(d)
                await message.channel.send(d)

        if (command == "help" and (isinstance(message.channel, discord.abc.PrivateChannel) or message.guild.id == guild_id)):
            names = ['`{}{}`'.format(prefix, role.name.replace('color_', '')) for role in teams]
            if len(names) > 1:
                names[-1] = 'or {}'.format(names[-1])
            await message.channel.send(
                'To Color™ yourself, say {0}. To Un-Color™, say `{1}remove`. To get a Random™ Color™, use `{1}random`.'.format(', '.join(names),prefix)
            )

        if (command == "list" and (isinstance(message.channel, discord.abc.PrivateChannel) or message.guild.id == guild_id)):
            await message.channel.send(
                'Here\'s an image showing all the available Colors™: <https://i.imgur.com/SIPaKUM.png>'
            )

        try:
            if (inHTC and (isinstance(message.channel, discord.abc.PrivateChannel) or message.guild.id == guild_id)):
                user = htc.get_member(message.author.id)

                if command == "remove":
                    removed = False
                    for role in teams:
                        if role in user.roles:
                            removed = True
                            await user.remove_roles(role)


                    if removed:  d = "You have successfully been Un-Colored™."
                    else: d = "You aren't Colored™!"

                    if isinstance(message.channel, discord.abc.PrivateChannel):
                        await message.channel.send(d)
                    else:
                        await message.channel.send(d, delete_after=5)

                        try: await message.delete()
                        except discord.Forbidden: pass

                elif command == "random":
                    for role in teams:
                        if role in user.roles:
                            await user.remove_roles(role)

                    team = random.choice(teams)
                    await user.add_roles(team)

                    if isinstance(message.channel, discord.abc.PrivateChannel):
                        await message.channel.send("Your Color™ is now {}.".format(team.name))
                    else:
                        await message.channel.send(
                            "Your Color™ is now {}.".format(team.name),
                            delete_after=5
                        )
                        try: await message.delete()
                        except: pass


                else:
                    if command in [role.name.replace('color_', '') for role in teams]:
                        for role in teams:
                            if role in user.roles:
                                await user.remove_roles(role)


                        team = discord.utils.get(teams,name="color_{}".format(command))
                        await user.add_roles(team)

                        if isinstance(message.channel, discord.abc.PrivateChannel):
                            await message.channel.send("Your Color™ is now {}.".format(team.name))
                        else:
                            await message.channel.send(
                                "Your Color™ is now {}.".format(team.name),
                                delete_after=5
                            )
                            try: await message.delete()
                            except: pass


        except Exception as e:
            if debug:
                raise e
            else:
                print("[ERROR] A Color™-crashing error occured somewhere in the code.")

    @staticmethod
    def get_role_count(role_name, guild):
        team = discord.utils.get(guild.roles,name=role_name)
        count = len(
                    list(
                        filter(
                            lambda x:team in x.roles,
                            guild.members
                        )
                    )
                )
        return count


def setup(bot):
    bot.add_cog(Colors(bot))
