import random

import discord
from discord.ext import commands


class Misc:
    @commands.command()
    async def roll(self, ctx, sides: int, how_many_dice: int = 1):
        '''Rolls a dice.'''
        if sides < 1 or how_many_dice < 1:
            return await ctx.send('Yeah, sorry, but you can\'t roll something that doesn\'t exist.')

        if sides > 100 and how_many_dice > 1:
            return await ctx.send('Woahh, that\'s a lot of sides. Try lowering it below 100?')
        elif how_many_dice > 30:
            return await ctx.send('Woahh, that\'s a lot of dice to roll. Try lowering it below 30?')

        if sides == 1:
            return await ctx.send('All {} of the 1-sided dice shocking rolled a 1.'.format(how_many_dice))

        # easter eggs
        if sides == 666:
            return await ctx.send('Satan rolled a nice {} for you.'.format(random.randint(1, sides)))
        elif sides == 1337:
            return await ctx.send('Th3 {}-51d3d d13 r0ll3d 4 {}.'.format(sides, random.randint(1, sides)))
        elif isinstance(ctx.channel, discord.abc.GuildChannel) and sides == ctx.guild.member_count:
            members = sorted(ctx.guild.members, key=lambda m: m.joined_at)
            rolled = random.randint(0, len(members) - 1)
            chosen = members[rolled]
            return await ctx.send('{}? That\'s how many users are on the server! Well, your die rolled a {}, '
                                  'and according to the cache, that member is `{}`.'.format(sides, rolled + 1,
                                                                                            chosen.name))
        result = ', '.join(str(random.randint(1, sides)) for i in range(how_many_dice))
        await ctx.send('The {} {}-sided {} rolled {}.'.format(how_many_dice, sides, 'die' if how_many_dice == 1 else 'dice', result))


def setup(bot):
    bot.add_cog(Misc())
