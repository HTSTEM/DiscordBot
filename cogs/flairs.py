from discord.ext import commands
import discord

import asyncio


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
            'bleh': 376318324910456834,
        },
        'TWOW': {
            'midnight': 334310926713094145,
            'meester': 334311173619056641,
            'yessoan': 334310796219908098,
        },
    },
    282219466589208576: {
        'Colors': {
            'chestnut': 373961754650345493,
            'magenta': 373961032898445312,
            'celtic': 376823314909495307,
            'orange': 373961743073935363,
            'purple': 373960941802356746,
            'yellow': 373961846996205569,
            'green': 373961689269272586,
            'blue': 373961580397985793,
            'grey': 373961877996437505,
            'lime': 373961454606614528,
            'pink': 376345385603563521,
            'teal': 373961640263155713,
            'red': 373961119657885696,
        },
        'YouTube': {
            'youtube': 289942717419749377,
        }
    },
    381941901462470658: {
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
                    inline=False)
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
                role = discord.utils.get(ctx.guild.roles,
                                         id=flairs[category][f])
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

    @commands.command(aliases=['flair'])
    @commands.guild_only()
    async def f(self, ctx, *, flair: str=''):
        """Get a flair"""
        await self.safe_delete(ctx)

        flairs = FLAIRS.get(ctx.guild.id)
        if flairs is None or len(flairs) == 0:
            return await ctx.send('No flairs setup', delete_after=5)

        if not flair:
            return await ctx.send('I need to know what flair you want.. '
                                  f'Use `{ctx.prefix}flairs` to list them all.',
                                  delete_after=5)

        if not ctx.me.guild_permissions.manage_roles:
            return await ctx.send('I don\'t have `Manage Roles` permission.',
                                  delete_after=5)

        for category in flairs:
            if flair in flairs[category]:
                break
        else:
            return await ctx.send('No such flair avaliable with that name.',
                                  delete_after=5)

        to_remove = []
        to_add = None
        for f in flairs[category]:
            role = discord.utils.get(ctx.guild.roles, id=flairs[category][f])
            if f == flair:
                if role is None:
                    return await ctx.send('The flairs have be configured '
                                          'incorrectly; this flair is '
                                          'unavaliable.',
                                          delete_after=5)
                to_add = role
            elif role is not None:
                to_remove.append(role)

        await ctx.author.remove_roles(*to_remove)
        await ctx.author.add_roles(to_add)

        return await ctx.send('You have been given the requested flair!',
                              delete_after=5)


def setup(bot):
    bot.add_cog(Flairs(bot))
