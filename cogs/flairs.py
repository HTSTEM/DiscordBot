from discord.ext import commands
import discord

import asyncio
import os


FLAIRS = {
    184755239952318464: {
        'BFB': {
            'bettername': 376315776338100235,
            'deathpact': 376314992301047808,
            'freefood': 376316488228798466,
            'icecube': 376316300701728773,
            'losers': 376316879066628096,
            'iance': 376317160739438594,
            'beep': 376317479401553920,
            'bleh': (376318324910456834, ['8names', 'gabop', '6abop', 'babop', 'sabop']),
        },
        'TWOW': {
            'midnight': 334310926713094145,
            'meester': 334311173619056641,
            'yessoan': 334310796219908098,
        },
        'Spoilers': {
            'spoilers': (392842859931369483, ['spoilers', 'spoil', 'spoilme', 'spoil_me', 'spoiler', 'spoilerme', 'spoiler_me']),
            'spoilers_forever': (392847202575187970, ['spoil_forever', 'spoilforever', 'spoilersforever', 'sadama',
                                                      'spoilerforever', 'spoiler_forever', 'spoilers_forever']),
        },
        'Vote Spoilers': {
            'vote_spoilers': (397130936464048129, ['votespoilers', 'spoilvotes', 'spoilv', 'vspoilers', 'vspoil',
                                                   'spoil_votes', 'vote_spoilers', 'spoilervote', 'spoilervotes',
                                                   'votespoil', 'vote_spoil', 'spoiler_vote', 'spoiler_votes']),
        }
    },
    282219466589208576: {
        'Colors': {
            'blue': 373961580397985793,
            'teal': 373961640263155713,
            'olive': 445741953829830668,
            'green': 373961689269272586,
            'lime': 373961454606614528,
            'yellow': 373961846996205569,
            'orange': 373961743073935363,
            'red': 373961119657885696,
            'maroon': 445742065658363914,
            'fuchsia': 373961032898445312,
            'purple': 373960941802356746,
            'grey': 373961877996437505,
            'silver': 445742262584999947,
        },
        'Community': {
            'io': 451479507573145621,
        },
        'YouTube': {
            'youtube': 289942717419749377,
        }
    },
    381941901462470658: {
        'No Distraction': {
            'no-distraction': 434105424053141504,
        },
        'BFB': {
            'bfb': 388731042829434920,
        },
        'TTT': {
            'ttt': 386367707131674624,
        },
        'UHC': {
            'uhc': 383751709446373376,
        },
        'Jackbox': {
            'jackbox': 404123399611351060,
        },
        'Left 4 Dead': {
            'l4d': 393652774174195712,
        },
        'RPG': {
            'rpg': 391784480588824577,
        },
        'Payday': {
            'payday': 409499286079012864,
        },
        'Terraria': {
            'terraria': 409809297967415296,
        },
        'Midnight': {
            'mindnight': 410268466956730368,
        },
        'Games': {
            'games': 415251227186561034,
        }
    }
}


