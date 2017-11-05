import discord

prefix = "!"
flairs = {  # (role_name, twower/command name)
    'meester': '#TeamMeester',
    'midnight': '#TeamMidnight',
    'yessoan': '#TeamYessoan'
}

debug = False  # set false for normal use

if debug:
    guild_id = 297811083308171264
    owner_id = [240995021208289280]

else:
    guild_id = 184755239952318464
    owner_id = [
        140564059417346049,
        149313154512322560,
        98569889437990912,
        154825973278310400,
        185164223259607040,
        127373929600778240,
        184884413664854016,
        164379304879194112,
        184079890373541889,
        110461599176724480
    ]


class Flairs:
    def __init__(self, bot):
        self.bot = bot

    async def on_message(self, message):
        if (not message.content.startswith(prefix)) or message.content.startswith(prefix + prefix):
            return

        command = message.content.split(' ')[0][len(prefix):].lower()

        htc = self.bot.get_guild(guild_id)
        bot = htc.get_member(self.bot.user.id)
        inHTC = (htc.get_member(message.author.id) != None)
        isOwner = message.author.id in owner_id

        if isOwner:
            if command == "permcheck":
                hasPerm = bot.guild_permissions.manage_roles
                if not hasPerm:
                    print("**Alert:** The bot does not have permission to manage roles.")
                else:
                    print("The bot currently has permission to manage roles.")

            if command == "teamstats":
                if htc.large: await self.bot.request_offline_members(htc)
                d = "--- FLAIR STATS ---\n"
                for name, role in flairs.items():
                    d += '**{}**: {}\n'.format(name.title(), self.get_role_count(role, htc))

                d += "--- END STATS ---"
                print(d)
                await message.channel.send(d)

        if (command == "help" and (isinstance(message.channel, discord.abc.PrivateChannel) or
           (message.guild.id == guild_id and message.channel.name != "music"))):
            names = ['`{}{}`'.format(prefix, name.lower()) for name in flairs.keys()]
            if len(names) > 1:
                names[-1] = 'or {}'.format(names[-1])
            await message.channel.send(
                'To join a team, say {}. To leave your team, say `!remove`'.format(', '.join(names))
            )

        try:
            if (command != "help" and (isinstance(message.channel, discord.abc.PrivateChannel) or
               (message.guild.id == guild_id and message.channel.name not in ["music", "serious"]))):
                user = htc.get_member(message.author.id)
                roles = htc.roles
                teams = []

                for role in roles:
                    if role.name.startswith("#Team"):
                        teams.append(role)

                if command == "remove":
                    removed = False
                    for role in teams:
                        if role in user.roles:
                            removed = True
                            await user.remove_roles(role)

                    if removed:
                        d = "You have successfully been removed from your team."
                    else:
                        d = "You're not on a team!"

                    if isinstance(message.channel, discord.abc.PrivateChannel):
                        await message.channel.send(d)
                    else:
                        await message.channel.send(d, delete_after=5)

                        try:
                            await message.delete()
                        except discord.Forbidden:
                            pass
                else:
                    if command in flairs:
                        for role in teams:
                            if role in user.roles:
                                await user.remove_roles(role)

                        team = discord.utils.get(teams, name=flairs[command])
                        await user.add_roles(team)

                        if isinstance(message.channel, discord.abc.PrivateChannel):
                            await message.channel.send("You have joined {}.".format(team.name))
                        else:
                            await message.channel.send(
                                "You have joined {}.".format(team.name),
                                delete_after=5
                            )
                            try:
                                await message.delete()
                            except:
                                pass
        except Exception as e:
            if debug:
                raise e
            else:
                print("[ERROR] A bot-crashing error occured somewhere in the code.")

    def get_role_count(self, role_name, guild):
        team = discord.utils.get(guild.roles, name=role_name)
        count = len(
            list(
                filter(
                    lambda x: team in x.roles,
                    guild.members
                )
            )
        )
        return count


def setup(bot):
    bot.add_cog(Flairs(bot))
