import random

from discord.ext import commands


class Misc:
    @commands.command()
    async def roll(self, ctx, sides: int, number: int):
        '''Rolls a dice.'''
        await ctx.send(', '.join(str(random.randint(1, sides)) for i in range(number)))


def setup(bot):
    bot.add_cog(Misc())
