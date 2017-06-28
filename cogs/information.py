import collections
import random

from discord.ext import commands
import discord
import psutil
import git


def format_fields(fields):
    string = '```ini\n'
    longest_field_name = max(len(t[0]) for t in fields) + 2
    for name, value in fields:
        name = '[{}]'.format(name.title())
        string += '{0:<{max}} {1}\n'.format(name, value, max=longest_field_name)
    string += '```'
    return string


class Information:
    '''Commands that tell useful information about miscellaneous things'''

    @commands.command()
    async def about(self, ctx):
        '''Info about the bot'''
        def format_commit(commit):
            sha = commit.hexsha[0:6]
            repo = 'https://github.com/HTSTEM/discord-bot/commit/{}'
            return '[`{}`]({}) {}'.format(sha, repo.format(commit.hexsha), commit.message.splitlines()[0])
        repo = git.Repo()
        commits = list(repo.iter_commits(repo.active_branch, max_count=3))
        log = '\n'.join(map(format_commit, commits))
        memory_usage = round(psutil.Process().memory_full_info().uss / 1024 ** 2, 2)

        embed = discord.Embed(title='About HTStem Bote', description=log)
        embed.add_field(name='Memory Usage', value='{} MB'.format(memory_usage))

        await ctx.send(embed=embed)

    @commands.command(aliases=['contributors'])
    async def credits(self, ctx):
        '''Views credits!'''
        await ctx.channel.trigger_typing()
        contributors = []

        repo = git.Repo()

        for commit in repo.iter_commits(repo.active_branch):
            contributors.append(commit.author.name.replace(' <>', ''))

        # max fields in an embed is 25
        contributors = collections.Counter(contributors).most_common(25)

        embed = discord.Embed(title='Contributors to HTSTEM-Bote')
        for contributor, commits in contributors:
            plural = '' if commits == 1 else 's'
            embed.add_field(name=contributor, value='{} contribution{}'.format(commits, plural))

        # fill rest with blank fields
        leftover = len(contributors) % round(len(contributors) / 3)
        for _ in range(leftover):
            embed.add_field(name='\u200b', value='\u200b')

        await ctx.send(embed=embed)

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

    @commands.command(aliases=['whois'])
    @commands.guild_only()
    async def userinfo(self, ctx, member: str = ''):
        '''Info about yourself or a specific member'''
        def levenshtein(s1, s2):
            if len(s1) < len(s2):
                return levenshtein(s2, s1)

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

        if ctx.message.mentions:
            member = ctx.message.mentions[0]
        elif not member:
            member = ctx.author
        else:
            usr = ctx.author
            closest = -1
            for m in ctx.guild.members:
                d = levenshtein(member.lower(), m.name.lower())
                if member.lower() in m.name.lower() and (closest == -1 or d < closest):
                    closest = d
                    usr = m
            member = usr

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

        status_emoji = {
            discord.Status.online: '<:online:328659633147215884>',
            discord.Status.idle: '<:idle:328670650220806144>',
            discord.Status.dnd: '<:dnd:328659633109598208>',
            discord.Status.offline: '<:offline:328659633214324757>'
        }

        mods_by_status = collections.defaultdict(list)
        mods = (m for m in ctx.guild.members if ctx.channel.permissions_for(m).manage_channels)

        for mod in mods:
            mods_by_status[mod.status] += [mod]

        # Wow this is such a stupid hack
        def predicate(item):
            status = str(item[0])
            return 'online idle dnd offline'.split().index(status)

        sorted_mods = collections.OrderedDict(sorted(mods_by_status.items(), key=predicate))
        message = ''
        for status, mods in sorted_mods.items():
            # header
            title = 'DND' if status is discord.Status.dnd else status.name.title()
            message += '**{} {} moderators:**\n'.format(status_emoji[status], title)

            # body
            message += '\n'.join(['{0.display_name} ({0})'.format(mod) for mod in sorted(mods, key=lambda m: m.name)]) + '\n\n'

        # Prevent pings
        await ctx.send(message.replace('@', '@\u200b'))

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
