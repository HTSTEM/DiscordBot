import discord


PREFIX = "s!"
HTC = 184755239952318464
SPOILER_ROLE = 392842859931369483
SADAMA_ROLE = 392847202575187970


class Spoilers:
    def __init__(self, bot):
        self.bot = bot

    async def on_message(self, message):
        if (not message.content.startswith(PREFIX)) or message.content.startswith(PREFIX * 2):
            return
        if message.guild is None or message.guild.id != HTC:
            return

        command = message.content.split(' ')[0][len(PREFIX):].lower()

        spoiler_role = discord.utils.get(message.guild.roles, id=SPOILER_ROLE)
        sadama_role = discord.utils.get(message.guild.roles, id=SADAMA_ROLE)

        if command in ['spoilerwall', 'spoiler_wall']:
            if message.channel.permissions_for(message.author).manage_channels:
                if message.guild.large:
                    await self.bot.request_offline_members(message.guild)
                for member in message.guild.members:
                    if spoiler_role in member.roles:
                        await member.remove_roles(spoiler_role)

                await message.channel.send('Spoiler wall raised!')
            else:
                pass  # You can't do this, suckah'
        elif command in ['spoilers', 'spoil', 'spoilme', 'spoil_me', 'access']:
            if spoiler_role not in message.author.roles and sadama_role not in message.author.roles:
                await message.author.add_roles(spoiler_role)
                await message.channel.send('You can now view the spoilers channel.', delete_after=10)
            else:
                await message.channel.send('You already have access to the spoilers channel.', delete_after=10)

        elif command in ['spoil_forever', 'spoilforever']:
            def check(m):
                if not m.content: return False
                is_author = m.author == message.author
                is_channel = m.channel == message.channel
                return is_author and is_channel

            await ctx.send('Are you **sure** you want to do this? You will have this role **forever**. (Type `y` to continue)', delete_after=10)
            response_message = await ctx.bot.wait_for('message', check=check)
            if response_message.content.lower() != 'y':
                return message.channel.send('Aborted.', delete_after=10)

            if spoiler_role in message.author.roles:
                await message.author.remove_roles(spoiler_role)
            if sadama_role not in message.author.roles:
                await message.author.add_roles(sadama_role)
                await message.channel.send('You can now view the spoilers channel forever.', delete_after=10)
            else:
                await message.channel.send('You already have access to the spoilers channel forever.', delete_after=10)

        elif command in ['remove']:
            if spoiler_role in message.author.roles or sadama_role in message.author.roles:
                await message.author.remove_roles(spoiler_role, sadama_role)
                await message.channel.send('You can now no longer view the spoilers channel.', delete_after=10)
            else:
                await message.channel.send('You already don\'t have access to the spoilers channel.', delete_after=10)
        elif command in ['help']:
            msg  = f'**SpoilerBot Help:**\n'
            msg += f'- Type `{PREFIX}spoil_me` to gain access to spoilers.\n'
            msg += f'- Type `{PREFIX}spoil_forever` to gain access to spoilers forever.\n'
            msg += f'- Type `{PREFIX}remove` to revoke access.'
            await message.channel.send(msg)


def setup(bot):
    bot.add_cog(Spoilers(bot))
