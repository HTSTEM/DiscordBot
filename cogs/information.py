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
    async def moderators(self, ctx):
        '''Lists all the moderators of the server'''
        
        members = sorted([m for m in ctx.guild.members if ctx.channel.permissions_for(m).manage_channels],
                         key=lambda m: m.display_name)

        offline_mods = []
        idle_mods = []
        dnd_mods = []
        online_mods = []
        
        for m in members:
            if m.status == discord.Status.online:
                online_mods.append(m)
            elif m.status == discord.Status.idle:
                idle_mods.append(m)
            elif m.status == discord.Status.dnd:
                dnd_mods.append(m)
            else:
                offline_mods.append(m)
        
        out_message = ""
        if online_mods:
            out_message += ":green_heart: **Online Moderators:**\n"
            for i in online_mods:
                out_message += "{} ({}#{})\n".format(i.display_name, i.name, i.discriminator)
        if idle_mods:
            out_message += ":large_orange_diamond: **Idle Moderators:**\n"
            for i in idle_mods:
                out_message += "{} ({}#{})\n".format(i.display_name, i.name, i.discriminator)
        if dnd_mods:
            out_message += ":large_orange_diamond: **DND Moderators:**\n"
            for i in dnd_mods:
                out_message += "{} ({}#{})\n".format(i.display_name, i.name, i.discriminator)
        if offline_mods:
            out_message += ":red_circle: **Offline Moderators:**\n"
            for i in offline_mods:
                out_message += "{} ({}#{})\n".format(i.display_name, i.name, i.discriminator)
        
        await ctx.send(out_message)
        
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
            return str(n) + 'ᵗˢⁿʳʰᵗᵈᵈ'[(n / 10 % 10 != 1) * (n % 10 < 4) * n % 10::4]

        await ctx.send('Your random user of the day is {} who was the {} member to join the server.'.format(chosen, ordinal(joined + 1)))


def setup(bot):
    bot.add_cog(Information())
