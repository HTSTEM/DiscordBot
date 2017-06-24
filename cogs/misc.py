import random

from discord.ext import commands


class Misc:
    @commands.command()
    async def roll(self, ctx, dice: str):
        '''Roll dice in NdN format'''
        # Taken from the discord.py repository examples
        try:
            dice, sides = map(int, dice.split('d'))
        except:
            await ctx.send('Format has to be in NdN.')
            return

        await ctx.send(', '.join(str(random.randint(1, sides)) for i in range(dice)))


def setup(bot):
    bot.add_cog(Misc())
