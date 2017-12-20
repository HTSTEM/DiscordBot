import discord


PREFIX = "s!"
HTC = 184755239952318464
SPOILER_ROLE = 392842859931369483


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
            if spoiler_role not in message.author.roles:
                await message.author.add_roles(spoiler_role)
                await message.channel.send('You can now view the spoilers channel.', delete_after=10)
            else:
                await message.channel.send('You already have access to the spoilers channel.', delete_after=10)
        elif command in ['remove']:
            if spoiler_role in message.author.roles:
                await message.author.remove_roles(spoiler_role)
                await message.channel.send('You can now no longer view the spoilers channel.', delete_after=10)
            else:
                await message.channel.send('You already don\'t have access to the spoilers channel.', delete_after=10)
        elif command in ['help']:
            msg  = f'**SpoilerBot Help:**\n'
            msg += f'- Type `{PREFIX}spoil_me` to gain access to spoilers.\n'
            msg += f'- Type `{PREFIX}remove` to loose access.'
            await message.channel.send(msg)


def setup(bot):
    bot.add_cog(Spoilers(bot))
