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

    @commands.command(aliases=['guildinfo'])
    @commands.guild_only()
    async def serverinfo(self, ctx):
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

    @commands.command()
    @commands.guild_only()
    async def userinfo(self, ctx, member: discord.Member = None):
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

    @commands.command(aliases=['mods', 'list_mods', 'listmods'])
    @commands.guild_only()
    async def moderators(self, ctx):
        '''Lists all the moderators of the server'''
        
        members = sorted([m for m in ctx.guild.members if ctx.channel.permissions_for(m).manage_channels],
                         key=lambda m: m.display_name)

        offline_mods = [m for m in members if m.status == discord.Status.offline]
        idle_mods = [m for m in members if m.status == discord.Status.idle]
        dnd_mods = [m for m in members if m.status == discord.Status.dnd]
        online_mods = [m for m in members if m.status == discord.Status.online]

        out_message = ''

        def format(mod_list, emoji, descriptor):
            nonlocal out_message
            if not mod_list:
                return
            out_message += '{} **{} Moderators:**\n'.format(emoji, descriptor)
            for mod in mod_list:
                out_message += '\N{BULLET} {} ({})\n'.format(mod.display_name, mod)
            out_message += '\n'

        format(online_mods, '\N{GREEN HEART}', 'Online')
        format(idle_mods, '\N{LARGE ORANGE DIAMOND}', 'Idle')
        format(dnd_mods, '\N{BLACK DIAMOND SUIT}', 'DND')
        format(offline_mods, '\N{LARGE RED CIRCLE}', 'Offline')

        await ctx.send(out_message)
        
    @commands.command()
    @commands.guild_only()
    async def usercount(self, ctx):
        '''Tells you how many users a server has'''
        await ctx.send('{0.name} has {0.member_count} members.'.format(ctx.guild))

    @commands.command()
    @commands.guild_only()
    async def randomuser(self, ctx):
        '''Chooses a random user from the server'''
        members = sorted(ctx.guild.members, key=lambda m: m.joined_at)

        chosen = random.choice(members)
        joined = list(members).index(chosen)

        def ordinal(n):
            return str(n) + 'ᵗˢⁿʳʰᵗᵈᵈ'[(n / 10 % 10 != 1) * (n % 10 < 4) * n % 10::4]

        await ctx.send('Your random user of the day is {} who was the {} member to join the server.'.format(chosen, ordinal(joined + 1)))


def setup(bot):
    bot.add_cog(Information())