class Flairs:
    def __init__(self, bot):
        self.bot = bot

    async def safe_delete(self, ctx, after=5):
        async def _delete():
            await asyncio.sleep(after)
            if ctx.me.guild_permissions.manage_messages:
                await ctx.message.delete()

        asyncio.ensure_future(_delete(), loop=self.bot.loop)

    @commands.command()
    @commands.guild_only()
    async def listids(self, ctx):
        '''Get all of the IDs for the current server'''
        data = 'Your ID: {}\n\n'.format(ctx.author.id)

        data += 'Text Channel IDs:\n'
        for c in ctx.guild.channels:
            if isinstance(c, discord.TextChannel):
                data += '{}: {}\n'.format(c.name, c.id)

        data += '\nVoice Channel IDs:\n'
        for c in ctx.guild.channels:
            if isinstance(c, discord.VoiceChannel):
                data += '{}: {}\n'.format(c.name, c.id)

        data += '\nRole IDs:\n'
        for r in ctx.guild.roles:
            data += '{}: {}\n'.format(r.name, r.id)

        data += '\nUser IDs:\n'
        if ctx.guild.large:
            await self.bot.request_offline_members(ctx.guild)
        for msg in ctx.guild.members:
            data += '{}: {}\n'.format(msg.name, msg.id)

        filename = '{}-ids-all.txt'.format("".join([x if x.isalnum() else "_" for x in ctx.guild.name]))

        with open(filename, 'wb') as ids_file:
            ids_file.write(data.encode('utf-8'))

        await ctx.send(':mailbox_with_mail:')
        with open(filename, 'rb') as ids_file:
            await ctx.author.send(file=discord.File(ids_file))

        os.remove(filename)

    @commands.command(aliases=['listflairs'])
    @commands.guild_only()
    async def flairs(self, ctx):
        """List the available flairs for this server"""
        embed = discord.Embed(title='Available flairs:',
                              color=ctx.me.color.value)
        flairs = FLAIRS.get(ctx.guild.id)
        if flairs is None or len(flairs) == 0:
            embed.add_field(name='Error', value='No flairs setup')
        else:
            embed.description = f'*Use `{ctx.prefix}fclear [category '\
                                 '(optional)]` to remove your flairs.*'

            for f in flairs:
                embed.add_field(
                    name=f'*{f}*',
                    value='\n'.join(f'`{ctx.prefix}f {i}`' for i in flairs[f]),
                    inline=True)
        embed.set_footer(text=f'Requested by {ctx.author}')

        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def fclear(self, ctx, *, flair: str=''):
        """Remove all your flairs for this server"""
        await self.safe_delete(ctx)

        flairs = FLAIRS.get(ctx.guild.id)
        if flairs is None or len(flairs) == 0:
            return await ctx.send('No flairs setup', delete_after=5)

        if not ctx.me.guild_permissions.manage_roles:
            return await ctx.send('I don\'t have `Manage Roles` permission.',
                                  delete_after=5)

        if flair:
            for category in flairs:
                if category.lower() == flair.lower():
                    break
            else:
                return await ctx.send('No category found with that name.',
                                      delete_after=5)

            to_remove = []
            for f in flairs[category]:
                id_ = flairs[category][f]
                if isinstance(id_, tuple):
                    id_ = id_[0]
                role = discord.utils.get(ctx.guild.roles,
                                         id=id_)
                if role is not None:
                    to_remove.append(role)

            await ctx.author.remove_roles(*to_remove)

            return await ctx.send(f'All "{category}" flairs have been removed.',
                                  delete_after=5)
        else:
            to_remove = []

            for category in flairs:
                for f in flairs[category]:
                    role = discord.utils.get(ctx.guild.roles,
                                             id=flairs[category][f])
                    if role is not None:
                        to_remove.append(role)

            await ctx.author.remove_roles(*to_remove)

            return await ctx.send('All your flairs have been removed.',
                                  delete_after=5)

    @commands.command()
    @commands.guild_only()
    async def f_remove_all(self, ctx, *, flair: str):
        if not ctx.channel.permissions_for(ctx.author).manage_roles:
            await self.safe_delete(ctx)
            return

        flairs = FLAIRS.get(ctx.guild.id)
        if flairs is None or len(flairs) == 0:
            return await ctx.send('No flairs setup')

        if not ctx.me.guild_permissions.manage_roles:
            return await ctx.send('I don\'t have `Manage Roles` permission.')

        flat_flairs = [(i, flairs[category][i]) for category in flairs for i in flairs[category]]
        for flair_name, flair_id in flat_flairs:
            if isinstance(flair_id, tuple):
                if flair.lower() in [i.lower() for i in flair_id[1]]:
                    flair_id = flair_id[0]
                    break
            if flair_name.lower() == flair.lower():
                if isinstance(flair_id, tuple):
                    flair_id = flair_id[0]
                break
        else:
            return await ctx.send('No flair found with that name.')

        role = discord.utils.get(ctx.guild.roles, id=flair_id)

        if role is None:
            return await ctx.send(f'Failed to locate the role with id {flair_id}. Please check the configuration.')

        if ctx.guild.large:
            await ctx.bot.request_offline_members(ctx.guild)
        for member in ctx.guild.members:
            if role in member.roles:
                await member.remove_roles(role)

        return await ctx.send(f'The flair "{flair_name}" has been removed from every member.')

    @commands.command(aliases=['flair'])
    @commands.guild_only()
    async def f(self, ctx, *, flair: str=''):
        """Get a flair"""
        await self.safe_delete(ctx)

        flairs = FLAIRS.get(ctx.guild.id)
        if flairs is None or len(flairs) == 0:
            return await ctx.send('No flairs setup', delete_after=5)

        if not flair:
            return await ctx.send(f'I need to know what flair you want.. Use `{ctx.prefix}flairs` to list them all.',
                                  delete_after=5)

        if not ctx.me.guild_permissions.manage_roles:
            return await ctx.send('I don\'t have `Manage Roles` permission.', delete_after=5)

        flat_flairs = [(i, flairs[category][i], category) for category in flairs for i in flairs[category]]
        for flair_name, flair_id, category in flat_flairs:
            if isinstance(flair_id, tuple):
                if flair.lower() in [i.lower() for i in flair_id[1]]:
                    flair_id = flair_id[0]
                    break
            if flair.lower() == flair_name.lower():
                if isinstance(flair_id, tuple):
                    flair_id = flair_id[0]
                break
        else:
            return await ctx.send('No such flair available with that name.', delete_after=5)

        to_remove = []
        to_add = None
        for f in flairs[category]:
            if isinstance(flairs[category][f], tuple):
                id_ = flairs[category][f][0]
            else:
                id_ = flairs[category][f]
            role = discord.utils.get(ctx.guild.roles, id=id_)
            if id_ == flair_id:
                if role is None:
                    return await ctx.send('The flairs have be configured incorrectly; this flair is unavailable.',
                                          delete_after=5)
                to_add = role
            elif role is not None:
                to_remove.append(role)

        await ctx.author.remove_roles(*to_remove)
        await ctx.author.add_roles(to_add)

        return await ctx.send('You have been given the requested flair!', delete_after=5)


def setup(bot):
    bot.add_cog(Flairs(bot))
