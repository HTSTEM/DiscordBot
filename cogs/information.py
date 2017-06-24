from collections import OrderedDict
import random

from discord.ext import commands
import discord


def format_fields(fields):
    string = '```ini\n'
    longest_field_name = max(len(t[0]) for t in fields) + 2 # [ ]
    for name, value in fields:
        name = '[{}]'.format(name.title())
        string += '{0: <{max}} {1}\n'.format(name, value, max=longest_field_name)
    string += '```'
    return string


class Information:
    '''
    Commands that tell useful information about miscellaneous things
    '''

    @commands.group(invoke_without_command=True)
    async def info(self, ctx):
        '''Tells you how to use the info command'''
        formatted = await ctx.bot.formatter.format_help_for(ctx, ctx.command)

        for page in formatted:
            await ctx.send(page)

    @info.command(aliases=['guild'])
    async def server(self, ctx):
        '''Info about the server'''
        guild = ctx.guild
        fields = [
            ('name', guild.name),
            ('id', guild.id),
            ('user count', guild.member_count),
            ('bots', sum(1 for member in guild.members if member.bot)),
            ('channels', len(guild.channels)),
            ('voice channels', len(guild.voice_channels)),
            ('roles', len(guild.roles)),
            ('owner', str(guild.owner)),
            ('created', guild.created_at.strftime('%x %X')),
            ('newest user', str(list(sorted(guild.members, key=lambda m: m.joined_at, reverse=True))[0])),
            ('emotes', len(guild.emojis)),
            ('icon', guild.icon_url)
        ]

        await ctx.send(format_fields(fields))

    @info.command()
    async def member(self, ctx, member: discord.Member = None):
        '''Info about yourself or a specific member'''
        member = member or ctx.author
        fields = [
            ('name', member.name),
            ('discriminator', member.discriminator),
            ('id', member.id),
            ('bot', 'Yes' if member.bot else 'No'),
            ('created', member.created_at.strftime('%x %X')),
            ('joined', member.joined_at.strftime('%x %X')),
            ('status', member.status),
            ('playing', member.game.name if member.game else 'Nothing'),
            ('colour', member.colour),
            ('highest role', member.top_role.name),
            ('avatar', member.avatar_url),
        ]

        await ctx.send(format_fields(fields))

    @commands.command(aliases=['mods', 'admins', 'moderators'])
    async def administrators(self, ctx):
        '''Lists all the moderators of the server'''
        # This is disgusting
        emotes = OrderedDict()
        emotes[discord.Status.online] = '<:online:328162997128134669>',
        emotes[discord.Status.idle] = '<:idle:328162996218232832>',
        emotes[discord.Status.dnd] = '<:dnd:328162995526041609>',
        emotes[discord.Status.offline] = '<:offline:328162996494794754>'
        members = sorted([m for m in ctx.guild.members if ctx.channel.permissions_for(m).manage_messages],
                         key=lambda m: list(emotes).index(m.status))

        bot_emoji = '<:bot:328162994746032129>'
        fmt = '{0}{1} {bot}\n'

        await ctx.send(''.join(fmt.format(m, emotes[m.status][0], bot=bot_emoji if m.bot else '') for m in members))

    @commands.command()
    async def usercount(self, ctx):
        '''Tells you how many users a server has'''
        await ctx.send('{0.name} has {0.member_count} members.'.format(ctx.guild))

    @commands.command()
    async def randomuser(self, ctx):
        '''Chooses a random user from the server'''
        members = sorted(ctx.guild.members, key=lambda m: m.joined_at)

        chosen = random.choice(members)
        joined = list(members).index(chosen)

        def ordinal(n):
            return str(n) + 'tsnrhtdd'[(n / 10 % 10 != 1) * (n % 10 < 4) * n % 10::4]

        await ctx.send('Randomly chose {} who is the {} member to join the server'.format(chosen, ordinal(joined + 1)))


def setup(bot):
    bot.add_cog(Information())
